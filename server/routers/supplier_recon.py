from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.supplier import Supplier
from models.purchase import PurchaseStockin, PurchaseReturn
from models.finance import Payment
from schemas.common import ResponseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/supplier-recon", tags=["供应商对账"])


@router.get("/statement", response_model=ResponseModel)
def supplier_statement(
    supplier_id: int = Query(...),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """供应商对账单：期初应付+本期采购-本期退货-本期付款=期末应付"""
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    now = datetime.now()
    if not end_date:
        end_date = now.strftime("%Y-%m-%d")
    if not start_date:
        start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # 期初应付 = 当前应付 - 本期净发生额（简化计算，实际应从期初余额导入）
    opening_balance = supplier.payable_balance or 0

    # 本期采购额
    purchase_amount = 0
    for si in db.query(PurchaseStockin).filter(
        PurchaseStockin.supplier_id == supplier_id,
        PurchaseStockin.status == 2,
        PurchaseStockin.created_at >= start_date,
        PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        purchase_amount += si.total_amount or 0

    # 本期退货额
    return_amount = 0
    for ret in db.query(PurchaseReturn).filter(
        PurchaseReturn.supplier_id == supplier_id,
        PurchaseReturn.status == 2,
        PurchaseReturn.created_at >= start_date,
        PurchaseReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        return_amount += ret.total_amount or 0

    # 本期付款额
    payment_amount = 0
    for p in db.query(Payment).filter(
        Payment.supplier_id == supplier_id,
        Payment.status == 1,
        Payment.created_at >= start_date,
        Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        payment_amount += p.amount or 0

    closing_balance = opening_balance + purchase_amount - return_amount - payment_amount

    # 明细列表
    items = []
    for si in db.query(PurchaseStockin).filter(
        PurchaseStockin.supplier_id == supplier_id,
        PurchaseStockin.status == 2,
        PurchaseStockin.created_at >= start_date,
        PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        items.append({
            "date": str(si.created_at)[:10], "code": si.code, "type": "采购入库",
            "purchase": si.total_amount or 0, "return": 0, "payment": 0
        })
    for ret in db.query(PurchaseReturn).filter(
        PurchaseReturn.supplier_id == supplier_id,
        PurchaseReturn.status == 2,
        PurchaseReturn.created_at >= start_date,
        PurchaseReturn.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        items.append({
            "date": str(ret.created_at)[:10], "code": ret.code, "type": "采购退货",
            "purchase": 0, "return": ret.total_amount or 0, "payment": 0
        })
    for p in db.query(Payment).filter(
        Payment.supplier_id == supplier_id,
        Payment.status == 1,
        Payment.created_at >= start_date,
        Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    ).all():
        items.append({
            "date": str(p.created_at)[:10], "code": p.code, "type": "付款",
            "purchase": 0, "return": 0, "payment": p.amount or 0
        })

    items.sort(key=lambda x: x["date"])

    # 计算逐笔余额
    running = opening_balance
    for item in items:
        running = running + item["purchase"] - item["return"] - item["payment"]
        item["balance"] = round(running, 2)

    return ResponseModel(data={
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "start_date": start_date,
        "end_date": end_date,
        "opening_balance": round(opening_balance, 2),
        "purchase_amount": round(purchase_amount, 2),
        "return_amount": round(return_amount, 2),
        "payment_amount": round(payment_amount, 2),
        "closing_balance": round(closing_balance, 2),
        "items": items
    })


@router.get("/summary", response_model=ResponseModel)
def supplier_summary(db: Session = Depends(get_db)):
    """所有供应商应付汇总"""
    suppliers = db.query(Supplier).filter(Supplier.payable_balance > 0).all()
    result = []
    for s in suppliers:
        result.append({
            "supplier_id": s.id, "supplier_name": s.name,
            "payable_balance": s.payable_balance or 0,
            "contact": s.contact or "", "phone": s.phone or ""
        })
    result.sort(key=lambda x: x["payable_balance"], reverse=True)
    return ResponseModel(data=result)
