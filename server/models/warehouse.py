from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    warehouse_type = Column(String(20), default="normal")  # normal=普通仓库, vehicle=车仓, other=其他
    address = Column(String(500))
    manager = Column(String(50))
    phone = Column(String(50))
    description = Column(String(500))  # 仓库描述
    is_default = Column(Boolean, default=False)
    plate_number = Column(String(20))  # 车牌号（车仓用）
    driver_name = Column(String(50))  # 驾驶员
    driver_phone = Column(String(20))  # 驾驶员电话
    capacity = Column(Float)  # 载货量
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    routes = relationship("Route", back_populates="warehouse")
