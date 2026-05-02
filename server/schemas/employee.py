from pydantic import BaseModel, ConfigDict
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
    role_type: Optional[str] = None
    warehouse_ids: Optional[str] = None
    route_ids: Optional[str] = None
    bypass_audit: Optional[int] = None
    online_status: Optional[str] = None


class EmployeeOut(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
