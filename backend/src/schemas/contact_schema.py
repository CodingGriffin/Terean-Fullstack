from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactBase(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    client_id: int

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

    class Config:
        from_attributes = True 

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    client_id: Optional[int] = None 