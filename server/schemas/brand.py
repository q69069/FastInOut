from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrandCreate(BaseModel):
    name: str
    code: Optional[str] = None
    contact: Optional[str] = None
    remark: Optional[str] = None
    status: int = 1


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    contact: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class BrandOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    contact: Optional[str] = None
    remark: Optional[str] = None
    status: int = 1
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True