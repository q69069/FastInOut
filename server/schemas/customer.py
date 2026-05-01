from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    code: str
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category_id: Optional[int] = None
    level: Optional[str] = None
    credit_limit: float = 0
    receivable_balance: float = 0
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_number: Optional[str] = None
    remark: Optional[str] = None
    status: int = 1


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category_id: Optional[int] = None
    level: Optional[str] = None
    credit_limit: Optional[float] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_number: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class CustomerOut(CustomerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
