from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class PromotionBase(BaseModel):
    name: str
    promo_type: str = "threshold"  # threshold(满减) / discount(折扣)
    threshold_amount: float = Field(ge=0, default=0)
    discount_value: float = Field(ge=0, default=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: int = 1
    remark: Optional[str] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    promo_type: Optional[str] = None
    threshold_amount: Optional[float] = None
    discount_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class PromotionOut(PromotionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
