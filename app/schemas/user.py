from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    id: str
    email: str
    is_verified: bool
    plan: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None