from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.customer_level import CustomerLevel
from schemas.customer_level import CustomerLevelCreate, CustomerLevelUpdate, CustomerLevelOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/customer-levels", tags=["客户等级"])


@router.get("", response_model=PaginatedResponse)
def list_customer_levels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(CustomerLevel)
    if keyword:
        q = q.filter(CustomerLevel.name.contains(keyword) | CustomerLevel.code.contains(keyword))
    if status is not None:
        q = q.filter(CustomerLevel.status == status)
    total = q.count()
    items = q.order_by(CustomerLevel.sort_order, CustomerLevel.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[CustomerLevelOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_customer_level(req: CustomerLevelCreate, db: Session = Depends(get_db)):
    level = CustomerLevel(**req.model_dump())
    db.add(level)
    db.commit()
    db.refresh(level)
    return ResponseModel(data=CustomerLevelOut.model_validate(level))


@router.get("/{level_id}", response_model=ResponseModel)
def get_customer_level(level_id: int, db: Session = Depends(get_db)):
    level = db.query(CustomerLevel).get(level_id)
    if not level:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="客户等级不存在")
    return ResponseModel(data=CustomerLevelOut.model_validate(level))


@router.put("/{level_id}", response_model=ResponseModel)
def update_customer_level(level_id: int, req: CustomerLevelUpdate, db: Session = Depends(get_db)):
    level = db.query(CustomerLevel).get(level_id)
    if not level:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="客户等级不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(level, k, v)
    db.commit()
    db.refresh(level)
    return ResponseModel(data=CustomerLevelOut.model_validate(level))


@router.delete("/{level_id}", response_model=ResponseModel)
def delete_customer_level(level_id: int, db: Session = Depends(get_db)):
    level = db.query(CustomerLevel).get(level_id)
    if not level:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="客户等级不存在")
    db.delete(level)
    db.commit()
    return ResponseModel(message="删除成功")