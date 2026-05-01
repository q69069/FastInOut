from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class Salesman(Base):
    """业务员提成配置"""
    __tablename__ = "salesmen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)
    commission_rate = Column(Float, default=0)  # 提成比例 (0.05 = 5%)
    target_amount = Column(Float, default=0)  # 月度目标金额
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
