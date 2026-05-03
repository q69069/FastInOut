from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact = Column(String(50))
    phone = Column(String(50))
    address = Column(String(500))
    category_id = Column(Integer, ForeignKey("supplier_categories.id"))
    payment_term = Column(String(50))  # 账期
    payable_balance = Column(Float, default=0)  # 应付余额
    bank_name = Column(String(200))
    bank_account = Column(String(100))
    tax_number = Column(String(50))
    remark = Column(String(500))
    status = Column(Integer, default=1)
    created_by = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
