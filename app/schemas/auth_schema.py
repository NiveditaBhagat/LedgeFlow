#login and Registration JSON structure

from pydantic import BaseModel, EmailStr, Field
from enum import Enum



class UserRole(str, Enum):
    BORROWER = "BORROWER"
    CREDIT = "CREDIT"
    OPS = "OPS"
    ADMIN = "ADMIN"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str