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
from models.warehouse import Warehouse
from models.inventory import Inventory
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse, ReverseRequest
from services.inventory_service import InventoryService
from schemas.sales import SalesReturnCreate, SalesReturnOut
from utils.status import ReturnDeliveryStatus
from utils.role_check import require_role, require_owner_or_admin
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level
from deps import get_current_user

router = APIRouter(prefix="/api", tags=["退货单"])

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
    q = db.query(SalesReturn).filter(SalesReturn.doc_type == "return_delivery")

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
        warehouse_name = ""
        if ret.warehouse_id:
            wh = db.query(Warehouse).get(ret.warehouse_id)
            warehouse_name = wh.name if wh else ""
        result.append({
            "id": ret.id,
            "code": ret.code,
            "customer_id": ret.customer_id,
            "customer_name": customer.name if customer else "",
            "warehouse_id": ret.warehouse_id,
            "warehouse_name": warehouse_name,
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


def _gen_code(db):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"TD{today}"
    last = db.query(SalesReturn).filter(SalesReturn.code.like(f"{prefix}%")).order_by(SalesReturn.id.desc()).first()
    if last:
        seq = int(last.code[-4:]) + 1
    else:
        seq = 1
    # 再次检查确保不重复
    while True:
        code = f"{prefix}{seq:04d}"
        existing = db.query(SalesReturn).filter(SalesReturn.code == code).first()
        if not existing:
            return code
        seq += 1


@router.post("/return-deliveries", response_model=ResponseModel)
def create_return_delivery(req: SalesReturnCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    if not req.items:
        raise HTTPException(400, "请添加退货明细")
    code = _gen_code(db)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    ret = SalesReturn(
        code=code, stockout_id=req.stockout_id, doc_type="return_delivery",
        customer_id=req.customer_id, warehouse_id=req.warehouse_id,
        total_amount=total, remark=req.remark, operator_id=user.id, status=0
    )
    db.add(ret)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = SalesReturnItem(
            return_id=ret.id, product_id=item.product_id,
            quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate,
            price=item.price, amount=amount
        )
        db.add(ri)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=SalesReturnOut.model_validate(ret))


# ========== 修改退货单（仅草稿状态） ==========
@router.put("/return-deliveries/{return_id}", response_model=ResponseModel)
def update_return_delivery(
    return_id: int,
    req: SalesReturnCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(404, "退货单不存在")
    if ret.doc_type != "return_delivery":
        raise HTTPException(400, "非退货出库单")
    if ret.status != 0:
        raise HTTPException(400, f"当前状态 {ret.status} 不允许修改")

    if not req.items:
        raise HTTPException(400, "请添加退货明细")

    # 删除旧明细
    db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).delete()

    # 计算新总金额
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)

    # 更新主单
    ret.stockout_id = req.stockout_id
    ret.customer_id = req.customer_id
    ret.warehouse_id = req.warehouse_id
    ret.total_amount = total
    ret.remark = req.remark

    # 创建新明细
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = SalesReturnItem(
            return_id=ret.id, product_id=item.product_id,
            quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate,
            price=item.price, amount=amount
        )
        db.add(ri)

    db.commit()
    db.refresh(ret)
    return ResponseModel(data=SalesReturnOut.model_validate(ret))


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

    auditor_name = ""
    if ret.auditor_id:
        auditor = db.query(Employee).get(ret.auditor_id)
        if auditor:
            auditor_name = auditor.name
    operator_name = ""
    if ret.operator_id:
        operator = db.query(Employee).get(ret.operator_id)
        if operator:
            operator_name = operator.name

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
        "operator_name": operator_name,
        "auditor_id": ret.auditor_id,
        "auditor_name": auditor_name,
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
    ret.auditor_id = user.id
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


# ========== 冲红 ==========
@router.post("/return-deliveries/{return_id}/reverse", response_model=ResponseModel)
def reverse_return_delivery(
    return_id: int,
    req: ReverseRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """冲红退货单 — 回滚库存和应收"""
    user = get_current_user(authorization, db)
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(404, "退货单不存在")
    if ret.status == 0:
        raise HTTPException(400, "草稿状态不能冲红")
    if ret.status == 3:
        raise HTTPException(400, "已冲红单据不能重复冲红")

    # 只有管理员可以冲红
    require_role(user, db, "admin", message="只有管理员可以冲红")

    items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()

    # 如果仓管已确认（增加了库存），需要扣回库存
    if ret.status >= 2:
        for item in items:
            InventoryService.deduct(db, item.product_id, ret.warehouse_id, item.quantity)

    # 如果财务已确认（冲减了应收），需要加回应收
    if ret.status >= 3:
        customer = db.query(Customer).get(ret.customer_id)
        if customer and ret.total_amount:
            customer.receivable_balance = (customer.receivable_balance or 0) + ret.total_amount

    ret.status = 3  # 已冲红（复用status=3）
    ret.reverse_reason = req.reason
    ret.reversed_by = user.id
    ret.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功，库存已回滚")
