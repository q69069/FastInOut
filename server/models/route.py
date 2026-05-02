"""
路线档案表
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, comment="路线编码")
    name = Column(String(50), nullable=False, comment="路线名称")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="所属仓库")
    sort_order = Column(Integer, default=0, comment="排序")
    description = Column(Text, comment="描述")
    status = Column(String(10), default="active", comment="状态 active/inactive")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    warehouse = relationship("Warehouse", back_populates="routes")
    # employee_routes 关联通过关联表
