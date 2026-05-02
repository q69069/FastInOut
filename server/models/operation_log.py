"""
操作日志
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("employees.id"), comment="用户ID")
    username = Column(String(50), comment="用户名")
    module = Column(String(50), comment="模块: sales/purchase/inventory/finance")
    action = Column(String(20), comment="动作: create/update/delete/read/confirm")
    target_type = Column(String(50), comment="操作对象类型")
    target_id = Column(Integer, comment="操作对象ID")
    target_name = Column(String(200), comment="操作对象名称")
    detail = Column(Text, comment="操作详情")
    ip_address = Column(String(50), comment="IP地址")
    created_at = Column(DateTime, server_default=func.now())
