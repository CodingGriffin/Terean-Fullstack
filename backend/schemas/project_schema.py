import datetime

from pydantic import BaseModel

from backend.utils.custom_types.Priority import Priority
from backend.utils.custom_types.ProjectStatus import ProjectStatus


class ProjectBase(BaseModel):
    name: str
    client: str
    status: ProjectStatus
    priority: Priority
    velocity: float
    geophone_count: int
    geophone_spacing: float
    survey_date: datetime.datetime
    received_date: datetime.datetime


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class ProjectCreate(ProjectBase):
    pass
