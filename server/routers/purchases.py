from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseStockin, PurchaseStockinItem, PurchaseReturn
from schemas.purchase import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderOut,
    PurchaseStockinCreate, PurchaseStockinOut,
    PurchaseReturnCreate, PurchaseReturnOut
)
from schemas.common import ResponseModel, PaginatedResponse
from datetime import datetime

router = APIRouter(prefix="/api", tags=["采购"])


def _gen_code(prefix: str, db: Session, model) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(model).count()
    return f"{prefix}{today}{count + 1:03d}"


# === 采购订单 ===
@router.get("/purchase-orders", response_model=PaginatedResponse)
def list_purchase_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None), supplier_id: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseOrder)
    if status is not None:
        q = q.filter(PurchaseOrder.status == status)
    if supplier_id:
        q = q.filter(PurchaseOrder.supplier_id == supplier_id)
    total = q.count()
    items = q.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[PurchaseOrderOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/purchase-orders", response_model=ResponseModel)
def create_purchase_order(req: PurchaseOrderCreate, db: Session = Depends(get_db)):
    code = _gen_code("CG", db, PurchaseOrder)
    order = PurchaseOrder(code=code, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(order)
    db.flush()
    for item in req.items:
        oi = PurchaseOrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
        db.add(oi)
    db.commit()
    db.refresh(order)
    return ResponseModel(data=PurchaseOrderOut.model_validate(order))


@router.put("/purchase-orders/{order_id}", response_model=ResponseModel)
def update_purchase_order(order_id: int, req: PurchaseOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    for k, v in req.model_dump(exclude_unset=True, exclude={"items"}).items():
        setattr(order, k, v)
    if req.items is not None:
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).delete()
        for item in req.items:
            oi = PurchaseOrderItem(order_id=order_id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
            db.add(oi)
    db.commit()
    db.refresh(order)
    return ResponseModel(data=PurchaseOrderOut.model_validate(order))


@router.delete("/purchase-orders/{order_id}", response_model=ResponseModel)
def delete_purchase_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/purchase-orders/{order_id}/stockin", response_model=ResponseModel)
def order_to_stockin(order_id: int, db: Session = Depends(get_db)):
    """订单转入库"""
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    code = _gen_code("RK", db, PurchaseStockin)
    stockin = PurchaseStockin(code=code, order_id=order_id, supplier_id=order.supplier_id, warehouse_id=order.warehouse_id, total_amount=order.total_amount)
    db.add(stockin)
    db.flush()
    items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).all()
    for item in items:
        si = PurchaseStockinItem(stockin_id=stockin.id, product_id=item.product_id, quantity=item.quantity - item.received_qty, price=item.price, amount=item.amount)
        db.add(si)
        item.received_qty = item.quantity
    order.status = 2
    db.commit()
    return ResponseModel(message="转入库成功")


# === 采购入库 ===
@router.get("/purchase-stockins", response_model=PaginatedResponse)
def list_purchase_stockins(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseStockin)
    total = q.count()
    items = q.order_by(PurchaseStockin.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[PurchaseStockinOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/purchase-stockins", response_model=ResponseModel)
def create_purchase_stockin(req: PurchaseStockinCreate, db: Session = Depends(get_db)):
    code = _gen_code("RK", db, PurchaseStockin)
    si = PurchaseStockin(code=code, order_id=req.order_id, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(si)
    db.flush()
    for item in req.items:
        sii = PurchaseStockinItem(stockin_id=si.id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
        db.add(sii)
    db.commit()
    db.refresh(si)
    return ResponseModel(data=PurchaseStockinOut.model_validate(si))


# === 采购退货 ===
@router.get("/purchase-returns", response_model=PaginatedResponse)
def list_purchase_returns(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseReturn)
    total = q.count()
    items = q.order_by(PurchaseReturn.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[PurchaseReturnOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/purchase-returns", response_model=ResponseModel)
def create_purchase_return(req: PurchaseReturnCreate, db: Session = Depends(get_db)):
    code = _gen_code("CT", db, PurchaseReturn)
    ret = PurchaseReturn(code=code, stockin_id=req.stockin_id, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(ret)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=PurchaseReturnOut.model_validate(ret))


# === 采购统计/对账 ===
@router.get("/purchases/supplier-statement", response_model=ResponseModel)
def supplier_statement(supplier_id: int = Query(None), db: Session = Depends(get_db)):
    """供应商对账（预留）"""
    return ResponseModel(data=[], message="功能开发中")


@router.get("/purchases/statistics", response_model=ResponseModel)
def purchase_statistics(db: Session = Depends(get_db)):
    """采购统计（预留）"""
    return ResponseModel(data={}, message="功能开发中")
