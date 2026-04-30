from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # SK+日期+序号
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount = Column(Float, default=0)
    payment_method = Column(String(50))  # 现金/转账/微信/支付宝/其他
    stockout_id = Column(Integer, ForeignKey("sales_stockouts.id"), nullable=True)  # 关联出库单
    receipt_type = Column(String(20), default="normal")  # normal/pre 预收款
    status = Column(Integer, default=0)  # 0=待确认 1=已确认
    operator_id = Column(Integer, ForeignKey("employees.id"))
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # FK+日期+序号
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    amount = Column(Float, default=0)
    payment_method = Column(String(50))  # 现金/转账/微信/支付宝/其他
    stockin_id = Column(Integer, ForeignKey("purchase_stockins.id"), nullable=True)  # 关联入库单
    payment_type = Column(String(20), default="normal")  # normal/pre 预付款
    status = Column(Integer, default=0)  # 0=待确认 1=已确认
    operator_id = Column(Integer, ForeignKey("employees.id"))
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)
