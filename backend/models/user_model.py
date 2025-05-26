from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from backend.database import Base


class UserDBModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    auth_level: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    expiration: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
