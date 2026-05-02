"""
预收预付抵扣记录表
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from database import Base
from datetime import datetime


class AdvanceDeduction(Base):
    """预收/预付抵扣记录"""
    __tablename__ = "advance_deductions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(10), comment="类型: advance_receive(预收) / advance_payment(预付)")
    customer_id = Column(Integer, ForeignKey("customers.id"), comment="客户ID（预收用）")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), comment="供应商ID（预付用）")
    source_type = Column(String(20), comment="来源类型: prepayment/receipt")
    source_id = Column(Integer, comment="来源ID")
    source_code = Column(String(50), comment="来源单号")
    order_type = Column(String(20), comment="核销单据类型: sales_order/purchase_order")
    order_id = Column(Integer, comment="核销单据ID")
    order_code = Column(String(50), comment="核销单据编号")
    amount = Column(Float, comment="抵扣金额")
    remark = Column(Text, comment="备注")
    operator_id = Column(Integer, ForeignKey("employees.id"), comment="操作人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")