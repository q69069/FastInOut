from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    logo: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CompanyUpdate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
