"""客户对账模型 — Phase D"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class CustomerReconciliation(Base):
    __tablename__ = "customer_reconciliations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    total_sales = Column(Float, default=0)
    total_returns = Column(Float, default=0)
    total_receipts = Column(Float, default=0)
    balance = Column(Float, default=0)
    status = Column(String(20), default="pending")  # pending/confirmed
    confirmed_at = Column(DateTime)
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())
