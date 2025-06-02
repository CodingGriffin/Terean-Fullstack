from typing import List, Optional

from pydantic import BaseModel

from schemas.contact_schema import Contact


class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    
    class Config:
        from_attributes = True

class Client(ClientBase):
    id: int
    contacts: List[Contact] = []

    class Config:
        from_attributes = True