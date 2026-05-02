from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class PrintTemplateCreate(BaseModel):
    name: str
    template_type: str  # sales/purchase/stockin/stockout/statement/receipt
    paper_size: str = "A4"  # A4/58mm/80mm
    content: Optional[str] = None
    is_default: bool = False


class PrintTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    paper_size: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[int] = None


class PrintTemplateOut(BaseModel):
    id: int
    name: str
    template_type: str
    paper_size: str
    content: Optional[str] = None
    is_default: bool
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
