from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReceiptBase(BaseModel):
    customer_id: int
    amount: float
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptOut(ReceiptBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    supplier_id: int
    amount: float
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
