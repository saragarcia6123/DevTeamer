from datetime import timedelta
from fastapi import Cookie, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from lib.jwt import TokenPayload, parse_jwt, set_access_token_cookie
from lib.crypto import verify_password
from services.pg_client import pg_client
from models import User
from config import _Config

config = _Config()

ACCESS_TOKEN_EXPIRES = timedelta(days=14)
JWT_ALGORITHM = "HS256"

UnauthorizedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unauthorized.",
)

UserNotFoundException = HTTPException(
    detail="User not found",
    status_code=404
)


def authenticate_user(identifier: str, password: str) -> User:

    # 1. Check not already authenticated

    try:
        currentUser = get_current_user()
        if (currentUser):
            raise HTTPException(400, "Already authenticated.")
    except HTTPException:
        pass

    user: User | None = pg_client.get_user(identifier)

    GenericException = HTTPException(400, 'Authentication error.')

    # 2. Check user exists

    if not user:
        if config.DEBUG:
            raise HTTPException(
                status_code=404,
                detail=f'User with email or username {identifier} not found.'
            )
        else:
            raise GenericException

    # 3. Check password matches

    password_ok = verify_password(password, user.hashed_password)

    if not password_ok:
        if config.DEBUG:
            raise HTTPException(
                status_code=400,
                detail="Invalid password"
            )
        else:
            raise GenericException

    # 4. Check user is verified

    if not user.verified:
        raise HTTPException(
            status_code=403,
            detail='User not yet verified. Please check your email.'
        )
    return user


def get_current_user(
    access_token: str | None = Cookie(default=None, include_in_schema=False)
):
    jwt_data: TokenPayload = parse_jwt(access_token)
    username = jwt_data.get('sub')
    if username is None:
        raise UnauthorizedException

    user = pg_client.get_user(username)
    if not user:
        raise UnauthorizedException
    return user


def get_user_from_jwt(token: str) -> User:
    jwt_data: TokenPayload = parse_jwt(token)
    identifier = jwt_data.get('sub')
    user = pg_client.get_user(identifier)
    if not user:
        raise 
    return user


def response_or_redirect(
    access_token: str | None,
    redirect_uri: str | None,
    message: str,
    status: int
):
    response = None
    if redirect_uri:
        url = f"{redirect_uri}?message={message}&status={status}"
        response = RedirectResponse(url)
    else:
        if status == 200:
            response = Response(message, 200)
        else:
            raise HTTPException(
                status_code=status,
                detail=message
            )

    if access_token:
        set_access_token_cookie(response, access_token)
    return response
