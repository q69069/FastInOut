from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.sales import SalesOrder, SalesOrderItem, SalesStockout, SalesStockoutItem, SalesReturn
from schemas.sales import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderOut,
    SalesStockoutCreate, SalesStockoutOut,
    SalesReturnCreate, SalesReturnOut
)
from schemas.common import ResponseModel, PaginatedResponse
from datetime import datetime

router = APIRouter(prefix="/api", tags=["销售"])


def _gen_code(prefix: str, db: Session, model) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(model).count()
    return f"{prefix}{today}{count + 1:03d}"


# === 销售订单 ===
@router.get("/sales-orders", response_model=PaginatedResponse)
def list_sales_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None), customer_id: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(SalesOrder)
    if status is not None:
        q = q.filter(SalesOrder.status == status)
    if customer_id:
        q = q.filter(SalesOrder.customer_id == customer_id)
    total = q.count()
    items = q.order_by(SalesOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[SalesOrderOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/sales-orders", response_model=ResponseModel)
def create_sales_order(req: SalesOrderCreate, db: Session = Depends(get_db)):
    code = _gen_code("XS", db, SalesOrder)
    order = SalesOrder(code=code, customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(order)
    db.flush()
    for item in req.items:
        oi = SalesOrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
        db.add(oi)
    db.commit()
    db.refresh(order)
    return ResponseModel(data=SalesOrderOut.model_validate(order))


@router.put("/sales-orders/{order_id}", response_model=ResponseModel)
def update_sales_order(order_id: int, req: SalesOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    for k, v in req.model_dump(exclude_unset=True, exclude={"items"}).items():
        setattr(order, k, v)
    if req.items is not None:
        db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).delete()
        for item in req.items:
            oi = SalesOrderItem(order_id=order_id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
            db.add(oi)
    db.commit()
    db.refresh(order)
    return ResponseModel(data=SalesOrderOut.model_validate(order))


@router.delete("/sales-orders/{order_id}", response_model=ResponseModel)
def delete_sales_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).delete()
    db.delete(order)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/sales-orders/{order_id}/stockout", response_model=ResponseModel)
def order_to_stockout(order_id: int, db: Session = Depends(get_db)):
    """订单转出库"""
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    code = _gen_code("CK", db, SalesStockout)
    stockout = SalesStockout(code=code, order_id=order_id, customer_id=order.customer_id, warehouse_id=order.warehouse_id, total_amount=order.total_amount)
    db.add(stockout)
    db.flush()
    items = db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).all()
    for item in items:
        soi = SalesStockoutItem(stockout_id=stockout.id, product_id=item.product_id, quantity=item.quantity - item.delivered_qty, price=item.price, amount=item.amount)
        db.add(soi)
        item.delivered_qty = item.quantity
    order.status = 2
    db.commit()
    return ResponseModel(message="转出库成功")


# === 销售出库 ===
@router.get("/sales-stockouts", response_model=PaginatedResponse)
def list_sales_stockouts(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(SalesStockout)
    total = q.count()
    items = q.order_by(SalesStockout.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[SalesStockoutOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/sales-stockouts", response_model=ResponseModel)
def create_sales_stockout(req: SalesStockoutCreate, db: Session = Depends(get_db)):
    code = _gen_code("CK", db, SalesStockout)
    so = SalesStockout(code=code, order_id=req.order_id, customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(so)
    db.flush()
    for item in req.items:
        soi = SalesStockoutItem(stockout_id=so.id, product_id=item.product_id, quantity=item.quantity, price=item.price, amount=item.amount)
        db.add(soi)
    db.commit()
    db.refresh(so)
    return ResponseModel(data=SalesStockoutOut.model_validate(so))


# === 销售退货 ===
@router.get("/sales-returns", response_model=PaginatedResponse)
def list_sales_returns(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(SalesReturn)
    total = q.count()
    items = q.order_by(SalesReturn.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[SalesReturnOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("/sales-returns", response_model=ResponseModel)
def create_sales_return(req: SalesReturnCreate, db: Session = Depends(get_db)):
    code = _gen_code("ST", db, SalesReturn)
    ret = SalesReturn(code=code, stockout_id=req.stockout_id, customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=req.total_amount, remark=req.remark)
    db.add(ret)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=SalesReturnOut.model_validate(ret))


# === 销售统计/对账 ===
@router.get("/sales/customer-statement", response_model=ResponseModel)
def customer_statement(customer_id: int = Query(None), db: Session = Depends(get_db)):
    """客户对账（预留）"""
    return ResponseModel(data=[], message="功能开发中")


@router.get("/sales/statistics", response_model=ResponseModel)
def sales_statistics(db: Session = Depends(get_db)):
    """销售统计（预留）"""
    return ResponseModel(data={}, message="功能开发中")
