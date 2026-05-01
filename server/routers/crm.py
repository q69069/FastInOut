from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.crm import Contact, Visit
from schemas.crm import (
    ContactCreate, ContactUpdate, ContactOut,
    VisitCreate, VisitUpdate, VisitOut,
)
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(tags=["CRM"])


# ==================== 联系人 ====================

@router.get("/api/contacts", response_model=PaginatedResponse)
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    db: Session = Depends(get_db),
):
    """联系人列表"""
    q = db.query(Contact)
    if customer_id:
        q = q.filter(Contact.customer_id == customer_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[ContactOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/api/contacts", response_model=ResponseModel)
def create_contact(req: ContactCreate, db: Session = Depends(get_db)):
    """新增联系人"""
    obj = Contact(**req.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ResponseModel(data=ContactOut.model_validate(obj))


@router.put("/api/contacts/{contact_id}", response_model=ResponseModel)
def update_contact(contact_id: int, req: ContactUpdate, db: Session = Depends(get_db)):
    """更新联系人"""
    obj = db.query(Contact).get(contact_id)
    if not obj:
        raise HTTPException(status_code=404, detail="联系人不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return ResponseModel(data=ContactOut.model_validate(obj))


@router.delete("/api/contacts/{contact_id}", response_model=ResponseModel)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """删除联系人"""
    obj = db.query(Contact).get(contact_id)
    if not obj:
        raise HTTPException(status_code=404, detail="联系人不存在")
    db.delete(obj)
    db.commit()
    return ResponseModel(message="删除成功")


# ==================== 拜访记录 ====================

@router.get("/api/visits", response_model=PaginatedResponse)
def list_visits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    db: Session = Depends(get_db),
):
    """拜访记录列表"""
    q = db.query(Visit)
    if customer_id:
        q = q.filter(Visit.customer_id == customer_id)
    q = q.order_by(Visit.visit_date.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[VisitOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/api/visits", response_model=ResponseModel)
def create_visit(req: VisitCreate, db: Session = Depends(get_db)):
    """新增拜访记录"""
    obj = Visit(**req.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ResponseModel(data=VisitOut.model_validate(obj))


@router.delete("/api/visits/{visit_id}", response_model=ResponseModel)
def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    """删除拜访记录"""
    obj = db.query(Visit).get(visit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="拜访记录不存在")
    db.delete(obj)
    db.commit()
    return ResponseModel(message="删除成功")
