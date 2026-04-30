from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReceiptBase(BaseModel):
    customer_id: int
    amount: float
    payment_method: Optional[str] = None
    stockout_id: Optional[int] = None
    remark: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptOut(ReceiptBase):
    id: int
    code: str
    receipt_type: Optional[str] = "normal"
    status: int = 0
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    supplier_id: int
    amount: float
    payment_method: Optional[str] = None
    stockin_id: Optional[int] = None
    remark: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: int
    code: str
    payment_type: Optional[str] = "normal"
    status: int = 0
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PreReceiptCreate(BaseModel):
    customer_id: int
    amount: float
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class PrePaymentCreate(BaseModel):
    supplier_id: int
    amount: float
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class PreToReceivable(BaseModel):
    receipt_id: int  # 预收款ID
    stockout_id: int  # 出库单ID
    amount: float  # 冲销金额


class PreToPayable(BaseModel):
    payment_id: int  # 预付款ID
    stockin_id: int  # 入库单ID
    amount: float  # 冲销金额
