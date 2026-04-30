from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SalesOrderItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class SalesOrderItemCreate(SalesOrderItemBase):
    pass


class SalesOrderItemOut(SalesOrderItemBase):
    id: int
    order_id: int
    delivered_qty: float = 0

    class Config:
        from_attributes = True


class SalesOrderBase(BaseModel):
    customer_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    items: List[SalesOrderItemCreate] = []


class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    total_amount: Optional[float] = None
    remark: Optional[str] = None
    items: Optional[List[SalesOrderItemCreate]] = None


class SalesOrderOut(SalesOrderBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    paid_amount: float
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalesStockoutItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class SalesStockoutItemCreate(SalesStockoutItemBase):
    pass


class SalesStockoutItemOut(SalesStockoutItemBase):
    id: int
    stockout_id: int

    class Config:
        from_attributes = True


class SalesStockoutBase(BaseModel):
    order_id: Optional[int] = None
    customer_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class SalesStockoutCreate(SalesStockoutBase):
    items: List[SalesStockoutItemCreate] = []


class SalesStockoutOut(SalesStockoutBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalesReturnItemBase(BaseModel):
    product_id: int
    quantity: float
    price: float
    amount: float = 0


class SalesReturnItemCreate(SalesReturnItemBase):
    pass


class SalesReturnBase(BaseModel):
    stockout_id: Optional[int] = None
    customer_id: int
    warehouse_id: int
    total_amount: float = 0
    remark: Optional[str] = None


class SalesReturnCreate(SalesReturnBase):
    items: List[SalesReturnItemCreate] = []


class SalesReturnOut(SalesReturnBase):
    id: int
    code: str
    operator_id: Optional[int] = None
    status: int
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
