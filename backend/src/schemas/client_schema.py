from pydantic import BaseModel
from typing import Optional, List

from schemas.contact_schema import Contact

class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    contacts: List[Contact] = []

    class Config:
        from_attributes = True 