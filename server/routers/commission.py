"""员工提成路由 — Phase C"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.commission import Commission
from models.employee import Employee
from models.settlement import Settlement
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api", tags=["提成"])


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


@router.get("/commissions", response_model=PaginatedResponse)
def list_commissions(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    employee_id: int = Query(None), period: str = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(Commission)
    if employee_id:
        q = q.filter(Commission.employee_id == employee_id)
    if period:
        q = q.filter(Commission.period == period)
    total = q.count()
    items = q.order_by(Commission.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for c in items:
        emp = db.query(Employee).get(c.employee_id)
        result.append({
            "id": c.id, "employee_id": c.employee_id,
            "employee_name": emp.name if emp else "",
            "period": c.period, "base_amount": c.base_amount,
            "commission_rate": c.commission_rate,
            "commission_amount": c.commission_amount,
            "status": c.status, "remark": c.remark,
            "created_at": str(c.created_at)
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/commissions", response_model=ResponseModel)
def create_commission(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    c = Commission(
        employee_id=data["employee_id"], period=data["period"],
        base_amount=data.get("base_amount", 0),
        commission_rate=data.get("commission_rate", 0),
        commission_amount=data.get("commission_amount", 0),
        remark=data.get("remark")
    )
    db.add(c)
    db.commit()
    return ResponseModel(message="提成记录创建成功")


@router.post("/commissions/calculate", response_model=ResponseModel)
def calculate_commissions(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """自动计算提成 — 按已审核交账单汇总"""
    user = get_current_user(authorization, db)
    if user.role_id != 5:
        raise HTTPException(403, "只有管理员可以计算提成")
    period = data.get("period")
    rate = data.get("rate", 0.05)  # 默认5%
    if not period:
        raise HTTPException(400, "请指定期间")
    # 汇总该期间已审核的交账单
    settlements = db.query(Settlement).filter(
        Settlement.status == "audited",
        Settlement.settlement_date.like(f"{period}%")
    ).all()
    emp_sales = {}
    for s in settlements:
        emp_sales[s.employee_id] = emp_sales.get(s.employee_id, 0) + (s.total_sales or 0)
    count = 0
    for emp_id, base in emp_sales.items():
        existing = db.query(Commission).filter(
            Commission.employee_id == emp_id, Commission.period == period
        ).first()
        if existing:
            existing.base_amount = base
            existing.commission_rate = rate
            existing.commission_amount = base * rate
        else:
            db.add(Commission(
                employee_id=emp_id, period=period,
                base_amount=base, commission_rate=rate,
                commission_amount=base * rate
            ))
        count += 1
    db.commit()
    return ResponseModel(message=f"已计算 {count} 人的提成")
