from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.database import get_db
from backend.models.user_model import UserDBModel
from backend.schemas.user_schema import UserCreate,User as UserSchema, UserUpdate, UserOut
from backend.utils.authentication import hash_password, require_auth_level

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

# Dependency
db_dependency = Depends(get_db)

class DisableUserRequest(BaseModel):
    disabled: bool

# Get all users
@admin_router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = db_dependency,
    current_user: UserSchema = Depends(require_auth_level(3))
):
    return db.query(UserDBModel).all()


# Get one user by username
@admin_router.get("/users/{username}", response_model=UserOut)
def get_user(
    username: str, 
    db: Session = db_dependency,
    current_user: UserSchema = Depends(require_auth_level(3))
):

    user = db.query(UserDBModel).filter(UserDBModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Create a new user
@admin_router.post("/register_user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, 
    db: Session = db_dependency,
    current_user: UserSchema = Depends(require_auth_level(3))
):
   
    db_user = db.query(UserDBModel).filter(UserDBModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")


    new_user = UserDBModel(
        username=user.username,
        hashed_password=hash_password(user.password),
        disabled=user.disabled,
        auth_level=user.auth_level,
        email=user.email,
        full_name=user.full_name,
        expiration=user.expiration,
    )
    
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Update an existing user
@admin_router.put("/users/{username}", response_model=UserOut)
def update_user(
    username: str, 
    updates: UserUpdate, 
    db: Session = db_dependency,
    current_user : UserSchema = Depends(require_auth_level(3))
):
    user = db.query(UserDBModel).filter(UserDBModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# Toggle user's disabled status
@admin_router.patch("/disable_user/{username}", status_code=status.HTTP_200_OK)
def update_user_disabled_status(
    username: str, 
    payload: DisableUserRequest, 
    db: Session = db_dependency,
    current_user: UserSchema = Depends(require_auth_level(3))
):
    user = db.query(UserDBModel).filter(UserDBModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.disabled = payload.disabled
    db.commit()
    return {"message": f"User '{username}' disabled status set to {payload.disabled}."}
