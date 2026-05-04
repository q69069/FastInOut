from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from models.inventory import Inventory
from models.employee import Employee
from schemas.product import ProductCreate, ProductUpdate, ProductOut
from schemas.common import ResponseModel, PaginatedResponse
from deps import get_current_user

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.get("", response_model=PaginatedResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    status: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if keyword:
        q = q.filter(Product.name.contains(keyword) | Product.code.contains(keyword) | Product.barcode.contains(keyword))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if status is not None:
        q = q.filter(Product.status == status)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[ProductOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_product(req: ProductCreate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.code:
        existing = db.query(Product).filter(Product.code == req.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="商品编码已存在")
    prod = Product(**req.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.get("/barcode/{barcode}", response_model=ResponseModel)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.barcode == barcode).first()
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.get("/{product_id}", response_model=ResponseModel)
def get_product(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.put("/{product_id}", response_model=ResponseModel)
def update_product(product_id: int, req: ProductUpdate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    data = req.model_dump(exclude_unset=True)
    if "code" in data and data["code"] != prod.code:
        existing = db.query(Product).filter(Product.code == data["code"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="商品编码已存在")
    for k, v in data.items():
        setattr(prod, k, v)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.delete("/{product_id}", response_model=ResponseModel)
def delete_product(product_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    has_inv = db.query(Inventory).filter(Inventory.product_id == product_id, Inventory.quantity > 0).first()
    if has_inv:
        raise HTTPException(status_code=400, detail="商品有库存，无法删除")
    db.delete(prod)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/import", response_model=ResponseModel)
def import_products():
    return ResponseModel(message="功能开发中")


@router.get("/export", response_model=ResponseModel)
def export_products():
    return ResponseModel(message="功能开发中")
