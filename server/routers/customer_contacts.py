from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.customer_contact import CustomerContact
from schemas.customer_contact import CustomerContactCreate, CustomerContactUpdate, CustomerContactOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/customer-contacts", tags=["客户联系人"])


@router.get("", response_model=PaginatedResponse)
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(CustomerContact)
    if customer_id:
        q = q.filter(CustomerContact.customer_id == customer_id)
    if keyword:
        q = q.filter(CustomerContact.name.contains(keyword) | CustomerContact.phone.contains(keyword))
    total = q.count()
    items = q.order_by(CustomerContact.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[CustomerContactOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_contact(req: CustomerContactCreate, db: Session = Depends(get_db)):
    contact = CustomerContact(**req.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ResponseModel(data=CustomerContactOut.model_validate(contact))


@router.put("/{contact_id}", response_model=ResponseModel)
def update_contact(contact_id: int, req: CustomerContactUpdate, db: Session = Depends(get_db)):
    contact = db.query(CustomerContact).get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(contact, k, v)
    db.commit()
    db.refresh(contact)
    return ResponseModel(data=CustomerContactOut.model_validate(contact))


@router.delete("/{contact_id}", response_model=ResponseModel)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(CustomerContact).get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    db.delete(contact)
    db.commit()
    return ResponseModel(message="删除成功")
