import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from middleware.custom_interceptor import custom_interceptor
from middleware.exception_handlers import http_exception_handler, user_not_found_handler
from lib.http_exception import UserNotFoundException
from models.response import BaseResponse
from logger import get_app_logger

logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_app_logger()
    logger.info("Starting app...")

    import config
    from services import pg_client, redis_client

    db = pg_client.get_db()
    pg_con = pg_client.test_connection(db)
    if not pg_con:
        raise HTTPException(503, "PostgreSQL connection failed.")

    redis_con = await redis_client.redis_client.test_connection()
    if not redis_con:
        raise HTTPException(503, "Redis connection failed.")

    from routes.auth import auth_router
    from routes.users import users_router

    app.include_router(auth_router, prefix="/auth")
    app.include_router(users_router, prefix="/users")


    yield


app = FastAPI(lifespan=lifespan)

import os
from dotenv import load_dotenv

load_dotenv()

ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS")
if not ALLOW_ORIGINS:
    ALLOW_ORIGINS = ""

ALLOW_ORIGINS = ALLOW_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_logger = get_app_logger()


@app.exception_handler(UserNotFoundException)
async def _user_not_found_handler(request: Request, exc: UserNotFoundException):
    return await user_not_found_handler(request, exc)


@app.exception_handler(HTTPException)
async def _http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.middleware("http")
async def _custom_interceptor(request: Request, call_next):
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)
    return await custom_interceptor(request, call_next)


@app.get("/")
async def root():
    app_logger.info("Root endpoint called")
    return BaseResponse.ok("DevTeamer API")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config="log_conf.yaml")
