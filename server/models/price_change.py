"""
价格变动记录表
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from database import Base
from datetime import datetime


class PriceChangeLog(Base):
    __tablename__ = "price_change_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")

    field_name = Column(String(30), comment="变更字段: purchase_price/default_price")
    old_value = Column(Numeric(12, 2), comment="旧值")
    new_value = Column(Numeric(12, 2), comment="新值")

    operator_id = Column(Integer, ForeignKey("employees.id"), comment="操作人ID")
    operator_name = Column(String(50), comment="操作人姓名")

    change_time = Column(DateTime, default=datetime.now, comment="变更时间")
    ip_address = Column(String(50), comment="IP地址")
