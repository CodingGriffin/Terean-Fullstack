from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base

if TYPE_CHECKING:
    from models.project_model import ProjectDBModel

class SgyFileDBModel(Base):
    __tablename__ = "sgy_files"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    type: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["ProjectDBModel"] = relationship("ProjectDBModel", back_populates="records") 