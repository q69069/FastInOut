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
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
