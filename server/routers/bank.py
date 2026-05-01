from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models.bank import BankStatement
from models.finance import Receipt, Payment
from models.customer import Customer
from models.supplier import Supplier
from schemas.bank import BankStatementCreate, BankStatementOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/bank-statements", tags=["银行对账"])


@router.get("", response_model=PaginatedResponse)
def list_statements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bank_account: str = Query(None),
    matched: bool = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(BankStatement)
    if bank_account:
        q = q.filter(BankStatement.bank_account == bank_account)
    if matched is not None:
        q = q.filter(BankStatement.matched == matched)
    if start_date:
        q = q.filter(BankStatement.statement_date >= start_date)
    if end_date:
        q = q.filter(BankStatement.statement_date <= end_date)
    total = q.count()
    items = q.order_by(BankStatement.statement_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[BankStatementOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_statement(req: BankStatementCreate, db: Session = Depends(get_db)):
    stmt = BankStatement(**req.model_dump())
    db.add(stmt)
    db.commit()
    db.refresh(stmt)
    return ResponseModel(data=BankStatementOut.model_validate(stmt))


@router.post("/auto-match", response_model=ResponseModel)
def auto_match(db: Session = Depends(get_db)):
    """自动匹配银行流水与收付款记录"""
    unmatched = db.query(BankStatement).filter(BankStatement.matched == False).all()
    matched_count = 0

    for stmt in unmatched:
        # 匹配收款（credit > 0 匹配收款）
        if stmt.credit > 0:
            receipt = db.query(Receipt).filter(
                and_(
                    Receipt.amount == stmt.credit,
                    Receipt.status == 1,
                    Receipt.matched != True
                )
            ).first()
            if receipt:
                stmt.matched = True
                stmt.matched_id = receipt.id
                stmt.matched_type = "receipt"
                receipt.matched = True
                matched_count += 1
                continue

        # 匹配付款（debit > 0 匹配付款）
        if stmt.debit > 0:
            payment = db.query(Payment).filter(
                and_(
                    Payment.amount == stmt.debit,
                    Payment.status == 1,
                    Payment.matched != True
                )
            ).first()
            if payment:
                stmt.matched = True
                stmt.matched_id = payment.id
                stmt.matched_type = "payment"
                payment.matched = True
                matched_count += 1

    db.commit()
    return ResponseModel(message=f"自动匹配完成，成功匹配 {matched_count} 条")


@router.get("/summary", response_model=ResponseModel)
def get_summary(db: Session = Depends(get_db)):
    """银行对账汇总"""
    stmts = db.query(BankStatement).all()
    total_debit = sum(s.debit for s in stmts)
    total_credit = sum(s.credit for s in stmts)
    matched_count = sum(1 for s in stmts if s.matched)
    unmatched_count = sum(1 for s in stmts if not s.matched)
    return ResponseModel(data={
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balance": total_credit - total_debit,
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "total_count": len(stmts)
    })
