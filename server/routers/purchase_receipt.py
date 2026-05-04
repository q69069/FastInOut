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
from models.employee import Employee
from schemas.purchase_receipt import (
    PurchaseReceiptCreate, PurchaseReceiptOut, PurchaseReceiptItemOut
)
from schemas.common import ResponseModel, PaginatedResponse
from services.inventory_service import InventoryService
from utils.status import PurchaseReceiptStatus

router = APIRouter(prefix="/api", tags=["采购入库单"])


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


def _gen_receipt_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(PurchaseReceipt).filter(
        func.strftime("%Y%m%d", PurchaseReceipt.created_at) == today
    ).count()
    return f"RK{today}-{count + 1:03d}"


# ========== 创建采购入库单 ==========
@router.post("/purchase-receipts", response_model=ResponseModel)
def create_purchase_receipt(
    req: PurchaseReceiptCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    # 校验采购订单存在
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
        total_amount=total,
        status=PurchaseReceiptStatus.PENDING,
        received_by=user.id,
        remark=req.remark
    )
    db.add(receipt)
    db.flush()

    # 创建明细
    for item in req.items:
        amount = item.amount or (item.quantity * item.unit_price)
        ri = PurchaseReceiptItem(
            receipt_id=receipt.id,
            product_id=item.product_id,
            order_item_id=item.order_item_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=amount
        )
        db.add(ri)

    db.commit()
    db.refresh(receipt)
    return ResponseModel(data=PurchaseReceiptOut.model_validate(receipt))


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
    return PaginatedResponse(
        data=[PurchaseReceiptOut.model_validate(i) for i in items],
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
        inv_service = InventoryService
        # 先查询现有库存
        from models.inventory import Inventory
        inv = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.warehouse_id == receipt.warehouse_id
        ).first()
        if inv:
            # 移动加权平均成本
            total_cost = inv.quantity * (inv.cost_price or 0) + item.quantity * item.unit_price
            inv.quantity += item.quantity
            inv.cost_price = total_cost / inv.quantity if inv.quantity > 0 else 0
        else:
            inv = Inventory(
                warehouse_id=receipt.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
                cost_price=item.unit_price
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
    db.commit()
    return ResponseModel(message="入库确认成功，库存已更新")
