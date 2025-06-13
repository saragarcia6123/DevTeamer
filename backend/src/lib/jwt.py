from datetime import datetime, timedelta
from typing import Any, TypedDict, cast
from fastapi import HTTPException, Response
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, MissingRequiredClaimError

from lib import time
from config import config


JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = timedelta(days=14)
VERIFY_TOKEN_EXPIRES = timedelta(hours=24)


class TokenPayloadRaw(TypedDict):
    sub: str
    iat: int
    exp: int


class TokenPayload(TypedDict):
    sub: str
    iat: datetime
    exp: datetime


def _encode_jwt(payload: TokenPayloadRaw) -> str:
    encoded_jwt = jwt.encode(
        payload=cast(dict[str, Any], payload),
        key=config.SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
    return encoded_jwt


def issue_jwt(
    subject: str,
    expires: datetime
) -> str:
    to_encode: TokenPayloadRaw = {
        "sub": subject,
        "iat": int(time.now().timestamp()),
        "exp": int(expires.timestamp())
    }
    encoded_jwt = _encode_jwt(to_encode)
    return encoded_jwt


def issue_access_token(identifier: str) -> str:
    expires = time.now() + ACCESS_TOKEN_EXPIRES
    encoded_jwt = issue_jwt(identifier, expires)
    return encoded_jwt


def issue_verify_token(identifier: str,) -> str:
    expires = time.now() + VERIFY_TOKEN_EXPIRES
    encoded_jwt = issue_jwt(identifier, expires)
    return encoded_jwt


def _decode_jwt(
    token: str | None
) -> TokenPayloadRaw:
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    try:
        payload: TokenPayloadRaw = jwt.decode(
            jwt=token,
            key=config.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp"]}
        )
        return payload
    except MissingRequiredClaimError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing claim: {e.claim}"
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Verification token has expired."
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token."
        )


def parse_jwt(token: str | None) -> TokenPayload:
    payload_raw: TokenPayloadRaw = _decode_jwt(token)

    subject: str = payload_raw.get("sub")
    issued_at_str: int = payload_raw.get("iat")
    expires_str: int = payload_raw.get("exp")

    issued_at: datetime = (
        datetime.fromtimestamp(issued_at_str)
    )

    expires: datetime = (
        datetime.fromtimestamp(expires_str)
    )

    payload: TokenPayload = {
        "sub": subject,
        "iat": issued_at,
        "exp": expires
    }

    return payload


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(ACCESS_TOKEN_EXPIRES.total_seconds()),
        secure=not config.DEBUG,
        samesite="lax" if config.DEBUG else "none",
    )
