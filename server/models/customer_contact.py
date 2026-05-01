from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database import Base


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(50))
    position = Column(String(100))
    wechat = Column(String(100))
    email = Column(String(100))
    is_primary = Column(Integer, default=0)  # 1=主要联系人
    remark = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
