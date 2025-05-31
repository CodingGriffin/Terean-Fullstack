from sqlalchemy.orm import Session

from models.user_model import UserDBModel
from schemas.user_schema import UserCreate
from utils.authentication import hash_password


def get_all_users(db: Session):
    return db.query(UserDBModel)


def get_user_by_username(db: Session, username: str):
    return db.query(UserDBModel).filter(UserDBModel.username == username).first()


def get_user_by_id(db: Session, id: int):
    return db.query(UserDBModel).filter(UserDBModel.id == id).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = UserDBModel(
        username=user.username,
        hashed_password=hashed_password,
        disabled=user.disabled,
        auth_level=user.auth_level,
        email=user.email,
        full_name=user.full_name,
        expiration=user.expiration,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user