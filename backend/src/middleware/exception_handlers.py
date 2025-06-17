from fastapi import HTTPException, Request
from models.response import BaseResponse
from lib.jwt import delete_access_token_cookie
from lib.http_exception import UserNotFoundException


async def http_exception_handler(request: Request, exc: HTTPException):
    return BaseResponse.error(exc.detail, exc.status_code).to_json_response()


async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    response = BaseResponse.error(exc.detail, exc.status_code).to_json_response()

    if exc.clear_cookie:
        delete_access_token_cookie(response)

    return response
