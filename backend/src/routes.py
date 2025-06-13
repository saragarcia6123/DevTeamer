from datetime import datetime
from typing import Annotated
from email_validator import EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from lib.time import now
from models import UserCreate, UserRead, User, UserExists
from services.pg_client import pg_client
from services.redis_client import redis_client

from auth import (
    get_2fa_link,
    get_password_hash,
    authenticate_user,
    create_jwt_access_token,
    get_current_user as auth_current_user,
    get_verification_link,
    normalize_email,
    create_jwt_email_verification_token,
    response_or_redirect,
    validate_password,
    validate_username,
    get_user_from_jwt,
)
from services.email_client import send_2fa_email, send_verification_email
from config import config

api_router = APIRouter()

r = redis_client.r


@api_router.get('/users/get-current', response_model=UserRead)
async def get_current_user(
    current_user: Annotated[User, Depends(auth_current_user)],
):
    return current_user


@api_router.get("/users/check-exists", response_model=UserExists)
async def user_exists(username: str | None = Query(None)):
    if not username:
        raise HTTPException(
            status_code=400,
            detail="Must provide a username/email"
        )

    user = pg_client.get_user(username)
    return {"exists": bool(user)}


@api_router.get("/users/{username}", response_model=UserRead)
async def get_user_by_username(
    _: Annotated[User, Depends(auth_current_user)],
    username: str
):
    user = pg_client.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api_router.post('/auth/register')
async def register(
    request: Request,
    user: UserCreate,
    redirect_uri: str | None = Query(None)
) -> dict:
    try:
        currentUser = auth_current_user()
        if (currentUser):
            raise HTTPException(400, "Please logout before registering.")
    except (HTTPException):
        pass

    try:
        email_normalized = normalize_email(user.email)
    except EmailNotValidError as e:
        raise HTTPException(400, e.__str__())

    if pg_client.get_user_by_email(email_normalized):
        raise HTTPException(409, 'A user with that email already exists.')

    if pg_client.get_user_by_username(user.username):
        raise HTTPException(409, 'A user with that username already exists.')

    if not validate_username(user.username):
        raise HTTPException(
            status_code=400,
            detail=(
                "Username must only contain",
                "alphanumeric characters and underscores,",
                "and be at least 3 characters long."
            )
        )

    weak_password = validate_password(user.password)

    if weak_password:
        raise HTTPException(400, weak_password)

    hashed_password = get_password_hash(user.password)

    db_user: User = User(
        **user.model_dump(exclude={"email", "password", "username"}),
        email=email_normalized,
        hashed_password=hashed_password,
        username=user.username.lower(),
        verified=False
    )

    db_user: User = pg_client.insert_user(db_user)

    base_url = str(request.base_url).rstrip('/')
    token = create_jwt_email_verification_token(email_normalized, 30)
    verification_link = get_verification_link(
        base_url=base_url,
        token=token,
        redirect_uri=redirect_uri
    )  # goes to /verify

    if not config.DEBUG:
        send_verification_email(email_normalized, verification_link)
        return {
            "message": (
                "User registered successfully.",
                "Please verify your account using the link",
                "sent to your email address."
            )
        }
    else:
        return {"message": verification_link}


@api_router.get('/auth/resend-verification')
async def resend_verification_email(
    request: Request,
    username: str,
    redirect_uri: str | None = Query(None),
):
    user: User | None = pg_client.get_user(username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Could not find a user with that email or username"
        )

    if user.verified:
        return {"message": "User already verified."}

    COOLDOWN_SECONDS = 60

    # Check last resend request
    last_request_time_key = f"{user.email}_LAST_VERIFY_REQUEST"
    last_request_time_str = await r.get(last_request_time_key)

    if last_request_time_str:
        last_request_time = datetime.fromisoformat(
            last_request_time_str.decode()
        )
        time_since_last = (now() - last_request_time).total_seconds()

        if time_since_last < COOLDOWN_SECONDS:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Please wait",
                    f"{int(COOLDOWN_SECONDS - time_since_last)}",
                    "seconds before requesting again."
                )
            )

    # Update Redis with new timestamp
    await r.set(last_request_time_key, now().isoformat(), ex=COOLDOWN_SECONDS)

    base_url = str(request.base_url).rstrip('/')
    token = create_jwt_email_verification_token(user.email, 30)
    verification_link = get_verification_link(
        base_url=base_url,
        token=token,
        redirect_uri=redirect_uri
    )  # goes to /verify

    if not config.DEBUG:
        send_verification_email(user.email, verification_link)
        return {"message": f"A link has been sent to {user.email}."}
    else:
        return {"message": verification_link}


@api_router.get('/auth/verify')
async def verify(
    token: str,
    redirect_uri: str | None = Query(
        default=None,
        alias="redirectUri"
    )
):
    """
    Endpoint where verification link sent to user
    after registration directs to.
    """

    message = ""
    status = 500
    user = None

    try:
        user = get_user_from_jwt(token)

        if user.verified:
            message = "User already verified."
            status = 200
        else:
            # Mark user as verified
            user.verified = True
            pg_client.update_user(user)

            message = "Email verified. You may now log in."
            status = 200
    except HTTPException as e:
        message = e.detail
        status = e.status_code

    return response_or_redirect(None, redirect_uri, message, status)


@api_router.post("/auth/login")
async def request_login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    redirect_uri: str | None = Query(None, alias='redirectUri'),
):
    # Will throw exception if error or User is None
    user: User = authenticate_user(form_data.username, form_data.password)

    email_normalized = normalize_email(user.email)

    base_url = str(request.base_url).rstrip('/')

    # Proceed to 2fa
    token = create_jwt_email_verification_token(
        email=email_normalized,
        expires_minutes=5
    )
    await r.set(token, "UNUSED")  # set token unused

    verification_link = get_2fa_link(
        base_url=base_url,
        token=token,
        redirect_uri=redirect_uri
    )

    # Don't send emails in debug
    if not config.DEBUG:
        send_2fa_email(email_normalized, verification_link)
        return {
            "message": (
                "Please login using the link sent to your email address."
            )
        }
    else:
        return {"message": verification_link}


@api_router.get("/auth/verify-login")
async def verify_login(
    token: str,
    redirect_uri: str | None = Query(None, alias='redirectUri'),
):
    """
    Endpoint where 2fa link sent to user after login directs to.
    """

    message = ""
    status = 500
    access_token = ""

    try:
        # Ensure login token is only used once
        token_state = await r.get(token)
        if token_state != "UNUSED":
            raise HTTPException(409, "Token invalid or already used.")

        user = get_user_from_jwt(token)
        access_token = create_jwt_access_token(data={"sub": user.email})

        message = "Logged in"
        status = 200
    except HTTPException as e:
        if not redirect_uri:
            raise e

        # catch the error for redirects
        message = e.detail
        status = e.status_code
    finally:
        await r.delete(token)

    return response_or_redirect(access_token, redirect_uri, message, status)


@api_router.post("/auth/logout")
async def logout(response: Response):
    """Disinjects jwt"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}
