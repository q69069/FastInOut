from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base


class CustomerLevel(Base):
    __tablename__ = "customer_levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="等级名称(A/B/C)")
    code = Column(String(20), unique=True, comment="等级编码")
    discount_rate = Column(Float, default=1.0, comment="折扣率(0-1, 0.95=九五折)")
    credit_limit = Column(Float, default=0, comment="信用额度")
    sort_order = Column(Integer, default=0)
    remark = Column(String(500))
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())