from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class BankStatementCreate(BaseModel):
    bank_account: Optional[str] = None
    statement_date: date
    description: str
    debit: float = 0
    credit: float = 0
    remark: Optional[str] = None


class BankStatementOut(BaseModel):
    id: int
    bank_account: Optional[str] = None
    statement_date: Optional[date] = None
    description: str
    debit: float
    credit: float
    matched: bool
    matched_id: Optional[int] = None
    matched_type: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
