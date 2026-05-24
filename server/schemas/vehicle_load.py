"""装车单 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class VehicleLoadItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_id: Optional[int] = None
    unit_level: Optional[str] = None  # small/medium/large
    unit_quantity: Optional[float] = 1.0
    unit_conv_rate: Optional[float] = 1.0


class VehicleLoadItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str = ""
    quantity: float
    returned_quantity: float = 0
    unit_id: Optional[int] = None
    unit_quantity: Optional[float] = 1.0
    unit_conv_rate: Optional[float] = 1.0
    unit_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class VehicleLoadCreate(BaseModel):
    from_warehouse_id: Optional[int] = None
    vehicle_warehouse_id: Optional[int] = None
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
