from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from database import Base


class CustomerVisit(Base):
    __tablename__ = "customer_visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("customer_contacts.id"), nullable=True)
    visit_date = Column(DateTime, nullable=False)
    visit_type = Column(String(50))  # 拜访/电话/微信/其他
    content = Column(Text)  # 拜访内容
    result = Column(Text)  # 拜访结果
    next_plan = Column(Text)  # 下次计划
    operator = Column(String(50))  # 拜访人
    created_by = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
