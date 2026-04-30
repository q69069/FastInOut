from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/suppliers", tags=["供应商"])


@router.get("", response_model=PaginatedResponse)
def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """供应商列表"""
    q = db.query(Supplier)
    if keyword:
        q = q.filter(Supplier.name.contains(keyword) | Supplier.code.contains(keyword))
    if category_id:
        q = q.filter(Supplier.category_id == category_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[SupplierOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_supplier(req: SupplierCreate, db: Session = Depends(get_db)):
    """新增供应商"""
    sup = Supplier(**req.model_dump())
    db.add(sup)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.get("/{supplier_id}", response_model=ResponseModel)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """获取供应商详情"""
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.put("/{supplier_id}", response_model=ResponseModel)
def update_supplier(supplier_id: int, req: SupplierUpdate, db: Session = Depends(get_db)):
    """更新供应商"""
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(sup, k, v)
    db.commit()
    db.refresh(sup)
    return ResponseModel(data=SupplierOut.model_validate(sup))


@router.delete("/{supplier_id}", response_model=ResponseModel)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """删除供应商"""
    sup = db.query(Supplier).get(supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
    db.delete(sup)
    db.commit()
    return ResponseModel(message="删除成功")
