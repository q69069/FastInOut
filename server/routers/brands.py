from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.brand import Brand
from schemas.brand import BrandCreate, BrandUpdate, BrandOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/brands", tags=["品牌管理"])


@router.get("", response_model=PaginatedResponse)
def list_brands(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Brand)
    if keyword:
        q = q.filter(Brand.name.contains(keyword) | Brand.code.contains(keyword))
    if status is not None:
        q = q.filter(Brand.status == status)
    total = q.count()
    items = q.order_by(Brand.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[BrandOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_brand(req: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(**req.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return ResponseModel(data=BrandOut.model_validate(brand))


@router.get("/{brand_id}", response_model=ResponseModel)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).get(brand_id)
    if not brand:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="品牌不存在")
    return ResponseModel(data=BrandOut.model_validate(brand))


@router.put("/{brand_id}", response_model=ResponseModel)
def update_brand(brand_id: int, req: BrandUpdate, db: Session = Depends(get_db)):
    brand = db.query(Brand).get(brand_id)
    if not brand:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="品牌不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(brand, k, v)
    db.commit()
    db.refresh(brand)
    return ResponseModel(data=BrandOut.model_validate(brand))


@router.delete("/{brand_id}", response_model=ResponseModel)
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).get(brand_id)
    if not brand:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="品牌不存在")
    db.delete(brand)
    db.commit()
    return ResponseModel(message="删除成功")