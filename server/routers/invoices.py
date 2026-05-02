from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.invoice import Invoice
from models.customer import Customer
from models.supplier import Supplier
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/invoices", tags=["发票管理"])

STATUS_MAP = {1: "未认证", 2: "已认证", 3: "已作废"}


@router.get("", response_model=PaginatedResponse)
def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    invoice_type: str = Query(None),
    status: int = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Invoice)
    if invoice_type:
        q = q.filter(Invoice.invoice_type == invoice_type)
    if status:
        q = q.filter(Invoice.status == status)
    if keyword:
        q = q.filter(
            (Invoice.invoice_code.contains(keyword)) |
            (Invoice.invoice_no.contains(keyword))
        )
    total = q.count()
    items = q.order_by(Invoice.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for inv in items:
        out = InvoiceOut.model_validate(inv)
        if inv.customer_id:
            c = db.query(Customer).get(inv.customer_id)
            out.customer_name = c.name if c else None
        if inv.supplier_id:
            s = db.query(Supplier).get(inv.supplier_id)
            out.supplier_name = s.name if s else None
        result.append(out)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.get("/stats", response_model=ResponseModel)
def invoice_stats(
    invoice_type: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Invoice)
    if invoice_type:
        q = q.filter(Invoice.invoice_type == invoice_type)
    total_count = q.count()
    total_amount = sum(inv.total_amount or 0 for inv in q.all())
    uncertified = q.filter(Invoice.status == 1).count()
    certified = q.filter(Invoice.status == 2).count()
    voided = q.filter(Invoice.status == 3).count()
    return ResponseModel(data={
        "total_count": total_count, "total_amount": total_amount,
        "uncertified": uncertified, "certified": certified, "voided": voided
    })


@router.get("/{invoice_id}", response_model=ResponseModel)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="发票不存在")
    out = InvoiceOut.model_validate(inv)
    if inv.customer_id:
        c = db.query(Customer).get(inv.customer_id)
        out.customer_name = c.name if c else None
    if inv.supplier_id:
        s = db.query(Supplier).get(inv.supplier_id)
        out.supplier_name = s.name if s else None
    return ResponseModel(data=out)


@router.post("", response_model=ResponseModel)
def create_invoice(req: InvoiceCreate, db: Session = Depends(get_db)):
    inv = Invoice(**req.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return ResponseModel(data=InvoiceOut.model_validate(inv))


@router.put("/{invoice_id}", response_model=ResponseModel)
def update_invoice(invoice_id: int, req: InvoiceUpdate, db: Session = Depends(get_db)):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="发票不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(inv, k, v)
    db.commit()
    db.refresh(inv)
    return ResponseModel(data=InvoiceOut.model_validate(inv))


@router.put("/{invoice_id}/certify", response_model=ResponseModel)
def certify_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="发票不存在")
    if inv.status == 3:
        raise HTTPException(status_code=400, detail="已作废发票不能认证")
    inv.status = 2
    db.commit()
    return ResponseModel(message="认证成功")


@router.put("/{invoice_id}/void", response_model=ResponseModel)
def void_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="发票不存在")
    inv.status = 3
    db.commit()
    return ResponseModel(message="作废成功")


@router.delete("/{invoice_id}", response_model=ResponseModel)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="发票不存在")
    db.delete(inv)
    db.commit()
    return ResponseModel(message="删除成功")
