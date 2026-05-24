from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.purchase import (
    PurchaseOrder, PurchaseOrderItem,
    PurchaseStockin, PurchaseStockinItem,
    PurchaseReturn, PurchaseReturnItem
)
from models.supplier import Supplier
from models.inventory import Inventory
from models.warehouse import Warehouse
from models.employee import Employee
from schemas.purchase import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderOut, PurchaseOrderItemOut,
    PurchaseStockinCreate, PurchaseStockinOut, PurchaseStockinItemOut,
    PurchaseReturnCreate, PurchaseReturnOut, PurchaseReturnItemOut
)
from schemas.common import ResponseModel, PaginatedResponse, ReverseRequest
from services.inventory_service import InventoryService
from deps import require_purchases_module, require_owner_or_admin
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level

router = APIRouter(prefix="/api", tags=["采购"])


def _enrich_names(db, result):
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


# ========== 采购订单 ==========
@router.get("/purchase-orders", response_model=PaginatedResponse)
def list_purchase_orders(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None), supplier_id: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    keyword: str = Query(None),
    user: Employee = Depends(require_purchases_module),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseOrder)
    if status is not None:
        q = q.filter(PurchaseOrder.status == status)
    if supplier_id:
        q = q.filter(PurchaseOrder.supplier_id == supplier_id)
    if start_date:
        q = q.filter(PurchaseOrder.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseOrder.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(PurchaseOrder.code.contains(keyword))
    total = q.count()
    items = q.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for order in items:
        d = PurchaseOrderOut.model_validate(order).model_dump()
        if order.supplier_id:
            sup = db.query(Supplier).get(order.supplier_id)
            d['supplier_name'] = sup.name if sup else ''
        if order.warehouse_id:
            wh = db.query(Warehouse).get(order.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/purchase-orders", response_model=ResponseModel)
def create_purchase_order(req: PurchaseOrderCreate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    if not req.items or len(req.items) == 0:
        raise HTTPException(status_code=400, detail="订单商品不能为空")
    code = _gen_code("CG", db, PurchaseOrder)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    order = PurchaseOrder(code=code, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=total, remark=req.remark, operator_id=user.id)
    db.add(order)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        oi = PurchaseOrderItem(order_id=order.id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                               unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
        db.add(oi)
    db.commit()
    db.refresh(order)
    return ResponseModel(data=PurchaseOrderOut.model_validate(order))


@router.get("/purchase-orders/{order_id}", response_model=ResponseModel)
def get_purchase_order(order_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).all()
    result = PurchaseOrderOut.model_validate(order).model_dump()
    result["items"] = [PurchaseOrderItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.put("/purchase-orders/{order_id}", response_model=ResponseModel)
def update_purchase_order(order_id: int, req: PurchaseOrderUpdate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="已入库订单不能修改")
    data = req.model_dump(exclude_unset=True, exclude={"items"})
    for k, v in data.items():
        setattr(order, k, v)
    if req.items is not None:
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).delete()
        total = 0
        for item in req.items:
            amount = item.amount or (item.quantity * item.price)
            total += amount
            if getattr(item, 'unit_level', None):
                base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
            else:
                base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
            oi = PurchaseOrderItem(order_id=order_id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                                   unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
            db.add(oi)
        order.total_amount = total
    db.commit()
    db.refresh(order)
    return ResponseModel(data=PurchaseOrderOut.model_validate(order))


@router.delete("/purchase-orders/{order_id}", response_model=ResponseModel)
def delete_purchase_order(order_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="已入库订单不能作废")
    order.status = 3  # 已关闭/作废
    db.commit()
    return ResponseModel(message="订单已作废")


@router.post("/purchase-orders/{order_id}/confirm", response_model=ResponseModel)
def confirm_purchase_order(order_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    if order.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以确认")
    order.status = 1
    order.confirmed_at = datetime.now()
    order.auditor_id = user.id
    db.commit()
    db.refresh(order)
    return ResponseModel(message="订单已确认", data=PurchaseOrderOut.model_validate(order))


@router.post("/purchase-orders/{order_id}/stockin", response_model=ResponseModel)
def order_to_stockin(order_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    if order.status >= 2:
        raise HTTPException(status_code=400, detail="订单已入库或已关闭")
    code = _gen_code("RK", db, PurchaseStockin)
    stockin = PurchaseStockin(code=code, order_id=order_id, supplier_id=order.supplier_id, warehouse_id=order.warehouse_id, total_amount=order.total_amount)
    db.add(stockin)
    db.flush()
    items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).all()
    for item in items:
        remain = item.quantity - item.received_qty
        if remain > 0:
            ratio = remain / item.quantity if item.quantity else 1
            scaled_unit_qty = (item.unit_quantity or item.quantity) * ratio if item.unit_id else remain
            si = PurchaseStockinItem(stockin_id=stockin.id, product_id=item.product_id, quantity=remain, price=item.price, amount=remain * item.price,
                                     unit_id=item.unit_id, unit_quantity=scaled_unit_qty, unit_conv_rate=item.unit_conv_rate)
            db.add(si)
    order.status = 2
    db.commit()
    return ResponseModel(message="已生成入库单", data=PurchaseStockinOut.model_validate(stockin).model_dump())


@router.post("/purchase-orders/{order_id}/quick-confirm", response_model=ResponseModel)
def quick_confirm_purchase_order(order_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
    if order.status != 1:
        raise HTTPException(status_code=400, detail="只有已审核的订单才能确认到货")
    order_items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order_id).all()
    has_remaining = any(item.quantity - item.received_qty > 0 for item in order_items)
    if not has_remaining:
        raise HTTPException(status_code=400, detail="订单已全部入库")
    # 直接入库：移动加权平均成本更新库存
    for item in order_items:
        remain = item.quantity - item.received_qty
        if remain <= 0:
            continue
        item.received_qty = item.quantity
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == order.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if inv:
            total_cost = inv.quantity * inv.cost_price + remain * item.price
            inv.quantity += remain
            inv.cost_price = total_cost / inv.quantity
        else:
            inv = Inventory(warehouse_id=order.warehouse_id, product_id=item.product_id, quantity=remain, cost_price=item.price)
            db.add(inv)
    # 更新供应商应付
    supplier = db.query(Supplier).get(order.supplier_id)
    if supplier:
        supplier.payable_balance = (supplier.payable_balance or 0) + order.total_amount
    order.status = 2
    db.commit()
    return ResponseModel(message="到货确认成功，库存已更新")


# ========== 采购入库 ==========
@router.get("/purchase-stockins", response_model=PaginatedResponse)
def list_purchase_stockins(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    supplier_id: int = Query(None), status: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    user: Employee = Depends(require_purchases_module),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseStockin)
    if supplier_id:
        q = q.filter(PurchaseStockin.supplier_id == supplier_id)
    if status is not None:
        q = q.filter(PurchaseStockin.status == status)
    if start_date:
        q = q.filter(PurchaseStockin.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    total = q.count()
    items = q.order_by(PurchaseStockin.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for si in items:
        d = PurchaseStockinOut.model_validate(si).model_dump()
        if si.supplier_id:
            sup = db.query(Supplier).get(si.supplier_id)
            d['supplier_name'] = sup.name if sup else ''
        if si.warehouse_id:
            wh = db.query(Warehouse).get(si.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/purchase-stockins", response_model=ResponseModel)
def create_purchase_stockin(req: PurchaseStockinCreate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    code = _gen_code("RK", db, PurchaseStockin)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    si = PurchaseStockin(code=code, order_id=req.order_id, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=total, remark=req.remark)
    db.add(si)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        sii = PurchaseStockinItem(stockin_id=si.id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                                  unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
        db.add(sii)
    db.commit()
    db.refresh(si)
    return ResponseModel(data=PurchaseStockinOut.model_validate(si))


@router.get("/purchase-stockins/{stockin_id}", response_model=ResponseModel)
def get_purchase_stockin(stockin_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    si = db.query(PurchaseStockin).get(stockin_id)
    if not si:
        raise HTTPException(status_code=404, detail="入库单不存在")
    items = db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id == stockin_id).all()
    result = PurchaseStockinOut.model_validate(si).model_dump()
    result["items"] = [PurchaseStockinItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.put("/purchase-stockins/{stockin_id}", response_model=ResponseModel)
def update_purchase_stockin(stockin_id: int, req: PurchaseStockinCreate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    si = db.query(PurchaseStockin).get(stockin_id)
    if not si:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if si.status == 2:
        raise HTTPException(status_code=400, detail="已确认入库不能修改")
    data = req.model_dump(exclude={"items"})
    for k, v in data.items():
        setattr(si, k, v)
    if req.items:
        db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id == stockin_id).delete()
        total = 0
        for item in req.items:
            amount = item.amount or (item.quantity * item.price)
            total += amount
            if getattr(item, 'unit_level', None):
                base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
            else:
                base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
            sii = PurchaseStockinItem(stockin_id=stockin_id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                                      unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
            db.add(sii)
        si.total_amount = total
    db.commit()
    db.refresh(si)
    return ResponseModel(data=PurchaseStockinOut.model_validate(si))


@router.delete("/purchase-stockins/{stockin_id}", response_model=ResponseModel)
def delete_purchase_stockin(stockin_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    si = db.query(PurchaseStockin).get(stockin_id)
    if not si:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if si.status == 2:
        raise HTTPException(status_code=400, detail="已确认入库不能删除")
    db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id == stockin_id).delete()
    db.delete(si)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 入库确认 ==========
@router.post("/purchase-stockins/{stockin_id}/confirm", response_model=ResponseModel)
def confirm_stockin(stockin_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    si = db.query(PurchaseStockin).get(stockin_id)
    if not si:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if si.status == 2:
        raise HTTPException(status_code=400, detail="已确认过")
    items = db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id == stockin_id).all()
    for item in items:
        # 更新订单已收数量
        if si.order_id:
            order_item = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.order_id == si.order_id,
                PurchaseOrderItem.product_id == item.product_id
            ).first()
            if order_item:
                order_item.received_qty = (order_item.received_qty or 0) + item.quantity
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == si.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if inv:
            # 移动加权平均成本计算
            total_cost = inv.quantity * inv.cost_price + item.quantity * item.price
            inv.quantity += item.quantity
            inv.cost_price = total_cost / inv.quantity
        else:
            inv = Inventory(warehouse_id=si.warehouse_id, product_id=item.product_id, quantity=item.quantity, cost_price=item.price)
            db.add(inv)
    supplier = db.query(Supplier).get(si.supplier_id)
    if supplier:
        supplier.payable_balance = (supplier.payable_balance or 0) + si.total_amount
    si.status = 2
    si.confirmed_at = datetime.now()
    si.auditor_id = user.id
    db.commit()
    return ResponseModel(message="入库确认成功，库存已更新")


# ========== 采购退货 ==========
@router.get("/purchase-returns", response_model=PaginatedResponse)
def list_purchase_returns(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    user: Employee = Depends(require_purchases_module),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseReturn)
    total = q.count()
    items = q.order_by(PurchaseReturn.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for ret in items:
        d = PurchaseReturnOut.model_validate(ret).model_dump()
        if ret.supplier_id:
            sup = db.query(Supplier).get(ret.supplier_id)
            d['supplier_name'] = sup.name if sup else ''
        if ret.warehouse_id:
            wh = db.query(Warehouse).get(ret.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result.append(d)
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/purchase-returns", response_model=ResponseModel)
def create_purchase_return(req: PurchaseReturnCreate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    code = _gen_code("TH", db, PurchaseReturn)
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    ret = PurchaseReturn(code=code, stockin_id=req.stockin_id, supplier_id=req.supplier_id, warehouse_id=req.warehouse_id, total_amount=total, remark=req.remark)
    db.add(ret)
    db.flush()
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = PurchaseReturnItem(return_id=ret.id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                                unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
        db.add(ri)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=PurchaseReturnOut.model_validate(ret))


@router.put("/purchase-returns/{return_id}", response_model=ResponseModel)
def update_purchase_return(return_id: int, req: PurchaseReturnCreate, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以修改")
    if req.supplier_id:
        supplier = db.query(Supplier).get(req.supplier_id)
        if not supplier:
            raise HTTPException(status_code=400, detail="供应商不存在")
    total = sum(item.amount or (item.quantity * item.price) for item in req.items)
    db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id == return_id).delete()
    ret.supplier_id = req.supplier_id
    ret.warehouse_id = req.warehouse_id
    ret.total_amount = total
    ret.remark = req.remark
    for item in req.items:
        amount = item.amount or (item.quantity * item.price)
        if getattr(item, 'unit_level', None):
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = PurchaseReturnItem(return_id=ret.id, product_id=item.product_id, quantity=base_qty, price=item.price, amount=amount,
                                unit_id=item.unit_id, unit_quantity=item.unit_quantity or item.quantity, unit_conv_rate=conv_rate)
        db.add(ri)
    db.commit()
    db.refresh(ret)
    return ResponseModel(data=PurchaseReturnOut.model_validate(ret))


@router.get("/purchase-returns/{return_id}", response_model=ResponseModel)
def get_purchase_return(return_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    items = db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id == return_id).all()
    result = PurchaseReturnOut.model_validate(ret).model_dump()
    result["items"] = [PurchaseReturnItemOut.model_validate(i).model_dump() for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


@router.post("/purchase-returns/{return_id}/confirm", response_model=ResponseModel)
def confirm_purchase_return(return_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 0:
        raise HTTPException(status_code=400, detail="只有草稿状态可以审核")
    ret.status = 1
    ret.confirmed_at = datetime.now()
    ret.auditor_id = user.id
    db.commit()
    return ResponseModel(message="退货订单已审核")


@router.post("/purchase-returns/{return_id}/fulfill", response_model=ResponseModel)
def fulfill_purchase_return(return_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status != 1:
        raise HTTPException(status_code=400, detail="只有已审核的退货单才能确认退货")
    items = db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id == return_id).all()
    for item in items:
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == ret.warehouse_id,
            Inventory.product_id == item.product_id
        ).first()
        if inv:
            if inv.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"商品{item.product_id}库存不足，当前{inv.quantity}，退货{item.quantity}")
            inv.quantity -= item.quantity
    supplier = db.query(Supplier).get(ret.supplier_id)
    if supplier:
        supplier.payable_balance = (supplier.payable_balance or 0) - ret.total_amount
    ret.status = 2
    db.commit()
    return ResponseModel(message="退货确认成功，库存已更新")


@router.delete("/purchase-returns/{return_id}", response_model=ResponseModel)
def delete_purchase_return(return_id: int, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status not in (0, 3):
        raise HTTPException(status_code=400, detail="只有草稿或已冲红状态可以删除")
    db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id == return_id).delete()
    db.delete(ret)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 供应商对账 ==========
@router.get("/purchases/supplier-statement", response_model=ResponseModel)
def supplier_statement(
    supplier_id: int = Query(...),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_purchases_module),
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    stockins_q = db.query(PurchaseStockin).filter(PurchaseStockin.supplier_id == supplier_id, PurchaseStockin.status == 2)
    returns_q = db.query(PurchaseReturn).filter(PurchaseReturn.supplier_id == supplier_id, PurchaseReturn.status == 2)

    if start_date:
        stockins_q = stockins_q.filter(PurchaseStockin.created_at >= start_date)
        returns_q = returns_q.filter(PurchaseReturn.created_at >= start_date)
    if end_date:
        stockins_q = stockins_q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        returns_q = returns_q.filter(PurchaseReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    stockins = stockins_q.all()
    returns = returns_q.all()

    total_in = sum(s.total_amount for s in stockins)
    total_return = sum(r.total_amount for r in returns)

    return ResponseModel(data={
        "supplier_name": supplier.name,
        "payable_balance": supplier.payable_balance,
        "total_in": total_in,
        "total_return": total_return,
        "net_amount": total_in - total_return,
        "stockins": [{"code": s.code, "amount": s.total_amount, "date": str(s.created_at)} for s in stockins],
        "returns": [{"code": r.code, "amount": r.total_amount, "date": str(r.created_at)} for r in returns],
    })


# ========== 采购统计 ==========
@router.get("/purchases/statistics", response_model=ResponseModel)
def purchase_statistics(
    group_by: str = Query("supplier", description="supplier/product/date"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_purchases_module),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseStockin).filter(PurchaseStockin.status == 2)
    if start_date:
        q = q.filter(PurchaseStockin.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    stockins = q.all()

    if group_by == "supplier":
        stats = {}
        for s in stockins:
            sup = db.query(Supplier).get(s.supplier_id)
            name = sup.name if sup else f"供应商{s.supplier_id}"
            if name not in stats:
                stats[name] = {"count": 0, "amount": 0}
            stats[name]["count"] += 1
            stats[name]["amount"] += s.total_amount
        return ResponseModel(data=stats)

    elif group_by == "date":
        stats = {}
        for s in stockins:
            date_key = str(s.created_at)[:10]
            if date_key not in stats:
                stats[date_key] = {"count": 0, "amount": 0}
            stats[date_key]["count"] += 1
            stats[date_key]["amount"] += s.total_amount
        return ResponseModel(data=stats)


# ========== 冲红 ==========

@router.post("/purchase-orders/{order_id}/reverse", response_model=ResponseModel)
def reverse_purchase_order(order_id: int, req: ReverseRequest, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="采购订单不存在")
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


@router.post("/purchase-stockins/{stockin_id}/reverse", response_model=ResponseModel)
def reverse_purchase_stockin(stockin_id: int, req: ReverseRequest, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    si = db.query(PurchaseStockin).get(stockin_id)
    if not si:
        raise HTTPException(status_code=404, detail="入库单不存在")
    if si.status == 0:
        raise HTTPException(status_code=400, detail="草稿状态不能冲红")
    if si.status == 3:
        raise HTTPException(status_code=400, detail="已冲红单据不能重复冲红")
    # 回滚库存（入库单确认时增加了库存，冲红需扣回）
    items = db.query(PurchaseStockinItem).filter(PurchaseStockinItem.stockin_id == stockin_id).all()
    for item in items:
        InventoryService.deduct(db, item.product_id, si.warehouse_id, item.quantity)
    # 回滚供应商应付
    supplier = db.query(Supplier).get(si.supplier_id)
    if supplier and si.total_amount:
        supplier.payable_balance = max(0, (supplier.payable_balance or 0) - si.total_amount)
    si.status = 3
    si.reverse_reason = req.reason
    si.reversed_by = user.id
    si.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功，库存已回滚")


@router.post("/purchase-returns/{return_id}/reverse", response_model=ResponseModel)
def reverse_purchase_return(return_id: int, req: ReverseRequest, user: Employee = Depends(require_purchases_module), db: Session = Depends(get_db)):
    ret = db.query(PurchaseReturn).get(return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="退货单不存在")
    if ret.status == 0:
        raise HTTPException(status_code=400, detail="草稿状态不能冲红")
    if ret.status == 3:
        raise HTTPException(status_code=400, detail="已冲红单据不能重复冲红")
    # status=2（已确认退货）需要回滚库存和财务
    if ret.status == 2:
        items = db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id == return_id).all()
        for item in items:
            InventoryService.restore(db, item.product_id, ret.warehouse_id, item.quantity)
        supplier = db.query(Supplier).get(ret.supplier_id)
        if supplier and ret.total_amount:
            supplier.payable_balance = (supplier.payable_balance or 0) + ret.total_amount
    ret.status = 3
    ret.reverse_reason = req.reason
    ret.reversed_by = user.id
    ret.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功")

    return ResponseModel(data={})
