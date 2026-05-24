from datetime import datetime
from sqlalchemy import text, Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class CustomerPrice(Base):
    """客户专属价格协议"""
    __tablename__ = "customer_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)  # 专属价格
    remark = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
