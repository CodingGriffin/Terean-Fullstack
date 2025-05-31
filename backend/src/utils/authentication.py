import logging
import os
from datetime import timedelta, datetime, timezone
from typing import Annotated
import uuid
import hashlib

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import jwt, JWTError
from starlette import status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import bcrypt
if not hasattr(bcrypt, '__about__'):
    ## Fix issue with passlib depending on about, which was removed in 4.2
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})

from database import get_db
from models.user_model import UserDBModel
from schemas.user_schema import User as UserSchema
from config import settings

logger = logging.getLogger(__name__)

# Your JWT secret and algorithm
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
SALT = settings.PASSWORD_SALT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password + SALT)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password + SALT, hashed_password)


def decode_jwt(token, secret=SECRET_KEY, algorithms=None) -> dict:
    if algorithms is None:
        algorithms = [ALGORITHM]
    return jwt.decode(token, secret, algorithms)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserSchema:
    # Read the token data
    try:
        payload = decode_jwt(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        ) from e

    # Get the user from the database
    user = db.query(UserDBModel).filter(UserDBModel.id == payload.get("id")).first()

    # Check if the user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if the user is disabled
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    psig = hashlib.sha256(user.hashed_password.encode()).hexdigest()[:16]

    # Verify login related token data matches the database
    if user.username != payload.get("username"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token username has changed.")

    if user.auth_level != payload.get("auth_level"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token auth_level has changed.")

    if user.email != payload.get("email"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token email has changed.")

    if psig != payload.get("psig"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has changed passwords.")

    decoded_user = UserSchema(
        auth_level=user.auth_level,
        disabled=user.disabled,
        email=user.email,
        full_name=user.full_name,
        id=user.id,
        username=user.username,
    )

    return decoded_user


# New helper function to check permissions
def check_permissions(user: UserSchema, required_auth_level: int):
    if user.auth_level < required_auth_level:
        raise HTTPException(status_code=403, detail="Insufficient permissions")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(token)
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=403,
                                detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403,
                            detail="Token is invalid or expired")


# Authenticate the user
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(UserDBModel).filter(UserDBModel.username == username).first()
    if not user:
        return False
    if not verify_password(password, str(user.hashed_password)):
        return False
    return user

#Check auth level for admin and users for routes
def require_auth_level(required_auth_level: int):
    def permission_dependency(current_user: UserSchema = Depends(get_current_user)) -> UserSchema:
        if current_user.auth_level < required_auth_level:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_dependency

# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Create access token
def create_access_token_v2(
        data: dict,
        expires_delta: timedelta | None = None,
        refresh: bool = False,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt