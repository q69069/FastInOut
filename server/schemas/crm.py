from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ==================== 联系人 ====================

class ContactCreate(BaseModel):
    customer_id: int
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: int = 0
    remark: Optional[str] = None


class ContactUpdate(BaseModel):
    customer_id: Optional[int] = None
    name: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: Optional[int] = None
    remark: Optional[str] = None


class ContactOut(BaseModel):
    id: int
    customer_id: int
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: int = 0
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== 拜访记录 ====================

class VisitCreate(BaseModel):
    customer_id: int
    contact_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator_id: Optional[int] = None


class VisitUpdate(BaseModel):
    customer_id: Optional[int] = None
    contact_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator_id: Optional[int] = None


class VisitOut(BaseModel):
    id: int
    customer_id: int
    contact_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
