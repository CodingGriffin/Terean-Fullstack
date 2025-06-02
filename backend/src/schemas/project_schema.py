import datetime
from typing import Optional, List

from pydantic import BaseModel

from schemas.client_schema import Client
from schemas.file_schema import FileBase
from schemas.sgy_file_schema import SgyFileBase
from utils.custom_types.Priority import Priority
from utils.custom_types.ProjectStatus import ProjectStatus


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
        # Extract only the relevant fields, excluding SQLAlchemy internal attributes
        project_data = {}
        
        # Add all fields from ProjectBase
        for field in ['name', 'status', 'priority', 'survey_date', 'received_date', 
                      'geometry', 'record_options', 'plot_limits', 'freq', 'slow', 
                      'picks', 'disper_settings']:
            if hasattr(db_project, field):
                project_data[field] = getattr(db_project, field)
        
        # Add id
        project_data['id'] = db_project.id
        
        # Handle relationships - convert SQLAlchemy models to Pydantic models
        if hasattr(db_project, 'client') and db_project.client:
            # Client expects a Client schema instance
            project_data['client'] = Client.model_validate(db_project.client, from_attributes=True)
        
        if hasattr(db_project, 'records') and db_project.records:
            # Convert each SgyFileDBModel to SgyFileBase
            project_data['records'] = [
                SgyFileBase.model_validate(record, from_attributes=True) 
                for record in db_project.records
            ]
            
        if hasattr(db_project, 'additional_files') and db_project.additional_files:
            # Convert each FileDBModel to FileBase
            project_data['additional_files'] = [
                FileBase.model_validate(file, from_attributes=True) 
                for file in db_project.additional_files
            ]
        
        return cls(**project_data)


class ProjectCreate(ProjectBase):
    id: Optional[str] = None
    pass


class ProjectCreateWithFiles(ProjectBase):
    sgy_files: Optional[List[str]] = None  # List of SgyFile IDs
    additional_files: Optional[List[str]] = None  # List of File IDs


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    survey_date: Optional[datetime.datetime] = None
    received_date: Optional[datetime.datetime] = None