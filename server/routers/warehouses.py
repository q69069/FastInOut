from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.warehouse import Warehouse
from schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/warehouses", tags=["仓库"])


@router.get("", response_model=PaginatedResponse)
def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    """仓库列表"""
    q = db.query(Warehouse)
    if keyword:
        q = q.filter(Warehouse.name.contains(keyword) | Warehouse.code.contains(keyword))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[WarehouseOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_warehouse(req: WarehouseCreate, db: Session = Depends(get_db)):
    """新增仓库"""
    wh = Warehouse(**req.model_dump())
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return ResponseModel(data=WarehouseOut.model_validate(wh))


@router.put("/{warehouse_id}", response_model=ResponseModel)
def update_warehouse(warehouse_id: int, req: WarehouseUpdate, db: Session = Depends(get_db)):
    """更新仓库"""
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(wh, k, v)
    db.commit()
    db.refresh(wh)
    return ResponseModel(data=WarehouseOut.model_validate(wh))


@router.delete("/{warehouse_id}", response_model=ResponseModel)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """删除仓库"""
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    db.delete(wh)
    db.commit()
    return ResponseModel(message="删除成功")
