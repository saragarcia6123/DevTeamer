import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from logger import get_app_logger, get_api_logger, get_postgres_logger, get_redis_logger


logging.getLogger("passlib").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_app_logger()
    logger.info("Starting app...")

    import config
    from services import pg_client, redis_client

    from routes.auth import auth_router
    from routes.users import users_router

    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(users_router, prefix="/api/users")

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


@app.get("/")
async def root():
    app_logger.info("Root endpoint called")
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config="log_conf.yaml")
