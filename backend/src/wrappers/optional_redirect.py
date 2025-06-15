import functools
from typing import Any
from urllib.parse import urlencode
from collections.abc import Callable, Awaitable
from fastapi import HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from models.response import BaseResponse


def get_redirect_url(redirect_uri: str, message: str, status: int) -> str:
    """Generate redirect URL with message and status parameters."""
    params = {"message": message, "status": str(status)}
    return f"{redirect_uri}?{urlencode(params)}"


def optional_redirect(f: Callable[..., Awaitable[BaseResponse]]) -> Callable:
    """
    Decorator that optionally redirects based on redirectUri query parameter.
    If redirectUri is provided, redirects with status and message.
    Otherwise, returns the normal response or raises the exception.
    """

    @functools.wraps(f)
    async def response_or_redirect(
        *args,
        request: Request,
        response: Response,
        redirect_uri: str | None = Query(None, alias="redirectUri"),
        **kwargs,
    ) -> BaseResponse | RedirectResponse:

        try:
            # Call the original function (don't pass request/response unless it expects them)
            base_response: BaseResponse[Any] = await f(*args, **kwargs)

            # If no redirect URI provided, return normal response
            if not redirect_uri:
                return base_response

            # Create redirect URL with success message
            url = get_redirect_url(
                redirect_uri, base_response.detail, base_response.status
            )

        except HTTPException as e:
            if not redirect_uri:
                raise e

            # Create redirect URL with error message
            url = get_redirect_url(redirect_uri, str(e.detail), e.status_code)

        except Exception as e:
            if not redirect_uri:
                raise e

            # Create redirect URL with generic error message
            url = get_redirect_url(redirect_uri, "Internal server error", 500)

        redirect_response = RedirectResponse(
            url=url,
            status_code=302,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
            },
        )

        # Copy cookies ie. JWT
        for cookie in response.raw_headers:
            if cookie[0].lower() == b"set-cookie":
                redirect_response.raw_headers.append(cookie)

        return redirect_response

    return response_or_redirect
