"""装车单 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class VehicleLoadItemCreate(BaseModel):
    product_id: int
    quantity: float


class VehicleLoadItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str = ""
    quantity: float
    returned_quantity: float = 0
    model_config = ConfigDict(from_attributes=True)


class VehicleLoadCreate(BaseModel):
    from_warehouse_id: int
    vehicle_warehouse_id: int
    employee_id: Optional[int] = None
    remark: Optional[str] = None
    items: List[VehicleLoadItemCreate]


class VehicleLoadOut(BaseModel):
    id: int
    load_no: str
    from_warehouse_id: int
    from_warehouse_name: str = ""
    vehicle_warehouse_id: int
    vehicle_warehouse_name: str = ""
    employee_id: Optional[int] = None
    employee_name: str = ""
    status: str
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    loaded_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    items: List[VehicleLoadItemOut] = []
    model_config = ConfigDict(from_attributes=True)
