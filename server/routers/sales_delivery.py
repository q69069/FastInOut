"""销售单（SalesDelivery）— Phase A Day 1-2 核心模块

状态流转：pending → voided / settling → settled / locked → reversed
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from database import get_db
from models.sales_delivery import SalesDelivery, SalesDeliveryItem
from models.sales import SalesOrder, SalesOrderItem
from models.customer import Customer
from models.product import Product
from models.employee import Employee
from schemas.sales_delivery import (
    SalesDeliveryCreate, SalesDeliveryOut, SalesDeliveryItemOut, SalesDeliveryVoid
)
from schemas.common import ResponseModel, PaginatedResponse
from services.inventory_service import InventoryService
from utils.status import SalesDeliveryStatus

router = APIRouter(prefix="/api", tags=["销售单"])


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


def _gen_delivery_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(SalesDelivery).filter(
        func.strftime("%Y%m%d", SalesDelivery.created_at) == today
    ).count()
    return f"XS{today}-{count + 1:03d}"


# ========== 创建销售单（开单） ==========
@router.post("/sales-deliveries", response_model=ResponseModel)
def create_sales_delivery(
    req: SalesDeliveryCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    # 校验：warehouse_id 和 vehicle_id 必须有一个且仅有一个
    if not req.warehouse_id and not req.vehicle_id:
        raise HTTPException(400, "warehouse_id 和 vehicle_id 必须提供一个")
    if req.warehouse_id and req.vehicle_id:
        raise HTTPException(400, "warehouse_id 和 vehicle_id 不能同时提供")

    # 校验客户存在
    customer = db.query(Customer).get(req.customer_id)
    if not customer:
        raise HTTPException(400, "客户不存在")

    delivery_no = _gen_delivery_no(db)

    # 计算总金额
    total = req.total_amount
    if not total and req.items:
        total = sum(item.amount or (item.quantity * item.unit_price) for item in req.items)

    delivery = SalesDelivery(
        delivery_no=delivery_no,
        customer_id=req.customer_id,
        warehouse_id=req.warehouse_id,
        vehicle_id=req.vehicle_id,
        total_amount=total,
        cash_amount=req.cash_amount,
        wechat_amount=req.wechat_amount,
        alipay_amount=req.alipay_amount,
        credit_amount=req.credit_amount,
        status=SalesDeliveryStatus.PENDING,
        source_type=req.source_type,
        created_by=user.id,
        remark=req.remark
    )
    db.add(delivery)
    db.flush()

    # 创建明细 + 扣库存
    for item in req.items:
        amount = item.amount or (item.quantity * item.unit_price)
        di = SalesDeliveryItem(
            delivery_id=delivery.id,
            product_id=item.product_id,
            batch_id=item.batch_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=amount,
            source_order_item_id=item.source_order_item_id
        )
        db.add(di)

        # 扣库存（仓库或车辆）
        stock_id = req.warehouse_id or req.vehicle_id
        InventoryService.deduct(db, item.product_id, stock_id, item.quantity)

    # 更新客户应收
    if total > 0:
        customer.receivable_balance = (customer.receivable_balance or 0) + total - (req.cash_amount or 0) - (req.wechat_amount or 0) - (req.alipay_amount or 0)

    db.commit()
    db.refresh(delivery)
    return ResponseModel(data=SalesDeliveryOut.model_validate(delivery))


# ========== 销售单列表 ==========
@router.get("/sales-deliveries", response_model=PaginatedResponse)
def list_sales_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    customer_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(SalesDelivery)

    if status:
        q = q.filter(SalesDelivery.status == status)
    if customer_id:
        q = q.filter(SalesDelivery.customer_id == customer_id)
    if start_date:
        q = q.filter(SalesDelivery.created_at >= start_date)
    if end_date:
        q = q.filter(SalesDelivery.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(SalesDelivery.delivery_no.contains(keyword))

    total = q.count()
    items = q.order_by(SalesDelivery.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[SalesDeliveryOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


# ========== 销售单详情 ==========
@router.get("/sales-deliveries/{delivery_id}", response_model=ResponseModel)
def get_sales_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(SalesDelivery).get(delivery_id)
    if not delivery:
        raise HTTPException(404, "销售单不存在")

    items = db.query(SalesDeliveryItem).filter(
        SalesDeliveryItem.delivery_id == delivery_id
    ).all()

    result = SalesDeliveryOut.model_validate(delivery).model_dump()
    result["items"] = [SalesDeliveryItemOut.model_validate(i) for i in items]
    return ResponseModel(data=result)


# ========== 作废销售单（当日） ==========
@router.post("/sales-deliveries/{delivery_id}/void", response_model=ResponseModel)
def void_sales_delivery(
    delivery_id: int,
    req: SalesDeliveryVoid,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    delivery = db.query(SalesDelivery).get(delivery_id)
    if not delivery:
        raise HTTPException(404, "销售单不存在")

    # 只有 pending 状态可以作废
    if delivery.status != SalesDeliveryStatus.PENDING:
        raise HTTPException(400, f"当前状态 {delivery.status} 不允许作废")

    # 校验当日（服务器时间）
    if delivery.created_at and delivery.created_at.date() != date.today():
        raise HTTPException(400, "只能作废当日的销售单，跨日请使用红冲")

    # 校验操作人
    if user.role_id != 5 and delivery.created_by != user.id:
        raise HTTPException(403, "只能作废自己开的单")

    # 回滚库存
    items = db.query(SalesDeliveryItem).filter(
        SalesDeliveryItem.delivery_id == delivery_id
    ).all()
    stock_id = delivery.warehouse_id or delivery.vehicle_id
    for item in items:
        InventoryService.restore(db, item.product_id, stock_id, item.quantity)

    # 回滚客户应收
    customer = db.query(Customer).get(delivery.customer_id)
    if customer and delivery.total_amount:
        credit_amount = delivery.total_amount - (delivery.cash_amount or 0) - (delivery.wechat_amount or 0) - (delivery.alipay_amount or 0)
        customer.receivable_balance = max(0, (customer.receivable_balance or 0) - credit_amount)

    delivery.status = SalesDeliveryStatus.VOIDED
    delivery.void_reason = req.void_reason
    db.commit()
    return ResponseModel(message="作废成功，库存已回滚")


# ========== 红冲销售单 ==========
@router.post("/sales-deliveries/{delivery_id}/reverse", response_model=ResponseModel)
def reverse_sales_delivery(
    delivery_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    delivery = db.query(SalesDelivery).get(delivery_id)
    if not delivery:
        raise HTTPException(404, "销售单不存在")

    # 只有 locked/settled 可以红冲
    if delivery.status not in (SalesDeliveryStatus.LOCKED, SalesDeliveryStatus.SETTLED):
        raise HTTPException(400, f"当前状态 {delivery.status} 不允许红冲")

    # 只有主管/admin可以红冲
    if user.role_id != 5:
        raise HTTPException(403, "只有管理员可以红冲")

    # 回滚库存
    items = db.query(SalesDeliveryItem).filter(
        SalesDeliveryItem.delivery_id == delivery_id
    ).all()
    stock_id = delivery.warehouse_id or delivery.vehicle_id
    for item in items:
        InventoryService.restore(db, item.product_id, stock_id, item.quantity)

    # 回滚客户应收
    customer = db.query(Customer).get(delivery.customer_id)
    if customer and delivery.total_amount:
        credit_amount = delivery.total_amount - (delivery.cash_amount or 0) - (delivery.wechat_amount or 0) - (delivery.alipay_amount or 0)
        customer.receivable_balance = max(0, (customer.receivable_balance or 0) - credit_amount)

    delivery.status = SalesDeliveryStatus.REVERSED
    db.commit()
    return ResponseModel(message="红冲成功，库存已回滚")
