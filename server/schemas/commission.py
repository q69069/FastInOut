"""提成 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CommissionCreate(BaseModel):
    employee_id: int
    period: str
    base_amount: float = 0
    commission_rate: float = 0
    commission_amount: float = 0
    remark: Optional[str] = None


class CommissionOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str = ""
    period: str
    base_amount: float = 0
    commission_rate: float = 0
    commission_amount: float = 0
    status: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
