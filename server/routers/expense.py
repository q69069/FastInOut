"""费用管理 — Phase A Day 5-6"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.expense import Expense, ExpenseCategory
from models.employee import Employee
from schemas.expense import (
    ExpenseCategoryCreate, ExpenseCategoryOut,
    ExpenseCreate, ExpenseOut
)
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api", tags=["费用管理"])


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


def _gen_expense_no(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Expense).filter(
        func.strftime("%Y%m%d", Expense.created_at) == today
    ).count()
    return f"FY{today}-{count + 1:03d}"


# ========== 费用类别 ==========
@router.get("/expense-categories", response_model=ResponseModel)
def list_expense_categories(db: Session = Depends(get_db)):
    items = db.query(ExpenseCategory).filter(ExpenseCategory.status == 1).order_by(ExpenseCategory.sort_order).all()
    return ResponseModel(data=[ExpenseCategoryOut.model_validate(i) for i in items])


@router.post("/expense-categories", response_model=ResponseModel)
def create_expense_category(req: ExpenseCategoryCreate, db: Session = Depends(get_db)):
    cat = ExpenseCategory(name=req.name, type=req.type, sort_order=req.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=ExpenseCategoryOut.model_validate(cat))


@router.delete("/expense-categories/{cat_id}", response_model=ResponseModel)
def delete_expense_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(ExpenseCategory).get(cat_id)
    if not cat:
        raise HTTPException(404, "类别不存在")
    cat.status = 0
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 费用记录 ==========
@router.post("/expenses", response_model=ResponseModel)
def create_expense(
    req: ExpenseCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    expense_no = _gen_expense_no(db)

    expense = Expense(
        expense_no=expense_no,
        category_id=req.category_id,
        amount=req.amount,
        payee=req.payee,
        payee_is_employee=req.payee_is_employee,
        description=req.description,
        status="pending",
        created_by=user.id,
        remark=req.remark
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return ResponseModel(data=ExpenseOut.model_validate(expense))


@router.get("/expenses", response_model=PaginatedResponse)
def list_expenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    category_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Expense)

    if status:
        q = q.filter(Expense.status == status)
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if start_date:
        q = q.filter(Expense.created_at >= start_date)
    if end_date:
        q = q.filter(Expense.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    total = q.count()
    items = q.order_by(Expense.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[ExpenseOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/expenses/{expense_id}", response_model=ResponseModel)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).get(expense_id)
    if not expense:
        raise HTTPException(404, "费用记录不存在")
    return ResponseModel(data=ExpenseOut.model_validate(expense))


@router.post("/expenses/{expense_id}/approve", response_model=ResponseModel)
def approve_expense(
    expense_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    expense = db.query(Expense).get(expense_id)
    if not expense:
        raise HTTPException(404, "费用记录不存在")
    if expense.status != "pending":
        raise HTTPException(400, f"当前状态 {expense.status} 不允许审批")

    # 只有主管/admin可以审批
    if user.role_id != 5:
        raise HTTPException(403, "只有管理员可以审批")

    expense.status = "approved"
    expense.approver_id = user.id
    expense.approved_at = datetime.now()
    db.commit()
    return ResponseModel(message="审批通过")


@router.post("/expenses/{expense_id}/reject", response_model=ResponseModel)
def reject_expense(
    expense_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    expense = db.query(Expense).get(expense_id)
    if not expense:
        raise HTTPException(404, "费用记录不存在")
    if expense.status != "pending":
        raise HTTPException(400, f"当前状态 {expense.status} 不允许驳回")

    if user.role_id != 5:
        raise HTTPException(403, "只有管理员可以驳回")

    expense.status = "rejected"
    expense.approver_id = user.id
    expense.approved_at = datetime.now()
    db.commit()
    return ResponseModel(message="已驳回")
