"""客户对账 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ReconciliationCreate(BaseModel):
    customer_id: int
    period_start: datetime
    period_end: datetime
    remark: Optional[str] = None


class ReconciliationOut(BaseModel):
    id: int
    code: str
    customer_id: int
    customer_name: str = ""
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_sales: float = 0
    total_returns: float = 0
    total_receipts: float = 0
    balance: float = 0
    status: str
    confirmed_at: Optional[datetime] = None
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
