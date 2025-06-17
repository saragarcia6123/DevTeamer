from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from services.pg_client import depends_get_db, get_user, get_user_by_email, get_user_by_username, insert_user, update_user
from logger import get_api_logger
from models import BaseResponse, UserCreate, UserRead, User

from lib.http_exception import UserNotFoundException
from lib.jwt import delete_access_token_cookie, issue_access_token, issue_verify_token, set_access_token_cookie
from lib.links import get_2fa_link, get_verification_link
from lib.utils import get_client_ip, mask_email, now
from lib.crypto import hash_password
from lib.auth import get_user_from_token, require_authenticated, require_unauthenticated, validate_credentials

from services.redis_client import redis_client
from services.rate_limit import enforce_email_action_cooldown
from services.email_client import send_2fa_email, send_verification_email

from config import config

api_logger = get_api_logger()
r = redis_client.r

auth_router = APIRouter()


@auth_router.post("/register", response_model=BaseResponse[UserRead])
async def register(
    _: Annotated[None, Depends(require_unauthenticated)],
    request: Request,
    user: UserCreate,
    db: Session = Depends(depends_get_db),
    client_url: str | None = Query(None, alias="clientUrl"),
):
    if get_user_by_email(db, user.email.lower()):
        raise HTTPException(409, "A user with that email already exists.")

    if get_user_by_username(db, user.username):
        raise HTTPException(409, "A user with that username already exists.")

    hashed_password: str = hash_password(user.password)

    api_logger.debug(
        f"HASHED PASSWORD ({mask_email(user.email)}): {hashed_password[:3]}***"
    )

    db_user = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        verified=False
    )

    db_user: User = insert_user(db, db_user)

    base_url = str(request.base_url).rstrip("/")
    token = issue_verify_token(user.email)

    verification_link: str = get_verification_link(
        base_url=base_url, token=token, client_url=client_url
    )  # goes to /verify

    if not config.DEBUG:
        api_logger.info(f"Sending verification email to {user.email}")
        send_verification_email(user.email, verification_link)
        message = """User registered successfully.
            Please verify your account using the link
            sent to your email address."""
    else:
        message = verification_link

    user_read = UserRead(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        verified=db_user.verified
    )
    return BaseResponse[UserRead].ok(
        detail=message,
        data=user_read,
    )


@auth_router.get("/resend-verification", response_model=BaseResponse[None])
async def resend_verification_email(
    _: Annotated[None, Depends(require_unauthenticated)],
    request: Request,
    username: str,
    db: Session = Depends(depends_get_db),
    client_url: str | None = Query(None, alias="clientUrl"),
):
    user: User | None = get_user(db, username)
    if not user:
        raise UserNotFoundException

    if user.verified:
        return BaseResponse.ok("User already verified.")

    await enforce_email_action_cooldown(user.email, "VERIFY")

    base_url = str(request.base_url).rstrip("/")
    token = issue_verify_token(user.email)
    verification_link = get_verification_link(
        base_url=base_url, token=token, client_url=client_url
    )  # goes to /verify

    if not config.DEBUG:
        send_verification_email(user.email, verification_link)
        return BaseResponse.ok(f"A link has been sent to {user.email}.")
    else:
        return BaseResponse.ok(verification_link)


@auth_router.get("/verify", response_model=BaseResponse[None])
async def verify(
    _: Annotated[User, Depends(require_unauthenticated)],
    db: Session = Depends(depends_get_db),
    access_token: str = Query(..., alias="token"),
):
    """
    Endpoint to verify JWT sent from /register
    """
    user: User = get_user_from_token(db, access_token)

    if user.verified:
        return BaseResponse.ok("User already verified.")

    user.verified = True
    update_user(db, user)

    return BaseResponse.ok("Email verified. You may now log in.")


@auth_router.post("/login", response_model=BaseResponse[None])
async def request_login(
    _: Annotated[None, Depends(require_unauthenticated)],
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(depends_get_db),
    client_url: str | None = Query(None, alias="clientUrl"),
):
    user: User = validate_credentials(db, form_data.username, form_data.password)

    # Proceed to 2fa
    token = issue_access_token(user.email)
    await r.set(token, "UNUSED", ex=300)  # 5 minutes

    verification_link = get_2fa_link(
        base_url=str(request.base_url).rstrip("/"),
        token=token,
        client_url=client_url,
    )  # goes to /verify-login


    await enforce_email_action_cooldown(user.email, "LOGIN")

    # Don't send emails in debug
    if not config.DEBUG:
        send_2fa_email(user.email, verification_link)
        return BaseResponse.ok(
            "Please login using the link sent to your email address."
        )
    else:
        return BaseResponse.ok(verification_link)


@auth_router.get("/confirm-login", response_model=BaseResponse[None])
async def confirm_login(
    _: Annotated[None, Depends(require_unauthenticated)],
    request: Request,
    response: Response,
    token: str,
    db: Session = Depends(depends_get_db),
):
    """
    Endpoint to verify JWT sent from /login
    """

    # Ensure login token is only used once
    token_state: str = await r.get(token)

    # if token_state and token_state.startswith("USED"):
    #     raise HTTPException(409, "This link has already been used.")

    if not token_state:
        raise HTTPException(400, "Invalid or expired token.")

    user: User = get_user_from_token(db, token)

    access_token = issue_access_token(user.email)
    api_logger.debug(f"ACCESS TOKEN: {access_token[:5]}...")

    set_access_token_cookie(response, access_token)

    timestamp = now().timestamp

    ip = get_client_ip(request)
    ip = ip if ip else "UNKNOWN"

    await r.set(token, f"USED - {ip} - {timestamp}")

    return BaseResponse.ok("Authenticated.")


@auth_router.post("/logout", response_model=BaseResponse[None])
async def logout(
    _: Annotated[User, Depends(require_authenticated)],
    request: Request,
    response: Response,
):
    """Disinjects jwt"""
    delete_access_token_cookie(response)
    return BaseResponse.ok(detail="Logged out.")
