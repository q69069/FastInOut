from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_key = Column(String(20), unique=True, comment="角色标识: admin/supervisor/sales/finance/warehouse")
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    permissions_json = Column(Text, default="[]")
    is_system = Column(Integer, default=1, comment="系统角色不可删除")
    sort_order = Column(Integer, default=0)
    status = Column(String(10), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
