from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str
    name: str
    position: Optional[str] = None


class CurrentUser(BaseModel):
    id: int
    code: str
    name: str
    username: str
    position: Optional[str] = None
    phone: Optional[str] = None
    status: int

    class Config:
        from_attributes = True
