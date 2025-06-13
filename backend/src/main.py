from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import config


# Load environment variables
config.init()


@asynccontextmanager
async def lifespan(app: FastAPI):

    from services.pg_client import pg_client
    from services.redis_client import redis_client

    # Initialize PostgreSQL
    pg_client.init()
    # Initialize Redis
    redis_client.init()

    from routes import api_router

    app.include_router(api_router, prefix='/api')

    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
