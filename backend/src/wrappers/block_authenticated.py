import functools
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException

from lib.http_exception import UserNotFoundException
from lib.auth import get_user_from_token
from models.response import BaseResponse


def require_unauthenticated(
    access_token: str | None = Cookie(default=None, include_in_schema=False)
) -> BaseResponse[None] | None:
    try:
        get_user_from_token(access_token)
        raise HTTPException(status_code=403, detail="Already authenticated.")
    except UserNotFoundException:
        return None


def block_authenticated(func):
    @functools.wraps(func)
    async def wrapper(
        *args,
        unauthenticated: Annotated[
            BaseResponse[None] | None, Depends(require_unauthenticated)
        ],
        **kwargs
    ):
        if unauthenticated:
            return unauthenticated
        return await func(*args, **kwargs)

    return wrapper
