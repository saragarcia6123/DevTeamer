from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from models import Token, UserCreate, UserRead, User
from db import DB
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    normalize_email,
    ACCESS_TOKEN_EXPIRES,
)

users_router = APIRouter()
auth_router = APIRouter()

db = DB()

@users_router.get('/me', response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@users_router.post('/register')
async def register(user: UserCreate) -> Token | dict:
    emailNormalized = normalize_email(user.email)
    if (not isinstance(emailNormalized, str)):
        return {'error': emailNormalized.__str__(), 'status': 400}
    hashed_password = get_password_hash(user.password)
    user: User = User(
        **user.model_dump(exclude={"email", "password"}),
        email=emailNormalized,
        hashed_password=hashed_password
    )
    user: User = db.insert_user(user)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=ACCESS_TOKEN_EXPIRES
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post("/auth")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    user: Optional[User] = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=ACCESS_TOKEN_EXPIRES
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # secure=True,
        # samesite="strict",
        max_age=int(ACCESS_TOKEN_EXPIRES.total_seconds())
    )
    
    return {"message": "Authenticated."}