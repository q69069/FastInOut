from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operator = Column(String(100))
    action = Column(String(100))
    target = Column(String(200))
    detail = Column(Text)
    ip = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    content = Column(Text)
    msg_type = Column(String(50))  # alert/system/task
    target_user_id = Column(Integer)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime)


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500))
    file_size = Column(Integer)
    backup_type = Column(String(50))  # manual/auto
    operator = Column(String(100))
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
