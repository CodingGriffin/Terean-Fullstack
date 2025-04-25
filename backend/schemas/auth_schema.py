from pydantic import BaseModel

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str