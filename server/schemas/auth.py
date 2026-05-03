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
    role_id: Optional[int] = None  # 主角色ID（兼容旧版）
    role_name: Optional[str] = None  # 主角色名称
    roles: List[dict] = []  # 所有角色列表
    permissions: Dict[str, Any] = {}


class CurrentUser(BaseModel):
    id: int
    code: str
    name: str
    username: str
    position: Optional[str] = None
    phone: Optional[str] = None
    status: int
    role_id: Optional[int] = None  # 主角色ID
    role_name: Optional[str] = None  # 主角色名称
    roles: List[dict] = []  # 所有角色列表
    permissions: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
