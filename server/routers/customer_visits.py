from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.customer_visit import CustomerVisit
from models.customer_contact import CustomerContact
from schemas.customer_visit import CustomerVisitCreate, CustomerVisitUpdate, CustomerVisitOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/customer-visits", tags=["拜访记录"])


@router.get("", response_model=PaginatedResponse)
def list_visits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(CustomerVisit)
    if customer_id:
        q = q.filter(CustomerVisit.customer_id == customer_id)
    total = q.count()
    items = q.order_by(CustomerVisit.visit_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for v in items:
        out = CustomerVisitOut.model_validate(v)
        if v.contact_id:
            contact = db.query(CustomerContact).get(v.contact_id)
            if contact:
                out = CustomerVisitOut.model_validate(v)
        result.append(out)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_visit(req: CustomerVisitCreate, db: Session = Depends(get_db)):
    visit = CustomerVisit(**req.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return ResponseModel(data=CustomerVisitOut.model_validate(visit))


@router.put("/{visit_id}", response_model=ResponseModel)
def update_visit(visit_id: int, req: CustomerVisitUpdate, db: Session = Depends(get_db)):
    visit = db.query(CustomerVisit).get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="拜访记录不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(visit, k, v)
    db.commit()
    db.refresh(visit)
    return ResponseModel(data=CustomerVisitOut.model_validate(visit))


@router.delete("/{visit_id}", response_model=ResponseModel)
def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(CustomerVisit).get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="拜访记录不存在")
    db.delete(visit)
    db.commit()
    return ResponseModel(message="删除成功")
