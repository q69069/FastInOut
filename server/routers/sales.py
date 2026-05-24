from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.sales import (
    SalesOrder, SalesOrderItem,
    SalesStockout, SalesStockoutItem,
    SalesReturn, SalesReturnItem
)
from models.customer import Customer
from models.product import Product
from models.warehouse import Warehouse
from models.inventory import Inventory
from models.employee import Employee
from schemas.sales import (
    SalesOrderCreate, SalesOrderUpdate, SalesOrderOut, SalesOrderItemOut,
    SalesStockoutCreate, SalesStockoutOut, SalesStockoutItemOut,
    SalesReturnCreate, SalesReturnOut, SalesReturnItemOut
)
from schemas.common import ResponseModel, PaginatedResponse, ReverseRequest
from services.inventory_service import InventoryService
from utils.data_filter import DataFilter
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level
from deps import require_sales_module
from datetime import datetime

router = APIRouter(prefix="/api", tags=["销售"])

def _enrich_names(db, result):
    """给返回结果添加审核人/操作人姓名"""
    if result.get("auditor_id"):
        emp = db.query(Employee).get(result["auditor_id"])
        if emp:
            result["auditor_name"] = emp.name
    if result.get("operator_id"):
        emp = db.query(Employee).get(result["operator_id"])
        if emp:
            result["operator_name"] = emp.name


def _gen_code(prefix: str, db: Session, model, max_retries: int = 5) -> str:
    today = datetime.now().strftime("%Y%m%d")
    pfx = f"{prefix}{today}"
    for attempt in range(max_retries):
        count = db.query(func.count(model.id)).filter(
            model.code.like(f"{pfx}%")
        ).scalar()
        code = f"{pfx}-{count + 1:03d}"
        existing = db.query(model).filter(model.code == code).first()
        if not existing:
            return code
    import time
    return f"{pfx}-{int(time.time() % 10000):04d}"


def _get_product_price(product: Product, customer: Customer) -> float:
    if not product:
        return 0
    if customer and customer.level == "VIP":
        return product.member_price or product.retail_price
    elif customer and customer.level == "会员":
        return product.member_price or product.retail_price
    return product.retail_price


# ========== 销售订单 ==========
@router.get("/sales-orders", response_model=PaginatedResponse)
def list_sales_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None), customer_id: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    keyword: str = Query(None),
    user: Employee = Depends(require_sales_module),
    db: Session = Depends(get_db)
):
    q = db.query(SalesOrder)
    # 应用数据权限过滤
    q = DataFilter.apply_scope(q, SalesOrder, user, db, scope_field="route_id", module_key="sales")
    if status is not None:
        q = q.filter(SalesOrder.status == status)
    if customer_id:
        q = q.filter(SalesOrder.customer_id == customer_id)
    if start_date:
        q = q.filter(SalesOrder.created_at >= start_date)
    if end_date:
        q = q.filter(SalesOrder.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(SalesOrder.code.contains(keyword))
    total = q.count()
    items = q.order_by(SalesOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for order in items:
        d = SalesOrderOut.model_validate(order).model_dump()
        if order.customer_id:
            cust = db.query(Customer).get(order.customer_id)
            d['customer_name'] = cust.name if cust else ''
        if order.warehouse_id:
            wh = db.query(Warehouse).get(order.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/sales-orders", response_model=ResponseModel)
def create_sales_order(req: SalesOrderCreate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    if not req.items or len(req.items) == 0:
        raise HTTPException(status_code=400, detail="订单商品不能为空")
    code = _gen_code("XS", db, SalesOrder)
    customer = db.query(Customer).get(req.customer_id)
    total = 0
    order = SalesOrder(code=code, customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=0, remark=req.remark, operator_id=user.id)
    db.add(order)
    db.flush()
    for item in req.items:
        product = db.query(Product).get(item.product_id)
        price = item.price if item.price > 0 else _get_product_price(product, customer)
        amount = item.quantity * price
        total += amount
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        oi = SalesOrderItem(order_id=order.id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=price, amount=amount)
        db.add(oi)
    order.total_amount = total
    db.commit()
    db.refresh(order)
    return ResponseModel(data=SalesOrderOut.model_validate(order))


@router.get("/sales-orders/{order_id}", response_model=ResponseModel)
def get_sales_order(order_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    items = db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).all()
    result = SalesOrderOut.model_validate(order).model_dump()
    result["items"] = [SalesOrderItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.put("/sales-orders/{order_id}", response_model=ResponseModel)
def update_sales_order(order_id: int, req: SalesOrderUpdate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="已出库订单不能修改")
    data = req.model_dump(exclude_unset=True, exclude={"items"})
    for k, v in data.items():
        setattr(order, k, v)
    if req.items is not None:
        db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).delete()
        customer = db.query(Customer).get(order.customer_id)
        total = 0
        for item in req.items:
            product = db.query(Product).get(item.product_id)
            price = item.price if item.price > 0 else _get_product_price(product, customer)
            amount = item.quantity * price
            total += amount
            if getattr(item, 'unit_level', None):
                base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
            else:
                base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
            oi = SalesOrderItem(order_id=order_id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=price, amount=amount)
            db.add(oi)
        order.total_amount = total
    db.commit()
    db.refresh(order)
    return ResponseModel(data=SalesOrderOut.model_validate(order))


@router.delete("/sales-orders/{order_id}", response_model=ResponseModel)
def delete_sales_order(order_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="已出库订单不能作废")
    order.status = 3
    db.commit()
    return ResponseModel(message="订单已作废")


@router.post("/sales-orders/{order_id}/audit", response_model=ResponseModel)
def audit_sales_order(order_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以确认")
    order.status = 1
    order.confirmed_at = datetime.now()
    order.auditor_id = user.id
    order.audit_time = datetime.now()
    db.commit()
    db.refresh(order)
    return ResponseModel(message="订单已确认", data=SalesOrderOut.model_validate(order))


@router.post("/sales-orders/{order_id}/stockout", response_model=ResponseModel)
def order_to_stockout(order_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="订单已出库或已关闭")
    code = _gen_code("CK", db, SalesStockout)
    stockout = SalesStockout(code=code, order_id=order_id, customer_id=order.customer_id, warehouse_id=order.warehouse_id, total_amount=order.total_amount)
    db.add(stockout)
    db.flush()
    items = db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).all()
    for item in items:
        remain = item.quantity - item.delivered_qty
        if remain > 0:
            ratio = remain / item.quantity if item.quantity else 1
            scaled_unit_qty = (item.unit_quantity or item.quantity) * ratio if item.unit_id else remain
            soi = SalesStockoutItem(stockout_id=stockout.id, product_id=item.product_id, quantity=remain, price=item.price, amount=remain * item.price,
                                    unit_id=item.unit_id, unit_quantity=scaled_unit_qty, unit_conv_rate=item.unit_conv_rate)
            db.add(soi)
    order.status = 2
    db.commit()
    return ResponseModel(message="已生成出库单", data=SalesStockoutOut.model_validate(stockout).model_dump())


@router.post("/sales-orders/{order_id}/quick-confirm", response_model=ResponseModel)
def quick_confirm_sales_order(order_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="只有已审核的订单才能确认发货")
    order_items = db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order_id).all()
    has_remaining = any(item.quantity - item.delivered_qty > 0 for item in order_items)
    if not has_remaining:
        raise HTTPException(status_code=400, detail="订单已全部出库")
    # 先检查库存
    for item in order_items:
        remain = item.quantity - item.delivered_qty
        if remain <= 0:
            continue
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == order.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if not inv or inv.quantity < remain:
            raise HTTPException(status_code=400, detail=f"商品{item.product_id}库存不足，当前{inv.quantity if inv else 0}，需要{remain}")
    # 直接出库
    for item in order_items:
        remain = item.quantity - item.delivered_qty
        if remain <= 0:
            continue
        item.delivered_qty = item.quantity
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == order.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        inv.quantity -= remain
    # 更新客户应收
    customer = db.query(Customer).get(order.customer_id)
    if customer:
        customer.receivable_balance = (customer.receivable_balance or 0) + order.total_amount
    order.status = 2
    db.commit()
    return ResponseModel(message="发货确认成功，库存已更新")


# ========== 销售出库 ==========
@router.get("/sales-stockouts", response_model=PaginatedResponse)
def list_sales_stockouts(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None), status: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    user: Employee = Depends(require_sales_module),
    db: Session = Depends(get_db)
):
    q = db.query(SalesStockout)
    if customer_id:
        q = q.filter(SalesStockout.customer_id == customer_id)
    if status is not None:
        q = q.filter(SalesStockout.status == status)
    if start_date:
        q = q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(SalesStockout.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for so in items:
        d = SalesStockoutOut.model_validate(so).model_dump()
        if so.customer_id:
            cust = db.query(Customer).get(so.customer_id)
            d['customer_name'] = cust.name if cust else ''
        if so.warehouse_id:
            wh = db.query(Warehouse).get(so.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/sales-stockouts", response_model=ResponseModel)
def create_sales_stockout(req: SalesStockoutCreate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    code = _gen_code("CK", db, SalesStockout)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    so = SalesStockout(code=code, order_id=req.order_id, customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=total, remark=req.remark)
    db.add(so)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        soi = SalesStockoutItem(stockout_id=so.id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=item.price, amount=amount)
        db.add(soi)
    db.commit()
    db.refresh(so)
    return ResponseModel(data=SalesStockoutOut.model_validate(so))


@router.get("/sales-stockouts/{stockout_id}", response_model=ResponseModel)
def get_sales_stockout(stockout_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    so = db.query(SalesStockout).get(stockout_id)
    if not so:
        raise HTTPException(status_code=404, detail="出库单不存在")
    items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == stockout_id).all()
    result = SalesStockoutOut.model_validate(so).model_dump()
    result["items"] = [SalesStockoutItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.put("/sales-stockouts/{stockout_id}", response_model=ResponseModel)
def update_sales_stockout(stockout_id: int, req: SalesStockoutCreate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    so = db.query(SalesStockout).get(stockout_id)
    if not so:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if so.status == 2:
        raise HTTPException(status_code=400, detail="已确认出库不能修改")
    data = req.model_dump(exclude={"items"})
    for k, v in data.items():
        setattr(so, k, v)
    if req.items:
        db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == stockout_id).delete()
        total = 0
        for item in req.items:
            amount = item.amount or (item.quantity * item.price)
            total += amount
            if getattr(item, 'unit_level', None):
                base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
            else:
                base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
            soi = SalesStockoutItem(stockout_id=stockout_id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=item.price, amount=amount)
            db.add(soi)
        so.total_amount = total
    db.commit()
    db.refresh(so)
    return ResponseModel(data=SalesStockoutOut.model_validate(so))


@router.delete("/sales-stockouts/{stockout_id}", response_model=ResponseModel)
def delete_sales_stockout(stockout_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    so = db.query(SalesStockout).get(stockout_id)
    if not so:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if so.status == 2:
        raise HTTPException(status_code=400, detail="已确认出库不能删除")
    db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == stockout_id).delete()
    db.delete(so)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 出库确认 ==========
@router.post("/sales-stockouts/{stockout_id}/confirm", response_model=ResponseModel)
def confirm_stockout(stockout_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    so = db.query(SalesStockout).get(stockout_id)
    if not so:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if so.status == 2:
        raise HTTPException(status_code=400, detail="已确认过")
    items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == stockout_id).all()
    for item in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == so.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if not inv or inv.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品{item.product_id}库存不足，当前库存{inv.quantity if inv else 0}，需要{item.quantity}")
    for item in items:
        # 更新订单已出库数量
        if so.order_id:
            order_item = db.query(SalesOrderItem).filter(
                SalesOrderItem.order_id == so.order_id,
                SalesOrderItem.product_id == item.product_id
            ).first()
            if order_item:
                order_item.delivered_qty = (order_item.delivered_qty or 0) + item.quantity
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == so.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        inv.quantity -= item.quantity
    customer = db.query(Customer).get(so.customer_id)
    if customer:
        customer.receivable_balance = (customer.receivable_balance or 0) + so.total_amount
    so.status = 2
    so.confirmed_at = datetime.now()
    so.auditor_id = user.id
    db.commit()
    return ResponseModel(message="出库确认成功，库存已更新")


# ========== 销售退货 ==========
@router.get("/sales-returns", response_model=PaginatedResponse)
def list_sales_returns(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    user: Employee = Depends(require_sales_module),
    db: Session = Depends(get_db)
):
    q = db.query(SalesReturn).filter(SalesReturn.doc_type == "return_order")
    total = q.count()
    items = q.order_by(SalesReturn.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for ret in items:
        d = SalesReturnOut.model_validate(ret).model_dump()
        if ret.customer_id:
            cust = db.query(Customer).get(ret.customer_id)
            d['customer_name'] = cust.name if cust else ''
        if ret.warehouse_id:
            wh = db.query(Warehouse).get(ret.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/sales-returns", response_model=ResponseModel)
def create_sales_return(req: SalesReturnCreate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    code = _gen_code("XT", db, SalesReturn)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    ret = SalesReturn(code=code, stockout_id=req.stockout_id, doc_type="return_order", customer_id=req.customer_id, warehouse_id=req.warehouse_id, total_amount=total, remark=req.remark)
    db.add(ret)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = SalesReturnItem(return_id=ret.id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=item.price, amount=amount)
        db.add(ri)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=SalesReturnOut.model_validate(ret))


@router.put("/sales-returns/{return_id}", response_model=ResponseModel)
def update_sales_return(return_id: int, req: SalesReturnCreate, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以修改")
    if req.customer_id:
        customer = db.query(Customer).get(req.customer_id)
        if not customer:
            raise HTTPException(status_code=400, detail="客户不存在")
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).delete()
    ret.customer_id = req.customer_id
    ret.warehouse_id = req.warehouse_id
    ret.total_amount = total
    ret.remark = req.remark
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = SalesReturnItem(return_id=ret.id, product_id=item.product_id, quantity=base_qty, unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate, price=item.price, amount=amount)
        db.add(ri)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=SalesReturnOut.model_validate(ret))


@router.get("/sales-returns/{return_id}", response_model=ResponseModel)
def get_sales_return(return_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()
    result = SalesReturnOut.model_validate(ret).model_dump()
    result["items"] = [SalesReturnItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.post("/sales-returns/{return_id}/confirm", response_model=ResponseModel)
def confirm_sales_return(return_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以审核")
    ret.status = 1
    ret.confirmed_at = datetime.now()
    ret.auditor_id = user.id
    db.commit()
    return ResponseModel(message="退货订单已审核")


@router.post("/sales-returns/{return_id}/fulfill", response_model=ResponseModel)
def fulfill_sales_return(return_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 1:
        raise HTTPException(status_code=400, detail="只有已审核的退货单才能确认退货")
    items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()
    for item in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == ret.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if inv:
            total_cost = inv.quantity * inv.cost_price + item.quantity * item.price
            inv.quantity += item.quantity
            inv.cost_price = total_cost / inv.quantity
        else:
            inv = Inventory(warehouse_id=ret.warehouse_id, product_id=item.product_id, quantity=item.quantity, cost_price=item.price)
            db.add(inv)
    customer = db.query(Customer).get(ret.customer_id)
    if customer:
        customer.receivable_balance = (customer.receivable_balance or 0) - ret.total_amount
    ret.status = 2
    db.commit()
    return ResponseModel(message="退货确认成功，库存已更新")


@router.delete("/sales-returns/{return_id}", response_model=ResponseModel)
def delete_sales_return(return_id: int, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status not in (0, 3):
        raise HTTPException(status_code=400, detail="只有草稿或已冲红状态可以删除")
    db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).delete()
    db.delete(ret)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 客户对账 ==========
@router.get("/sales/customer-statement", response_model=ResponseModel)
def customer_statement(
    customer_id: int = Query(...),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_sales_module),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    stockouts_q = db.query(SalesStockout).filter(SalesStockout.customer_id == customer_id, SalesStockout.status == 2)
    returns_q = db.query(SalesReturn).filter(SalesReturn.customer_id == customer_id, SalesReturn.status == 2)

    if start_date:
        stockouts_q = stockouts_q.filter(SalesStockout.created_at >= start_date)
        returns_q = returns_q.filter(SalesReturn.created_at >= start_date)
    if end_date:
        stockouts_q = stockouts_q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        returns_q = returns_q.filter(SalesReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    stockouts = stockouts_q.all()
    returns = returns_q.all()

    total_out = sum(s.total_amount for s in stockouts)
    total_return = sum(r.total_amount for r in returns)

    return ResponseModel(data={
        "customer_name": customer.name,
        "receivable_balance": customer.receivable_balance,
        "total_out": total_out,
        "total_return": total_return,
        "net_amount": total_out - total_return,
        "stockouts": [{"code": s.code, "amount": s.total_amount, "date": str(s.created_at)} for s in stockouts],
        "returns": [{"code": r.code, "amount": r.total_amount, "date": str(r.created_at)} for r in returns],
    })


# ========== 销售统计 ==========
@router.get("/sales/statistics", response_model=ResponseModel)
def sales_statistics(
    group_by: str = Query("customer", description="customer/product/employee/date"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_sales_module),
    db: Session = Depends(get_db)
):
    q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date:
        q = q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    stockouts = q.all()

    if group_by == "customer":
        stats = {}
        for s in stockouts:
            cust = db.query(Customer).get(s.customer_id)
            name = cust.name if cust else f"客户{s.customer_id}"
            if name not in stats:
                stats[name] = {"count": 0, "amount": 0}
            stats[name]["count"] += 1
            stats[name]["amount"] += s.total_amount
        return ResponseModel(data=stats)

    elif group_by == "date":
        stats = {}
        for s in stockouts:
            date_key = str(s.created_at)[:10]
            if date_key not in stats:
                stats[date_key] = {"count": 0, "amount": 0}
            stats[date_key]["count"] += 1
            stats[date_key]["amount"] += s.total_amount
        return ResponseModel(data=stats)

    return ResponseModel(data={})


# ========== 冲红 ==========

@router.post("/sales-orders/{order_id}/reverse", response_model=ResponseModel)
def reverse_sales_order(order_id: int, req: ReverseRequest, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    order = db.query(SalesOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="销售订单不存在")
    if order.status == 0:
        raise HTTPException(status_code=400, detail="草稿状态不能冲红")
    if order.status == 3:
        raise HTTPException(status_code=400, detail="已冲红单据不能重复冲红")
    order.status = 3
    order.reverse_reason = req.reason
    order.reversed_by = user.id
    order.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功")


@router.post("/sales-stockouts/{stockout_id}/reverse", response_model=ResponseModel)
def reverse_sales_stockout(stockout_id: int, req: ReverseRequest, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    so = db.query(SalesStockout).get(stockout_id)
    if not so:
        raise HTTPException(status_code=404, detail="出库单不存在")
    if so.status == 0:
        raise HTTPException(status_code=400, detail="草稿状态不能冲红")
    if so.status == 3:
        raise HTTPException(status_code=400, detail="已冲红单据不能重复冲红")
    # 回滚库存
    items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == stockout_id).all()
    for item in items:
        InventoryService.restore(db, item.product_id, so.warehouse_id, item.quantity)
    # 回滚客户应收（冲红撤销出库，应收应减少）
    customer = db.query(Customer).get(so.customer_id)
    if customer and so.total_amount:
        customer.receivable_balance = (customer.receivable_balance or 0) - so.total_amount
    so.status = 3
    so.reverse_reason = req.reason
    so.reversed_by = user.id
    so.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功，库存已回滚")


@router.post("/sales-returns/{return_id}/reverse", response_model=ResponseModel)
def reverse_sales_return(return_id: int, req: ReverseRequest, user: Employee = Depends(require_sales_module), db: Session = Depends(get_db)):
    ret = db.query(SalesReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status == 0:
        raise HTTPException(status_code=400, detail="草稿状态不能冲红")
    if ret.status == 3:
        raise HTTPException(status_code=400, detail="已冲红单据不能重复冲红")
    # status=2（已确认退货）需要回滚库存和财务
    if ret.status == 2:
        items = db.query(SalesReturnItem).filter(SalesReturnItem.return_id == return_id).all()
        for item in items:
            InventoryService.deduct(db, item.product_id, ret.warehouse_id, item.quantity)
        customer = db.query(Customer).get(ret.customer_id)
        if customer and ret.total_amount:
            customer.receivable_balance = (customer.receivable_balance or 0) + ret.total_amount
    ret.status = 3
    ret.reverse_reason = req.reason
    ret.reversed_by = user.id
    ret.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功")
