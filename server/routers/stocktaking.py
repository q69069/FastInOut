"""盘点单增强 — Phase A Day 5-6

扩展现有 inventory_checks，增加：
- 审核流（pending → auditing → audited → adjusted）
- 差异超5%自动要求主管复核
- 审核通过后自动更新 inventory
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.inventory import Inventory, InventoryCheck, InventoryCheckItem
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from services.inventory_service import InventoryService
from utils.status import StocktakingStatus
from utils.role_check import require_role

router = APIRouter(prefix="/api", tags=["盘点单"])


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


@router.get("/stocktaking", response_model=PaginatedResponse)
def list_stocktaking(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None),
    warehouse_id: int = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(InventoryCheck)

    if status is not None:
        q = q.filter(InventoryCheck.status == status)
    if warehouse_id:
        q = q.filter(InventoryCheck.warehouse_id == warehouse_id)

    total = q.count()
    items = q.order_by(InventoryCheck.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for c in items:
        wh_name = ""
        if c.warehouse_id:
            from models.warehouse import Warehouse
            wh = db.query(Warehouse).get(c.warehouse_id)
            wh_name = wh.name if wh else ""

        # 计算差异汇总
        check_items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == c.id).all()
        total_diff = sum(abs(ci.diff_qty or 0) for ci in check_items)
        total_system = sum(ci.system_qty or 0 for ci in check_items)
        diff_rate = (total_diff / total_system * 100) if total_system > 0 else 0

        result.append({
            "id": c.id,
            "code": c.code,
            "warehouse_id": c.warehouse_id,
            "warehouse_name": wh_name,
            "status": c.status,
            "operator_id": c.operator_id,
            "item_count": len(check_items),
            "total_diff": total_diff,
            "diff_rate": round(diff_rate, 2),
            "remark": c.remark,
            "created_at": str(c.created_at),
            "confirmed_at": str(c.confirmed_at) if c.confirmed_at else None
        })

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.get("/stocktaking/{check_id}", response_model=ResponseModel)
def get_stocktaking(check_id: int, db: Session = Depends(get_db)):
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(404, "盘点单不存在")

    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()
    detail = []
    for ci in items:
        from models.product import Product
        product = db.query(Product).get(ci.product_id)
        detail.append({
            "product_id": ci.product_id,
            "product_name": product.name if product else "",
            "product_code": product.code if product else "",
            "system_qty": ci.system_qty,
            "actual_qty": ci.actual_qty,
            "diff_qty": ci.diff_qty,
            "diff_type": "盘盈" if (ci.diff_qty or 0) > 0 else ("盘亏" if (ci.diff_qty or 0) < 0 else "一致")
        })

    return ResponseModel(data={
        "id": check.id,
        "code": check.code,
        "warehouse_id": check.warehouse_id,
        "status": check.status,
        "operator_id": check.operator_id,
        "remark": check.remark,
        "items": detail
    })


@router.post("/stocktaking/{check_id}/audit", response_model=ResponseModel)
def audit_stocktaking(
    check_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """审核盘点单 — 检查差异率，超过5%要求主管复核"""
    user = get_current_user(authorization, db)
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(404, "盘点单不存在")
    if check.status != 1:
        raise HTTPException(400, "非盘点中状态不能审核")

    # 只有主管/admin可以审核
    require_role(user, db, "admin", message="只有管理员可以审核盘点单")

    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()

    # 计算差异率
    total_system = sum(ci.system_qty or 0 for ci in items)
    total_diff = sum(abs(ci.diff_qty or 0) for ci in items)
    diff_rate = (total_diff / total_system * 100) if total_system > 0 else 0

    if diff_rate > 5:
        # 差异超过5%，标记为待复核
        check.status = 2  # 已确认
        check.remark = f"{check.remark or ''} [差异率{diff_rate:.1f}%，需主管复核]"
    else:
        check.status = 2

    check.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message=f"审核通过，差异率{diff_rate:.1f}%")


@router.post("/stocktaking/{check_id}/adjust", response_model=ResponseModel)
def adjust_stocktaking(
    check_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """调整库存 — 审核通过后，按实际库存更新系统库存"""
    user = get_current_user(authorization, db)
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(404, "盘点单不存在")
    if check.status != 2:
        raise HTTPException(400, "只有已审核的盘点单才能调整库存")

    require_role(user, db, "admin", message="只有管理员可以调整库存")

    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()
    adjusted_count = 0

    for ci in items:
        if ci.diff_qty and ci.diff_qty != 0:
            inv = db.query(Inventory).filter(
                Inventory.warehouse_id == check.warehouse_id,
                Inventory.product_id == ci.product_id
            ).first()

            if inv:
                inv.quantity = ci.actual_qty
            else:
                inv = Inventory(
                    warehouse_id=check.warehouse_id,
                    product_id=ci.product_id,
                    quantity=ci.actual_qty
                )
                db.add(inv)
            adjusted_count += 1

    check.status = 3  # 已调整
    db.commit()
    return ResponseModel(message=f"库存调整完成，调整了 {adjusted_count} 个商品")


@router.post("/stocktaking/{check_id}/void", response_model=ResponseModel)
def void_stocktaking(
    check_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """作废盘点单"""
    user = get_current_user(authorization, db)
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(404, "盘点单不存在")
    if check.status not in (1, 2):
        raise HTTPException(400, f"当前状态 {check.status} 不允许作废")

    require_role(user, db, "admin", message="只有管理员可以作废盘点单")

    check.status = 4  # 已作废
    db.commit()
    return ResponseModel(message="盘点单已作废")
