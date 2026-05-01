from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    quantity: float = Field(gt=0, description="数量必须大于0")
    price: float = Field(ge=0, description="单价不能为负")


class PurchaseOrderItemOut(PurchaseOrderItemBase):
    id: int
    order_id: int
    received_qty: float = 0

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    supplier_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate] = []


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    total_amount: Optional[float] = None
    remark: Optional[str] = None
    items: Optional[List[PurchaseOrderItemCreate]] = None


class PurchaseOrderOut(PurchaseOrderBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    paid_amount: float
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseStockinItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class PurchaseStockinItemCreate(PurchaseStockinItemBase):
    quantity: float = Field(gt=0, description="数量必须大于0")
    price: float = Field(ge=0, description="单价不能为负")


class PurchaseStockinItemOut(PurchaseStockinItemBase):
    id: int
    stockin_id: int

    model_config = ConfigDict(from_attributes=True)


class PurchaseStockinBase(BaseModel):
    order_id: Optional[int] = None
    supplier_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class PurchaseStockinCreate(PurchaseStockinBase):
    items: List[PurchaseStockinItemCreate] = []


class PurchaseStockinOut(PurchaseStockinBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseReturnItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class PurchaseReturnItemCreate(PurchaseReturnItemBase):
    quantity: float = Field(gt=0, description="数量必须大于0")
    price: float = Field(ge=0, description="单价不能为负")


class PurchaseReturnBase(BaseModel):
    stockin_id: Optional[int] = None
    supplier_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class PurchaseReturnCreate(PurchaseReturnBase):
    items: List[PurchaseReturnItemCreate] = []


class PurchaseReturnOut(PurchaseReturnBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
