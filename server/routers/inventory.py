from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.inventory import (
    Inventory, InventoryCheck, InventoryCheckItem,
    InventoryTransfer, InventoryTransferItem,
    InventoryAlert, OtherInventoryLog
)
from models.product import Product
from models.warehouse import Warehouse
from models.system import Message
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.auth import decode_access_token
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/api/inventory", tags=["仓库管理"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


# ========== Schemas ==========
class CheckItemCreate(BaseModel):
    product_id: int
    count_num: float  # 实盘数量


class CheckCreate(BaseModel):
    warehouse_id: int
    remark: Optional[str] = None
    items: Optional[List[CheckItemCreate]] = None


class TransferItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="调拨数量必须大于0")


class TransferCreate(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    remark: Optional[str] = None
    items: List[TransferItemCreate] = []


class OtherInOut(BaseModel):
    warehouse_id: int
    product_id: int
    quantity: float = Field(gt=0, description="数量必须大于0")
    reason: Optional[str] = None
    remark: Optional[str] = None


# ========== Helper ==========
def _check_alert(db: Session, product_id: int, warehouse_id: int, quantity: float):
    product = db.query(Product).get(product_id)
    if not product:
        return
    if product.stock_min > 0 and quantity < product.stock_min:
        alert = InventoryAlert(
            product_id=product_id, warehouse_id=warehouse_id,
            current_qty=quantity, min_qty=product.stock_min, max_qty=product.stock_max,
            alert_type="low"
        )
        db.add(alert)
        msg = Message(title=f"库存预警：{product.name}库存不足", content=f"当前库存{quantity}，低于下限{product.stock_min}", msg_type="inventory_alert")
        db.add(msg)
    if product.stock_max > 0 and quantity > product.stock_max:
        alert = InventoryAlert(
            product_id=product_id, warehouse_id=warehouse_id,
            current_qty=quantity, min_qty=product.stock_min, max_qty=product.stock_max,
            alert_type="high"
        )
        db.add(alert)
        msg = Message(title=f"库存预警：{product.name}库存积压", content=f"当前库存{quantity}，高于上限{product.stock_max}", msg_type="inventory_alert")
        db.add(msg)


# ========== 库存查询 ==========
@router.get("", response_model=PaginatedResponse)
def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: int = Query(None),
    product_id: int = Query(None),
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Inventory)
    # 应用数据权限过滤 - 库存按仓库权限过滤
    q = DataFilter.apply_scope(q, Inventory, user, db, scope_field="warehouse_id", module_key="inventory")
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    if product_id:
        q = q.filter(Inventory.product_id == product_id)
    if keyword:
        product_ids = [p.id for p in db.query(Product).filter(
            Product.name.contains(keyword) | Product.code.contains(keyword) | Product.barcode.contains(keyword)
        ).all()]
        q = q.filter(Inventory.product_id.in_(product_ids))
    total = q.count()
    items = q.order_by(Inventory.warehouse_id, Inventory.product_id).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for inv in items:
        product = db.query(Product).get(inv.product_id)
        warehouse = db.query(Warehouse).get(inv.warehouse_id)
        result.append({
            "id": inv.id,
            "warehouse_id": inv.warehouse_id,
            "warehouse_name": warehouse.name if warehouse else "",
            "product_id": inv.product_id,
            "product_code": product.code if product else "",
            "product_name": product.name if product else "",
            "product_spec": product.spec if product else "",
            "product_unit": product.unit if product else "",
            "quantity": inv.quantity,
            "cost_price": inv.cost_price,
            "total_value": inv.quantity * inv.cost_price,
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


# ========== 库存流水（M7: N+1 查询优化） ==========
@router.get("/flow", response_model=PaginatedResponse)
def inventory_flow(
    warehouse_id: int = Query(None),
    product_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    flow_type: str = Query(None),  # purchase_in/purchase_return/sales_out/sales_return/transfer/other_in/other_out
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    from models.purchase import PurchaseStockin, PurchaseStockinItem, PurchaseReturn, PurchaseReturnItem
    from models.sales import SalesStockout, SalesStockoutItem, SalesReturn, SalesReturnItem

    # M7: 批量预加载所有商品名称，避免逐条查询
    products_map = {p.id: p.name for p in db.query(Product).all()}

    def _product_name(pid):
        return products_map.get(pid, "")

    records = []

    # 采购入库
    if not flow_type or flow_type == "purchase_in":
        q = db.query(PurchaseStockin).filter(PurchaseStockin.status == 1)
        if warehouse_id:
            q = q.filter(PurchaseStockin.warehouse_id == warehouse_id)
        if start_date:
            q = q.filter(PurchaseStockin.created_at >= start_date)
        if end_date:
            q = q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        stockin_ids = [si.id for si in q.all()]
        if stockin_ids:
            items_q = db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id.in_(stockin_ids))
            if product_id:
                items_q = items_q.filter(PurchaseStockinItem.product_id == product_id)
            items = items_q.all()
            stockin_map = {si.id: si for si in db.query(PurchaseStockin).filter(PurchaseStockin.id.in_(stockin_ids)).all()}
            for item in items:
                si = stockin_map[item.stockin_id]
                records.append({
                    "id": si.id, "warehouse_id": si.warehouse_id, "product_id": item.product_id,
                    "product_name": _product_name(item.product_id),
                    "type": "purchase_in", "quantity": item.quantity, "price": item.price,
                    "reason": "采购入库", "code": si.code,
                    "created_at": str(si.created_at)
                })

    # 采购退货
    if not flow_type or flow_type == "purchase_return":
        q = db.query(PurchaseReturn).filter(PurchaseReturn.status == 1)
        if warehouse_id:
            q = q.filter(PurchaseReturn.warehouse_id == warehouse_id)
        if start_date:
            q = q.filter(PurchaseReturn.created_at >= start_date)
        if end_date:
            q = q.filter(PurchaseReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        return_ids = [pr.id for pr in q.all()]
        if return_ids:
            items_q = db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id.in_(return_ids))
            if product_id:
                items_q = items_q.filter(PurchaseReturnItem.product_id == product_id)
            items = items_q.all()
            return_map = {pr.id: pr for pr in db.query(PurchaseReturn).filter(PurchaseReturn.id.in_(return_ids)).all()}
            for item in items:
                pr = return_map[item.return_id]
                records.append({
                    "id": pr.id, "warehouse_id": pr.warehouse_id, "product_id": item.product_id,
                    "product_name": _product_name(item.product_id),
                    "type": "purchase_return", "quantity": -item.quantity, "price": item.price,
                    "reason": "采购退货", "code": pr.code,
                    "created_at": str(pr.created_at)
                })

    # 销售出库
    if not flow_type or flow_type == "sales_out":
        q = db.query(SalesStockout).filter(SalesStockout.status == 1)
        if warehouse_id:
            q = q.filter(SalesStockout.warehouse_id == warehouse_id)
        if start_date:
            q = q.filter(SalesStockout.created_at >= start_date)
        if end_date:
            q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        stockout_ids = [so.id for so in q.all()]
        if stockout_ids:
            items_q = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id.in_(stockout_ids))
            if product_id:
                items_q = items_q.filter(SalesStockoutItem.product_id == product_id)
            items = items_q.all()
            stockout_map = {so.id: so for so in db.query(SalesStockout).filter(SalesStockout.id.in_(stockout_ids)).all()}
            for item in items:
                so = stockout_map[item.stockout_id]
                records.append({
                    "id": so.id, "warehouse_id": so.warehouse_id, "product_id": item.product_id,
                    "product_name": _product_name(item.product_id),
                    "type": "sales_out", "quantity": -item.quantity, "price": item.price,
                    "reason": "销售出库", "code": so.code,
                    "created_at": str(so.created_at)
                })

    # 销售退货
    if not flow_type or flow_type == "sales_return":
        q = db.query(SalesReturn).filter(SalesReturn.status == 1)
        if warehouse_id:
            q = q.filter(SalesReturn.warehouse_id == warehouse_id)
        if start_date:
            q = q.filter(SalesReturn.created_at >= start_date)
        if end_date:
            q = q.filter(SalesReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        return_ids = [sr.id for sr in q.all()]
        if return_ids:
            items_q = db.query(SalesReturnItem).filter(SalesReturnItem.return_id.in_(return_ids))
            if product_id:
                items_q = items_q.filter(SalesReturnItem.product_id == product_id)
            items = items_q.all()
            return_map = {sr.id: sr for sr in db.query(SalesReturn).filter(SalesReturn.id.in_(return_ids)).all()}
            for item in items:
                sr = return_map[item.return_id]
                records.append({
                    "id": sr.id, "warehouse_id": sr.warehouse_id, "product_id": item.product_id,
                    "product_name": _product_name(item.product_id),
                    "type": "sales_return", "quantity": item.quantity, "price": item.price,
                    "reason": "销售退货", "code": sr.code,
                    "created_at": str(sr.created_at)
                })

    # 库存调拨
    if not flow_type or flow_type == "transfer":
        q = db.query(InventoryTransfer).filter(InventoryTransfer.status == 2)
        if start_date:
            q = q.filter(InventoryTransfer.created_at >= start_date)
        if end_date:
            q = q.filter(InventoryTransfer.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        transfer_ids = [t.id for t in q.all()]
        if transfer_ids:
            items_q = db.query(InventoryTransferItem).filter(InventoryTransferItem.transfer_id.in_(transfer_ids))
            if product_id:
                items_q = items_q.filter(InventoryTransferItem.product_id == product_id)
            items = items_q.all()
            transfer_map = {t.id: t for t in db.query(InventoryTransfer).filter(InventoryTransfer.id.in_(transfer_ids)).all()}
            for item in items:
                t = transfer_map[item.transfer_id]
                if not warehouse_id or t.from_warehouse_id == warehouse_id:
                    records.append({
                        "id": t.id, "warehouse_id": t.from_warehouse_id, "product_id": item.product_id,
                        "product_name": _product_name(item.product_id),
                        "type": "transfer_out", "quantity": -item.quantity,
                        "reason": f"调拨出库→{t.to_warehouse_id}", "code": t.code,
                        "created_at": str(t.created_at)
                    })
                if not warehouse_id or t.to_warehouse_id == warehouse_id:
                    records.append({
                        "id": t.id, "warehouse_id": t.to_warehouse_id, "product_id": item.product_id,
                        "product_name": _product_name(item.product_id),
                        "type": "transfer_in", "quantity": item.quantity,
                        "reason": f"调拨入库←{t.from_warehouse_id}", "code": t.code,
                        "created_at": str(t.created_at)
                    })

    # 其他出入库
    if not flow_type or flow_type in ("other_in", "other_out"):
        q = db.query(OtherInventoryLog)
        if warehouse_id:
            q = q.filter(OtherInventoryLog.warehouse_id == warehouse_id)
        if product_id:
            q = q.filter(OtherInventoryLog.product_id == product_id)
        if flow_type:
            q = q.filter(OtherInventoryLog.type == ("in" if flow_type == "other_in" else "out"))
        if start_date:
            q = q.filter(OtherInventoryLog.created_at >= start_date)
        if end_date:
            q = q.filter(OtherInventoryLog.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        for i in q.all():
            records.append({
                "id": i.id, "warehouse_id": i.warehouse_id, "product_id": i.product_id,
                "product_name": _product_name(i.product_id),
                "type": f"other_{i.type}", "quantity": i.quantity if i.type == "in" else -i.quantity,
                "reason": i.reason, "remark": i.remark,
                "created_at": str(i.created_at)
            })

    # 按时间倒序排列
    records.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(data=records[start:end], total=total, page=page, page_size=page_size)


# ========== 库存预警 ==========
@router.get("/alerts", response_model=ResponseModel)
def list_alerts(
    alert_type: str = Query(None),
    warehouse_id: int = Query(None),
    is_handled: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(InventoryAlert)
    if alert_type:
        q = q.filter(InventoryAlert.alert_type == alert_type)
    if warehouse_id:
        q = q.filter(InventoryAlert.warehouse_id == warehouse_id)
    if is_handled is not None:
        q = q.filter(InventoryAlert.is_handled == is_handled)
    items = q.order_by(InventoryAlert.created_at.desc()).all()
    result = []
    for a in items:
        product = db.query(Product).get(a.product_id)
        result.append({
            "id": a.id, "product_name": product.name if product else "",
            "warehouse_id": a.warehouse_id, "current_qty": a.current_qty,
            "min_qty": a.min_qty, "max_qty": a.max_qty,
            "alert_type": a.alert_type, "is_handled": a.is_handled,
            "created_at": str(a.created_at)
        })
    return ResponseModel(data=result)


# ========== 库存盘点 ==========
@router.get("/checks", response_model=PaginatedResponse)
def list_checks(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    warehouse_id: int = Query(None), status: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(InventoryCheck)
    if warehouse_id:
        q = q.filter(InventoryCheck.warehouse_id == warehouse_id)
    if status is not None:
        q = q.filter(InventoryCheck.status == status)
    if start_date:
        q = q.filter(InventoryCheck.created_at >= start_date)
    if end_date:
        q = q.filter(InventoryCheck.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(InventoryCheck.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for c in items:
        wh = db.query(Warehouse).get(c.warehouse_id)
        result.append({
            "id": c.id, "code": c.code, "warehouse_id": c.warehouse_id,
            "warehouse_name": wh.name if wh else "",
            "status": c.status, "remark": c.remark,
            "created_at": str(c.created_at), "confirmed_at": str(c.confirmed_at) if c.confirmed_at else None
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/checks", response_model=ResponseModel)
def create_check(req: CheckCreate, db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(InventoryCheck).filter(InventoryCheck.code.like(f"PD{today}-%")).count()
    code = f"PD{today}-{count + 1:03d}"
    check = InventoryCheck(code=code, warehouse_id=req.warehouse_id, status=1, remark=req.remark)
    db.add(check)
    db.flush()
    if req.items:
        for item in req.items:
            inv = db.query(Inventory).filter(Inventory.warehouse_id == req.warehouse_id, Inventory.product_id == item.product_id).first()
            system_qty = inv.quantity if inv else 0
            ci = InventoryCheckItem(check_id=check.id, product_id=item.product_id, system_qty=system_qty, actual_qty=item.count_num, diff_qty=item.count_num - system_qty)
            db.add(ci)
    else:
        invs = db.query(Inventory).filter(Inventory.warehouse_id == req.warehouse_id).all()
        for inv in invs:
            ci = InventoryCheckItem(check_id=check.id, product_id=inv.product_id, system_qty=inv.quantity, actual_qty=inv.quantity, diff_qty=0)
            db.add(ci)
    db.commit()
    db.refresh(check)
    return ResponseModel(data={"id": check.id, "code": code, "status": check.status})


@router.get("/checks/{check_id}", response_model=ResponseModel)
def get_check(check_id: int, db: Session = Depends(get_db)):
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()
    detail = []
    for ci in items:
        product = db.query(Product).get(ci.product_id)
        detail.append({
            "product_id": ci.product_id,
            "product_name": product.name if product else "",
            "system_qty": ci.system_qty,
            "actual_qty": ci.actual_qty,
            "diff_qty": ci.diff_qty
        })
    return ResponseModel(data={"id": check.id, "code": check.code, "warehouse_id": check.warehouse_id, "status": check.status, "items": detail})


@router.put("/checks/{check_id}", response_model=ResponseModel)
def update_check(check_id: int, items: List[CheckItemCreate], db: Session = Depends(get_db)):
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    if check.status != 1:
        raise HTTPException(status_code=400, detail="非盘点中状态不能修改")
    for item in items:
        ci = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id, InventoryCheckItem.product_id == item.product_id).first()
        if ci:
            ci.actual_qty = item.count_num
            ci.diff_qty = item.count_num - ci.system_qty
    db.commit()
    return ResponseModel(message="更新成功")


@router.post("/checks/{check_id}/confirm", response_model=ResponseModel)
def confirm_check(check_id: int, db: Session = Depends(get_db)):
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    if check.status != 1:
        raise HTTPException(status_code=400, detail="已确认或已作废")
    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()
    profit_amount = 0
    loss_amount = 0
    for ci in items:
        if ci.diff_qty != 0:
            inv = db.query(Inventory).filter(Inventory.warehouse_id == check.warehouse_id, Inventory.product_id == ci.product_id).first()
            if inv:
                inv.quantity = ci.actual_qty
            else:
                inv = Inventory(warehouse_id=check.warehouse_id, product_id=ci.product_id, quantity=ci.actual_qty)
                db.add(inv)
            _check_alert(db, ci.product_id, check.warehouse_id, ci.actual_qty)
            if ci.diff_qty > 0:
                profit_amount += ci.diff_qty * (inv.cost_price if inv else 0)
            else:
                loss_amount += abs(ci.diff_qty) * (inv.cost_price if inv else 0)
    check.status = 2
    check.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="盘点确认成功", data={"profit_amount": profit_amount, "loss_amount": loss_amount})


@router.delete("/checks/{check_id}", response_model=ResponseModel)
def delete_check(check_id: int, db: Session = Depends(get_db)):
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    if check.status != 1:
        raise HTTPException(status_code=400, detail="非盘点中状态不能作废")
    check.status = 3
    db.commit()
    return ResponseModel(message="已作废")


# ========== 库存调拨 ==========
@router.get("/transfers", response_model=PaginatedResponse)
def list_transfers(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(InventoryTransfer)
    if status is not None:
        q = q.filter(InventoryTransfer.status == status)
    if start_date:
        q = q.filter(InventoryTransfer.created_at >= start_date)
    if end_date:
        q = q.filter(InventoryTransfer.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(InventoryTransfer.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for t in items:
        from_wh = db.query(Warehouse).get(t.from_warehouse_id)
        to_wh = db.query(Warehouse).get(t.to_warehouse_id)
        result.append({
            "id": t.id, "code": t.code,
            "from_warehouse_name": from_wh.name if from_wh else "",
            "to_warehouse_name": to_wh.name if to_wh else "",
            "status": t.status, "remark": t.remark,
            "created_at": str(t.created_at), "confirmed_at": str(t.confirmed_at) if t.confirmed_at else None
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/transfers", response_model=ResponseModel)
def create_transfer(req: TransferCreate, db: Session = Depends(get_db)):
    # M5: 检查源仓库和目标仓库不能相同
    if req.from_warehouse_id == req.to_warehouse_id:
        raise HTTPException(status_code=400, detail="源仓库和目标仓库不能相同")
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(InventoryTransfer).filter(InventoryTransfer.code.like(f"DB{today}-%")).count()
    code = f"DB{today}-{count + 1:03d}"
    for item in req.items:
        inv = db.query(Inventory).filter(Inventory.warehouse_id == req.from_warehouse_id, Inventory.product_id == item.product_id).first()
        if not inv or inv.quantity < item.quantity:
            product = db.query(Product).get(item.product_id)
            raise HTTPException(status_code=400, detail=f"商品{product.name if product else item.product_id}库存不足")
    transfer = InventoryTransfer(code=code, from_warehouse_id=req.from_warehouse_id, to_warehouse_id=req.to_warehouse_id, status=1, remark=req.remark)
    db.add(transfer)
    db.flush()
    for item in req.items:
        ti = InventoryTransferItem(transfer_id=transfer.id, product_id=item.product_id, quantity=item.quantity)
        db.add(ti)
    db.commit()
    db.refresh(transfer)
    return ResponseModel(data={"id": transfer.id, "code": code, "status": transfer.status})


@router.get("/transfers/{transfer_id}", response_model=ResponseModel)
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(InventoryTransfer).get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨单不存在")
    items = db.query(InventoryTransferItem).filter(InventoryTransferItem.transfer_id == transfer_id).all()
    detail = []
    for ti in items:
        product = db.query(Product).get(ti.product_id)
        detail.append({"product_id": ti.product_id, "product_name": product.name if product else "", "quantity": ti.quantity})
    return ResponseModel(data={"id": transfer.id, "code": transfer.code, "from_warehouse_id": transfer.from_warehouse_id, "to_warehouse_id": transfer.to_warehouse_id, "status": transfer.status, "items": detail})


@router.post("/transfers/{transfer_id}/confirm", response_model=ResponseModel)
def confirm_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(InventoryTransfer).get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨单不存在")
    if transfer.status != 1:
        raise HTTPException(status_code=400, detail="已确认或已取消")
    items = db.query(InventoryTransferItem).filter(InventoryTransferItem.transfer_id == transfer_id).all()
    for ti in items:
        from_inv = db.query(Inventory).filter(Inventory.warehouse_id == transfer.from_warehouse_id, Inventory.product_id == ti.product_id).first()
        if not from_inv or from_inv.quantity < ti.quantity:
            raise HTTPException(status_code=400, detail=f"商品{ti.product_id}库存不足")
        from_inv.quantity -= ti.quantity
        to_inv = db.query(Inventory).filter(Inventory.warehouse_id == transfer.to_warehouse_id, Inventory.product_id == ti.product_id).first()
        if to_inv:
            to_inv.quantity += ti.quantity
        else:
            to_inv = Inventory(warehouse_id=transfer.to_warehouse_id, product_id=ti.product_id, quantity=ti.quantity, cost_price=from_inv.cost_price)
            db.add(to_inv)
        _check_alert(db, ti.product_id, transfer.from_warehouse_id, from_inv.quantity)
    transfer.status = 2
    transfer.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="调拨确认成功")


@router.delete("/transfers/{transfer_id}", response_model=ResponseModel)
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(InventoryTransfer).get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨单不存在")
    if transfer.status != 1:
        raise HTTPException(status_code=400, detail="非调拨中状态不能取消")
    transfer.status = 3
    db.commit()
    return ResponseModel(message="已取消")


# ========== 报损报溢 ==========
@router.post("/other-in", response_model=ResponseModel)
def other_in(req: OtherInOut, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.warehouse_id == req.warehouse_id, Inventory.product_id == req.product_id).first()
    if inv:
        inv.quantity += req.quantity
    else:
        inv = Inventory(warehouse_id=req.warehouse_id, product_id=req.product_id, quantity=req.quantity)
        db.add(inv)
    log = OtherInventoryLog(warehouse_id=req.warehouse_id, product_id=req.product_id, type="in", quantity=req.quantity, reason=req.reason, remark=req.remark)
    db.add(log)
    _check_alert(db, req.product_id, req.warehouse_id, inv.quantity)
    db.commit()
    return ResponseModel(message="其他入库成功")


@router.post("/other-out", response_model=ResponseModel)
def other_out(req: OtherInOut, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.warehouse_id == req.warehouse_id, Inventory.product_id == req.product_id).first()
    if not inv or inv.quantity < req.quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    inv.quantity -= req.quantity
    log = OtherInventoryLog(warehouse_id=req.warehouse_id, product_id=req.product_id, type="out", quantity=req.quantity, reason=req.reason, remark=req.remark)
    db.add(log)
    _check_alert(db, req.product_id, req.warehouse_id, inv.quantity)
    db.commit()
    return ResponseModel(message="其他出库成功")


@router.get("/other-log", response_model=PaginatedResponse)
def list_other_log(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    type: str = Query(None), warehouse_id: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(OtherInventoryLog)
    if type:
        q = q.filter(OtherInventoryLog.type == type)
    if warehouse_id:
        q = q.filter(OtherInventoryLog.warehouse_id == warehouse_id)
    if start_date:
        q = q.filter(OtherInventoryLog.created_at >= start_date)
    if end_date:
        q = q.filter(OtherInventoryLog.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(OtherInventoryLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[{
        "id": i.id, "warehouse_id": i.warehouse_id, "product_id": i.product_id,
        "type": i.type, "quantity": i.quantity, "reason": i.reason,
        "remark": i.remark, "created_at": str(i.created_at)
    } for i in items], total=total, page=page, page_size=page_size)


# ========== 库存统计 ==========
@router.get("/summary", response_model=ResponseModel)
def inventory_summary(db: Session = Depends(get_db)):
    invs = db.query(Inventory).all()
    total_qty = sum(i.quantity for i in invs)
    total_value = sum(i.quantity * i.cost_price for i in invs)
    wh_stats = {}
    for i in invs:
        wh = db.query(Warehouse).get(i.warehouse_id)
        name = wh.name if wh else f"仓库{i.warehouse_id}"
        if name not in wh_stats:
            wh_stats[name] = {"qty": 0, "value": 0}
        wh_stats[name]["qty"] += i.quantity
        wh_stats[name]["value"] += i.quantity * i.cost_price
    return ResponseModel(data={"total_qty": total_qty, "total_value": total_value, "product_count": len(set(i.product_id for i in invs)), "warehouse_stats": wh_stats})


@router.get("/slow-moving", response_model=ResponseModel)
def slow_moving(days: int = Query(30), db: Session = Depends(get_db)):
    from models.sales import SalesStockoutItem, SalesStockout
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    recent_product_ids = set()
    recent_items = db.query(SalesStockoutItem).join(SalesStockout).filter(SalesStockout.created_at >= cutoff).all()
    for item in recent_items:
        recent_product_ids.add(item.product_id)
    invs = db.query(Inventory).filter(Inventory.quantity > 0).all()
    result = []
    for inv in invs:
        if inv.product_id not in recent_product_ids:
            product = db.query(Product).get(inv.product_id)
            result.append({"product_id": inv.product_id, "product_name": product.name if product else "", "quantity": inv.quantity})
    return ResponseModel(data=result)


@router.get("/turnover", response_model=ResponseModel)
def turnover(start_date: str = Query(None), end_date: str = Query(None), warehouse_id: int = Query(None), db: Session = Depends(get_db)):
    from models.sales import SalesStockout, SalesStockoutItem
    q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date:
        q = q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    stockouts = q.all()
    total_out = 0
    for so in stockouts:
        items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == so.id).all()
        for item in items:
            total_out += item.quantity
    invs = db.query(Inventory).all()
    avg_stock = sum(i.quantity for i in invs) / len(invs) if invs else 1
    return ResponseModel(data={"total_out": total_out, "avg_stock": avg_stock, "turnover_rate": total_out / avg_stock if avg_stock > 0 else 0})


# ========== 智能补货建议 ==========
@router.get("/reorder-suggestions", response_model=ResponseModel)
def get_reorder_suggestions(db: Session = Depends(get_db)):
    """获取需要补货的商品（当前库存 <= 最低库存）"""
    products = db.query(Product).filter(Product.stock_min > 0, Product.status == 1).all()
    suggestions = []
    for p in products:
        # 汇总所有仓库的库存
        total_qty = sum(inv.quantity for inv in db.query(Inventory).filter(Inventory.product_id == p.id).all())
        if total_qty <= p.stock_min:
            # 建议补货到最高库存
            suggest_qty = p.stock_max - total_qty if p.stock_max > 0 else p.stock_min * 2
            suggestions.append({
                "product_id": p.id,
                "product_code": p.code,
                "product_name": p.name,
                "current_qty": total_qty,
                "min_stock": p.stock_min,
                "max_stock": p.stock_max,
                "suggest_qty": suggest_qty,
                "supplier_id": p.supplier_id
            })
    return ResponseModel(data=suggestions)


# ========== 库存详情（放在最后避免路由冲突）==========
@router.get("/detail/{warehouse_id}/{product_id}", response_model=ResponseModel)
def get_inventory_detail(warehouse_id: int, product_id: int, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id, Inventory.product_id == product_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    product = db.query(Product).get(product_id)
    warehouse = db.query(Warehouse).get(warehouse_id)
    return ResponseModel(data={
        "warehouse_name": warehouse.name if warehouse else "",
        "product_name": product.name if product else "",
        "quantity": inv.quantity,
        "cost_price": inv.cost_price,
        "total_value": inv.quantity * inv.cost_price,
    })
