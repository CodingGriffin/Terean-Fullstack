from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Todos, Users
from ..database import SessionLocal
from .auth  import get_current_user
from passlib.context import CryptContext
import bcrypt
if not hasattr(bcrypt, '__about__'):
    ## Fix issue with passlib depending on about, which was removed in 4.2
    bcrypt.__about__ = type('about', (object,), {'__version__': bcrypt.__version__})

users_router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# @users_router.get('/', status_code=status.HTTP_200_OK)
# async def get_user(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
    
#     return db.query(Users).filter(Users.id == user.get('id')).first()
