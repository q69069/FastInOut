"""采购入库单（PurchaseReceipt）— Phase A Day 3-4

状态流转：pending → confirmed / reversed
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.purchase_receipt import PurchaseReceipt, PurchaseReceiptItem
from models.purchase import PurchaseOrder, PurchaseOrderItem
from models.supplier import Supplier
from models.product import Product
from models.warehouse import Warehouse
from models.employee import Employee
from schemas.purchase_receipt import (
    PurchaseReceiptCreate, PurchaseReceiptOut, PurchaseReceiptItemOut
)
from schemas.common import ResponseModel, PaginatedResponse, ReverseRequest
from services.inventory_service import InventoryService
from utils.status import PurchaseReceiptStatus
from utils.unit_convert import resolve_unit_conversion, resolve_by_unit_level
from deps import get_current_user

router = APIRouter(prefix="/api", tags=["采购入库单"])


def _enrich_names(db, result):
    if result.get("auditor_id"):
        emp = db.query(Employee).get(result["auditor_id"])
        if emp:
            result["auditor_name"] = emp.name
    if result.get("received_by"):
        emp = db.query(Employee).get(result["received_by"])
        if emp:
            result["received_by_name"] = emp.name

def _gen_receipt_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"RK{today}"
    count = db.query(func.count(PurchaseReceipt.id)).filter(
        PurchaseReceipt.receipt_no.like(f"{prefix}%")
    ).scalar()
    return f"{prefix}-{count + 1:03d}"


# ========== 创建采购入库单 ==========
@router.post("/purchase-receipts", response_model=ResponseModel)
def create_purchase_receipt(
    req: PurchaseReceiptCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    # 校验采购订单存在（如果提供了purchase_order_id）
    order = None
    if req.purchase_order_id:
        order = db.query(PurchaseOrder).get(req.purchase_order_id)
        if not order:
            raise HTTPException(400, "采购订单不存在")

    # 校验供应商
    supplier = db.query(Supplier).get(req.supplier_id)
    if not supplier:
        raise HTTPException(400, "供应商不存在")

    receipt_no = _gen_receipt_no(db)

    # 计算总金额
    total = req.total_amount
    if not total and req.items:
        total = sum(item.amount or (item.quantity * item.unit_price) for item in req.items)

    receipt = PurchaseReceipt(
        receipt_no=receipt_no,
        purchase_order_id=req.purchase_order_id,
        supplier_id=req.supplier_id,
        warehouse_id=req.warehouse_id,
        purchaser_id=req.purchaser_id,
        trade_date=req.trade_date,
        total_amount=total,
        status=PurchaseReceiptStatus.PENDING,
        received_by=user.id,
        remark=req.remark
    )
    db.add(receipt)
    db.flush()

    # 创建明细
    for item in req.items:
        if not item.product_id:
            continue
        amount = item.amount or (item.quantity * item.unit_price)
        if item.unit_level:
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = PurchaseReceiptItem(
            receipt_id=receipt.id,
            product_id=item.product_id,
            order_item_id=item.order_item_id,
            quantity=base_qty,
            unit_id=item.unit_id,
            unit_level=item.unit_level or 'small',
            unit_quantity=item.unit_quantity or item.quantity,
            unit_conv_rate=conv_rate,
            unit_price=item.unit_price,
            amount=amount
        )
        db.add(ri)

    db.commit()
    db.refresh(receipt)
    return ResponseModel(data=PurchaseReceiptOut.model_validate(receipt))


@router.put("/purchase-receipts/{receipt_id}", response_model=ResponseModel)
def update_purchase_receipt(
    receipt_id: int,
    req: PurchaseReceiptCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    receipt = db.query(PurchaseReceipt).get(receipt_id)
    if not receipt:
        raise HTTPException(404, "入库单不存在")
    if receipt.status != PurchaseReceiptStatus.PENDING:
        raise HTTPException(400, "只有待处理状态可以编辑")

    supplier = db.query(Supplier).get(req.supplier_id)
    if not supplier:
        raise HTTPException(400, "供应商不存在")

    total = req.total_amount
    if not total and req.items:
        total = sum(item.amount or (item.quantity * item.unit_price) for item in req.items)

    receipt.supplier_id = req.supplier_id
    receipt.warehouse_id = req.warehouse_id
    receipt.purchaser_id = req.purchaser_id
    receipt.trade_date = req.trade_date
    receipt.total_amount = total
    receipt.remark = req.remark

    # 删除旧明细，重建
    db.query(PurchaseReceiptItem).filter(PurchaseReceiptItem.receipt_id == receipt_id).delete()
    for item in req.items:
        if not item.product_id:
            continue
        amount = item.amount or (item.quantity * item.unit_price)
        if item.unit_level:
            base_qty, conv_rate = resolve_by_unit_level(item.product_id, item.unit_level, item.unit_quantity or item.quantity, item.unit_conv_rate, db)
        else:
            base_qty, conv_rate = resolve_unit_conversion(item.product_id, item.unit_id, item.unit_quantity or item.quantity, db)
        ri = PurchaseReceiptItem(
            receipt_id=receipt_id,
            product_id=item.product_id,
            order_item_id=item.order_item_id,
            quantity=base_qty,
            unit_id=item.unit_id,
            unit_level=item.unit_level or 'small',
            unit_quantity=item.unit_quantity or item.quantity,
            unit_conv_rate=conv_rate,
            unit_price=item.unit_price,
            amount=amount
        )
        db.add(ri)

    db.commit()
    db.refresh(receipt)
    result = PurchaseReceiptOut.model_validate(receipt).model_dump()
    _enrich_names(db, result)
    return ResponseModel(data=result)


# ========== 采购入库单列表 ==========
@router.get("/purchase-receipts", response_model=PaginatedResponse)
def list_purchase_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    supplier_id: int = Query(None),
    purchase_order_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(PurchaseReceipt)

    if status:
        q = q.filter(PurchaseReceipt.status == status)
    if supplier_id:
        q = q.filter(PurchaseReceipt.supplier_id == supplier_id)
    if purchase_order_id:
        q = q.filter(PurchaseReceipt.purchase_order_id == purchase_order_id)
    if start_date:
        q = q.filter(PurchaseReceipt.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseReceipt.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if keyword:
        q = q.filter(PurchaseReceipt.receipt_no.contains(keyword))

    total = q.count()
    items = q.order_by(PurchaseReceipt.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result_list = []
    for i in items:
        d = PurchaseReceiptOut.model_validate(i).model_dump()
        _enrich_names(db, d)
        if i.supplier_id:
            sup = db.query(Supplier).get(i.supplier_id)
            d['supplier_name'] = sup.name if sup else ''
        if i.warehouse_id:
            wh = db.query(Warehouse).get(i.warehouse_id)
            d['warehouse_name'] = wh.name if wh else ''
        result_list.append(d)
    return PaginatedResponse(
        data=result_list,
        total=total, page=page, page_size=page_size
    )


# ========== 采购入库单详情 ==========
@router.get("/purchase-receipts/{receipt_id}", response_model=ResponseModel)
def get_purchase_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(PurchaseReceipt).get(receipt_id)
    if not receipt:
        raise HTTPException(404, "入库单不存在")

    items = db.query(PurchaseReceiptItem).filter(
        PurchaseReceiptItem.receipt_id == receipt_id
    ).all()

    result = PurchaseReceiptOut.model_validate(receipt).model_dump()
    result["items"] = [PurchaseReceiptItemOut.model_validate(i) for i in items]
    _enrich_names(db, result)
    return ResponseModel(data=result)


# ========== 确认入库 ==========
@router.post("/purchase-receipts/{receipt_id}/confirm", response_model=ResponseModel)
def confirm_purchase_receipt(
    receipt_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    receipt = db.query(PurchaseReceipt).get(receipt_id)
    if not receipt:
        raise HTTPException(404, "入库单不存在")
    if receipt.status != PurchaseReceiptStatus.PENDING:
        raise HTTPException(400, f"当前状态 {receipt.status} 不允许确认")

    items = db.query(PurchaseReceiptItem).filter(
        PurchaseReceiptItem.receipt_id == receipt_id
    ).all()

    # 增加库存
    for item in items:
        # 先查询现有库存
        from models.inventory import Inventory
        inv = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.warehouse_id == receipt.warehouse_id
        ).first()
        # unit_price 是选定单位的单价，需要换算为基本单位单价
        conv = item.unit_conv_rate if item.unit_conv_rate and item.unit_conv_rate > 0 else 1.0
        base_unit_price = item.unit_price / conv
        if inv:
            # 移动加权平均成本
            total_cost = inv.quantity * (inv.cost_price or 0) + item.quantity * base_unit_price
            inv.quantity += item.quantity
            inv.cost_price = total_cost / inv.quantity if inv.quantity > 0 else 0
        else:
            inv = Inventory(
                warehouse_id=receipt.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
                cost_price=base_unit_price
            )
            db.add(inv)

        # 更新采购订单明细的已入库数量
        if item.order_item_id:
            order_item = db.query(PurchaseOrderItem).get(item.order_item_id)
            if order_item:
                order_item.received_qty = (order_item.received_qty or 0) + item.quantity

    # 更新供应商应付
    supplier = db.query(Supplier).get(receipt.supplier_id)
    if supplier and receipt.total_amount:
        supplier.payable_balance = (supplier.payable_balance or 0) + receipt.total_amount

    receipt.status = PurchaseReceiptStatus.CONFIRMED
    receipt.confirmed_at = datetime.now()
    receipt.auditor_id = user.id
    db.commit()
    return ResponseModel(message="入库确认成功，库存已更新")


# ========== 冲红 ==========
@router.post("/purchase-receipts/{receipt_id}/reverse", response_model=ResponseModel)
def reverse_purchase_receipt(
    receipt_id: int,
    req: ReverseRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    receipt = db.query(PurchaseReceipt).get(receipt_id)
    if not receipt:
        raise HTTPException(404, "入库单不存在")
    if receipt.status != PurchaseReceiptStatus.CONFIRMED:
        raise HTTPException(400, f"当前状态 {receipt.status} 不允许冲红")

    # 只有管理员可以冲红
    from utils.role_check import require_role
    require_role(user, db, "admin", message="只有管理员可以冲红")

    items = db.query(PurchaseReceiptItem).filter(
        PurchaseReceiptItem.receipt_id == receipt_id
    ).all()

    # 回滚库存（入库时增加了库存，冲红需扣回）
    for item in items:
        InventoryService.deduct(db, item.product_id, receipt.warehouse_id, item.quantity)
        # 回滚采购订单已入库数量
        if item.order_item_id:
            order_item = db.query(PurchaseOrderItem).get(item.order_item_id)
            if order_item:
                order_item.received_qty = max(0, (order_item.received_qty or 0) - item.quantity)

    # 回滚供应商应付
    supplier = db.query(Supplier).get(receipt.supplier_id)
    if supplier and receipt.total_amount:
        supplier.payable_balance = max(0, (supplier.payable_balance or 0) - receipt.total_amount)

    receipt.status = PurchaseReceiptStatus.REVERSED
    receipt.reverse_reason = req.reason
    receipt.reversed_by = user.id
    receipt.reversed_at = datetime.now()
    db.commit()
    return ResponseModel(message="冲红成功，库存已回滚")
