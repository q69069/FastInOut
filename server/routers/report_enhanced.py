"""增强报表路由 — Phase C"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.sales_delivery import SalesDelivery, SalesDeliveryItem
from models.purchase_receipt import PurchaseReceipt, PurchaseReceiptItem
from models.commission import Commission
from models.employee import Employee
from models.product import Product
from models.customer import Customer
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/reports", tags=["增强报表"])


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


@router.get("/sales-detail", response_model=ResponseModel)
def sales_detail_report(
    start_date: str = Query(None), end_date: str = Query(None),
    group_by: str = Query("product"),  # product/customer/employee/date/warehouse
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(SalesDeliveryItem).join(SalesDelivery)
    q = q.filter(SalesDelivery.status.in_(["locked", "settled"]))
    if start_date:
        q = q.filter(SalesDelivery.created_at >= start_date)
    if end_date:
        q = q.filter(SalesDelivery.created_at <= f"{end_date} 23:59:59")

    items = q.all()
    groups = {}
    for item in items:
        delivery = db.query(SalesDelivery).get(item.delivery_id)
        if group_by == "product":
            prod = db.query(Product).get(item.product_id)
            key = item.product_id
            label = prod.name if prod else f"商品{item.product_id}"
        elif group_by == "customer":
            cust = db.query(Customer).get(delivery.customer_id) if delivery else None
            key = delivery.customer_id if delivery else 0
            label = cust.name if cust else ""
        elif group_by == "employee":
            emp = db.query(Employee).get(delivery.created_by) if delivery else None
            key = delivery.created_by if delivery else 0
            label = emp.name if emp else ""
        elif group_by == "date":
            key = str(delivery.created_at)[:10] if delivery else ""
            label = key
        else:
            key = delivery.warehouse_id if delivery else 0
            label = f"仓库{key}"

        if key not in groups:
            groups[key] = {"label": label, "quantity": 0, "amount": 0, "count": 0}
        groups[key]["quantity"] += item.quantity or 0
        groups[key]["amount"] += item.amount or 0
        groups[key]["count"] += 1

    result = sorted(groups.values(), key=lambda x: x["amount"], reverse=True)
    return ResponseModel(data=result)


@router.get("/purchase-detail", response_model=ResponseModel)
def purchase_detail_report(
    start_date: str = Query(None), end_date: str = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(PurchaseReceipt).filter(PurchaseReceipt.status == "confirmed")
    if start_date:
        q = q.filter(PurchaseReceipt.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseReceipt.created_at <= f"{end_date} 23:59:59")
    receipts = q.all()
    result = [{
        "id": r.id, "receipt_no": r.receipt_no,
        "supplier_id": r.supplier_id, "total_amount": r.total_amount,
        "confirmed_at": str(r.confirmed_at) if r.confirmed_at else None
    } for r in receipts]
    total = sum(r.total_amount or 0 for r in receipts)
    return ResponseModel(data={"items": result, "total": total, "count": len(result)})


@router.get("/commission", response_model=ResponseModel)
def commission_report(
    period: str = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Commission)
    if period:
        q = q.filter(Commission.period == period)
    items = q.all()
    result = []
    for c in items:
        emp = db.query(Employee).get(c.employee_id)
        result.append({
            "employee_name": emp.name if emp else "",
            "period": c.period, "base_amount": c.base_amount,
            "commission_rate": c.commission_rate,
            "commission_amount": c.commission_amount, "status": c.status
        })
    total = sum(c.commission_amount or 0 for c in items)
    return ResponseModel(data={"items": result, "total": total})
