"""采购退货出库单 — Phase A+

状态流转：pending → warehouse_confirmed → finance_confirmed → settled
权限校验：仓管确认(warehouse角色) + 财务确认(finance角色)
锁定验证：已确认状态不允许修改/删除
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.purchase_return_dlv import PurchaseReturnDelivery, PurchaseReturnDeliveryItem
from models.purchase import PurchaseReturn
from models.supplier import Supplier
from models.product import Product
from models.warehouse import Warehouse
from models.employee import Employee
from models.inventory import Inventory
from schemas.purchase_return_dlv import (
    PurchaseReturnDlvCreate, PurchaseReturnDlvOut, PurchaseReturnDlvItemOut
)
from schemas.common import ResponseModel, PaginatedResponse, ReverseRequest
from services.inventory_service import InventoryService
from utils.role_check import require_role, require_owner_or_admin
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level
from deps import get_current_user

router = APIRouter(prefix="/api", tags=["采购退货出库单"])


def _enrich_names(db, result):
    if result.get("wh_confirmed_by"):
        emp = db.query(Employee).get(result["wh_confirmed_by"])
        if emp:
            result["auditor_name"] = emp.name
    if result.get("created_by"):
        emp = db.query(Employee).get(result["created_by"])
        if emp:
            result["created_by_name"] = emp.name

def _gen_return_dlv_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(PurchaseReturnDelivery).filter(
        func.strftime("%Y%m%d", PurchaseReturnDelivery.created_at) == today
    ).count()
    return f"CT{today}-{count + 1:03d}"


STATUS_TEXT = {
    "pending": "待仓管确认",
    "warehouse_confirmed": "仓管已确认",
    "finance_confirmed": "财务已确认",
    "settled": "已结算"
}


# ========== 创建采购退货出库单 ==========
@router.post("/purchase-return-deliveries", response_model=ResponseModel)
def create_purchase_return_dlv(
    req: PurchaseReturnDlvCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    # 校验供应商（可选）
    if req.supplier_id:
        supplier = db.query(Supplier).get(req.supplier_id)
        if not supplier:
            raise HTTPException(400, "供应商不存在")

    # 校验关联退货订单（可选）
    if req.purchase_return_id:
        ret = db.query(PurchaseReturn).get(req.purchase_return_id)
        if not ret:
            raise HTTPException(400, "关联退货订单不存在")

    return_dlv_no = _gen_return_dlv_no(db)

    total = req.total_amount
    if not total and req.items:
        total = sum(item.amount or (item.quantity * item.unit_price) for item in req.items)

    dlv = PurchaseReturnDelivery(
        return_dlv_no=return_dlv_no,
        purchase_return_id=req.purchase_return_id,
        supplier_id=req.supplier_id,
        warehouse_id=req.warehouse_id,
        total_amount=total,
        status="pending",
        created_by=user.id,
        remark=req.remark
    )
    db.add(dlv)
    db.flush()

    for item in req.items:
        amount = item.amount or (item.quantity * item.unit_price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        di = PurchaseReturnDeliveryItem(
            return_dlv_id=dlv.id,
            product_id=item.product_id,
            quantity=base_qty,
            unit_id=item.unit_id,
            unit_quantity=item.unit_quantity or item.quantity,
            unit_conv_rate=conv_rate,
            unit_price=item.unit_price,
            amount=amount
        )
        db.add(di)

    db.commit()
    db.refresh(dlv)
    return ResponseModel(data=PurchaseReturnDlvOut.model_validate(dlv))


# ========== 修改采购退货出库单（仅pending状态） ==========
@router.put("/purchase-return-deliveries/{dlv_id}", response_model=ResponseModel)
def update_purchase_return_dlv(
    dlv_id: int,
    req: PurchaseReturnDlvCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")
    if dlv.status != "pending":
        raise HTTPException(400, f"当前状态「{STATUS_TEXT.get(dlv.status, dlv.status)}」不允许修改")

    if req.supplier_id:
        supplier = db.query(Supplier).get(req.supplier_id)
        if not supplier:
            raise HTTPException(400, "供应商不存在")

    if req.purchase_return_id:
        ret = db.query(PurchaseReturn).get(req.purchase_return_id)
        if not ret:
            raise HTTPException(400, "关联退货订单不存在")

    # 删除旧明细
    db.query(PurchaseReturnDeliveryItem).filter(
        PurchaseReturnDeliveryItem.return_dlv_id == dlv_id
    ).delete()

    # 计算新总金额
    total = req.total_amount
    if not total and req.items:
        total = sum(item.amount or (item.quantity * item.unit_price) for item in req.items)

    # 更新主单
    dlv.purchase_return_id = req.purchase_return_id
    dlv.supplier_id = req.supplier_id
    dlv.warehouse_id = req.warehouse_id
    dlv.total_amount = total
    dlv.remark = req.remark

    # 创建新明细
    for item in req.items:
        amount = item.amount or (item.quantity * item.unit_price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        di = PurchaseReturnDeliveryItem(
            return_dlv_id=dlv.id,
            product_id=item.product_id,
            quantity=base_qty,
            unit_id=item.unit_id,
            unit_quantity=item.unit_quantity or item.quantity,
            unit_conv_rate=conv_rate,
            unit_price=item.unit_price,
            amount=amount
        )
        db.add(di)

    db.commit()
    db.refresh(dlv)
    return ResponseModel(data=PurchaseReturnDlvOut.model_validate(dlv))


# ========== 列表 ==========
@router.get("/purchase-return-deliveries", response_model=PaginatedResponse)
def list_purchase_return_dlvs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    supplier_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(PurchaseReturnDelivery)

    if status:
        q = q.filter(PurchaseReturnDelivery.status == status)
    if supplier_id:
        q = q.filter(PurchaseReturnDelivery.supplier_id == supplier_id)
    if start_date:
        q = q.filter(PurchaseReturnDelivery.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseReturnDelivery.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(PurchaseReturnDelivery.return_dlv_no.contains(keyword))

    total = q.count()
    items = q.order_by(PurchaseReturnDelivery.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for dlv in items:
        data = PurchaseReturnDlvOut.model_validate(dlv).model_dump()
        supplier = db.query(Supplier).get(dlv.supplier_id)
        data["supplier_name"] = supplier.name if supplier else ""
        if dlv.warehouse_id:
            wh = db.query(Warehouse).get(dlv.warehouse_id)
            data["warehouse_name"] = wh.name if wh else ""
        data["status_text"] = STATUS_TEXT.get(dlv.status, dlv.status)
        _enrich_names(db, data)
        result.append(data)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


# ========== 详情 ==========
@router.get("/purchase-return-deliveries/{dlv_id}", response_model=ResponseModel)
def get_purchase_return_dlv(dlv_id: int, db: Session = Depends(get_db)):
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")

    items = db.query(PurchaseReturnDeliveryItem).filter(
        PurchaseReturnDeliveryItem.return_dlv_id == dlv_id
    ).all()

    supplier = db.query(Supplier).get(dlv.supplier_id)
    result = PurchaseReturnDlvOut.model_validate(dlv).model_dump()
    result["supplier_name"] = supplier.name if supplier else ""
    result["status_text"] = STATUS_TEXT.get(dlv.status, dlv.status)
    _enrich_names(db, result)
    result["items"] = []
    for item in items:
        product = db.query(Product).get(item.product_id)
        item_data = PurchaseReturnDlvItemOut.model_validate(item).model_dump()
        item_data["product_name"] = product.name if product else ""
        result["items"].append(item_data)

    _enrich_names(db, result)
    return ResponseModel(data=result)


# ========== 仓管确认（扣库存） ==========
@router.post("/purchase-return-deliveries/{dlv_id}/warehouse-confirm", response_model=ResponseModel)
def warehouse_confirm_return_dlv(
    dlv_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")

    # 锁定验证：只有 pending 状态可以仓管确认
    if dlv.status != "pending":
        raise HTTPException(400, f"当前状态「{STATUS_TEXT.get(dlv.status, dlv.status)}」不允许仓管确认")

    # 权限校验：仓管或管理员
    require_role(user, db, "warehouse", "admin", message="只有仓管或管理员可以确认退货出库")

    items = db.query(PurchaseReturnDeliveryItem).filter(
        PurchaseReturnDeliveryItem.return_dlv_id == dlv_id
    ).all()

    # 扣减库存
    for item in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == dlv.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if not inv or inv.quantity < item.quantity:
            raise HTTPException(400, f"商品{item.product_id}库存不足，当前{inv.quantity if inv else 0}，需出库{item.quantity}")
        inv.quantity -= item.quantity

    dlv.status = "warehouse_confirmed"
    dlv.wh_confirmed_by = user.id
    dlv.wh_confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="仓管确认成功，已扣减库存")


# ========== 财务确认（冲减应付） ==========
@router.post("/purchase-return-deliveries/{dlv_id}/finance-confirm", response_model=ResponseModel)
def finance_confirm_return_dlv(
    dlv_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")

    # 锁定验证：只有 warehouse_confirmed 状态可以财务确认
    if dlv.status != "warehouse_confirmed":
        raise HTTPException(400, f"当前状态「{STATUS_TEXT.get(dlv.status, dlv.status)}」不允许财务确认")

    # 权限校验：财务或管理员
    require_role(user, db, "finance", "admin", message="只有财务或管理员可以确认退货冲账")

    # 冲减供应商应付
    supplier = db.query(Supplier).get(dlv.supplier_id)
    if supplier:
        supplier.payable_balance = max(0, (supplier.payable_balance or 0) - dlv.total_amount)

    dlv.status = "finance_confirmed"
    dlv.fin_confirmed_by = user.id
    dlv.fin_confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="财务确认成功，已冲减供应商应付")


# ========== 删除（仅pending状态） ==========
@router.delete("/purchase-return-deliveries/{dlv_id}", response_model=ResponseModel)
def delete_purchase_return_dlv(
    dlv_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")

    # 锁定验证：只有 pending 状态可以删除
    if dlv.status != "pending":
        raise HTTPException(400, f"当前状态「{STATUS_TEXT.get(dlv.status, dlv.status)}」不允许删除，已确认的单据不能删除")

    # 权限校验：管理员或创建人
    require_owner_or_admin(user, dlv.created_by, db, "只有管理员或创建人可以删除")

    db.query(PurchaseReturnDeliveryItem).filter(
        PurchaseReturnDeliveryItem.return_dlv_id == dlv_id
    ).delete()
    db.delete(dlv)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 冲红 ==========
@router.post("/purchase-return-deliveries/{dlv_id}/reverse", response_model=ResponseModel)
def reverse_purchase_return_dlv(
    dlv_id: int,
    req: ReverseRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    dlv = db.query(PurchaseReturnDelivery).get(dlv_id)
    if not dlv:
        raise HTTPException(404, "退货出库单不存在")

    # 只有已确认状态可以冲红
    if dlv.status == "pending":
        raise HTTPException(400, "草稿状态不能冲红")
    if dlv.status == "reversed":
        raise HTTPException(400, "已冲红单据不能重复冲红")

    # 只有管理员可以冲红
    require_role(user, db, "admin", message="只有管理员可以冲红")

    items = db.query(PurchaseReturnDeliveryItem).filter(
        PurchaseReturnDeliveryItem.return_dlv_id == dlv_id
    ).all()

    # 如果仓管已确认（扣了库存），需要回滚库存
    if dlv.status in ("warehouse_confirmed", "finance_confirmed", "settled"):
        for item in items:
            InventoryService.restore(db, item.product_id, dlv.warehouse_id, item.quantity)

    # 如果财务已确认（冲减了应付），需要回滚应付
    if dlv.status in ("finance_confirmed", "settled"):
        supplier = db.query(Supplier).get(dlv.supplier_id)
        if supplier and dlv.total_amount:
            supplier.payable_balance = (supplier.payable_balance or 0) + dlv.total_amount

    dlv.status = "reversed"
    dlv.reverse_reason = req.reason
    dlv.reversed_by = user.id
    dlv.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功，库存已回滚")
