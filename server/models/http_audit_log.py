from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class HttpAuditLog(Base):
    __tablename__ = "http_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    method = Column(String(10), nullable=False)
    path = Column(String(200), nullable=False)
    entity_type = Column(String(30))
    entity_id = Column(Integer)
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
