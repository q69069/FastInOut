"""预收付款模型 — Phase C"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class AdvancePayment(Base):
    __tablename__ = "advance_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # receivable=预收款, payable=预付款
    party_type = Column(String(20), nullable=False)  # customer/supplier
    party_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    used_amount = Column(Float, default=0)
    remaining_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending/confirmed/cancelled
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)
