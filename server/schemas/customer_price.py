from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerPriceCreate(BaseModel):
    customer_id: int
    product_id: int
    price: float
    remark: Optional[str] = None


class CustomerPriceUpdate(BaseModel):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    price: Optional[float] = None
    remark: Optional[str] = None


class CustomerPriceOut(BaseModel):
    id: int
    customer_id: int
    product_id: int
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    price: float
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
