"""退货单增强 — Phase A Day 7-8

扩展现有 sales_returns，增加：
- 仓管确认（warehouse_confirmed）
- 财务确认（finance_confirmed）
- 状态流转：pending → warehouse_confirmed → finance_confirmed → settled
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.sales import SalesReturn, SalesReturnItem
from models.customer import Customer
from models.product import Product
from models.inventory import Inventory
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.status import ReturnDeliveryStatus
from utils.role_check import require_role, require_owner_or_admin

router = APIRouter(prefix="/api", tags=["退货单"])


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


@router.get("/return-deliveries", response_model=PaginatedResponse)
def list_return_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None),
    customer_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(SalesReturn)

    if status is not None:
        q = q.filter(SalesReturn.status == status)
    if customer_id:
        q = q.filter(SalesReturn.customer_id == customer_id)
    if start_date:
        q = q.filter(SalesReturn.created_at >= start_date)
    if end_date:
        q = q.filter(SalesReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(SalesReturn.code.contains(keyword))

    total = q.count()
    items = q.order_by(SalesReturn.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for ret in items:
        customer = db.query(Customer).get(ret.customer_id)
        result.append({
            "id": ret.id,
            "code": ret.code,
            "customer_id": ret.customer_id,
            "customer_name": customer.name if customer else "",
            "warehouse_id": ret.warehouse_id,
            "total_amount": ret.total_amount,
            "status": ret.status,
            "status_text": _get_status_text(ret.status),
            "operator_id": ret.operator_id,
            "remark": ret.remark,
            "created_at": str(ret.created_at),
            "confirmed_at": str(ret.confirmed_at) if ret.confirmed_at else None
        })

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


def _get_status_text(status: int) -> str:
    texts = {0: "草稿", 1: "已确认", 2: "仓管已确认", 3: "财务已确认"}
    return texts.get(status, "未知")


@router.get("/return-deliveries/{return_id}", response_model=ResponseModel)
def get_return_delivery(return_id: int, db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(404, "退货单不存在")

    items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()
    customer = db.query(Customer).get(ret.customer_id)

    detail = []
    for item in items:
        product = db.query(Product).get(item.product_id)
        detail.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "",
            "quantity": item.quantity,
            "price": item.price,
            "amount": item.amount
        })

    return ResponseModel(data={
        "id": ret.id,
        "code": ret.code,
        "customer_id": ret.customer_id,
        "customer_name": customer.name if customer else "",
        "warehouse_id": ret.warehouse_id,
        "total_amount": ret.total_amount,
        "status": ret.status,
        "status_text": _get_status_text(ret.status),
        "operator_id": ret.operator_id,
        "remark": ret.remark,
        "items": detail,
        "created_at": str(ret.created_at),
        "confirmed_at": str(ret.confirmed_at) if ret.confirmed_at else None
    })


@router.post("/return-deliveries/{return_id}/warehouse-confirm", response_model=ResponseModel)
def warehouse_confirm_return(
    return_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """仓管确认退货 — 入库+增加库存"""
    user = get_current_user(authorization, db)
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(404, "退货单不存在")
    if ret.status != 0:
        raise HTTPException(400, f"当前状态 {ret.status} 不允许仓管确认")

    # 仓管或admin可以确认
    require_role(user, db, "warehouse", "admin", message="只有仓管或管理员可以确认退货入库")

    items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()

    # 增加库存
    for item in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == ret.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if inv:
            # 移动加权平均成本
            total_cost = inv.quantity * (inv.cost_price or 0) + item.quantity * item.price
            inv.quantity += item.quantity
            inv.cost_price = total_cost / inv.quantity if inv.quantity > 0 else 0
        else:
            inv = Inventory(
                warehouse_id=ret.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
                cost_price=item.price
            )
            db.add(inv)

    ret.status = 2  # 仓管已确认
    db.commit()
    return ResponseModel(message="仓管确认成功，退货已入库")


@router.post("/return-deliveries/{return_id}/finance-confirm", response_model=ResponseModel)
def finance_confirm_return(
    return_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """财务确认退货 — 冲减客户应收"""
    user = get_current_user(authorization, db)
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(404, "退货单不存在")
    if ret.status != 2:
        raise HTTPException(400, "只有仓管已确认的退货单才能财务确认")

    # 财务或admin可以确认
    require_role(user, db, "finance", "admin", message="只有财务或管理员可以确认退货冲账")

    # 冲减客户应收
    customer = db.query(Customer).get(ret.customer_id)
    if customer:
        customer.receivable_balance = max(0, (customer.receivable_balance or 0) - ret.total_amount)

    ret.status = 3  # 财务已确认
    db.commit()
    return ResponseModel(message="财务确认成功，已冲减客户应收")
