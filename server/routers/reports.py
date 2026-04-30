from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from models.customer import Customer
from models.supplier import Supplier
from models.inventory import InventoryAlert
from schemas.report import DashboardOut
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/reports", tags=["报表"])


@router.get("/dashboard", response_model=ResponseModel)
def dashboard(db: Session = Depends(get_db)):
    """经营看板"""
    data = DashboardOut(
        product_count=db.query(Product).count(),
        customer_count=db.query(Customer).count(),
        supplier_count=db.query(Supplier).count(),
        alert_count=db.query(InventoryAlert).filter(InventoryAlert.is_handled == 0).count(),
    )
    return ResponseModel(data=data)


@router.get("/sales", response_model=ResponseModel)
def sales_report(db: Session = Depends(get_db)):
    """销售报表（预留）"""
    return ResponseModel(data=[], message="功能开发中")


@router.get("/purchase", response_model=ResponseModel)
def purchase_report(db: Session = Depends(get_db)):
    """采购报表（预留）"""
    return ResponseModel(data=[], message="功能开发中")


@router.get("/inventory", response_model=ResponseModel)
def inventory_report(db: Session = Depends(get_db)):
    """库存报表（预留）"""
    return ResponseModel(data=[], message="功能开发中")


@router.get("/profit", response_model=ResponseModel)
def profit_report(db: Session = Depends(get_db)):
    """利润报表（预留）"""
    return ResponseModel(data=[], message="功能开发中")
