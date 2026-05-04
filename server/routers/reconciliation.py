"""客户对账路由 — Phase D"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.reconciliation import CustomerReconciliation
from models.sales_delivery import SalesDelivery
from models.sales import SalesReturn
from models.finance import Receipt
from models.customer import Customer
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api", tags=["客户对账"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    from utils.auth import decode_access_token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def _gen_code(db):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"DZ{today}"
    last = db.query(CustomerReconciliation).filter(CustomerReconciliation.code.like(f"{prefix}%")).order_by(CustomerReconciliation.id.desc()).first()
    seq = int(last.code[-4:]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


@router.get("/reconciliations", response_model=PaginatedResponse)
def list_reconciliations(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None), customer_id: int = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(CustomerReconciliation)
    if status:
        q = q.filter(CustomerReconciliation.status == status)
    if customer_id:
        q = q.filter(CustomerReconciliation.customer_id == customer_id)
    total = q.count()
    items = q.order_by(CustomerReconciliation.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for r in items:
        cust = db.query(Customer).get(r.customer_id)
        result.append({
            "id": r.id, "code": r.code,
            "customer_id": r.customer_id,
            "customer_name": cust.name if cust else "",
            "period_start": str(r.period_start) if r.period_start else None,
            "period_end": str(r.period_end) if r.period_end else None,
            "total_sales": r.total_sales, "total_returns": r.total_returns,
            "total_receipts": r.total_receipts, "balance": r.balance,
            "status": r.status,
            "confirmed_at": str(r.confirmed_at) if r.confirmed_at else None,
            "created_at": str(r.created_at)
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/reconciliations", response_model=ResponseModel)
def create_reconciliation(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """生成对账单 — 自动汇总指定期间的销售/退货/收款"""
    user = get_current_user(authorization, db)
    customer_id = data["customer_id"]
    period_start = data["period_start"]
    period_end = data["period_end"]

    # 汇总销售
    sales = db.query(SalesDelivery).filter(
        SalesDelivery.customer_id == customer_id,
        SalesDelivery.status.in_(["locked", "settled"]),
        SalesDelivery.created_at >= period_start,
        SalesDelivery.created_at <= f"{period_end} 23:59:59"
    ).all()
    total_sales = sum(d.total_amount or 0 for d in sales)

    # 汇总退货
    returns = db.query(SalesReturn).filter(
        SalesReturn.customer_id == customer_id,
        SalesReturn.status >= 2,
        SalesReturn.created_at >= period_start,
        SalesReturn.created_at <= f"{period_end} 23:59:59"
    ).all()
    total_returns = sum(r.total_amount or 0 for r in returns)

    # 汇总收款
    receipts = db.query(Receipt).filter(
        Receipt.customer_id == customer_id,
        Receipt.created_at >= period_start,
        Receipt.created_at <= f"{period_end} 23:59:59"
    ).all()
    total_receipts = sum(r.amount or 0 for r in receipts)

    balance = total_sales - total_returns - total_receipts

    recon = CustomerReconciliation(
        code=_gen_code(db), customer_id=customer_id,
        period_start=period_start, period_end=period_end,
        total_sales=total_sales, total_returns=total_returns,
        total_receipts=total_receipts, balance=balance,
        status="pending", created_by=user.id
    )
    db.add(recon)
    db.commit()
    return ResponseModel(message="对账单生成成功", data={"id": recon.id, "code": recon.code, "balance": balance})


@router.post("/reconciliations/{recon_id}/confirm", response_model=ResponseModel)
def confirm_reconciliation(recon_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    recon = db.query(CustomerReconciliation).get(recon_id)
    if not recon:
        raise HTTPException(404, "对账单不存在")
    if recon.status != "pending":
        raise HTTPException(400, "非待确认状态")
    recon.status = "confirmed"
    recon.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="对账确认成功")
