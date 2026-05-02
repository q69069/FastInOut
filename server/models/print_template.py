from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from database import Base


class PrintTemplate(Base):
    """打印模板"""
    __tablename__ = "print_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 模板名称
    template_type = Column(String(50), nullable=False)  # 类型：sales/purchase/stockin/stockout/statement/receipt
    paper_size = Column(String(20), default="A4")  # 纸张：A4/58mm/80mm
    content = Column(Text)  # HTML模板内容
    is_default = Column(Boolean, default=False)  # 是否默认模板
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
