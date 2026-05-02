"""
消息中心表
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class AppMessage(Base):
    """消息中心"""
    __tablename__ = "app_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), comment="消息类型: system/order/audit/reminder/payment")
    title = Column(String(200), comment="消息标题")
    content = Column(Text, comment="消息内容")
    recipient_id = Column(Integer, ForeignKey("employees.id"), comment="接收人ID")
    sender_id = Column(Integer, ForeignKey("employees.id"), comment="发送人ID")
    status = Column(String(20), default="unread", comment="状态 unread/read")
    reference_type = Column(String(50), comment="关联类型: sales_order/purchase_order等")
    reference_id = Column(Integer, comment="关联ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    read_at = Column(DateTime, comment="阅读时间")