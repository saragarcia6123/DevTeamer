from json import JSONDecodeError
import json

from fastapi import Request

from logger import get_app_logger
from lib.utils import get_client_ip
from models.response import BaseResponse


async def custom_interceptor(request: Request, call_next):
    # Check for duplicate request first
    duplicate_response = await check_duplicate_request(request)
    if duplicate_response:
        return duplicate_response.to_json_response()

    response = await call_next(request)
    original_headers = dict(response.headers)

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        response_data = json.loads(body.decode())
        get_app_logger().info(response_data)

        # Check if FastAPI error response
        if "detail" in response_data and len(response_data) == 1:
            base_response = BaseResponse.error(
                detail=response_data["detail"], status=response.status_code
            )
        else:
            # Custom response
            if "detail" not in response_data:
                response_data["detail"] = "Something went wrong"
            if "status" not in response_data:
                response_data["status"] = response.status_code
            if "meta" not in response_data:
                response_data["meta"] = {}

            base_response = BaseResponse(**response_data)

        await store_request(request, base_response)

        new_response = base_response.to_json_response()
        for key, value in original_headers.items():
            if key.lower() not in ["content-length", "content-type"]:
                new_response.headers[key] = value

        return new_response

    except (JSONDecodeError, UnicodeDecodeError):
        wrapped = BaseResponse.error(detail="Invalid response format")
        await store_request(request, wrapped)
        return wrapped.to_json_response()


async def check_duplicate_request(request: Request):
    from services.redis_client import redis_client

    ip = get_client_ip(request)
    last_request_key = f"{ip}_LAST_REQUEST"

    last_request = await redis_client.r.get(last_request_key)
    if last_request:
        # Return cached response for duplicate
        response = BaseResponse(**json.loads(last_request))
        response.meta["cached"] = "true"
        return response

    return None


async def store_request(request: Request, base_response: BaseResponse):
    from services.redis_client import redis_client

    ip = get_client_ip(request)
    last_request_key = f"{ip}_LAST_REQUEST"
    last_request_expiry_px = 250

    await redis_client.r.set(
        last_request_key, base_response.model_dump_json(), px=last_request_expiry_px
    )
