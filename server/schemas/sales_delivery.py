from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class SalesDeliveryItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="数量必须大于0")
    unit_price: float = Field(ge=0, description="单价不能为负")
    amount: float = 0
    batch_id: Optional[int] = None
    source_order_item_id: Optional[int] = None


class SalesDeliveryItemOut(BaseModel):
    id: int
    delivery_id: int
    product_id: int
    batch_id: Optional[int] = None
    quantity: float
    unit_price: float
    amount: float
    source_order_item_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SalesDeliveryCreate(BaseModel):
    customer_id: int
    warehouse_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    total_amount: float = 0
    cash_amount: float = 0
    wechat_amount: float = 0
    alipay_amount: float = 0
    credit_amount: float = 0
    source_type: str = "direct"
    remark: Optional[str] = None
    items: List[SalesDeliveryItemCreate] = []


class SalesDeliveryOut(BaseModel):
    id: int
    delivery_no: str
    customer_id: int
    warehouse_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    total_amount: float
    cash_amount: float
    wechat_amount: float
    alipay_amount: float
    credit_amount: float
    status: str
    source_type: str
    void_reason: Optional[str] = None
    originated_from_id: Optional[int] = None
    created_by: int
    auditor_id: Optional[int] = None
    audited_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    settlement_id: Optional[int] = None
    created_at: Optional[datetime] = None
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SalesDeliveryVoid(BaseModel):
    void_reason: str = Field(min_length=1, description="作废原因必填")
