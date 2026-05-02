"""
预收预付抵扣记录路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db
from models.advance_deduction import AdvanceDeduction
from routers.auth import get_current_user

router = APIRouter(prefix="/advance-deductions", tags=["预收预付"])


class AdvanceDeductionResponse(BaseModel):
    id: int
    type: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    source_type: Optional[str] = None
    source_id: Optional[int] = None
    source_code: Optional[str] = None
    order_type: Optional[str] = None
    order_id: Optional[int] = None
    order_code: Optional[str] = None
    amount: Optional[float] = None
    remark: Optional[str] = None
    operator_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdvanceDeductionCreate(BaseModel):
    type: str
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    source_type: str
    source_id: int
    source_code: str
    order_type: str
    order_id: int
    order_code: str
    amount: float
    remark: Optional[str] = None


@router.get("/", response_model=list[AdvanceDeductionResponse])
def list_deductions(
    type: str = None,
    customer_id: int = None,
    supplier_id: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(AdvanceDeduction)
    if type:
        query = query.filter(AdvanceDeduction.type == type)
    if customer_id:
        query = query.filter(AdvanceDeduction.customer_id == customer_id)
    if supplier_id:
        query = query.filter(AdvanceDeduction.supplier_id == supplier_id)
    return query.order_by(AdvanceDeduction.created_at.desc()).all()


@router.post("/", response_model=AdvanceDeductionResponse)
def create_deduction(
    data: AdvanceDeductionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deduction = AdvanceDeduction(**data.model_dump(), operator_id=current_user.id)
    db.add(deduction)
    db.commit()
    db.refresh(deduction)
    return deduction