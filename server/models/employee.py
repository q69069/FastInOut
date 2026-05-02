from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # 工号
    name = Column(String(50), nullable=False)
    phone = Column(String(50))
    position = Column(String(100))  # 岗位
    username = Column(String(100), unique=True)
    password_hash = Column(String(200))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)  # 角色
    role_type = Column(String(20), comment="角色类型: admin/sales/warehouse/finance")  # 角色类型
    warehouse_ids = Column(String(200), comment="负责仓库IDs，逗号分隔")  # 负责仓库
    route_ids = Column(String(200), comment="负责路线IDs，逗号分隔")  # 负责路线
    bypass_audit = Column(Integer, default=0, comment="是否免审核 0=否 1=是")  # 免审核
    online_status = Column(String(10), default="offline", comment="在线状态 online/offline/busy")  # 在线状态
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
