from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChannelCreate(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: int = 0
    level: int = 1
    sort_order: int = 0
    remark: Optional[str] = None
    status: int = 1


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort_order: Optional[int] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class ChannelOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    parent_id: int
    level: int
    sort_order: int
    remark: Optional[str] = None
    status: int = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True