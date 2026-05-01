from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from database import get_db
from models.batch import ProductBatch
from models.product import Product
from models.warehouse import Warehouse
from schemas.batch import BatchCreate, BatchUpdate, BatchOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/batches", tags=["批次管理"])


@router.get("", response_model=PaginatedResponse)
def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_id: int = Query(None),
    warehouse_id: int = Query(None),
    status: str = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(ProductBatch)
    if product_id:
        q = q.filter(ProductBatch.product_id == product_id)
    if warehouse_id:
        q = q.filter(ProductBatch.warehouse_id == warehouse_id)
    if status:
        q = q.filter(ProductBatch.status == status)
    if keyword:
        q = q.filter(ProductBatch.batch_no.contains(keyword))
    total = q.count()
    items = q.order_by(ProductBatch.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 批量查询商品和仓库名称
    product_ids = list(set(b.product_id for b in items))
    warehouse_ids = list(set(b.warehouse_id for b in items if b.warehouse_id))
    products_map = {p.id: p.name for p in db.query(Product).filter(Product.id.in_(product_ids)).all()} if product_ids else {}
    warehouses_map = {w.id: w.name for w in db.query(Warehouse).filter(Warehouse.id.in_(warehouse_ids)).all()} if warehouse_ids else {}

    result = []
    for b in items:
        out = BatchOut.model_validate(b)
        out.product_name = products_map.get(b.product_id, "")
        out.warehouse_name = warehouses_map.get(b.warehouse_id, "")
        result.append(out)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_batch(req: BatchCreate, db: Session = Depends(get_db)):
    product = db.query(Product).get(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if req.warehouse_id:
        warehouse = db.query(Warehouse).get(req.warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="仓库不存在")
    batch = ProductBatch(**req.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return ResponseModel(data=BatchOut.model_validate(batch))


@router.put("/{batch_id}", response_model=ResponseModel)
def update_batch(batch_id: int, req: BatchUpdate, db: Session = Depends(get_db)):
    batch = db.query(ProductBatch).get(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(batch, k, v)
    db.commit()
    db.refresh(batch)
    return ResponseModel(data=BatchOut.model_validate(batch))


@router.get("/expiring", response_model=ResponseModel)
def get_expiring_batches(days: int = Query(30, ge=1), db: Session = Depends(get_db)):
    """获取即将过期的批次（默认30天内）"""
    cutoff = date.today() + timedelta(days=days)
    batches = db.query(ProductBatch).filter(
        and_(
            ProductBatch.expire_date <= cutoff,
            ProductBatch.expire_date >= date.today(),
            ProductBatch.status == "active",
            ProductBatch.quantity > 0
        )
    ).order_by(ProductBatch.expire_date).all()

    product_ids = list(set(b.product_id for b in batches))
    products_map = {p.id: p.name for p in db.query(Product).filter(Product.id.in_(product_ids)).all()} if product_ids else {}

    result = []
    for b in batches:
        out = BatchOut.model_validate(b)
        out.product_name = products_map.get(b.product_id, "")
        result.append(out)

    return ResponseModel(data=result)


@router.get("/fifo/{product_id}", response_model=ResponseModel)
def get_fifo_batches(
    product_id: int,
    warehouse_id: int = Query(None),
    quantity: float = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    """FIFO先进先出：获取扣减批次列表"""
    q = db.query(ProductBatch).filter(
        and_(
            ProductBatch.product_id == product_id,
            ProductBatch.status == "active",
            ProductBatch.quantity > 0
        )
    )
    if warehouse_id:
        q = q.filter(ProductBatch.warehouse_id == warehouse_id)

    # 按生产日期排序（先进先出），没有生产日期的按创建时间
    batches = q.order_by(ProductBatch.production_date.nullsfirst(), ProductBatch.created_at).all()

    remaining = quantity
    result = []
    for b in batches:
        if remaining <= 0:
            break
        deduct = min(b.quantity, remaining)
        result.append({
            "batch_id": b.id,
            "batch_no": b.batch_no,
            "available": b.quantity,
            "deduct": deduct,
            "expire_date": str(b.expire_date) if b.expire_date else None
        })
        remaining -= deduct

    if remaining > 0:
        raise HTTPException(status_code=400, detail=f"库存不足，缺少 {remaining} 数量")

    return ResponseModel(data=result)


@router.post("/deduct", response_model=ResponseModel)
def deduct_batch_stock(
    product_id: int = Query(...),
    warehouse_id: int = Query(None),
    quantity: float = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    """FIFO扣减批次库存"""
    q = db.query(ProductBatch).filter(
        and_(
            ProductBatch.product_id == product_id,
            ProductBatch.status == "active",
            ProductBatch.quantity > 0
        )
    )
    if warehouse_id:
        q = q.filter(ProductBatch.warehouse_id == warehouse_id)

    batches = q.order_by(ProductBatch.production_date.nullsfirst(), ProductBatch.created_at).all()

    remaining = quantity
    deducted = []
    for b in batches:
        if remaining <= 0:
            break
        deduct = min(b.quantity, remaining)
        b.quantity -= deduct
        if b.quantity <= 0:
            b.status = "used"
        remaining -= deduct
        deducted.append({"batch_id": b.id, "batch_no": b.batch_no, "deducted": deduct})

    if remaining > 0:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"库存不足，缺少 {remaining} 数量")

    db.commit()
    return ResponseModel(data={"deducted": deducted})
