from datetime import datetime, timedelta, timezone
import re
from typing import Literal
from fastapi import Cookie, HTTPException, Response, status
from fastapi.responses import RedirectResponse
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from password_validator import PasswordValidator
from db_client import DBClient
from models import User
from config import Config

config = Config()

ACCESS_TOKEN_EXPIRES = timedelta(days=14)
JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = DBClient()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
    return pwd_context.hash(password)

def authenticate_user(identifier: str, password: str) -> User:

    # 1. Check not already authenticated

    try:
        currentUser = get_current_user()
        if (currentUser):
            raise HTTPException(400, "Already authenticated.")
    except HTTPException:
        pass

    user: User | None = db.get_user(identifier)

    GenericException = HTTPException(400, 'Authentication error.')

    # 2. Check user exists

    if not user:
        if config.DEBUG:
            raise HTTPException(404, f'User with email or username {identifier} not found.')
        else:
            raise GenericException
    
    # 3. Check password matches

    password_ok = verify_password(password, user.hashed_password)

    if not password_ok:
        if config.DEBUG:
            raise HTTPException(400, "Invalid password")
        else:
            raise GenericException

    # 4. Check user is verified

    if not user.verified:
        raise HTTPException(403, 'User not yet verified. Please check your email.')
    
    return user

def _encode_jwt(to_encode: dict) -> str:
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_jwt_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRES
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = _encode_jwt(to_encode)
    return encoded_jwt

def create_jwt_email_verification_token(email: str, expires_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = _encode_jwt(to_encode)
    return encoded_jwt

def get_current_user(
    access_token: str | None = Cookie(default=None, include_in_schema=False)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized.",
    )
    if access_token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(access_token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.get_user(username)
    if not user:
        raise credentials_exception
    
    return user

def normalize_email(email: str) -> str:
    try:
        emailinfo = validate_email(email)
        return emailinfo.normalized.lower()
    except EmailNotValidError as e:
        raise e


def extract_email_from_jwt(token: str) -> str | None:
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    email = payload.get("sub")
    return email

def _get_link(endpoint: str, base_url: str, token: str, redirect_uri: str | None):
    link = f"{base_url.rstrip('/')}/api/auth/{endpoint}?token={token}"
    if redirect_uri:
        link = f"{link}&redirectUri={redirect_uri}"
    return link

def get_verification_link(base_url: str, token: str, redirect_uri: str | None):
    return _get_link("verify", base_url, token, redirect_uri)

def get_2fa_link(base_url: str, token: str, redirect_uri: str | None):
    return _get_link("verify-login", base_url, token, redirect_uri)
    
def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(ACCESS_TOKEN_EXPIRES.total_seconds()),
        secure=not config.DEBUG,
        samesite="lax" if config.DEBUG else "none",
    )

def validate_username(username: str):
    """Ensure only alphanumeric and underscore usernames"""
    return re.match(r'^[a-zA-Z0-9_]{3,}$', username)

def validate_password(password: str):
    """Enforce strict password requirements"""

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

def get_user_from_jwt(token: str) -> User:
    """
    Attempts to read email from jwt payload
    Then looks up user by email in the database
    Will throw HTTPException if any errors occur
    """
    try:
        email = extract_email_from_jwt(token)
        if not email:
            raise HTTPException(400, "Token payload missing email.")
        
        user = db.get_user_by_email(email)
        
        if not user:
            raise HTTPException(404, "User not found.")

        return user
    except ExpiredSignatureError:
        raise HTTPException(400, "Verification token has expired.")
    except InvalidTokenError:
        raise HTTPException(400, "Invalid verification token.")
    except Exception as e:
        raise HTTPException(500, e)

def response_or_redirect(
    access_token: str | None,
    redirect_uri: str | None,
    message: str,
    status: int
):
    response = None
    if redirect_uri:
        response = RedirectResponse(url=f"{redirect_uri}?message={message}&status={status}")
    else:
        if status == 200:
            response = Response(message, 200)
        else:
            raise HTTPException(status_code=status, detail=message)
    
    if access_token:
        set_access_token_cookie(response, access_token)
    return response