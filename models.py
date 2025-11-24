from pydantic import BaseModel
from typing import List, Optional

# Base model with common fields
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str

# Input model for Registration (includes password)
class UserCreate(UserBase):
    password: str

# Output model for Responses (excludes password, includes roles)
class User(UserBase):
    disabled: Optional[bool] = None
    roles: List[str] = []

    class Config:
        # This allows Pydantic to read data from SQLAlchemy database objects
        from_attributes = True