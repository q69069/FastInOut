"""报损单 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class DamageReportItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_cost: float = 0
    amount: float = 0
    reason: Optional[str] = None


class DamageReportItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str = ""
    quantity: float
    unit_cost: float = 0
    amount: float = 0
    reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DamageReportCreate(BaseModel):
    warehouse_id: int
    report_type: str = "general"
    remark: Optional[str] = None
    items: List[DamageReportItemCreate]


class DamageReportOut(BaseModel):
    id: int
    code: str
    warehouse_id: int
    warehouse_name: str = ""
    report_type: str
    total_amount: float = 0
    status: str
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    audited_at: Optional[datetime] = None
    items: List[DamageReportItemOut] = []
    model_config = ConfigDict(from_attributes=True)
