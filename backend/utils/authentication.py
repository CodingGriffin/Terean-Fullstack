import logging
from datetime import timedelta, datetime, timezone
from typing import Annotated
import uuid

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import bcrypt
if not hasattr(bcrypt, '__about__'):
    ## Fix issue with passlib depending on about, which was removed in 4.2
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})

from backend.models.user_model import UserDBModel
from backend.schemas.user_schema import User as UserSchema

# Your JWT secret and algorithm
SECRET_KEY = "M3wYVjqjYnJlrHcEDBnR5RunLQ_b7xsMrePSWwiccFQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240
REFRESH_TOKEN_EXPIRE_MINUTES = 240
SALT = "adsefaestdfaADFDSVZXCWEsgfatgs"
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
        token: Annotated[str, Depends(oauth2_scheme)]
) -> UserSchema:
    payload = decode_jwt(token)
    print(payload)
    decoded_user = UserSchema(
        username=payload.get("username"),
        disabled=payload.get("disabled"),
        auth_level=payload.get("auth_level"),
        email=payload.get("email"),
        full_name=payload.get("full_name"),
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