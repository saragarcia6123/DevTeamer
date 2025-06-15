import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config

logging.getLogger("passlib").setLevel(logging.ERROR)

if config.DEBUG:
    print(f"ALLOW ORIGINS: {config.ALLOW_ORIGINS}")

app = FastAPI()


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


from routes.auth import auth_router
from routes.users import users_router

app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")
