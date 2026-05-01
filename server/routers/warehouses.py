from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from models.warehouse import Warehouse
from models.inventory import Inventory
from schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/warehouses", tags=["仓库"])

VALID_WAREHOUSE_TYPES = ("normal", "vehicle", "other")


@router.get("", response_model=PaginatedResponse)
def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    warehouse_type: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Warehouse)
    if keyword:
        q = q.filter(Warehouse.name.contains(keyword) | Warehouse.code.contains(keyword))
    if warehouse_type:
        q = q.filter(Warehouse.warehouse_type == warehouse_type)
    total = q.count()
    items = q.order_by(Warehouse.is_default.desc(), Warehouse.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[WarehouseOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_warehouse(req: WarehouseCreate, db: Session = Depends(get_db)):
    if req.warehouse_type not in VALID_WAREHOUSE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的仓库类型: {req.warehouse_type}")
    existing = db.query(Warehouse).filter(Warehouse.code == req.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="仓库编码已存在")
    wh = Warehouse(**req.model_dump())
    db.add(wh)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="仓库编码已存在")
    db.refresh(wh)
    return ResponseModel(data=WarehouseOut.model_validate(wh))


@router.get("/{warehouse_id}", response_model=ResponseModel)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return ResponseModel(data=WarehouseOut.model_validate(wh))


@router.put("/{warehouse_id}", response_model=ResponseModel)
def update_warehouse(warehouse_id: int, req: WarehouseUpdate, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    update_data = req.model_dump(exclude_unset=True)
    if "warehouse_type" in update_data and update_data["warehouse_type"] not in VALID_WAREHOUSE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的仓库类型: {update_data['warehouse_type']}")
    if "code" in update_data:
        existing = db.query(Warehouse).filter(Warehouse.code == update_data["code"], Warehouse.id != warehouse_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="仓库编码已存在")
    for k, v in update_data.items():
        setattr(wh, k, v)
    db.commit()
    db.refresh(wh)
    return ResponseModel(data=WarehouseOut.model_validate(wh))


@router.delete("/{warehouse_id}", response_model=ResponseModel)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    has_inventory = db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id, Inventory.quantity > 0).first()
    if has_inventory:
        raise HTTPException(status_code=400, detail="仓库还有库存，无法删除")
    db.delete(wh)
    db.commit()
    return ResponseModel(message="删除成功")


@router.put("/{warehouse_id}/default", response_model=ResponseModel)
def set_default_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    wh = db.query(Warehouse).get(warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="仓库不存在")
    db.query(Warehouse).update({"is_default": False})
    wh.is_default = True
    db.commit()
    return ResponseModel(message="已设为默认仓库")
