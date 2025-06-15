from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm

from lib.utils import mask_email
from logger import get_api_logger
from wrappers.block_authenticated import block_authenticated
from models import BaseResponse, UserCreate, UserRead, User

from wrappers.optional_redirect import optional_redirect

from lib.http_exception import UserNotFoundException
from lib.jwt import issue_access_token, issue_verify_token, set_access_token_cookie
from lib.links import get_2fa_link, get_verification_link
from lib.crypto import hash_password
from lib.auth import (
    get_user_from_token,
    validate_credentials,
)

from services.pg_client import pg_client
from services.redis_client import redis_client
from services.rate_limit import enforce_email_action_cooldown
from services.email_client import send_2fa_email, send_verification_email

from config import config

api_logger = get_api_logger()
r = redis_client.r

auth_router = APIRouter()


@block_authenticated
@auth_router.post("/register", response_model=BaseResponse[UserRead])
@optional_redirect
async def register(
    request: Request,
    response: Response,
    user: UserCreate,
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    if pg_client.get_user_by_email(user.email.lower()):
        raise HTTPException(409, "A user with that email already exists.")

    if pg_client.get_user_by_username(user.username):
        raise HTTPException(409, "A user with that username already exists.")

    hashed_password: str = hash_password(user.password)

    api_logger.debug(
        f"HASHED PASSWORD ({mask_email(user.email)}): {hashed_password[:3]}***"
    )

    db_user: User = User(
        **user.model_dump(exclude={"email", "password", "username"}),
        email=user.email.lower(),
        hashed_password=hashed_password,
        username=user.username.lower(),
        verified=False,
    )

    db_user: User = pg_client.insert_user(db_user)

    base_url = str(request.base_url).rstrip("/")
    token = issue_verify_token(user.email)

    verification_link: str = get_verification_link(
        base_url=base_url, token=token, redirect_uri=redirect_uri
    )  # goes to /verify

    if not config.DEBUG:
        api_logger.info(f"Sending verification email to {user.email}")
        send_verification_email(user.email, verification_link)
        message = """User registered successfully.
            Please verify your account using the link
            sent to your email address."""
        data = UserRead(**user.model_dump())
    else:
        message = verification_link
        data = UserRead(**user.model_dump())

    return BaseResponse[UserRead].ok(
        detail=message,
        data=data,
    )


@block_authenticated
@auth_router.get("/resend-verification", response_model=BaseResponse[None])
async def resend_verification_email(
    request: Request,
    response: Response,
    username: str,
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    user: User | None = pg_client.get_user(username)
    if not user:
        raise UserNotFoundException

    if user.verified:
        return BaseResponse.ok("User already verified.")

    await enforce_email_action_cooldown(user.email, "VERIFY")

    base_url = str(request.base_url).rstrip("/")
    token = issue_verify_token(user.email)
    verification_link = get_verification_link(
        base_url=base_url, token=token, redirect_uri=redirect_uri
    )  # goes to /verify

    if not config.DEBUG:
        send_verification_email(user.email, verification_link)
        return BaseResponse.ok(f"A link has been sent to {user.email}.")
    else:
        return BaseResponse.ok(verification_link)


@block_authenticated
@auth_router.get("/verify", response_model=BaseResponse[None], include_in_schema=False)
@optional_redirect
async def verify(
    request: Request,
    response: Response,
    access_token: str = Query(..., alias="token"),
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    """
    Endpoint where verification link sent to user
    after registration directs to.
    """
    user: User = get_user_from_token(access_token)

    if user.verified:
        return BaseResponse.ok("User already verified.")

    user.verified = True
    pg_client.update_user(user)

    return BaseResponse.ok("Email verified. You may now log in.")


@block_authenticated
@auth_router.post("/login", response_model=BaseResponse[None])
async def request_login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    user: User = validate_credentials(form_data.username, form_data.password)

    await enforce_email_action_cooldown(user.email, "LOGIN")

    # Proceed to 2fa
    token = issue_access_token(user.email)
    await r.set(token, "UNUSED", ex=300)  # 5 minutes

    verification_link = get_2fa_link(
        base_url=str(request.base_url).rstrip("/"),
        token=token,
        redirect_uri=redirect_uri,
    )

    # Don't send emails in debug
    if not config.DEBUG:
        send_2fa_email(user.email, verification_link)
        return BaseResponse.ok(
            "Please login using the link sent to your email address."
        )
    else:
        return BaseResponse.ok(verification_link)


@block_authenticated
@auth_router.get(
    "/verify-login", response_model=BaseResponse[None], include_in_schema=False
)
@optional_redirect
async def verify_login(
    request: Request,
    response: Response,
    token: str,
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    """
    Endpoint where 2fa link sent to user after login directs to.
    """

    try:
        # Ensure login token is only used once
        token_state = await r.get(token)
        if token_state != "UNUSED":
            raise HTTPException(409, "Token invalid or already used.")

        user: User = get_user_from_token(token)
        access_token = issue_access_token(user.email)
        api_logger.debug(f"ACCESS TOKEN: {access_token[:5]}...")

        set_access_token_cookie(response, access_token)
        return BaseResponse.ok("Authenticated.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    finally:
        await r.getdel(token)


@auth_router.post("/logout", response_model=BaseResponse[None])
@optional_redirect
async def logout(
    request: Request,
    response: Response,
    redirect_uri: str | None = Query(None, alias="redirectUri"),
):
    """Disinjects jwt"""
    response.delete_cookie(key="access_token")
    return BaseResponse.ok(detail="Logged out.")
