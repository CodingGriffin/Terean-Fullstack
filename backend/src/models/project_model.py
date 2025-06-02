from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from utils.custom_types.Priority import Priority
from utils.custom_types.ProjectStatus import ProjectStatus

if TYPE_CHECKING:
    from models.client_model import ClientDBModel
    from models.sgy_file_model import SgyFileDBModel
    from models.file_model import FileDBModel

class ProjectDBModel(Base):
    __tablename__ = 'projects'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[ProjectStatus | None] = mapped_column(Enum(ProjectStatus), index=True)
    priority: Mapped[Priority | None] = mapped_column(Enum(Priority), index=True)
    survey_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    received_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    geometry: Mapped[str | None] = mapped_column(String, index=False)
    record_options: Mapped[str | None] = mapped_column(String, index=False)
    plot_limits: Mapped[str | None] = mapped_column(String, index=False)
    freq: Mapped[str | None] = mapped_column(String, index=False)
    slow: Mapped[str | None] = mapped_column(String, index=False)
    picks: Mapped[str | None] = mapped_column(String, index=False)
    disper_settings: Mapped[str | None] = mapped_column(String, index=False)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), index=True)
    
    # Relationships
    client: Mapped["ClientDBModel | None"] = relationship("ClientDBModel", back_populates="projects")
    records: Mapped[list["SgyFileDBModel"]] = relationship("SgyFileDBModel", back_populates="project")
    additional_files: Mapped[list["FileDBModel"]] = relationship("FileDBModel", back_populates="project")
