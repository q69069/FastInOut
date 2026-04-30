from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.inventory import Inventory, InventoryCheck, InventoryCheckItem, InventoryTransfer, InventoryTransferItem, InventoryAlert
from schemas.inventory import (
    InventoryOut, InventoryCheckCreate, InventoryCheckOut,
    InventoryTransferCreate, InventoryTransferOut, InventoryAlertOut, InventoryAdjust
)
from schemas.common import ResponseModel, PaginatedResponse
from datetime import datetime

router = APIRouter(prefix="/api/inventory", tags=["仓库管理"])


@router.get("", response_model=PaginatedResponse)
def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: int = Query(None),
    product_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """库存查询"""
    q = db.query(Inventory)
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    if product_id:
        q = q.filter(Inventory.product_id == product_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[InventoryOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/alerts", response_model=ResponseModel)
def list_alerts(is_handled: int = Query(None), db: Session = Depends(get_db)):
    """库存预警"""
    q = db.query(InventoryAlert)
    if is_handled is not None:
        q = q.filter(InventoryAlert.is_handled == is_handled)
    items = q.order_by(InventoryAlert.created_at.desc()).all()
    return ResponseModel(data=[InventoryAlertOut.model_validate(i) for i in items])


@router.get("/checks", response_model=PaginatedResponse)
def list_checks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """盘点列表"""
    q = db.query(InventoryCheck)
    total = q.count()
    items = q.order_by(InventoryCheck.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[InventoryCheckOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("/checks", response_model=ResponseModel)
def create_check(req: InventoryCheckCreate, db: Session = Depends(get_db)):
    """新建盘点"""
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(InventoryCheck).count()
    code = f"PD{today}{count + 1:03d}"
    check = InventoryCheck(code=code, warehouse_id=req.warehouse_id, remark=req.remark)
    db.add(check)
    db.flush()
    for item in req.items:
        ci = InventoryCheckItem(
            check_id=check.id,
            product_id=item.product_id,
            system_qty=item.system_qty,
            actual_qty=item.actual_qty,
            diff_qty=item.actual_qty - item.system_qty
        )
        db.add(ci)
    db.commit()
    db.refresh(check)
    return ResponseModel(data=InventoryCheckOut.model_validate(check))


@router.post("/checks/{check_id}/confirm", response_model=ResponseModel)
def confirm_check(check_id: int, db: Session = Depends(get_db)):
    """确认盘点"""
    check = db.query(InventoryCheck).get(check_id)
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    check.status = 1
    check.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="盘点已确认")


@router.get("/transfers", response_model=PaginatedResponse)
def list_transfers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """调拨列表"""
    q = db.query(InventoryTransfer)
    total = q.count()
    items = q.order_by(InventoryTransfer.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[InventoryTransferOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("/transfers", response_model=ResponseModel)
def create_transfer(req: InventoryTransferCreate, db: Session = Depends(get_db)):
    """新建调拨"""
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(InventoryTransfer).count()
    code = f"DB{today}{count + 1:03d}"
    transfer = InventoryTransfer(
        code=code,
        from_warehouse_id=req.from_warehouse_id,
        to_warehouse_id=req.to_warehouse_id,
        remark=req.remark
    )
    db.add(transfer)
    db.flush()
    for item in req.items:
        ti = InventoryTransferItem(
            transfer_id=transfer.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(ti)
    db.commit()
    db.refresh(transfer)
    return ResponseModel(data=InventoryTransferOut.model_validate(transfer))


@router.post("/transfers/{transfer_id}/confirm", response_model=ResponseModel)
def confirm_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """确认调拨"""
    transfer = db.query(InventoryTransfer).get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="调拨单不存在")
    transfer.status = 1
    transfer.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="调拨已确认")


@router.post("/adjust", response_model=ResponseModel)
def adjust_inventory(req: InventoryAdjust, db: Session = Depends(get_db)):
    """报损报溢"""
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == req.warehouse_id,
        Inventory.product_id == req.product_id
    ).first()
    if not inv:
        inv = Inventory(warehouse_id=req.warehouse_id, product_id=req.product_id, quantity=0)
        db.add(inv)
    inv.quantity += req.adjust_qty
    db.commit()
    return ResponseModel(message="调整成功")
