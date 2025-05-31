from pydantic import BaseModel, EmailStr

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