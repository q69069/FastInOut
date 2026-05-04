"""员工提成模型 — Phase C"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class Commission(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    period = Column(String(10), nullable=False)  # 2026-05
    base_amount = Column(Float, default=0)  # 提成基数（销售金额）
    commission_rate = Column(Float, default=0)  # 提成比例
    commission_amount = Column(Float, default=0)  # 提成金额
    status = Column(String(20), default="pending")  # pending/paid
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
