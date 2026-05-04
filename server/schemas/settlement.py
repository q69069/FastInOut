"""交账 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class SettlementCreate(BaseModel):
    employee_id: int
    delivery_ids: List[int]
    return_ids: List[int] = []
    expense_ids: List[int] = []
    remark: Optional[str] = None


class SettlementOut(BaseModel):
    id: int
    settlement_no: str
    employee_id: int
    employee_name: str = ""
    settlement_date: Optional[datetime] = None
    total_sales: float = 0
    total_returns: float = 0
    total_expenses: float = 0
    total_cash: float = 0
    total_wechat: float = 0
    total_alipay: float = 0
    total_credit: float = 0
    actual_cash: float = 0
    status: str
    auditor_id: Optional[int] = None
    audited_at: Optional[datetime] = None
    audit_comment: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    deliveries: List[dict] = []
    returns: List[dict] = []
    model_config = ConfigDict(from_attributes=True)
