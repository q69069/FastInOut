from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerLevelCreate(BaseModel):
    name: str
    code: Optional[str] = None
    discount_rate: float = 1.0
    credit_limit: float = 0
    sort_order: int = 0
    remark: Optional[str] = None
    status: int = 1


class CustomerLevelUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    discount_rate: Optional[float] = None
    credit_limit: Optional[float] = None
    sort_order: Optional[int] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class CustomerLevelOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    discount_rate: float = 1.0
    credit_limit: float = 0
    sort_order: int = 0
    remark: Optional[str] = None
    status: int = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True