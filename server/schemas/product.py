from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    code: str
    barcode: Optional[str] = None
    name: str
    spec: Optional[str] = None
    unit: Optional[str] = None
    category_id: Optional[int] = None
    purchase_price: float = 0
    retail_price: float = 0
    member_price: float = 0
    cost_price: float = 0
    supplier_id: Optional[int] = None
    stock_min: float = 0
    stock_max: float = 0
    image: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    code: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    category_id: Optional[int] = None
    purchase_price: Optional[float] = None
    retail_price: Optional[float] = None
    member_price: Optional[float] = None
    cost_price: Optional[float] = None
    supplier_id: Optional[int] = None
    stock_min: Optional[float] = None
    stock_max: Optional[float] = None
    image: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
