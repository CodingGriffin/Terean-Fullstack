from sqlalchemy import Column, Integer, String, Boolean, DateTime

from backend.database import Base


class UserDBModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, index=True, nullable=False)
    auth_level = Column(Integer, index=True, nullable=False)
    email = Column(String, index=True, nullable=True)
    full_name = Column(String, index=True, nullable=True)
    expiration = Column(DateTime, index=True, nullable=True)
