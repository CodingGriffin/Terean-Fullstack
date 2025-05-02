from sqlalchemy import Enum, Column, Integer, String, Float, DateTime
from typing import TYPE_CHECKING

from backend.utils.custom_types.Priority import Priority
from backend.utils.custom_types.ProjectStatus import ProjectStatus

from backend.database import Base


# if TYPE_CHECKING:
#     from X import X

class ProjectModel(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    client = Column(String, index=True)
    status = Column(Enum(ProjectStatus), index=True)
    priority = Column(Enum(Priority), index=True)
    velocity = Column(Float, index=True)
    geophone_count = Column(Integer, index=True)
    geophone_spacing = Column(Float, index=True)
    survey_date = Column(DateTime, index=True)
    received_date = Column(DateTime, index=True)
    # geometry = Column(String)
    # picks = Column(String)
    # model = Column(String)
    # pick_settings = Column(String)
    # disper_settings = Column(String)
    # record_paths = Column(String)
