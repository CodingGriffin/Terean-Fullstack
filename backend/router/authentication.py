import logging
import uuid
from datetime import timedelta
from typing import Annotated

import hashlib
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from jose import JWTError
from backend.crud.user_crud import get_user_by_username, get_user_by_id, create_user, \
    get_all_users
from backend.database import get_db
from backend.schemas.user_schema import UserCreate, User
from backend.schemas.auth_schema import UserPasswordChange
from backend.utils.authentication import decode_jwt, oauth2_scheme, authenticate_user, \
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, create_access_token, verify_token, \
    get_current_user, check_permissions, SECRET_KEY, ALGORITHM, verify_password, hash_password
from backend.models.user_model import UserDBModel

logger = logging.getLogger(__name__)

authentication_router = APIRouter()


@authentication_router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    return current_user


@authentication_router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    psig = hashlib.sha256(user.hashed_password.encode()).hexdigest()[:16]

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": f"username:{user.username}",
            "id": user.id,
            "username": user.username,
            "disabled": user.disabled,
            "auth_level": user.auth_level,
            "email": user.email,
            "psig": psig,
            "jti": str(uuid.uuid4()),
        },
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(
        data={
            "sub": f"username:{user.username}",
            "id": user.id,
            "username": user.username,
            "disabled": user.disabled,
            "auth_level": user.auth_level,
            "email": user.email,
            "psig": psig,
            "jti": str(uuid.uuid4()),
        },
        expires_delta=refresh_token_expires
    )

    # Include user data in the response
    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@authentication_router.post("/refresh-token")
async def refresh_access_token(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Parse request body
        logger.info("Refreshing token: Start")
        logger.info(f"Refreshing token: Request: {request}")
        request_body = await request.body()
        logger.info(f"Refreshing token: Request body: {request_body}")
        data = await request.json()
        logger.info(f"Refreshing token: Got data")
        token = data.get("token")
        logger.info(f"Refreshing token: {token}")

        # Read the token data
        try:
            payload = decode_jwt(token)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired",
            ) from e

        # Get the user from the database
        user = get_user_by_id(db, id=payload.get("id"))

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

        # Create a new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": f"username:{user.username}",
                "id": user.id,
                "username": user.username,
                "disabled": user.disabled,
                "auth_level": user.auth_level,
                "email": user.email,
                "psig": psig,
                "jti": str(uuid.uuid4()),
            },
            expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_access_token(
            data={
                "sub": f"username:{user.username}",
                "id": user.id,
                "username": user.username,
                "disabled": user.disabled,
                "auth_level": user.auth_level,
                "email": user.email,
                "psig": psig,
                "jti": str(uuid.uuid4()),
            },
            expires_delta=refresh_token_expires
        )

        return JSONResponse(
            content={
                "message": "Token refreshed successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
    except Exception as e:
        logger.warning(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@authentication_router.get("/protected-resource")
async def protected_resource(
    current_user: Annotated[User, Depends(get_current_user)]
):
    required_auth_level = 2
    check_permissions(current_user, required_auth_level)
    return {"message": "You have access to this protected resource!"}


@authentication_router.put("/change-password")
async def change_password(
    data: UserPasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    user_db = db.query(UserDBModel).filter(UserDBModel.username == current_user.username).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.current_password, user_db.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    user_db.hashed_password = hash_password(data.new_password)

    db.add(user_db)
    db.commit()

    return {"message": "Password changed successfully"}
