from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session

from services.pg_client import depends_get_db, get_user_by_username
from logger import get_api_logger
from lib.http_exception import UserNotFoundException
from lib.auth import is_user_verified, require_authenticated, user_exists
from models import BaseResponse, User, UserRead

users_router = APIRouter()


@users_router.get("/get-current", response_model=BaseResponse[UserRead])
async def get_current_user(
    response: Response,
    current_user: Annotated[User, Depends(require_authenticated)],
):
    return BaseResponse[UserRead].ok(data=UserRead(**current_user.model_dump()))


@users_router.get("/check-exists", response_model=BaseResponse[str])
async def get_user_exists(db: Session = Depends(depends_get_db), username: str = Query(...)):
    exists: bool = user_exists(db, username)
    get_api_logger().info(f"USER {username} EXISTS: {exists}")
    return BaseResponse[str].ok(data=str(exists).lower())


@users_router.get("/check-verified", response_model=BaseResponse[str])
async def get_user_verified_status(
    db: Session = Depends(depends_get_db), username: str = Query(...)
):
    verified: bool = is_user_verified(db, username)
    get_api_logger().info(f"USER {username} VERIFIED: {verified}")
    return BaseResponse[str].ok(data=str(verified).lower())


@users_router.get("/{username}", response_model=BaseResponse[UserRead])
async def route_get_user_by_username(
    response: Response,
    username: str,
    current_user: Annotated[User, Depends(require_authenticated)],
    db: Session = Depends(depends_get_db),
):
    user = get_user_by_username(db, username)
    if not user:
        raise UserNotFoundException
    return BaseResponse[UserRead].ok(data=UserRead(**user.model_dump()))
