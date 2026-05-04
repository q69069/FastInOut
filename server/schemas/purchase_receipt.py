from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class PurchaseReceiptItemCreate(BaseModel):
    product_id: int
    order_item_id: Optional[int] = None
    quantity: float = Field(gt=0, description="数量必须大于0")
    unit_price: float = Field(ge=0, description="单价不能为负")
    amount: float = 0


class PurchaseReceiptItemOut(BaseModel):
    id: int
    receipt_id: int
    product_id: int
    order_item_id: Optional[int] = None
    quantity: float
    unit_price: float
    amount: float

    model_config = ConfigDict(from_attributes=True)


class PurchaseReceiptCreate(BaseModel):
    purchase_order_id: int
    supplier_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None
    items: List[PurchaseReceiptItemCreate] = []


class PurchaseReceiptOut(BaseModel):
    id: int
    receipt_no: str
    purchase_order_id: int
    supplier_id: int
    warehouse_id: int
    total_amount: float
    status: str
    received_by: int
    confirmed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
