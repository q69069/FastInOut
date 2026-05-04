"""费用管理模型 — Phase A Day 5-6"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), default="expense")  # expense/income
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_no = Column(String(30), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    amount = Column(Float, default=0)
    payee = Column(String(50))  # 收款人
    payee_is_employee = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  # pending/approved/rejected/paid
    description = Column(Text)
    invoice_url = Column(String(500))
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("employees.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    remark = Column(Text)
