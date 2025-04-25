import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from backend.crud.user_crud import get_user_by_username, create_user, \
    get_all_users
from backend.database import get_db
from backend.schemas.user_schema import UserCreate, User
from backend.schemas.auth_schema import UserPasswordChange
from backend.utils.authentication import authenticate_user, \
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_token, \
    get_current_user, check_permissions, SECRET_KEY, ALGORITHM, verify_password, hash_password
from backend.models.user_model import UserDBModel


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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": f"username:{user.username}",
            "username": user.username,
            "disabled": user.disabled,
            "auth_level": user.auth_level,
            "email": user.email,
            "full_name": user.full_name,
            "jti": str(uuid.uuid4()),
        },
        expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={
            "sub": f"username:{user.username}",
            "username": user.username,
            "disabled": user.disabled,
            "auth_level": user.auth_level,
            "email": user.email,
            "full_name": user.full_name,
            "jti": str(uuid.uuid4()),
        },
        expires_delta=access_token_expires
    )

    # Include user data in the response
    return JSONResponse(
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "auth_level": user.auth_level,
                "disabled": user.disabled,
            }
        }
    )

@authentication_router.get("/verify-token/{token}")
async def verify_user_token(token: str):
    user_data = verify_token(token=token)
    return user_data


@authentication_router.get("/get_user_data/{token}")
async def get_user_token_data(token: str):
    user_data = get_current_user(token=token)
    return user_data

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
