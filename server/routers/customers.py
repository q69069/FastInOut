from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from database import get_db
from models.customer import Customer
from models.employee import Employee
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.auth import decode_access_token

router = APIRouter(prefix="/api/customers", tags=["客户"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    """从请求头解析当前用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.get("", response_model=PaginatedResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """客户列表"""
    user = get_current_user(authorization, db)
    q = db.query(Customer)
    # 应用数据权限过滤
    q = DataFilter.apply_scope(q, Customer, user, db, scope_field="route_id", module_key="customers")
    if keyword:
        q = q.filter(Customer.name.contains(keyword) | Customer.code.contains(keyword))
    if category_id:
        q = q.filter(Customer.category_id == category_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[CustomerOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_customer(req: CustomerCreate, db: Session = Depends(get_db)):
    """新增客户"""
    cust = Customer(**req.model_dump())
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return ResponseModel(data=CustomerOut.model_validate(cust))


@router.get("/{customer_id}", response_model=ResponseModel)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """获取客户详情"""
    cust = db.query(Customer).get(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="客户不存在")
    return ResponseModel(data=CustomerOut.model_validate(cust))


@router.put("/{customer_id}", response_model=ResponseModel)
def update_customer(customer_id: int, req: CustomerUpdate, db: Session = Depends(get_db)):
    """更新客户"""
    cust = db.query(Customer).get(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="客户不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(cust, k, v)
    db.commit()
    db.refresh(cust)
    return ResponseModel(data=CustomerOut.model_validate(cust))


@router.delete("/{customer_id}", response_model=ResponseModel)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """删除客户"""
    cust = db.query(Customer).get(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="客户不存在")
    db.delete(cust)
    db.commit()
    return ResponseModel(message="删除成功")
