from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SalesmanCreate(BaseModel):
    employee_id: int
    commission_rate: float = 0
    target_amount: float = 0


class SalesmanUpdate(BaseModel):
    employee_id: Optional[int] = None
    commission_rate: Optional[float] = None
    target_amount: Optional[float] = None
    status: Optional[int] = None


class SalesmanOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str = ""
    commission_rate: float
    target_amount: float
    status: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
