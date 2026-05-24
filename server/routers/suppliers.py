from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.supplier import Supplier
from models.employee import Employee
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.data_filter import DataFilter
from utils.role_check import require_owner_or_admin
from deps import require_suppliers_module

router = APIRouter(prefix="/api/suppliers", tags=["供应商"])

@router.get("", response_model=PaginatedResponse)
def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    user: Employee = Depends(require_suppliers_module),
    db: Session = Depends(get_db)
):
    q = db.query(Supplier)
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
def create_supplier(req: SupplierCreate, user: Employee = Depends(require_suppliers_module), db: Session = Depends(get_db)):
    sup = Supplier(**req.model_dump(), created_by=user.id)
    db.add(sup)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.get("/{supplier_id}", response_model=ResponseModel)
def get_supplier(supplier_id: int, user: Employee = Depends(require_suppliers_module), db: Session = Depends(get_db)):
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    require_owner_or_admin(user, sup.created_by, db, "无权查看此供应商")
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.put("/{supplier_id}", response_model=ResponseModel)
def update_supplier(supplier_id: int, req: SupplierUpdate, user: Employee = Depends(require_suppliers_module), db: Session = Depends(get_db)):
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    require_owner_or_admin(user, sup.created_by, db, "无权编辑此供应商")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(sup, k, v)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.delete("/{supplier_id}", response_model=ResponseModel)
def delete_supplier(supplier_id: int, user: Employee = Depends(require_suppliers_module), db: Session = Depends(get_db)):
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    require_owner_or_admin(user, sup.created_by, db, "无权删除此供应商")
    db.delete(sup)
    db.commit()
    return ResponseModel(message="删除成功")
