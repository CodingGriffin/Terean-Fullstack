import datetime

from pydantic import BaseModel


class User(BaseModel):
    username: str | None = None
    disabled: bool = False
    auth_level: int = 0
    email: str | None = None
    full_name: str | None = None
    expiration: datetime.datetime | None = None

    class Config:
        from_attributes = True

class UserCreate(User):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    auth_level: int | None = None
    disabled: bool | None = None
    expiration: datetime.datetime | None = None


class UserUpdatePassword(User):
    new_password: str


class UserOut(BaseModel):
    id: int
    username: str
    disabled: bool
    auth_level: int
    email: str | None = None
    full_name: str | None = None
    expiration: datetime.datetime | None = None

    class Config:
        from_attributes = True