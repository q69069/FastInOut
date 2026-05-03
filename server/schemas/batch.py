from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class BatchCreate(BaseModel):
    product_id: int
    batch_no: str
    production_date: Optional[date] = None
    expire_date: Optional[date] = None
    quantity: float = 0
    cost_price: float = 0
    warehouse_id: Optional[int] = None
    remark: Optional[str] = None


class BatchUpdate(BaseModel):
    batch_no: Optional[str] = None
    production_date: Optional[date] = None
    expire_date: Optional[date] = None
    quantity: Optional[float] = None
    cost_price: Optional[float] = None
    warehouse_id: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class BatchOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    batch_no: str
    production_date: Optional[date] = None
    expire_date: Optional[date] = None
    quantity: float
    cost_price: float
    warehouse_id: Optional[int] = None
    warehouse_name: Optional[str] = None
    status: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
