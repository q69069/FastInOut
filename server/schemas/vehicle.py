from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleSalesOutResponse(BaseModel):
    id: int
    code: str
    employee_id: Optional[int] = None
    vehicle_warehouse_id: Optional[int] = None
    total_amount: float = 0
    remark: Optional[str] = None
    status: str = "draft"
    audit_status: str = "pending"
    auditor_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class VehicleReturnResponse(BaseModel):
    id: int
    code: str
    vehicle_sales_out_id: Optional[int] = None
    employee_id: Optional[int] = None
    total_amount: float = 0
    remark: Optional[str] = None
    status: str = "draft"
    audit_status: str = "pending"
    auditor_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class VehicleLossResponse(BaseModel):
    id: int
    code: str
    vehicle_sales_out_id: Optional[int] = None
    employee_id: Optional[int] = None
    total_amount: float = 0
    reason: Optional[str] = None
    status: str = "draft"
    audit_status: str = "pending"
    auditor_id: Optional[int] = None
    audit_time: Optional[datetime] = None
    audit_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}