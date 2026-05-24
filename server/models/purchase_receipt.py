from datetime import datetime
from sqlalchemy import text, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class PurchaseReceipt(Base):
    __tablename__ = "purchase_receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_no = Column(String(30), unique=True, nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    total_amount = Column(Float, default=0)
    status = Column(String(20), default="pending")
    purchaser_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    trade_date = Column(String(20), nullable=True)

    received_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    confirmed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.now)
    remark = Column(Text)
    reverse_reason = Column(String(200))
    reversed_by = Column(Integer, ForeignKey("employees.id"))
    reversed_at = Column(DateTime)


class PurchaseReceiptItem(Base):
    __tablename__ = "purchase_receipt_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("purchase_receipts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    order_item_id = Column(Integer, nullable=True)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    remark = Column(String(500), nullable=True)
    production_date = Column(String(20), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    unit_level = Column(String(10), nullable=True)  # small/medium/large
    unit_quantity = Column(Float, default=1)
    unit_conv_rate = Column(Float, default=1)