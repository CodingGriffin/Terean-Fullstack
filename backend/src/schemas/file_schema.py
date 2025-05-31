from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    id: str
    original_name: str
    path: str
    size: int
    upload_date: datetime = None
    mime_type: str
    file_extension: str
    project_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileCreate(FileBase):
    pass


class FileSchema(FileBase):
    class Config:
        from_attributes = True 