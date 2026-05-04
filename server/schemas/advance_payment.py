"""预收付款 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AdvancePaymentCreate(BaseModel):
    type: str  # receivable/payable
    party_type: str  # customer/supplier
    party_id: int
    amount: float
    remark: Optional[str] = None


class AdvancePaymentOut(BaseModel):
    id: int
    code: str
    type: str
    party_type: str
    party_id: int
    party_name: str = ""
    amount: float
    used_amount: float = 0
    remaining_amount: float
    status: str
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
