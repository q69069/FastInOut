from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class InvoiceCreate(BaseModel):
    invoice_type: str  # purchase/sales
    invoice_code: Optional[str] = None
    invoice_no: Optional[str] = None
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    amount: float = 0
    tax_amount: float = 0
    total_amount: float = 0
    invoice_date: Optional[date] = None
    status: int = 1
    remark: Optional[str] = None


class InvoiceUpdate(BaseModel):
    invoice_code: Optional[str] = None
    invoice_no: Optional[str] = None
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    invoice_date: Optional[date] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class InvoiceOut(BaseModel):
    id: int
    invoice_type: str
    invoice_code: Optional[str] = None
    invoice_no: Optional[str] = None
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None
    amount: float = 0
    tax_amount: float = 0
    total_amount: float = 0
    invoice_date: Optional[date] = None
    status: int = 1
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
