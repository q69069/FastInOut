"""预收付款路由 — Phase C"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.advance_payment import AdvancePayment
from models.customer import Customer
from models.supplier import Supplier
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api", tags=["预收付款"])


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


def _gen_code(db, prefix):
    today = datetime.now().strftime("%Y%m%d")
    p = f"{prefix}{today}"
    last = db.query(AdvancePayment).filter(AdvancePayment.code.like(f"{p}%")).order_by(AdvancePayment.id.desc()).first()
    seq = int(last.code[-4:]) + 1 if last else 1
    return f"{p}{seq:04d}"


@router.get("/advance-payments", response_model=PaginatedResponse)
def list_advance_payments(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    type: str = Query(None), status: str = Query(None),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(AdvancePayment)
    if type:
        q = q.filter(AdvancePayment.type == type)
    if status:
        q = q.filter(AdvancePayment.status == status)
    total = q.count()
    items = q.order_by(AdvancePayment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for ap in items:
        party_name = ""
        if ap.party_type == "customer":
            c = db.query(Customer).get(ap.party_id)
            party_name = c.name if c else ""
        else:
            s = db.query(Supplier).get(ap.party_id)
            party_name = s.name if s else ""
        result.append({
            "id": ap.id, "code": ap.code, "type": ap.type,
            "party_type": ap.party_type, "party_id": ap.party_id,
            "party_name": party_name,
            "amount": ap.amount, "used_amount": ap.used_amount,
            "remaining_amount": ap.remaining_amount,
            "status": ap.status, "remark": ap.remark,
            "created_at": str(ap.created_at),
            "confirmed_at": str(ap.confirmed_at) if ap.confirmed_at else None
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/advance-payments", response_model=ResponseModel)
def create_advance_payment(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    prefix = "YS" if data["type"] == "receivable" else "YF"
    ap = AdvancePayment(
        code=_gen_code(db, prefix),
        type=data["type"], party_type=data["party_type"],
        party_id=data["party_id"], amount=data["amount"],
        remaining_amount=data["amount"], status="pending",
        remark=data.get("remark"), created_by=user.id
    )
    db.add(ap)
    db.commit()
    return ResponseModel(message="预收付款创建成功", data={"id": ap.id, "code": ap.code})


@router.post("/advance-payments/{ap_id}/confirm", response_model=ResponseModel)
def confirm_advance_payment(ap_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    ap = db.query(AdvancePayment).get(ap_id)
    if not ap:
        raise HTTPException(404, "记录不存在")
    if ap.status != "pending":
        raise HTTPException(400, "非待确认状态")
    ap.status = "confirmed"
    ap.confirmed_at = datetime.now()
    db.commit()
    return ResponseModel(message="确认成功")
