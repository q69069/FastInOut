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

router = APIRouter(prefix="/api", tags=["报损单"])


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
        code=_gen_code(db), warehouse_id=data["warehouse_id"],
        report_type=data.get("report_type", "general"),
        status="pending", remark=data.get("remark"), created_by=user.id
    )
    db.add(dr)
    db.flush()
    total = 0
    for item in data["items"]:
        amount = item.get("amount", 0) or (item["quantity"] * item.get("unit_cost", 0))
        total += amount
        db.add(DamageReportItem(
            report_id=dr.id, product_id=item["product_id"],
            quantity=item["quantity"], unit_cost=item.get("unit_cost", 0),
            amount=amount, reason=item.get("reason")
        ))
    dr.total_amount = total
    db.commit()
    return ResponseModel(message="报损单创建成功", data={"id": dr.id, "code": dr.code})


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
    if user.role_id != 5:
        raise HTTPException(403, "只有管理员可以审核报损单")
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
    db.commit()
    return ResponseModel(message="报损审核通过，库存已扣减")
