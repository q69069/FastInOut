from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.company import Company
from schemas.company import CompanyUpdate, CompanyOut
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/company", tags=["公司信息"])


@router.get("", response_model=ResponseModel)
def get_company(db: Session = Depends(get_db)):
    """获取公司信息"""
    company = db.query(Company).first()
    return ResponseModel(data=CompanyOut.model_validate(company) if company else None)


@router.put("", response_model=ResponseModel)
def update_company(req: CompanyUpdate, db: Session = Depends(get_db)):
    """更新公司信息"""
    company = db.query(Company).first()
    if not company:
        company = Company(**req.model_dump())
        db.add(company)
    else:
        for k, v in req.model_dump(exclude_unset=True).items():
            setattr(company, k, v)
    db.commit()
    db.refresh(company)
    return ResponseModel(data=CompanyOut.model_validate(company))
