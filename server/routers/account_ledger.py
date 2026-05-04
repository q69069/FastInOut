"""往来账管理 — Phase A Day 7-8

客户应收/供应商应付的汇总和明细查询。
基于现有 finance.py 的收付款数据，提供往来账视图。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.customer import Customer
from models.supplier import Supplier
from models.finance import Receipt, Payment
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api", tags=["往来账"])


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


# ========== 客户应收汇总 ==========
@router.get("/account-ledger/receivables", response_model=ResponseModel)
def list_receivables(
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Customer).filter(Customer.receivable_balance > 0)
    if keyword:
        q = q.filter(Customer.name.contains(keyword))

    customers = q.order_by(Customer.receivable_balance.desc()).all()
    total_receivable = sum(c.receivable_balance or 0 for c in customers)

    result = []
    for c in customers:
        # 查询该客户的最近收款记录
        last_receipt = db.query(Receipt).filter(
            Receipt.customer_id == c.id
        ).order_by(Receipt.created_at.desc()).first()

        result.append({
            "customer_id": c.id,
            "customer_name": c.name,
            "phone": c.phone,
            "receivable_balance": c.receivable_balance or 0,
            "last_receipt_date": str(last_receipt.created_at) if last_receipt else None,
            "last_receipt_amount": last_receipt.amount if last_receipt else 0
        })

    return ResponseModel(data={
        "total_receivable": total_receivable,
        "count": len(result),
        "items": result
    })


# ========== 客户应收明细 ==========
@router.get("/account-ledger/receivables/{customer_id}", response_model=ResponseModel)
def get_receivable_detail(
    customer_id: int,
    start_date: str = Query(None),
    end_date: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    customer = db.query(Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "客户不存在")

    # 查询该客户的所有收款记录
    q = db.query(Receipt).filter(Receipt.customer_id == customer_id)
    if start_date:
        q = q.filter(Receipt.created_at >= start_date)
    if end_date:
        q = q.filter(Receipt.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    receipts = q.order_by(Receipt.created_at.desc()).all()
    total_received = sum(r.amount or 0 for r in receipts)

    return ResponseModel(data={
        "customer_id": customer.id,
        "customer_name": customer.name,
        "receivable_balance": customer.receivable_balance or 0,
        "total_received": total_received,
        "receipts": [{
            "id": r.id,
            "code": r.code,
            "amount": r.amount,
            "payment_method": r.payment_method,
            "status": r.status,
            "created_at": str(r.created_at)
        } for r in receipts]
    })


# ========== 供应商应付汇总 ==========
@router.get("/account-ledger/payables", response_model=ResponseModel)
def list_payables(
    keyword: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Supplier).filter(Supplier.payable_balance > 0)
    if keyword:
        q = q.filter(Supplier.name.contains(keyword))

    suppliers = q.order_by(Supplier.payable_balance.desc()).all()
    total_payable = sum(s.payable_balance or 0 for s in suppliers)

    result = []
    for s in suppliers:
        last_payment = db.query(Payment).filter(
            Payment.supplier_id == s.id
        ).order_by(Payment.created_at.desc()).first()

        result.append({
            "supplier_id": s.id,
            "supplier_name": s.name,
            "phone": s.phone,
            "payable_balance": s.payable_balance or 0,
            "last_payment_date": str(last_payment.created_at) if last_payment else None,
            "last_payment_amount": last_payment.amount if last_payment else 0
        })

    return ResponseModel(data={
        "total_payable": total_payable,
        "count": len(result),
        "items": result
    })


# ========== 供应商应付明细 ==========
@router.get("/account-ledger/payables/{supplier_id}", response_model=ResponseModel)
def get_payable_detail(
    supplier_id: int,
    start_date: str = Query(None),
    end_date: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    supplier = db.query(Supplier).get(supplier_id)
    if not supplier:
        raise HTTPException(404, "供应商不存在")

    q = db.query(Payment).filter(Payment.supplier_id == supplier_id)
    if start_date:
        q = q.filter(Payment.created_at >= start_date)
    if end_date:
        q = q.filter(Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    payments = q.order_by(Payment.created_at.desc()).all()
    total_paid = sum(p.amount or 0 for p in payments)

    return ResponseModel(data={
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "payable_balance": supplier.payable_balance or 0,
        "total_paid": total_paid,
        "payments": [{
            "id": p.id,
            "code": p.code,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "status": p.status,
            "created_at": str(p.created_at)
        } for p in payments]
    })
