"""交账模型 — Phase B"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_no = Column(String(30), unique=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    settlement_date = Column(DateTime)
    total_sales = Column(Float, default=0)
    total_returns = Column(Float, default=0)
    total_expenses = Column(Float, default=0)
    total_cash = Column(Float, default=0)
    total_wechat = Column(Float, default=0)
    total_alipay = Column(Float, default=0)
    total_credit = Column(Float, default=0)
    actual_cash = Column(Float, default=0)  # = total_cash - return_cash - expenses
    status = Column(String(20), default="pending")  # pending/audited/rejected
    auditor_id = Column(Integer, ForeignKey("employees.id"))
    audited_at = Column(DateTime)
    audit_comment = Column(Text)
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())


class SettlementDelivery(Base):
    __tablename__ = "settlement_deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=False)
    delivery_id = Column(Integer, ForeignKey("sales_deliveries.id"), nullable=False)


class SettlementReturn(Base):
    __tablename__ = "settlement_returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=False)
    return_id = Column(Integer, nullable=False)
