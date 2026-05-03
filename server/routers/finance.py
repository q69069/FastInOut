from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.finance import Receipt, Payment
from models.customer import Customer
from models.supplier import Supplier
from models.sales import SalesStockout
from models.purchase import PurchaseStockin
from models.employee import Employee
from schemas.finance import (
    ReceiptCreate, ReceiptOut, PaymentCreate, PaymentOut,
    PreReceiptCreate, PrePaymentCreate, PreToReceivable, PreToPayable
)
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.auth import decode_access_token
from datetime import datetime

router = APIRouter(prefix="/api/finance", tags=["财务"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    """从请求头解析当前用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def _gen_code(prefix: str, db: Session, model) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(model).count()
    return f"{prefix}{today}-{count + 1:03d}"


# ========== 收款管理 ==========
@router.get("/receipts", response_model=PaginatedResponse)
def list_receipts(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None), payment_method: str = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    receipt_type: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Receipt)
    # 应用数据权限过滤（财务按客户路线过滤）
    q = DataFilter.apply_scope(q, Receipt, user, db, scope_field="created_by", module_key="finance")
    if customer_id:
        q = q.filter(Receipt.customer_id == customer_id)
    if payment_method:
        q = q.filter(Receipt.payment_method == payment_method)
    if receipt_type:
        q = q.filter(Receipt.receipt_type == receipt_type)
    if start_date:
        q = q.filter(Receipt.created_at >= start_date)
    if end_date:
        q = q.filter(Receipt.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(Receipt.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in items:
        customer = db.query(Customer).get(r.customer_id)
        result.append({
            "id": r.id, "code": r.code, "customer_id": r.customer_id,
            "customer_name": customer.name if customer else "",
            "amount": r.amount, "payment_method": r.payment_method,
            "stockout_id": r.stockout_id, "receipt_type": r.receipt_type,
            "status": r.status, "remark": r.remark,
            "created_at": str(r.created_at),
            "confirmed_at": str(r.confirmed_at) if r.confirmed_at else None
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/receipts", response_model=ResponseModel)
def create_receipt(req: ReceiptCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    code = _gen_code("SK", db, Receipt)
    receipt = Receipt(
        code=code, customer_id=req.customer_id, amount=req.amount,
        payment_method=req.payment_method, stockout_id=req.stockout_id,
        receipt_type="normal", status=1, remark=req.remark,
        confirmed_at=datetime.now(), created_by=user.id
    )
    db.add(receipt)
    customer = db.query(Customer).get(req.customer_id)
    if customer:
        customer.receivable_balance -= req.amount
    db.commit()
    db.refresh(receipt)
    return ResponseModel(data={"id": receipt.id, "code": code})


@router.get("/receipts/{receipt_id}", response_model=ResponseModel)
def get_receipt(receipt_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    r = db.query(Receipt).get(receipt_id)
    if not r:
        raise HTTPException(status_code=404, detail="收款单不存在")
    if user.role_id != 5 and r.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权查看此收款单")
    customer = db.query(Customer).get(r.customer_id)
    return ResponseModel(data={
        "id": r.id, "code": r.code, "customer_id": r.customer_id,
        "customer_name": customer.name if customer else "",
        "amount": r.amount, "payment_method": r.payment_method,
        "stockout_id": r.stockout_id, "receipt_type": r.receipt_type,
        "status": r.status, "remark": r.remark,
        "created_at": str(r.created_at)
    })


@router.delete("/receipts/{receipt_id}", response_model=ResponseModel)
def delete_receipt(receipt_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    r = db.query(Receipt).get(receipt_id)
    if not r:
        raise HTTPException(status_code=404, detail="收款单不存在")
    if user.role_id != 5 and r.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权删除此收款单")
    if r.status == 1:
        customer = db.query(Customer).get(r.customer_id)
        if customer:
            customer.receivable_balance += r.amount
    db.delete(r)
    db.commit()
    return ResponseModel(message="已删除")


# ========== 付款管理 ==========
@router.get("/payments", response_model=PaginatedResponse)
def list_payments(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    supplier_id: int = Query(None), payment_method: str = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    payment_type: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Payment)
    # 应用数据权限过滤
    q = DataFilter.apply_scope(q, Payment, user, db, scope_field="created_by", module_key="finance")
    if supplier_id:
        q = q.filter(Payment.supplier_id == supplier_id)
    if payment_method:
        q = q.filter(Payment.payment_method == payment_method)
    if payment_type:
        q = q.filter(Payment.payment_type == payment_type)
    if start_date:
        q = q.filter(Payment.created_at >= start_date)
    if end_date:
        q = q.filter(Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for p in items:
        supplier = db.query(Supplier).get(p.supplier_id)
        result.append({
            "id": p.id, "code": p.code, "supplier_id": p.supplier_id,
            "supplier_name": supplier.name if supplier else "",
            "amount": p.amount, "payment_method": p.payment_method,
            "stockin_id": p.stockin_id, "payment_type": p.payment_type,
            "status": p.status, "remark": p.remark,
            "created_at": str(p.created_at),
            "confirmed_at": str(p.confirmed_at) if p.confirmed_at else None
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/payments", response_model=ResponseModel)
def create_payment(req: PaymentCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    code = _gen_code("FK", db, Payment)
    payment = Payment(
        code=code, supplier_id=req.supplier_id, amount=req.amount,
        payment_method=req.payment_method, stockin_id=req.stockin_id,
        payment_type="normal", status=1, remark=req.remark,
        confirmed_at=datetime.now(), created_by=user.id
    )
    db.add(payment)
    supplier = db.query(Supplier).get(req.supplier_id)
    if supplier:
        supplier.payable_balance -= req.amount
    db.commit()
    db.refresh(payment)
    return ResponseModel(data={"id": payment.id, "code": code})


@router.get("/payments/{payment_id}", response_model=ResponseModel)
def get_payment(payment_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    p = db.query(Payment).get(payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="付款单不存在")
    if user.role_id != 5 and p.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权查看此付款单")
    supplier = db.query(Supplier).get(p.supplier_id)
    return ResponseModel(data={
        "id": p.id, "code": p.code, "supplier_id": p.supplier_id,
        "supplier_name": supplier.name if supplier else "",
        "amount": p.amount, "payment_method": p.payment_method,
        "stockin_id": p.stockin_id, "payment_type": p.payment_type,
        "status": p.status, "remark": p.remark,
        "created_at": str(p.created_at)
    })


@router.delete("/payments/{payment_id}", response_model=ResponseModel)
def delete_payment(payment_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    p = db.query(Payment).get(payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="付款单不存在")
    if user.role_id != 5 and p.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权删除此付款单")
    if p.status == 1:
        supplier = db.query(Supplier).get(p.supplier_id)
        if supplier:
            supplier.payable_balance += p.amount
    db.delete(p)
    db.commit()
    return ResponseModel(message="已删除")


# ========== 预收款/预付款 ==========
@router.post("/pre-receipt", response_model=ResponseModel)
def create_pre_receipt(req: PreReceiptCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    code = _gen_code("SK", db, Receipt)
    receipt = Receipt(
        code=code, customer_id=req.customer_id, amount=req.amount,
        payment_method=req.payment_method, receipt_type="pre",
        status=1, remark=req.remark, confirmed_at=datetime.now(),
        created_by=user.id
    )
    db.add(receipt)
    # 预收款减少客户应收余额
    customer = db.query(Customer).get(req.customer_id)
    if customer:
        customer.receivable_balance = (customer.receivable_balance or 0) - req.amount
    db.commit()
    db.refresh(receipt)
    return ResponseModel(data={"id": receipt.id, "code": code, "message": "预收款登记成功"})


@router.post("/pre-payment", response_model=ResponseModel)
def create_pre_payment(req: PrePaymentCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    code = _gen_code("FK", db, Payment)
    payment = Payment(
        code=code, supplier_id=req.supplier_id, amount=req.amount,
        payment_method=req.payment_method, payment_type="pre",
        status=1, remark=req.remark, confirmed_at=datetime.now(),
        created_by=user.id
    )
    db.add(payment)
    # 预付款减少供应商应付余额
    supplier = db.query(Supplier).get(req.supplier_id)
    if supplier:
        supplier.payable_balance = (supplier.payable_balance or 0) - req.amount
    db.commit()
    db.refresh(payment)
    return ResponseModel(data={"id": payment.id, "code": code, "message": "预付款登记成功"})


@router.post("/pre-to-receivable", response_model=ResponseModel)
def pre_to_receivable(req: PreToReceivable, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    receipt = db.query(Receipt).get(req.receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="预收款单不存在")
    if user.role_id != 5 and receipt.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权操作此收款单")
    if receipt.receipt_type != "pre":
        raise HTTPException(status_code=400, detail="非预收款单")
    if receipt.amount < req.amount:
        raise HTTPException(status_code=400, detail="预收款余额不足")
    stockout = db.query(SalesStockout).get(req.stockout_id)
    if not stockout:
        raise HTTPException(status_code=404, detail="出库单不存在")
    receipt.amount -= req.amount
    customer = db.query(Customer).get(receipt.customer_id)
    if customer:
        customer.receivable_balance -= req.amount
    db.commit()
    return ResponseModel(message="预收冲应收成功")


@router.post("/pre-to-payable", response_model=ResponseModel)
def pre_to_payable(req: PreToPayable, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    payment = db.query(Payment).get(req.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="预付款单不存在")
    if user.role_id != 5 and payment.created_by != user.id:
        raise HTTPException(status_code=403, detail="无权操作此付款单")
    if payment.payment_type != "pre":
        raise HTTPException(status_code=400, detail="非预付款单")
    if payment.amount < req.amount:
        raise HTTPException(status_code=400, detail="预付款余额不足")
    stockin = db.query(PurchaseStockin).get(req.stockin_id)
    if not stockin:
        raise HTTPException(status_code=404, detail="入库单不存在")
    payment.amount -= req.amount
    supplier = db.query(Supplier).get(payment.supplier_id)
    if supplier:
        supplier.payable_balance -= req.amount
    db.commit()
    return ResponseModel(message="预付冲应付成功")


# ========== 应收账款 ==========
@router.get("/receivables", response_model=ResponseModel)
def list_receivables(db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.receivable_balance != 0).all()
    result = []
    for c in customers:
        result.append({
            "id": c.id, "name": c.name, "balance": c.receivable_balance,
            "contact": c.contact, "phone": c.phone
        })
    return ResponseModel(data=result)


@router.get("/receivables/{customer_id}", response_model=ResponseModel)
def get_receivable_detail(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    receipts = db.query(Receipt).filter(Receipt.customer_id == customer_id, Receipt.status == 1).all()
    from models.sales import SalesStockout
    stockouts = db.query(SalesStockout).filter(SalesStockout.customer_id == customer_id, SalesStockout.status == 2).all()
    detail = []
    for so in stockouts:
        detail.append({"type": "sales_out", "code": so.code, "amount": so.total_amount, "date": str(so.created_at)})
    for r in receipts:
        detail.append({"type": "receipt", "code": r.code, "amount": -r.amount, "date": str(r.created_at)})
    detail.sort(key=lambda x: x["date"])
    return ResponseModel(data={
        "customer_name": customer.name,
        "balance": customer.receivable_balance,
        "detail": detail
    })


# ========== 应付账款 ==========
@router.get("/payables", response_model=ResponseModel)
def list_payables(db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).filter(Supplier.payable_balance != 0).all()
    result = []
    for s in suppliers:
        result.append({
            "id": s.id, "name": s.name, "balance": s.payable_balance,
            "contact": s.contact, "phone": s.phone
        })
    return ResponseModel(data=result)


@router.get("/payables/{supplier_id}", response_model=ResponseModel)
def get_payable_detail(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    payments = db.query(Payment).filter(Payment.supplier_id == supplier_id, Payment.status == 1).all()
    from models.purchase import PurchaseStockin
    stockins = db.query(PurchaseStockin).filter(PurchaseStockin.supplier_id == supplier_id, PurchaseStockin.status == 2).all()
    detail = []
    for si in stockins:
        detail.append({"type": "purchase_in", "code": si.code, "amount": si.total_amount, "date": str(si.created_at)})
    for p in payments:
        detail.append({"type": "payment", "code": p.code, "amount": -p.amount, "date": str(p.created_at)})
    detail.sort(key=lambda x: x["date"])
    return ResponseModel(data={
        "supplier_name": supplier.name,
        "balance": supplier.payable_balance,
        "detail": detail
    })


# ========== 收支流水（M8: 批量加载优化） ==========
@router.get("/flow", response_model=PaginatedResponse)
def finance_flow(
    type: str = Query(None),  # income/expense
    start_date: str = Query(None), end_date: str = Query(None),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    # M8: 批量预加载客户和供应商名称，避免逐条查询
    customers_map = {c.id: c.name for c in db.query(Customer).all()}
    suppliers_map = {s.id: s.name for s in db.query(Supplier).all()}

    records = []
    # 收款记录
    if not type or type == "income":
        q = db.query(Receipt).filter(Receipt.status == 1)
        q = DataFilter.apply_scope(q, Receipt, user, db, scope_field="created_by", module_key="finance")
        if start_date:
            q = q.filter(Receipt.created_at >= start_date)
        if end_date:
            q = q.filter(Receipt.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        for r in q.all():
            records.append({
                "id": r.id, "code": r.code, "type": "income",
                "amount": r.amount, "payment_method": r.payment_method,
                "party_name": customers_map.get(r.customer_id, ""),
                "remark": r.remark, "created_at": str(r.created_at)
            })
    # 付款记录
    if not type or type == "expense":
        q = db.query(Payment).filter(Payment.status == 1)
        q = DataFilter.apply_scope(q, Payment, user, db, scope_field="created_by", module_key="finance")
        if start_date:
            q = q.filter(Payment.created_at >= start_date)
        if end_date:
            q = q.filter(Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        for p in q.all():
            records.append({
                "id": p.id, "code": p.code, "type": "expense",
                "amount": p.amount, "payment_method": p.payment_method,
                "party_name": suppliers_map.get(p.supplier_id, ""),
                "remark": p.remark, "created_at": str(p.created_at)
            })
    records.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(data=records[start:end], total=total, page=page, page_size=page_size)
