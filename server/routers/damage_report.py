"""报损单路由 — Phase C"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.damage_report import DamageReport, DamageReportItem
from models.warehouse import Warehouse
from models.product import Product
from models.inventory import Inventory
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.role_check import require_role
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level
from deps import get_current_user

router = APIRouter(prefix="/api", tags=["报损单"])

def _gen_code(db):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"BS{today}"
    last = db.query(DamageReport).filter(DamageReport.code.like(f"{prefix}%")).order_by(DamageReport.id.desc()).first()
    seq = int(last.code[-4:]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


@router.get("/damage-reports", response_model=PaginatedResponse)
def list_damage_reports(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None), authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(DamageReport)
    if status:
        q = q.filter(DamageReport.status == status)
    total = q.count()
    items = q.order_by(DamageReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for dr in items:
        wh = db.query(Warehouse).get(dr.warehouse_id)
        result.append({
            "id": dr.id, "code": dr.code,
            "warehouse_id": dr.warehouse_id,
            "warehouse_name": wh.name if wh else "",
            "report_type": dr.report_type,
            "total_amount": dr.total_amount, "status": dr.status,
            "remark": dr.remark, "created_at": str(dr.created_at)
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/damage-reports", response_model=ResponseModel)
def create_damage_report(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    if not data.get("items"):
        raise HTTPException(400, "请添加报损明细")
    dr = DamageReport(
        code=_gen_code(db), warehouse_id=data.get("warehouse_id"),
        report_type=data.get("report_type", "general"),
        status="pending", remark=data.get("remark"), created_by=user.id
    )
    db.add(dr)
    db.flush()
    total = 0
    for item in data["items"]:
        amount = item.get("amount", 0) or (item["quantity"] * item.get("unit_cost", 0))
        total += amount
        if item.get("unit_level"):
            base_qty, conv_rate = resolve_by_unit_level(item["product_id"], item["unit_level"], item.get("unit_quantity") or item["quantity"], item.get("unit_conv_rate", 1), db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item["product_id"], item.get("unit_id"), item.get("unit_quantity") or item["quantity"], db)
        db.add(DamageReportItem(
            report_id=dr.id, product_id=item["product_id"],
            quantity=base_qty, unit_id=item.get("unit_id"), unit_quantity=item.get("unit_quantity") or item["quantity"], unit_conv_rate=conv_rate,
            unit_cost=item.get("unit_cost", 0),
            amount=amount, reason=item.get("reason")
        ))
    dr.total_amount = total
    db.commit()
    return ResponseModel(message="报损单创建成功", data={"id": dr.id, "code": dr.code})


# ========== 修改报损单（仅pending状态） ==========
@router.put("/damage-reports/{report_id}", response_model=ResponseModel)
def update_damage_report(report_id: int, data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    dr = db.query(DamageReport).get(report_id)
    if not dr:
        raise HTTPException(404, "报损单不存在")
    if dr.status != "pending":
        raise HTTPException(400, f"当前状态 {dr.status} 不允许修改")

    if not data.get("items"):
        raise HTTPException(400, "请添加报损明细")

    # 删除旧明细
    db.query(DamageReportItem).filter(DamageReportItem.report_id == report_id).delete()

    # 更新主单
    dr.warehouse_id = data.get("warehouse_id", dr.warehouse_id)
    dr.report_type = data.get("report_type", dr.report_type)
    dr.remark = data.get("remark")

    # 创建新明细
    total = 0
    for item in data["items"]:
        amount = item.get("amount", 0) or (item["quantity"] * item.get("unit_cost", 0))
        total += amount
        if item.get("unit_level"):
            base_qty, conv_rate = resolve_by_unit_level(item["product_id"], item["unit_level"], item.get("unit_quantity") or item["quantity"], item.get("unit_conv_rate", 1), db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item["product_id"], item.get("unit_id"), item.get("unit_quantity") or item["quantity"], db)
        db.add(DamageReportItem(
            report_id=dr.id, product_id=item["product_id"],
            quantity=base_qty, unit_id=item.get("unit_id"), unit_quantity=item.get("unit_quantity") or item["quantity"], unit_conv_rate=conv_rate,
            unit_cost=item.get("unit_cost", 0),
            amount=amount, reason=item.get("reason")
        ))
    dr.total_amount = total

    db.commit()
    return ResponseModel(message="报损单修改成功", data={"id": dr.id, "code": dr.code})


@router.get("/damage-reports/{report_id}", response_model=ResponseModel)
def get_damage_report(report_id: int, db: Session = Depends(get_db)):
    dr = db.query(DamageReport).get(report_id)
    if not dr:
        raise HTTPException(404, "报损单不存在")
    wh = db.query(Warehouse).get(dr.warehouse_id)
    items = db.query(DamageReportItem).filter(DamageReportItem.report_id == report_id).all()
    item_list = []
    for di in items:
        prod = db.query(Product).get(di.product_id)
        item_list.append({
            "id": di.id, "product_id": di.product_id,
            "product_name": prod.name if prod else "",
            "quantity": di.quantity, "unit_cost": di.unit_cost,
            "amount": di.amount, "reason": di.reason
        })
    return ResponseModel(data={
        "id": dr.id, "code": dr.code,
        "warehouse_id": dr.warehouse_id,
        "warehouse_name": wh.name if wh else "",
        "report_type": dr.report_type, "total_amount": dr.total_amount,
        "status": dr.status, "remark": dr.remark,
        "created_at": str(dr.created_at),
        "items": item_list
    })


@router.post("/damage-reports/{report_id}/audit", response_model=ResponseModel)
def audit_damage_report(report_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """审核报损单 — 扣减库存"""
    user = get_current_user(authorization, db)
    require_role(user, db, "admin", message="只有管理员可以审核报损单")
    dr = db.query(DamageReport).get(report_id)
    if not dr:
        raise HTTPException(404, "报损单不存在")
    if dr.status != "pending":
        raise HTTPException(400, f"当前状态 {dr.status} 不允许审核")
    items = db.query(DamageReportItem).filter(DamageReportItem.report_id == report_id).all()
    for di in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == dr.warehouse_id,
            Inventory.product_id == di.product_id
        ).first()
        if inv:
            inv.quantity = max(0, inv.quantity - di.quantity)
    dr.status = "adjusted"
    dr.audited_at = datetime.now()
    dr.auditor_id = user.id
    db.commit()
    return ResponseModel(message="报损审核通过，库存已扣减")
