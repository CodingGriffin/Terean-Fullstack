from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from backend.database import Base

if TYPE_CHECKING:
    from backend.models.project_model import ProjectDBModel

class FileDBModel(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_extension: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["ProjectDBModel"] = relationship("ProjectDBModel", back_populates="files") 