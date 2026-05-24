from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    code: str
    barcode: Optional[str] = None
    name: str
    spec: Optional[str] = None
    unit: Optional[str] = None
    # 三单位
    small_unit_name: Optional[str] = ''
    medium_unit_name: Optional[str] = None
    medium_conv_rate: Optional[float] = None
    large_unit_name: Optional[str] = None
    large_conv_rate: Optional[float] = None
    default_unit_level: str = 'small'
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    purchase_price: float = 0
    retail_price: float = 0
    member_price: float = 0
    cost_price: float = 0
    supplier_id: Optional[int] = None
    stock_min: float = 0
    stock_max: float = 0
    image: Optional[str] = None
    level_prices: Optional[str] = None
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
    # 三单位
    small_unit_name: Optional[str] = None
    medium_unit_name: Optional[str] = None
    medium_conv_rate: Optional[float] = None
    large_unit_name: Optional[str] = None
    large_conv_rate: Optional[float] = None
    default_unit_level: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    purchase_price: Optional[float] = None
    retail_price: Optional[float] = None
    member_price: Optional[float] = None
    cost_price: Optional[float] = None
    supplier_id: Optional[int] = None
    stock_min: Optional[float] = None
    stock_max: Optional[float] = None
    image: Optional[str] = None
    level_prices: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    brand_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # 计算字段：三级价格（路由器填充）
    small_purchase_price: Optional[float] = None
    medium_purchase_price: Optional[float] = None
    large_purchase_price: Optional[float] = None
    small_retail_price: Optional[float] = None
    medium_retail_price: Optional[float] = None
    large_retail_price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
