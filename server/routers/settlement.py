"""交账路由 — Phase B

交账流程：
1. 业务员提交交账 — 选择待交账的销售单/退货单/费用
2. 系统自动汇总金额
3. 财务审核：通过→销售单settled+退货单settled；驳回→恢复pending
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.settlement import Settlement, SettlementDelivery, SettlementReturn
from models.sales_delivery import SalesDelivery
from models.sales import SalesReturn
from models.expense import Expense
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.status import SettlementStatus
from utils.role_check import require_role

router = APIRouter(prefix="/api", tags=["交账"])


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


def _gen_settlement_no(db):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"JZ{today}"
    last = db.query(Settlement).filter(Settlement.settlement_no.like(f"{prefix}%")).order_by(Settlement.id.desc()).first()
    seq = int(last.settlement_no[-4:]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


@router.get("/settlements", response_model=PaginatedResponse)
def list_settlements(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None), employee_id: int = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Settlement)
    if status:
        q = q.filter(Settlement.status == status)
    if employee_id:
        q = q.filter(Settlement.employee_id == employee_id)
    total = q.count()
    items = q.order_by(Settlement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for s in items:
        emp = db.query(Employee).get(s.employee_id)
        result.append({
            "id": s.id, "settlement_no": s.settlement_no,
            "employee_id": s.employee_id,
            "employee_name": emp.name if emp else "",
            "settlement_date": str(s.settlement_date) if s.settlement_date else None,
            "total_sales": s.total_sales, "total_returns": s.total_returns,
            "total_expenses": s.total_expenses,
            "total_cash": s.total_cash, "total_wechat": s.total_wechat,
            "total_alipay": s.total_alipay, "total_credit": s.total_credit,
            "actual_cash": s.actual_cash, "status": s.status,
            "created_at": str(s.created_at)
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/settlements", response_model=ResponseModel)
def create_settlement(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """创建交账单 — 自动汇总销售/退货/费用金额"""
    user = get_current_user(authorization, db)
    delivery_ids = data.get("delivery_ids", [])
    return_ids = data.get("return_ids", [])
    expense_ids = data.get("expense_ids", [])
    employee_id = data.get("employee_id", user.id)

    if not delivery_ids:
        raise HTTPException(400, "请选择至少一个销售单")

    # 检查销售单状态
    deliveries = []
    for did in delivery_ids:
        d = db.query(SalesDelivery).get(did)
        if not d:
            raise HTTPException(404, f"销售单 {did} 不存在")
        if d.status != "pending":
            raise HTTPException(400, f"销售单 {d.delivery_no} 状态不是pending")
        deliveries.append(d)

    # 汇总销售金额
    total_cash = sum(d.cash_amount or 0 for d in deliveries)
    total_wechat = sum(d.wechat_amount or 0 for d in deliveries)
    total_alipay = sum(d.alipay_amount or 0 for d in deliveries)
    total_credit = sum(d.credit_amount or 0 for d in deliveries)
    total_sales = sum(d.total_amount or 0 for d in deliveries)

    # 汇总退货金额
    total_returns = 0
    returns = []
    for rid in return_ids:
        r = db.query(SalesReturn).get(rid)
        if r:
            total_returns += r.total_amount or 0
            returns.append(r)

    # 汇总费用
    total_expenses = 0
    for eid in expense_ids:
        e = db.query(Expense).get(eid)
        if e:
            total_expenses += e.amount or 0

    actual_cash = total_cash - total_expenses

    settlement = Settlement(
        settlement_no=_gen_settlement_no(db),
        employee_id=employee_id,
        settlement_date=datetime.now(),
        total_sales=total_sales, total_returns=total_returns,
        total_expenses=total_expenses,
        total_cash=total_cash, total_wechat=total_wechat,
        total_alipay=total_alipay, total_credit=total_credit,
        actual_cash=actual_cash, status="pending",
        remark=data.get("remark"), created_by=user.id
    )
    db.add(settlement)
    db.flush()

    for d in deliveries:
        db.add(SettlementDelivery(settlement_id=settlement.id, delivery_id=d.id))
        d.status = "settling"
    for r in returns:
        db.add(SettlementReturn(settlement_id=settlement.id, return_id=r.id))
    db.commit()
    return ResponseModel(message="交账单创建成功", data={"id": settlement.id, "settlement_no": settlement.settlement_no})


@router.get("/settlements/{settlement_id}", response_model=ResponseModel)
def get_settlement(settlement_id: int, db: Session = Depends(get_db)):
    s = db.query(Settlement).get(settlement_id)
    if not s:
        raise HTTPException(404, "交账单不存在")
    emp = db.query(Employee).get(s.employee_id)
    # 关联的销售单
    sds = db.query(SettlementDelivery).filter(SettlementDelivery.settlement_id == settlement_id).all()
    deliveries = []
    for sd in sds:
        d = db.query(SalesDelivery).get(sd.delivery_id)
        if d:
            deliveries.append({
                "id": d.id, "delivery_no": d.delivery_no,
                "total_amount": d.total_amount, "status": d.status
            })
    # 关联的退货单
    srs = db.query(SettlementReturn).filter(SettlementReturn.settlement_id == settlement_id).all()
    returns = []
    for sr in srs:
        r = db.query(SalesReturn).get(sr.return_id)
        if r:
            returns.append({
                "id": r.id, "code": r.code,
                "total_amount": r.total_amount, "status": r.status
            })
    return ResponseModel(data={
        "id": s.id, "settlement_no": s.settlement_no,
        "employee_id": s.employee_id,
        "employee_name": emp.name if emp else "",
        "settlement_date": str(s.settlement_date) if s.settlement_date else None,
        "total_sales": s.total_sales, "total_returns": s.total_returns,
        "total_expenses": s.total_expenses,
        "total_cash": s.total_cash, "total_wechat": s.total_wechat,
        "total_alipay": s.total_alipay, "total_credit": s.total_credit,
        "actual_cash": s.actual_cash, "status": s.status,
        "auditor_id": s.auditor_id,
        "audited_at": str(s.audited_at) if s.audited_at else None,
        "audit_comment": s.audit_comment,
        "remark": s.remark, "created_at": str(s.created_at),
        "deliveries": deliveries, "returns": returns
    })


@router.post("/settlements/{settlement_id}/audit", response_model=ResponseModel)
def audit_settlement(settlement_id: int, data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """财务审核交账单 — 通过/驳回"""
    user = get_current_user(authorization, db)
    require_role(user, db, "finance", "admin", message="只有财务或管理员可以审核交账")
    s = db.query(Settlement).get(settlement_id)
    if not s:
        raise HTTPException(404, "交账单不存在")
    if s.status != "pending":
        raise HTTPException(400, f"当前状态 {s.status} 不允许审核")
    action = data.get("action", "approve")
    if action == "approve":
        # 通过 — 销售单→settled, 退货单→settled
        sds = db.query(SettlementDelivery).filter(SettlementDelivery.settlement_id == settlement_id).all()
        for sd in sds:
            d = db.query(SalesDelivery).get(sd.delivery_id)
            if d:
                d.status = "settled"
                d.settled_at = datetime.now()
                d.settlement_id = settlement_id
        srs = db.query(SettlementReturn).filter(SettlementReturn.settlement_id == settlement_id).all()
        for sr in srs:
            r = db.query(SalesReturn).get(sr.return_id)
            if r:
                r.status = 3  # 财务已确认
        s.status = "audited"
        s.auditor_id = user.id
        s.audited_at = datetime.now()
        s.audit_comment = data.get("comment", "")
        db.commit()
        return ResponseModel(message="交账审核通过")
    else:
        # 驳回 — 销售单恢复pending
        sds = db.query(SettlementDelivery).filter(SettlementDelivery.settlement_id == settlement_id).all()
        for sd in sds:
            d = db.query(SalesDelivery).get(sd.delivery_id)
            if d:
                d.status = "pending"
        s.status = "rejected"
        s.auditor_id = user.id
        s.audited_at = datetime.now()
        s.audit_comment = data.get("comment", "")
        db.commit()
        return ResponseModel(message="交账已驳回")


@router.get("/settlements/pending-deliveries", response_model=ResponseModel)
def list_pending_deliveries(employee_id: int = Query(None), db: Session = Depends(get_db)):
    """获取待交账的销售单"""
    q = db.query(SalesDelivery).filter(SalesDelivery.status == "pending")
    if employee_id:
        q = q.filter(SalesDelivery.created_by == employee_id)
    items = q.order_by(SalesDelivery.created_at.desc()).all()
    result = [{
        "id": d.id, "delivery_no": d.delivery_no,
        "customer_id": d.customer_id, "total_amount": d.total_amount,
        "cash_amount": d.cash_amount, "wechat_amount": d.wechat_amount,
        "alipay_amount": d.alipay_amount, "credit_amount": d.credit_amount,
        "created_at": str(d.created_at)
    } for d in items]
    return ResponseModel(data=result)
