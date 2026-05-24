from datetime import datetime
from sqlalchemy import text, Column, Integer, String, DateTime, func
from database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="渠道名称")
    code = Column(String(30), unique=True, comment="渠道编码")
    parent_id = Column(Integer, default=0, comment="上级渠道ID")
    level = Column(Integer, default=1, comment="层级(1/2/3)")
    sort_order = Column(Integer, default=0)
    remark = Column(String(500))
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)