from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from database import Base


class Invoice(Base):
    """发票管理"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_type = Column(String(20), nullable=False)  # purchase/sales
    invoice_code = Column(String(50))  # 发票代码
    invoice_no = Column(String(50))  # 发票号码
    related_id = Column(Integer)  # 关联单据ID
    related_type = Column(String(20))  # 关联类型：stockin/stockout
    customer_id = Column(Integer)  # 客户（销售发票）
    supplier_id = Column(Integer)  # 供应商（采购发票）
    amount = Column(Float, default=0)  # 不含税金额
    tax_amount = Column(Float, default=0)  # 税额
    total_amount = Column(Float, default=0)  # 价税合计
    invoice_date = Column(Date)  # 开票日期
    status = Column(Integer, default=1)  # 1=未认证 2=已认证 3=已作废
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
