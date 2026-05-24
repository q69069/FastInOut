from datetime import datetime
from sqlalchemy import text, Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact = Column(String(50))  # 联系人
    phone = Column(String(50))
    address = Column(String(500))
    category_id = Column(Integer, ForeignKey("customer_categories.id"))
    level = Column(String(20))  # 等级
    credit_limit = Column(Float, default=0)  # 信用额度
    receivable_balance = Column(Float, default=0)  # 应收余额
    prepaid_balance = Column(Float, default=0)  # 预收余额（客户多付的钱）
    bank_name = Column(String(200))  # 开户行
    bank_account = Column(String(100))  # 银行账号
    tax_number = Column(String(50))  # 税号
    remark = Column(String(500))
    route_id = Column(Integer, ForeignKey("routes.id"), comment="所属路线")
    salesman_ids = Column(String(200), comment="负责业务员IDs，逗号分隔")
    default_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="默认仓库")
    channel = Column(String(50), comment="渠道")
    customer_level = Column(String(20), comment="客户等级(A/B/C)")
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
