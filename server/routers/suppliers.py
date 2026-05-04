from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from database import get_db
from models.supplier import Supplier
from models.employee import Employee
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.auth import decode_access_token
from utils.role_check import require_role, require_owner_or_admin

router = APIRouter(prefix="/api/suppliers", tags=["供应商"])


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
def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """供应商列表"""
    user = get_current_user(authorization, db)
    q = db.query(Supplier)
    # 应用数据权限过滤（供应商一般没有路线，按创建人过滤）
    q = DataFilter.apply_scope(q, Supplier, user, db, scope_field="id", module_key="suppliers")
    if keyword:
        q = q.filter(Supplier.name.contains(keyword) | Supplier.code.contains(keyword))
    if category_id:
        q = q.filter(Supplier.category_id == category_id)
    total = q.count()
    items = q.order_by(Supplier.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[SupplierOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_supplier(req: SupplierCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    """新增供应商"""
    user = get_current_user(authorization, db)
    sup = Supplier(**req.model_dump(), created_by=user.id)
    db.add(sup)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.get("/{supplier_id}", response_model=ResponseModel)
def get_supplier(supplier_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """获取供应商详情"""
    user = get_current_user(authorization, db)
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    # 数据权限检查：非admin只能查看自己创建的
    require_owner_or_admin(user, sup.created_by, db, "无权查看此供应商")
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.put("/{supplier_id}", response_model=ResponseModel)
def update_supplier(supplier_id: int, req: SupplierUpdate, authorization: str = Header(None), db: Session = Depends(get_db)):
    """更新供应商"""
    user = get_current_user(authorization, db)
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    # 权限检查：非admin只能编辑自己创建的
    require_owner_or_admin(user, sup.created_by, db, "无权编辑此供应商")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(sup, k, v)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.delete("/{supplier_id}", response_model=ResponseModel)
def delete_supplier(supplier_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """删除供应商"""
    user = get_current_user(authorization, db)
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    # 权限检查：非admin只能删除自己创建的
    require_owner_or_admin(user, sup.created_by, db, "无权删除此供应商")
    db.delete(sup)
    db.commit()
    return ResponseModel(message="删除成功")
