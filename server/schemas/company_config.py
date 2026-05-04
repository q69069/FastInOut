"""公司设置 Schema"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CompanyConfigCreate(BaseModel):
    config_key: str
    config_value: Optional[str] = None
    description: Optional[str] = None


class CompanyConfigOut(BaseModel):
    id: int
    config_key: str
    config_value: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
