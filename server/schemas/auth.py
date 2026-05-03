from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
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
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    permissions: Dict[str, Any] = {}


class CurrentUser(BaseModel):
    id: int
    code: str
    name: str
    username: str
    position: Optional[str] = None
    phone: Optional[str] = None
    status: int
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    permissions: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
