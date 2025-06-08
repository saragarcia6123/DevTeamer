from datetime import datetime, timedelta, timezone
from typing import Literal, Union
from fastapi import Cookie, HTTPException, Response, status
import jwt
from jwt.exceptions import InvalidTokenError
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from password_validator import PasswordValidator
from dotenv import load_dotenv
import os
from db import DB
from models import User

load_dotenv()

DEBUG = os.getenv("DEBUG")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
EMAIL_TOKEN_EXPIRES = timedelta(minutes=60)
JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = DB()

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
    return pwd_context.hash(password)

def authenticate_user(identifier: str, password: str) -> User:
    user = db.get_user(identifier)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(400, 'Authentication error.')

    if not user.verified:
        raise HTTPException(403, 'User not yet verified. Please check your email.')
    
    return user

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRES
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    access_token: str | None = Cookie(default=None, include_in_schema=False)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized.",
    )
    if access_token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.get_user(username)
    if not user:
        raise credentials_exception
    
    return user

def normalize_email(email: str) -> str | EmailNotValidError:
    try:
        emailinfo = validate_email(email)
        return emailinfo.normalized
    except EmailNotValidError as e:
        return e

def generate_email_verify_token(email: str) -> str:
    expire = datetime.now() + EMAIL_TOKEN_EXPIRES
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def extract_email_from_jwt(token: str) -> str | None:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    email = payload.get("sub")
    return email

def get_verification_link(base_url: str, token: str, redirect_uri: str):
    return f"{base_url.rstrip('/')}/api/auth/verify?token={token}&redirectUri={redirect_uri}"
    
def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(ACCESS_TOKEN_EXPIRES.total_seconds()),
        secure=not DEBUG,
        samesite="none" if DEBUG else "strict",
    )

def validate_password(password: str):

    if PasswordValidator().spaces().validate(password):
        return "Password cannot contain spaces."
    
    ILLEGAL_SYMBOLS = [';', '|', '&', '$', '<', '>']

    if any(s in password for s in ILLEGAL_SYMBOLS):
        return f"Password cannot contain any of {', '.join(ILLEGAL_SYMBOLS)}"
    
    MIN_CHARS = 8
    MAX_CHARS = 50

    if not PasswordValidator().min(MIN_CHARS).validate(password):
        return f"Password must be at least {MIN_CHARS} characters long."
    if not PasswordValidator().max(MAX_CHARS).validate(password):
        return f"Password must be no more than {MAX_CHARS} characters long."
    
    if not PasswordValidator().lowercase().validate(password):
        return "Password must contain a lowercase letter."
    if not PasswordValidator().uppercase().validate(password):
        return "Password must contain an uppercase letter."
    
    if not PasswordValidator().digits().validate(password):
        return "Password must contain a digit."
    if not PasswordValidator().symbols().validate(password):
        return "Password must contain a special symbol."
    
    return False