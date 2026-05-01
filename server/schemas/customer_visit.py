from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerVisitCreate(BaseModel):
    customer_id: int
    contact_id: Optional[int] = None
    visit_date: datetime
    visit_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator: Optional[str] = None


class CustomerVisitUpdate(BaseModel):
    contact_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    visit_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator: Optional[str] = None


class CustomerVisitOut(BaseModel):
    id: int
    customer_id: int
    contact_id: Optional[int] = None
    visit_date: Optional[datetime] = None
    visit_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    next_plan: Optional[str] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
