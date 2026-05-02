"""
路线、审核、价格变动相关schema
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# Route
class RouteCreate(BaseModel):
    code: str
    name: str
    warehouse_id: Optional[int] = None
    sort_order: int = 0
    description: Optional[str] = None
    status: str = "active"


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    warehouse_id: Optional[int] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RouteResponse(BaseModel):
    id: int
    code: str
    name: str
    warehouse_id: Optional[int] = None
    sort_order: int = 0
    description: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# AuditLog
class AuditLogResponse(BaseModel):
    id: int
    target_type: str
    target_id: int
    target_code: Optional[str] = None
    action: str
    comment: Optional[str] = None
    auditor_id: Optional[int] = None
    auditor_name: Optional[str] = None
    created_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# PriceChangeLog
class PriceChangeLogResponse(BaseModel):
    id: int
    product_id: int
    field_name: Optional[str] = None
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    change_time: Optional[datetime] = None
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# VehicleSalesOut
class VehicleSalesOutResponse(BaseModel):
    id: int
    code: str
    employee_id: Optional[int] = None
    vehicle_warehouse_id: Optional[int] = None
    total_amount: float = 0
    remark: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# VehicleReturn
class VehicleReturnResponse(BaseModel):
    id: int
    code: str
    vehicle_sales_out_id: Optional[int] = None
    employee_id: Optional[int] = None
    total_amount: float = 0
    remark: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# VehicleLoss
class VehicleLossResponse(BaseModel):
    id: int
    code: str
    vehicle_sales_out_id: Optional[int] = None
    employee_id: Optional[int] = None
    total_amount: float = 0
    reason: Optional[str] = None
    status: str = "draft"
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
