from datetime import datetime
from sqlalchemy import text, Column, Integer, String, Text, DateTime, func
from database import Base

# OperationLog 已移至 operation_log.py，避免重复定义


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    content = Column(Text)
    msg_type = Column(String(50))  # alert/system/task
    target_user_id = Column(Integer)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime)


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500))
    file_size = Column(Integer)
    backup_type = Column(String(50))  # manual/auto
    operator = Column(String(100))
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
