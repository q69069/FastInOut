from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WarehouseBase(BaseModel):
    code: str
    name: str
    warehouse_type: str = "normal"  # normal/vehicle/other
    address: Optional[str] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False
    status: int = 1


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    warehouse_type: Optional[str] = None
    address: Optional[str] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[int] = None


class WarehouseOut(WarehouseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
