from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # SK+日期+序号
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount = Column(Float, default=0)
    payment_method = Column(String(50))  # 收款方式
    operator_id = Column(Integer, ForeignKey("employees.id"))
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # FK+日期+序号
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    amount = Column(Float, default=0)
    payment_method = Column(String(50))  # 付款方式
    operator_id = Column(Integer, ForeignKey("employees.id"))
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
