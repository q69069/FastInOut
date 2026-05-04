from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from database import get_db
from models.customer_visit import CustomerVisit
from models.customer_contact import CustomerContact
from models.employee import Employee
from schemas.customer_visit import CustomerVisitCreate, CustomerVisitUpdate, CustomerVisitOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.auth import decode_access_token
from utils.role_check import require_role, require_owner_or_admin

router = APIRouter(prefix="/api/customer-visits", tags=["拜访记录"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.get("", response_model=PaginatedResponse)
def list_visits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(CustomerVisit)
    # 应用数据权限过滤
    q = DataFilter.apply_scope(q, CustomerVisit, user, db, scope_field="route_id", module_key="customers")
    if customer_id:
        q = q.filter(CustomerVisit.customer_id == customer_id)
    total = q.count()
    items = q.order_by(CustomerVisit.visit_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for v in items:
        out = CustomerVisitOut.model_validate(v)
        if v.contact_id:
            contact = db.query(CustomerContact).get(v.contact_id)
            if contact:
                out = CustomerVisitOut.model_validate(v)
        result.append(out)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_visit(req: CustomerVisitCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    visit = CustomerVisit(**req.model_dump(), created_by=user.id)
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return ResponseModel(data=CustomerVisitOut.model_validate(visit))


@router.put("/{visit_id}", response_model=ResponseModel)
def update_visit(visit_id: int, req: CustomerVisitUpdate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    visit = db.query(CustomerVisit).get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="拜访记录不存在")
    require_owner_or_admin(user, visit.created_by, db, "无权编辑此拜访记录")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(visit, k, v)
    db.commit()
    db.refresh(visit)
    return ResponseModel(data=CustomerVisitOut.model_validate(visit))


@router.delete("/{visit_id}", response_model=ResponseModel)
def delete_visit(visit_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    visit = db.query(CustomerVisit).get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="拜访记录不存在")
    require_owner_or_admin(user, visit.created_by, db, "无权删除此拜访记录")
    db.delete(visit)
    db.commit()
    return ResponseModel(message="删除成功")
