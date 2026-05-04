from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class PurchaseReturnDlvItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="数量必须大于0")
    unit_price: float = Field(ge=0, description="单价不能为负")
    amount: float = 0


class PurchaseReturnDlvItemOut(BaseModel):
    id: int
    return_dlv_id: int
    product_id: int
    quantity: float
    unit_price: float
    amount: float

    model_config = ConfigDict(from_attributes=True)


class PurchaseReturnDlvCreate(BaseModel):
    purchase_return_id: Optional[int] = None
    supplier_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None
    items: List[PurchaseReturnDlvItemCreate] = []


class PurchaseReturnDlvOut(BaseModel):
    id: int
    return_dlv_no: str
    purchase_return_id: Optional[int] = None
    supplier_id: int
    warehouse_id: int
    total_amount: float
    status: str
    created_by: int
    wh_confirmed_by: Optional[int] = None
    wh_confirmed_at: Optional[datetime] = None
    fin_confirmed_by: Optional[int] = None
    fin_confirmed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
