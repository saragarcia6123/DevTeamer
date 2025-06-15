from typing import Annotated
from fastapi import APIRouter, Depends, Query

from services.pg_client import pg_client
from lib.http_exception import UserNotFoundException
from lib.auth import authenticate, user_exists
from models import BaseResponse, User, UserRead

users_router = APIRouter()


@users_router.get("/get-current", response_model=BaseResponse[UserRead])
async def get_current_user(
    current_user: Annotated[User, Depends(authenticate)],
):
    return BaseResponse[UserRead].ok(data=UserRead(**current_user.model_dump()))


@users_router.get("/check-exists", response_model=BaseResponse[str])
async def get_user_exists(username: str = Query(...)):
    exists: bool = user_exists(username)
    return BaseResponse[str].ok(data=str(exists).lower())


@users_router.get("/{username}", response_model=BaseResponse[UserRead])
async def get_user_by_username(
    current_user: Annotated[User, Depends(authenticate)], username: str
):
    user = pg_client.get_user_by_username(username)
    if not user:
        raise UserNotFoundException
    return BaseResponse[UserRead].ok(data=UserRead(**user.model_dump()))
