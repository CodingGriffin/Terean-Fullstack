from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SgyFileBase(BaseModel):
    id: str
    original_name: str
    path: str
    size: int
    upload_date: datetime = None
    type: str
    project_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class SgyFileCreate(SgyFileBase):
    pass


class SgyFile(SgyFileBase):

    class Config:
        from_attributes = True
