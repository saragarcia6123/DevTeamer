from fastapi import Cookie, HTTPException
from models.response import BaseResponse
from lib.http_exception import (
    AuthenticationException,
    IncorrectPasswordException,
    UnverifiedException,
    UserNotFoundException,
)
from lib.jwt import TokenPayload, parse_jwt
from lib.crypto import verify_password
from services.pg_client import _PGClient
from models import User
from config import _Config

config = _Config()
pg_client = _PGClient()


def authenticate(
    access_token: str | None = Cookie(default=None, include_in_schema=False)
):
    return get_user_from_token(access_token)


def user_exists(identifier: str):
    user = pg_client.get_user(identifier)
    return bool(user)


def validate_credentials(identifier: str, password: str) -> User:
    user: User | None = pg_client.get_user(identifier)

    # Check user exists
    if not user:
        if config.DEBUG:
            raise UserNotFoundException
        else:
            raise AuthenticationException

    # Check password matches
    password_ok = verify_password(password, user.hashed_password)

    if not password_ok:
        if config.DEBUG:
            raise IncorrectPasswordException
        else:
            raise AuthenticationException

    # Check user is verified
    if not user.verified:
        raise UnverifiedException

    return user


def get_user_from_token(access_token: str | None):
    jwt_data: TokenPayload = parse_jwt(access_token)
    username = jwt_data.get("sub")
    if username is None:
        raise UserNotFoundException
    user: User | None = pg_client.get_user(username)
    if not user:
        raise UserNotFoundException
    return user
