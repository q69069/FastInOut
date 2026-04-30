from pydantic import BaseModel
from typing import Optional, Any


class DashboardOut(BaseModel):
    total_sales: float = 0
    total_purchase: float = 0
    total_receivable: float = 0
    total_payable: float = 0
    product_count: int = 0
    customer_count: int = 0
    supplier_count: int = 0
    alert_count: int = 0


class SalesReportItem(BaseModel):
    date: str
    order_count: int
    total_amount: float


class PurchaseReportItem(BaseModel):
    date: str
    order_count: int
    total_amount: float


class InventoryReportItem(BaseModel):
    product_id: int
    product_name: str
    warehouse_name: str
    quantity: float
    cost_price: float
    total_value: float


class ProfitReportItem(BaseModel):
    date: str
    sales_amount: float
    cost_amount: float
    profit: float
