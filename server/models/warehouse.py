from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    manager = Column(String(50))
    phone = Column(String(50))
    is_default = Column(Boolean, default=False)
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
