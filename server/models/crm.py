from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from database import Base


class Contact(Base):
    """客户联系人"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(50))  # 职位
    phone = Column(String(50))
    email = Column(String(100))
    is_primary = Column(Integer, default=0)  # 是否主要联系人
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Visit(Base):
    """拜访记录"""
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    visit_date = Column(DateTime)
    content = Column(Text)  # 拜访内容
    result = Column(String(500))  # 拜访结果
    next_plan = Column(String(500))  # 下次计划
    operator_id = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())
