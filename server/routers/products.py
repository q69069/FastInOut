from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate, ProductOut
from schemas.common import ResponseModel, PaginatedResponse

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
    """商品列表"""
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
def create_product(req: ProductCreate, db: Session = Depends(get_db)):
    """新增商品"""
    prod = Product(**req.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.get("/{product_id}", response_model=ResponseModel)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.put("/{product_id}", response_model=ResponseModel)
def update_product(product_id: int, req: ProductUpdate, db: Session = Depends(get_db)):
    """更新商品"""
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(prod, k, v)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=ProductOut.model_validate(prod))


@router.delete("/{product_id}", response_model=ResponseModel)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除商品"""
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(prod)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/import", response_model=ResponseModel)
def import_products():
    """导入商品（预留）"""
    return ResponseModel(message="功能开发中")


@router.get("/export", response_model=ResponseModel)
def export_products():
    """导出商品（预留）"""
    return ResponseModel(message="功能开发中")
