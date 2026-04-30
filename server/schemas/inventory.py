from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InventoryOut(BaseModel):
    id: int
    warehouse_id: int
    product_id: int
    quantity: float
    cost_price: float
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryCheckBase(BaseModel):
    warehouse_id: int
    remark: Optional[str] = None


class InventoryCheckCreate(InventoryCheckBase):
    items: List["InventoryCheckItemCreate"] = []


class InventoryCheckItemCreate(BaseModel):
    product_id: int
    system_qty: float
    actual_qty: float


class InventoryCheckOut(InventoryCheckBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryTransferBase(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    remark: Optional[str] = None


class InventoryTransferCreate(InventoryTransferBase):
    items: List["InventoryTransferItemCreate"] = []


class InventoryTransferItemCreate(BaseModel):
    product_id: int
    quantity: float


class InventoryTransferOut(InventoryTransferBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryAlertOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    current_qty: float
    min_qty: float
    max_qty: float
    alert_type: str
    is_handled: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryAdjust(BaseModel):
    product_id: int
    warehouse_id: int
    adjust_qty: float  # 正数=报溢，负数=报损
    reason: Optional[str] = None
