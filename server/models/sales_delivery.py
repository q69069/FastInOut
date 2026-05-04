from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class SalesDelivery(Base):
    __tablename__ = "sales_deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_no = Column(String(30), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    vehicle_id = Column(Integer)

    total_amount = Column(Float, default=0)
    cash_amount = Column(Float, default=0)
    wechat_amount = Column(Float, default=0)
    alipay_amount = Column(Float, default=0)
    credit_amount = Column(Float, default=0)

    status = Column(String(20), default="pending")
    source_type = Column(String(20), default="direct")
    void_reason = Column(String(200))
    originated_from_id = Column(Integer)
    payment_evidence = Column(Text)

    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("employees.id"))
    audited_at = Column(DateTime)
    settled_at = Column(DateTime)
    settlement_id = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())
    remark = Column(Text)


class SalesDeliveryItem(Base):
    __tablename__ = "sales_delivery_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_id = Column(Integer, ForeignKey("sales_deliveries.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
    source_order_item_id = Column(Integer)
