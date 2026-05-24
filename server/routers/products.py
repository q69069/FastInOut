from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.product import Product
from models.inventory import Inventory, InventoryCheckItem, InventoryTransferItem, InventoryAlert
from models.inventory import OtherInventoryLog
from models.employee import Employee
from models.sales import SalesOrderItem, SalesStockoutItem, SalesReturnItem
from models.sales_delivery import SalesDeliveryItem
from models.purchase import PurchaseOrderItem, PurchaseStockinItem, PurchaseReturnItem
from models.purchase_receipt import PurchaseReceiptItem
from models.purchase_return_dlv import PurchaseReturnDeliveryItem
from models.vehicle_load import VehicleLoadItem
from models.damage_report import DamageReportItem
from models.customer_price import CustomerPrice
from models.batch import ProductBatch
from models.unit import UnitConversion
from models.price_change import PriceChangeLog
from schemas.product import ProductCreate, ProductUpdate, ProductOut
from schemas.common import ResponseModel, PaginatedResponse
from deps import require_products_module
from utils.unit_convert import get_product_available_units

router = APIRouter(prefix="/api/products", tags=["商品"])


def _enrich_product(p: Product) -> dict:
    """为 ProductOut 填充计算后的三级价格"""
    d = ProductOut.model_validate(p).model_dump()
    d['brand_name'] = p.brand_rel.name if p.brand_rel else None
    purchase = p.purchase_price or 0
    retail = p.retail_price or 0
    d['small_purchase_price'] = purchase
    d['small_retail_price'] = retail
    if p.medium_conv_rate:
        d['medium_purchase_price'] = round(purchase * p.medium_conv_rate, 2)
        d['medium_retail_price'] = round(retail * p.medium_conv_rate, 2)
    if p.large_conv_rate:
        d['large_purchase_price'] = round(purchase * p.large_conv_rate, 2)
        d['large_retail_price'] = round(retail * p.large_conv_rate, 2)
    return d


def _validate_units(data: dict):
    if data.get('medium_unit_name') and not data.get('medium_conv_rate'):
        raise HTTPException(400, "中单位换算率不能为空")
    if data.get('large_unit_name') and not data.get('large_conv_rate'):
        raise HTTPException(400, "大单位换算率不能为空")
    if data.get('medium_conv_rate', 0) and data['medium_conv_rate'] <= 0:
        raise HTTPException(400, "中单位换算率必须大于0")
    if data.get('large_conv_rate', 0) and data['large_conv_rate'] <= 0:
        raise HTTPException(400, "大单位换算率必须大于0")


@router.get("", response_model=PaginatedResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    category_id: int = Query(None),
    status: int = Query(None),
    warehouse_id: int = Query(None),
    user: Employee = Depends(require_products_module),
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if keyword:
        from models.brand import Brand
        q = q.outerjoin(Brand, Product.brand_id == Brand.id).filter(
            Product.name.contains(keyword) | Product.code.contains(keyword) | Product.barcode.contains(keyword) | Brand.name.contains(keyword)
        )
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if status is not None:
        q = q.filter(Product.status == status)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    data = [_enrich_product(i) for i in items]
    # 附加库存数据
    product_ids = [i.id for i in items]
    if product_ids:
        inv_q = db.query(Inventory.product_id, func.sum(Inventory.quantity).label('qty')).filter(Inventory.product_id.in_(product_ids))
        if warehouse_id:
            inv_q = inv_q.filter(Inventory.warehouse_id == warehouse_id)
        stock_map = {r.product_id: float(r.qty or 0) for r in inv_q.group_by(Inventory.product_id).all()}
        for d in data:
            d['available_stock'] = stock_map.get(d['id'], 0)
    return PaginatedResponse(data=data, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_product(req: ProductCreate, user: Employee = Depends(require_products_module), db: Session = Depends(get_db)):
    if req.code:
        existing = db.query(Product).filter(Product.code == req.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="商品编码已存在")
    data = req.model_dump()
    _validate_units(data)
    prod = Product(**data)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=_enrich_product(prod))


@router.get("/barcode/{barcode}", response_model=ResponseModel)
def get_product_by_barcode(barcode: str, user: Employee = Depends(require_products_module), db: Session = Depends(get_db)):
    prod = db.query(Product).filter(Product.barcode == barcode).first()
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    d = _enrich_product(prod)
    total_qty = db.query(func.sum(Inventory.quantity)).filter(Inventory.product_id == prod.id).scalar() or 0
    d['available_stock'] = float(total_qty)
    return ResponseModel(data=d)


@router.get("/{product_id}", response_model=ResponseModel)
def get_product(product_id: int, user: Employee = Depends(require_products_module), db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    d = _enrich_product(prod)
    total_qty = db.query(func.sum(Inventory.quantity)).filter(Inventory.product_id == product_id).scalar() or 0
    d['available_stock'] = float(total_qty)
    return ResponseModel(data=d)


@router.put("/{product_id}", response_model=ResponseModel)
def update_product(product_id: int, req: ProductUpdate, user: Employee = Depends(require_products_module), db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    data = req.model_dump(exclude_unset=True)
    _validate_units(data)
    if "code" in data and data["code"] != prod.code:
        existing = db.query(Product).filter(Product.code == data["code"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="商品编码已存在")
    for k, v in data.items():
        setattr(prod, k, v)
    db.commit()
    db.refresh(prod)
    return ResponseModel(data=_enrich_product(prod))


REF_TABLES = [
    ("销售订单明细", SalesOrderItem),
    ("销售出库明细", SalesStockoutItem),
    ("销售退货明细", SalesReturnItem),
    ("销售交货明细", SalesDeliveryItem),
    ("采购订单明细", PurchaseOrderItem),
    ("采购入库明细", PurchaseStockinItem),
    ("采购退货明细", PurchaseReturnItem),
    ("采购收货明细", PurchaseReceiptItem),
    ("采购退货交货明细", PurchaseReturnDeliveryItem),
    ("调拨明细", InventoryTransferItem),
    ("盘点明细", InventoryCheckItem),
    ("库存记录", Inventory),
    ("库存预警", InventoryAlert),
    ("其他库存日志", OtherInventoryLog),
    ("装车单明细", VehicleLoadItem),
    ("报损单明细", DamageReportItem),
    ("客户价格", CustomerPrice),
    ("产品批次", ProductBatch),
    ("单位换算", UnitConversion),
    ("价格变更日志", PriceChangeLog),
]


@router.delete("/{product_id}", response_model=ResponseModel)
def delete_product(product_id: int, user: Employee = Depends(require_products_module), db: Session = Depends(get_db)):
    prod = db.query(Product).get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="商品不存在")
    for label, model in REF_TABLES:
        if db.query(model).filter(model.product_id == product_id).first():
            raise HTTPException(status_code=400, detail=f"该商品存在{label}记录，无法删除，请停用该商品")
    db.delete(prod)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/import", response_model=ResponseModel)
def import_products():
    return ResponseModel(message="功能开发中")


@router.get("/export", response_model=ResponseModel)
def export_products():
    return ResponseModel(message="功能开发中")


@router.get("/{id}/available-units", response_model=ResponseModel)
def product_available_units(id: int, db: Session = Depends(get_db)):
    """返回商品所有可用单位及到基本单位的换算率"""
    product = db.query(Product).get(id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    units = get_product_available_units(id, db)
    return ResponseModel(data=units)
