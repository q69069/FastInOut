from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssignRole(BaseModel):
    employee_id: int
    role_id: int
