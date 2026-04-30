from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OperationLogOut(BaseModel):
    id: int
    operator: Optional[str] = None
    action: Optional[str] = None
    target: Optional[str] = None
    detail: Optional[str] = None
    ip: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    title: str
    content: Optional[str] = None
    msg_type: str = "system"
    target_user_id: Optional[int] = None


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: int
    is_read: int
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BackupRecordOut(BaseModel):
    id: int
    filename: Optional[str] = None
    file_size: Optional[int] = None
    backup_type: Optional[str] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
