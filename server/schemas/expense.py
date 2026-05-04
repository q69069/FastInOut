from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ExpenseCategoryCreate(BaseModel):
    name: str
    type: str = "expense"
    sort_order: int = 0


class ExpenseCategoryOut(BaseModel):
    id: int
    name: str
    type: str
    sort_order: int
    status: int

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    category_id: int
    amount: float = Field(gt=0, description="金额必须大于0")
    payee: Optional[str] = None
    payee_is_employee: bool = False
    description: Optional[str] = None
    remark: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    expense_no: str
    category_id: int
    amount: float
    payee: Optional[str] = None
    payee_is_employee: bool
    status: str
    description: Optional[str] = None
    created_by: int
    approver_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    remark: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
