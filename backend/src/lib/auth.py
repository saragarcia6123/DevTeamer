from fastapi import Cookie, Depends, HTTPException, Response
from sqlmodel import Session
from services.pg_client import depends_get_db, get_user
from logger import get_api_logger
from lib.http_exception import (
    AuthenticationException,
    IncorrectPasswordException,
    UnverifiedException,
    UserNotFoundException,
)
from lib.jwt import TokenPayload, parse_jwt
from lib.crypto import verify_password
from models import User
from config import _Config

config = _Config()


def require_authenticated(
    db: Session = Depends(depends_get_db),
    access_token: str | None = Cookie(default=None, include_in_schema=False),
) -> User:
    try:
        user: User = get_user_from_token(db, access_token)
        return user
    except UserNotFoundException as e:
        if access_token:
            get_api_logger().info(f"Deleting access token {access_token[:3]}***")
            e.clear_cookie = True
        raise e


def require_unauthenticated(
    db: Session = Depends(depends_get_db),
    access_token: str | None = Cookie(default=None, include_in_schema=False),
) -> None:
    try:
        get_user_from_token(db, access_token)
        raise HTTPException(status_code=403, detail="Already authenticated.")
    except Exception:
        return None


def user_exists(db: Session, identifier: str):
    user = get_user(db, identifier)
    return bool(user)


def is_user_verified(db: Session, identifier: str):
    user = get_user(db, identifier)
    if not user:
        raise UserNotFoundException
    return bool(user.verified)


def validate_credentials(db: Session, identifier: str, password: str) -> User:
    user: User | None = get_user(db, identifier)

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


def get_user_from_token(db: Session, access_token: str | None):
    jwt_data: TokenPayload = parse_jwt(access_token)
    username = jwt_data.get("sub")
    if username is None:
        raise UserNotFoundException
    user: User | None = get_user(db, username)
    if not user:
        raise UserNotFoundException
    return user
