"""
价格变动记录
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.price_change import PriceChangeLog
from schemas import PriceChangeLogResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/price-changes", tags=["价格"])


@router.get("/", response_model=list[PriceChangeLogResponse])
def list_price_changes(product_id: int = None, db: Session = Depends(get_db)):
    query = db.query(PriceChangeLog)
    if product_id:
        query = query.filter(PriceChangeLog.product_id == product_id)
    return query.order_by(PriceChangeLog.change_time.desc()).all()
