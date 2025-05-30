import datetime
from typing import Optional, List

from pydantic import BaseModel

from backend.utils.custom_types.Priority import Priority
from backend.utils.custom_types.ProjectStatus import ProjectStatus
from backend.schemas.client_schema import Client
from backend.schemas.sgy_file_schema import SgyFileBase
from backend.schemas.file_schema import FileBase


class ProjectBase(BaseModel):
    name: str
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    survey_date: Optional[datetime.datetime] = None
    received_date: Optional[datetime.datetime] = None
    geometry: Optional[str] = None
    record_options: Optional[str] = None
    plot_limits: Optional[str] = None
    freq: Optional[str] = None
    slow: Optional[str] = None
    picks: Optional[str] = None
    disper_settings: Optional[str] = None


class Project(ProjectBase):
    id: str
    client: Optional[Client] = None
    records: Optional[List[SgyFileBase]] = None
    additional_files: Optional[List[FileBase]] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, db_project):
        return cls(**db_project.__dict__)


class ProjectCreate(ProjectBase):
    pass


class ProjectCreateWithFiles(ProjectBase):
    pass