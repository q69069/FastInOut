from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.category import Category, CustomerCategory, SupplierCategory
from models.product import Product
from schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryOut,
    CustomerCategoryCreate, CustomerCategoryUpdate, CustomerCategoryOut,
    SupplierCategoryCreate, SupplierCategoryUpdate, SupplierCategoryOut
)
from schemas.common import ResponseModel

router = APIRouter(prefix="/api", tags=["分类"])


def _build_tree(items, parent_id=None):
    tree = []
    for item in items:
        if item.parent_id == parent_id:
            node = CategoryOut.model_validate(item).model_dump()
            node["children"] = _build_tree(items, item.id)
            tree.append(node)
    return tree


# === 商品分类 ===
@router.get("/categories", response_model=ResponseModel)
def list_categories(tree: bool = False, db: Session = Depends(get_db)):
    items = db.query(Category).order_by(Category.sort_order).all()
    if tree:
        return ResponseModel(data=_build_tree(items))
    return ResponseModel(data=[CategoryOut.model_validate(i) for i in items])


@router.post("/categories", response_model=ResponseModel)
def create_category(req: CategoryCreate, db: Session = Depends(get_db)):
    cat = Category(**req.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=CategoryOut.model_validate(cat))


@router.put("/categories/{cat_id}", response_model=ResponseModel)
def update_category(cat_id: int, req: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=CategoryOut.model_validate(cat))


@router.delete("/categories/{cat_id}", response_model=ResponseModel)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    has_product = db.query(Product).filter(Product.category_id == cat_id).first()
    if has_product:
        raise HTTPException(status_code=400, detail="分类下有商品，无法删除")
    children = db.query(Category).filter(Category.parent_id == cat_id).first()
    if children:
        raise HTTPException(status_code=400, detail="分类下有子分类，无法删除")
    db.delete(cat)
    db.commit()
    return ResponseModel(message="删除成功")


# === 客户分类 ===
@router.get("/customer-categories", response_model=ResponseModel)
def list_customer_categories(db: Session = Depends(get_db)):
    items = db.query(CustomerCategory).order_by(CustomerCategory.sort_order).all()
    return ResponseModel(data=[CustomerCategoryOut.model_validate(i) for i in items])


@router.post("/customer-categories", response_model=ResponseModel)
def create_customer_category(req: CustomerCategoryCreate, db: Session = Depends(get_db)):
    cat = CustomerCategory(**req.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=CustomerCategoryOut.model_validate(cat))


@router.put("/customer-categories/{cat_id}", response_model=ResponseModel)
def update_customer_category(cat_id: int, req: CustomerCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(CustomerCategory).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=CustomerCategoryOut.model_validate(cat))


@router.delete("/customer-categories/{cat_id}", response_model=ResponseModel)
def delete_customer_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(CustomerCategory).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    from models.customer import Customer
    has = db.query(Customer).filter(Customer.category_id == cat_id).first()
    if has:
        raise HTTPException(status_code=400, detail="分类下有客户，无法删除")
    db.delete(cat)
    db.commit()
    return ResponseModel(message="删除成功")


# === 供应商分类 ===
@router.get("/supplier-categories", response_model=ResponseModel)
def list_supplier_categories(db: Session = Depends(get_db)):
    items = db.query(SupplierCategory).order_by(SupplierCategory.sort_order).all()
    return ResponseModel(data=[SupplierCategoryOut.model_validate(i) for i in items])


@router.post("/supplier-categories", response_model=ResponseModel)
def create_supplier_category(req: SupplierCategoryCreate, db: Session = Depends(get_db)):
    cat = SupplierCategory(**req.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=SupplierCategoryOut.model_validate(cat))


@router.put("/supplier-categories/{cat_id}", response_model=ResponseModel)
def update_supplier_category(cat_id: int, req: SupplierCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(SupplierCategory).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return ResponseModel(data=SupplierCategoryOut.model_validate(cat))


@router.delete("/supplier-categories/{cat_id}", response_model=ResponseModel)
def delete_supplier_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(SupplierCategory).get(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    from models.supplier import Supplier
    has = db.query(Supplier).filter(Supplier.category_id == cat_id).first()
    if has:
        raise HTTPException(status_code=400, detail="分类下有供应商，无法删除")
    db.delete(cat)
    db.commit()
    return ResponseModel(message="删除成功")
