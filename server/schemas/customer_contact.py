from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CustomerContactCreate(BaseModel):
    customer_id: int
    name: str
    phone: Optional[str] = None
    position: Optional[str] = None
    wechat: Optional[str] = None
    email: Optional[str] = None
    is_primary: int = 0
    remark: Optional[str] = None


class CustomerContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    wechat: Optional[str] = None
    email: Optional[str] = None
    is_primary: Optional[int] = None
    remark: Optional[str] = None


class CustomerContactOut(BaseModel):
    id: int
    customer_id: int
    name: str
    phone: Optional[str] = None
    position: Optional[str] = None
    wechat: Optional[str] = None
    email: Optional[str] = None
    is_primary: int = 0
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
