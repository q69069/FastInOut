from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SupplierBase(BaseModel):
    code: str
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category_id: Optional[int] = None
    payment_term: Optional[str] = None
    payable_balance: float = 0
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_number: Optional[str] = None
    remark: Optional[str] = None
    status: int = 1


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category_id: Optional[int] = None
    payment_term: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_number: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class SupplierOut(SupplierBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
