"""
审核记录表
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 审核对象类型: sales_order, purchase_order, transfer_order, etc.
    target_type = Column(String(50), nullable=False, comment="对象类型")
    target_id = Column(Integer, nullable=False, comment="对象ID")
    target_code = Column(String(50), comment="对象编号")

    action = Column(String(20), nullable=False, comment="动作: approve/reject/create")
    comment = Column(Text, comment="审核意见")

    auditor_id = Column(Integer, ForeignKey("employees.id"), comment="审核人ID")
    auditor_name = Column(String(50), comment="审核人姓名")

    created_at = Column(DateTime, default=datetime.now, comment="审核时间")
    ip_address = Column(String(50), comment="IP地址")
    device_info = Column(String(200), comment="设备信息")
