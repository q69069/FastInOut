from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.finance import Receipt, Payment
from models.customer import Customer
from models.supplier import Supplier
from schemas.finance import ReceiptCreate, ReceiptOut, PaymentCreate, PaymentOut
from schemas.common import ResponseModel, PaginatedResponse
from datetime import datetime

router = APIRouter(prefix="/api/finance", tags=["财务"])


def _gen_code(prefix: str, db: Session, model) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(model).count()
    return f"{prefix}{today}{count + 1:03d}"


# === 收款 ===
@router.get("/receipts", response_model=PaginatedResponse)
def list_receipts(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None), db: Session = Depends(get_db)
):
    q = db.query(Receipt)
    if customer_id:
        q = q.filter(Receipt.customer_id == customer_id)
    total = q.count()
    items = q.order_by(Receipt.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[ReceiptOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/receipts", response_model=ResponseModel)
def create_receipt(req: ReceiptCreate, db: Session = Depends(get_db)):
    code = _gen_code("SK", db, Receipt)
    receipt = Receipt(code=code, customer_id=req.customer_id, amount=req.amount, payment_method=req.payment_method, remark=req.remark)
    db.add(receipt)
    # 更新客户应收余额
    customer = db.query(Customer).get(req.customer_id)
    if customer:
        customer.receivable_balance -= req.amount
    db.commit()
    db.refresh(receipt)
    return ResponseModel(data=ReceiptOut.model_validate(receipt))


# === 付款 ===
@router.get("/payments", response_model=PaginatedResponse)
def list_payments(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    supplier_id: int = Query(None), db: Session = Depends(get_db)
):
    q = db.query(Payment)
    if supplier_id:
        q = q.filter(Payment.supplier_id == supplier_id)
    total = q.count()
    items = q.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[PaymentOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/payments", response_model=ResponseModel)
def create_payment(req: PaymentCreate, db: Session = Depends(get_db)):
    code = _gen_code("FK", db, Payment)
    payment = Payment(code=code, supplier_id=req.supplier_id, amount=req.amount, payment_method=req.payment_method, remark=req.remark)
    db.add(payment)
    # 更新供应商应付余额
    supplier = db.query(Supplier).get(req.supplier_id)
    if supplier:
        supplier.payable_balance -= req.amount
    db.commit()
    db.refresh(payment)
    return ResponseModel(data=PaymentOut.model_validate(payment))


# === 应收/应付/流水 ===
@router.get("/receivables", response_model=ResponseModel)
def list_receivables(db: Session = Depends(get_db)):
    """应收账款"""
    customers = db.query(Customer).filter(Customer.receivable_balance != 0).all()
    return ResponseModel(data=[{"id": c.id, "name": c.name, "balance": c.receivable_balance} for c in customers])


@router.get("/payables", response_model=ResponseModel)
def list_payables(db: Session = Depends(get_db)):
    """应付账款"""
    suppliers = db.query(Supplier).filter(Supplier.payable_balance != 0).all()
    return ResponseModel(data=[{"id": s.id, "name": s.name, "balance": s.payable_balance} for s in suppliers])


@router.get("/flow", response_model=ResponseModel)
def finance_flow(db: Session = Depends(get_db)):
    """收支流水（预留）"""
    return ResponseModel(data=[], message="功能开发中")
