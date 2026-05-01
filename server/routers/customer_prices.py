from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.customer_price import CustomerPrice
from models.customer import Customer
from models.product import Product
from schemas.customer_price import CustomerPriceCreate, CustomerPriceUpdate, CustomerPriceOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/customer-prices", tags=["客户价格等级"])


@router.get("/query", response_model=ResponseModel)
def query_customer_price(
    customer_id: int = Query(...),
    product_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """查询客户对某商品的专属价格"""
    cp = db.query(CustomerPrice).filter(
        CustomerPrice.customer_id == customer_id,
        CustomerPrice.product_id == product_id
    ).first()
    if not cp:
        return ResponseModel(data=None)
    return ResponseModel(data=CustomerPriceOut.model_validate(cp))


@router.get("", response_model=PaginatedResponse)
def list_customer_prices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    customer_id: int = Query(None),
    product_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """客户价格列表"""
    q = db.query(CustomerPrice)
    if customer_id:
        q = q.filter(CustomerPrice.customer_id == customer_id)
    if product_id:
        q = q.filter(CustomerPrice.product_id == product_id)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # 拼接客户名和商品名
    result = []
    for cp in items:
        out = CustomerPriceOut.model_validate(cp)
        customer = db.query(Customer).get(cp.customer_id)
        product = db.query(Product).get(cp.product_id)
        out.customer_name = customer.name if customer else None
        out.product_name = product.name if product else None
        result.append(out)

    return PaginatedResponse(
        data=result,
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_customer_price(req: CustomerPriceCreate, db: Session = Depends(get_db)):
    """新增客户价格协议"""
    # 校验客户存在
    customer = db.query(Customer).get(req.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="客户不存在")
    # 校验商品存在
    product = db.query(Product).get(req.product_id)
    if not product:
        raise HTTPException(status_code=400, detail="商品不存在")
    # 校验不重复
    exists = db.query(CustomerPrice).filter(
        CustomerPrice.customer_id == req.customer_id,
        CustomerPrice.product_id == req.product_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该客户的价格协议已存在")

    cp = CustomerPrice(**req.model_dump())
    db.add(cp)
    db.commit()
    db.refresh(cp)

    out = CustomerPriceOut.model_validate(cp)
    out.customer_name = customer.name
    out.product_name = product.name
    return ResponseModel(data=out)


@router.put("/{price_id}", response_model=ResponseModel)
def update_customer_price(price_id: int, req: CustomerPriceUpdate, db: Session = Depends(get_db)):
    """更新客户价格协议"""
    cp = db.query(CustomerPrice).get(price_id)
    if not cp:
        raise HTTPException(status_code=404, detail="价格协议不存在")

    update_data = req.model_dump(exclude_unset=True)

    # 如果更新了客户或商品，校验不重复
    new_customer_id = update_data.get("customer_id", cp.customer_id)
    new_product_id = update_data.get("product_id", cp.product_id)
    if "customer_id" in update_data or "product_id" in update_data:
        # 校验客户存在
        if "customer_id" in update_data:
            customer = db.query(Customer).get(new_customer_id)
            if not customer:
                raise HTTPException(status_code=400, detail="客户不存在")
        # 校验商品存在
        if "product_id" in update_data:
            product = db.query(Product).get(new_product_id)
            if not product:
                raise HTTPException(status_code=400, detail="商品不存在")
        exists = db.query(CustomerPrice).filter(
            CustomerPrice.customer_id == new_customer_id,
            CustomerPrice.product_id == new_product_id,
            CustomerPrice.id != price_id
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="该客户的价格协议已存在")

    for k, v in update_data.items():
        setattr(cp, k, v)
    db.commit()
    db.refresh(cp)

    out = CustomerPriceOut.model_validate(cp)
    customer = db.query(Customer).get(cp.customer_id)
    product = db.query(Product).get(cp.product_id)
    out.customer_name = customer.name if customer else None
    out.product_name = product.name if product else None
    return ResponseModel(data=out)


@router.delete("/{price_id}", response_model=ResponseModel)
def delete_customer_price(price_id: int, db: Session = Depends(get_db)):
    """删除客户价格协议"""
    cp = db.query(CustomerPrice).get(price_id)
    if not cp:
        raise HTTPException(status_code=404, detail="价格协议不存在")
    db.delete(cp)
    db.commit()
    return ResponseModel(message="删除成功")
