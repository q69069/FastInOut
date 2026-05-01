from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.promotion import Promotion
from schemas.promotion import PromotionCreate, PromotionUpdate, PromotionOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/promotions", tags=["促销方案"])


@router.get("", response_model=PaginatedResponse)
def list_promotions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: int = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Promotion)
    if keyword:
        q = q.filter(Promotion.name.contains(keyword))
    if status is not None:
        q = q.filter(Promotion.status == status)
    total = q.count()
    items = q.order_by(Promotion.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[PromotionOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_promotion(req: PromotionCreate, db: Session = Depends(get_db)):
    if req.promo_type not in ("threshold", "discount"):
        raise HTTPException(status_code=400, detail="促销类型必须为 threshold(满减) 或 discount(折扣)")
    if req.promo_type == "threshold" and req.threshold_amount <= 0:
        raise HTTPException(status_code=400, detail="满减门槛金额必须大于0")
    if req.promo_type == "discount" and (req.discount_value <= 0 or req.discount_value >= 1):
        raise HTTPException(status_code=400, detail="折扣比例必须在0到1之间（如0.85=八五折）")
    promo = Promotion(**req.model_dump())
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return ResponseModel(data=PromotionOut.model_validate(promo))


@router.get("/{promo_id}", response_model=ResponseModel)
def get_promotion(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(Promotion).get(promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="促销方案不存在")
    return ResponseModel(data=PromotionOut.model_validate(promo))


@router.put("/{promo_id}", response_model=ResponseModel)
def update_promotion(promo_id: int, req: PromotionUpdate, db: Session = Depends(get_db)):
    promo = db.query(Promotion).get(promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="促销方案不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(promo, k, v)
    db.commit()
    db.refresh(promo)
    return ResponseModel(data=PromotionOut.model_validate(promo))


@router.delete("/{promo_id}", response_model=ResponseModel)
def delete_promotion(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(Promotion).get(promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="促销方案不存在")
    db.delete(promo)
    db.commit()
    return ResponseModel(message="删除成功")
