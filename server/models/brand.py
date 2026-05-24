from datetime import datetime
from sqlalchemy import text, Column, Integer, String, DateTime, func
from database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="品牌名称")
    code = Column(String(30), unique=True, comment="品牌编码")
    contact = Column(String(100), comment="联系方式")
    remark = Column(String(500))
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)