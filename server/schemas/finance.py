from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReceiptBase(BaseModel):
    customer_id: int
    amount: float
    payment_method: Optional[str] = None
    stockout_id: Optional[int] = None
    remark: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    amount: float = Field(gt=0, description="收款金额必须大于0")


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
    amount: float = Field(gt=0, description="付款金额必须大于0")


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
    amount: float = Field(gt=0, description="预收金额必须大于0")
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class PrePaymentCreate(BaseModel):
    supplier_id: int
    amount: float = Field(gt=0, description="预付金额必须大于0")
    payment_method: Optional[str] = None
    remark: Optional[str] = None


class PreToReceivable(BaseModel):
    receipt_id: int  # 预收款ID
    stockout_id: int  # 出库单ID
    amount: float = Field(gt=0, description="冲销金额必须大于0")


class PreToPayable(BaseModel):
    payment_id: int  # 预付款ID
    stockin_id: int  # 入库单ID
    amount: float = Field(gt=0, description="冲销金额必须大于0")
