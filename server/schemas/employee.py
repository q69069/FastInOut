from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    code: str
    name: str
    phone: Optional[str] = None
    position: Optional[str] = None
    username: Optional[str] = None
    status: int = 1


class EmployeeCreate(EmployeeBase):
    password: Optional[str] = None


class EmployeeUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None


class EmployeeOut(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
