from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class ModulePermissionItem(BaseModel):
    module_key: str
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_audit: bool = False
    can_export: bool = False
    data_scope: str = "self"  # all, warehouse, route, self


class OperationItem(BaseModel):
    operation_key: str
    data_scope: str = "self"


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    role_key: Optional[str] = None
    module_permissions: List[ModulePermissionItem] = []
    operations: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    module_permissions: Optional[List[ModulePermissionItem]] = None
    operations: Optional[List[str]] = None


class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    role_key: Optional[str] = None
    module_permissions: List[Dict] = []
    operations: List[str] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssignRole(BaseModel):
    employee_id: int
    role_id: int
