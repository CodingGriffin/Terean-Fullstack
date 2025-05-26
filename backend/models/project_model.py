from sqlalchemy import Enum, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

from backend.utils.custom_types.Priority import Priority
from backend.utils.custom_types.ProjectStatus import ProjectStatus

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.client_model import ClientDBModel
    from backend.models.sgy_file_model import SgyFileDBModel

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
    client: Mapped["ClientDBModel"] = relationship("ClientDBModel", back_populates="project")
    records: Mapped[list["SgyFileDBModel"]] = relationship("SgyFileDBModel", back_populates="project")
