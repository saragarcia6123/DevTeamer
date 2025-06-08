from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError

from models import Token, UserCreate, UserRead, User, UserExists
from db import DB
from auth import (
    extract_email_from_jwt,
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_verification_link,
    normalize_email,
    generate_email_verify_token,
    set_access_token_cookie,
    validate_password,
    ACCESS_TOKEN_EXPIRES,
)
from email_client import send_verification_email

api_router = APIRouter()

db = DB()

@api_router.get('/users/me', response_model=UserRead)
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@api_router.get("/users/exists", response_model=UserExists)
async def user_exists(username: str | None = Query(None)):
    if not username:
        raise HTTPException(status_code=400, detail="Must provide a username/email")
    
    user = db.get_user(username)
    return {"exists": user and user is not None}

@api_router.get("/users/@{username}", response_model=UserRead)
async def get_user_by_username(username: str):
    user = db.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.post('/auth/register')
async def register(user: UserCreate, request: Request, redirect_uri: str = Query(...)) -> dict:
    email_normalized = normalize_email(user.email)
    
    if (not isinstance(email_normalized, str)):
        raise HTTPException(400, email_normalized.__str__())
    
    if db.get_user_by_email(user.email):
        raise HTTPException(409, 'A user with that email already exists.')
    
    if len(user.username) < 3:
        raise HTTPException(400, 'Username must be at least 3 characters long.')

    weak_password = validate_password(user.password)

    if weak_password:
        raise HTTPException(400, weak_password)
    
    hashed_password = get_password_hash(user.password)

    user: User = User(
        **user.model_dump(exclude={"email", "password"}),
        email=email_normalized,
        hashed_password=hashed_password,
        verified=False
    )

    user: User = db.insert_user(user)

    base_url = str(request.base_url).rstrip('/')
    token = generate_email_verify_token(email_normalized)
    verification_link = get_verification_link(base_url, token, redirect_uri)
    
    send_verification_email(email_normalized, verification_link)
    
    return {"message": "User registered successfully. Please verify your account using the link sent to your email address."}

@api_router.get('/auth/verify')
async def verify(
    response: Response,
    token: str,
    redirect_uri: str = Query(..., alias="redirectUri")
):
    message = ""
    status = 500
    user = None

    try:
        email = extract_email_from_jwt(token)
        if not email:
            message = "Token payload missing email."
            status = 400
        else:
            user = db.get_user_by_email(email)
            if not user:
                message = "User not found."
                status = 404
            elif user.verified:
                message = "User already verified."
                status = 200
            else:
                user.verified = True
                db.update_user(user)
                message = "Email verified."
                status = 200

        if user and user.verified:
            access_token = create_access_token(data={"sub": user.username})
            set_access_token_cookie(response, access_token)

    except ExpiredSignatureError:
        message = "Verification token has expired."
        status = 400
    except InvalidTokenError:
        message = "Invalid verification token."
        status = 400
    except Exception as e:
        message = str(e)
        status = 500

    encoded_redirect_uri = f"{redirect_uri}?message={message}&status={status}"
    return RedirectResponse(url=encoded_redirect_uri)

@api_router.post("/auth/login")
async def jwt_login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user: Optional[User] = authenticate_user(form_data.username, form_data.password)
    
    access_token = create_access_token(data={"sub": user.username})
    set_access_token_cookie(response, access_token)
    
    return {"message": "Authenticated."}

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}