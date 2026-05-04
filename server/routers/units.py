from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.unit import Unit, UnitConversion
from models.product import Product
from models.employee import Employee
from schemas.unit import (
    UnitCreate, UnitUpdate, UnitOut,
    UnitConversionCreate, UnitConversionOut, ProductUnitConfig
)
from schemas.common import ResponseModel, PaginatedResponse
from deps import get_current_user

router = APIRouter(prefix="/api/units", tags=["单位管理"])


# ========== 单位 CRUD ==========
@router.get("", response_model=PaginatedResponse)
def list_units(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None), db: Session = Depends(get_db)
):
    q = db.query(Unit)
    if keyword:
        q = q.filter(Unit.name.contains(keyword) | Unit.symbol.contains(keyword))
    total = q.count()
    items = q.order_by(Unit.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[UnitOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_unit(req: UnitCreate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Unit).filter(Unit.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="单位名称已存在")
    unit = Unit(**req.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return ResponseModel(data=UnitOut.model_validate(unit))


@router.get("/all", response_model=ResponseModel)
def list_all_units(db: Session = Depends(get_db)):
    """获取所有启用的单位（不分页，用于下拉选择）"""
    units = db.query(Unit).filter(Unit.status == 1).all()
    return ResponseModel(data=[UnitOut.model_validate(u) for u in units])


@router.put("/{unit_id}", response_model=ResponseModel)
def update_unit(unit_id: int, req: UnitUpdate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    unit = db.query(Unit).get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="单位不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(unit, k, v)
    db.commit()
    db.refresh(unit)
    return ResponseModel(data=UnitOut.model_validate(unit))


@router.delete("/{unit_id}", response_model=ResponseModel)
def delete_unit(unit_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    unit = db.query(Unit).get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="单位不存在")
    # 检查是否被商品使用
    from models.product import Product
    used = db.query(Product).filter(Product.unit == unit.name).first()
    if used:
        raise HTTPException(status_code=400, detail="该单位已被商品使用，无法删除")
    # 检查是否在换算关系中使用
    conv = db.query(UnitConversion).filter(
        (UnitConversion.from_unit_id == unit_id) | (UnitConversion.to_unit_id == unit_id)
    ).first()
    if conv:
        raise HTTPException(status_code=400, detail="该单位在换算关系中使用，无法删除")
    db.delete(unit)
    db.commit()
    return ResponseModel(message="删除成功")


# ========== 单位换算 ==========
@router.get("/conversions", response_model=ResponseModel)
def list_conversions(
    product_id: int = Query(None), db: Session = Depends(get_db)
):
    q = db.query(UnitConversion)
    if product_id:
        q = q.filter(UnitConversion.product_id == product_id)
    items = q.order_by(UnitConversion.product_id, UnitConversion.level).all()
    result = []
    for c in items:
        from_unit = db.query(Unit).get(c.from_unit_id)
        to_unit = db.query(Unit).get(c.to_unit_id)
        result.append({
            "id": c.id, "product_id": c.product_id,
            "from_unit_id": c.from_unit_id, "to_unit_id": c.to_unit_id,
            "from_unit_name": from_unit.name if from_unit else "",
            "to_unit_name": to_unit.name if to_unit else "",
            "ratio": c.ratio, "level": c.level,
            "created_at": str(c.created_at)
        })
    return ResponseModel(data=result)


@router.post("/conversions", response_model=ResponseModel)
def create_conversion(req: UnitConversionCreate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    # 验证商品存在
    product = db.query(Product).get(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    # 验证单位存在
    from_unit = db.query(Unit).get(req.from_unit_id)
    to_unit = db.query(Unit).get(req.to_unit_id)
    if not from_unit or not to_unit:
        raise HTTPException(status_code=404, detail="单位不存在")
    if req.from_unit_id == req.to_unit_id:
        raise HTTPException(status_code=400, detail="源单位和目标单位不能相同")
    # 检查是否已存在相同换算
    existing = db.query(UnitConversion).filter(
        UnitConversion.product_id == req.product_id,
        UnitConversion.from_unit_id == req.from_unit_id,
        UnitConversion.to_unit_id == req.to_unit_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该换算关系已存在")
    conv = UnitConversion(**req.model_dump())
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ResponseModel(data=UnitConversionOut.model_validate(conv))


@router.delete("/conversions/{conv_id}", response_model=ResponseModel)
def delete_conversion(conv_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(UnitConversion).get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="换算关系不存在")
    db.delete(conv)
    db.commit()
    return ResponseModel(message="删除成功")


@router.get("/product/{product_id}/config", response_model=ResponseModel)
def get_product_unit_config(product_id: int, db: Session = Depends(get_db)):
    """获取商品的完整单位换算链"""
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    conversions = db.query(UnitConversion).filter(UnitConversion.product_id == product_id).order_by(UnitConversion.level).all()
    result = []
    base_unit_name = product.unit  # 商品的基本单位
    for c in conversions:
        from_unit = db.query(Unit).get(c.from_unit_id)
        to_unit = db.query(Unit).get(c.to_unit_id)
        result.append({
            "id": c.id, "product_id": c.product_id,
            "from_unit_id": c.from_unit_id, "to_unit_id": c.to_unit_id,
            "from_unit_name": from_unit.name if from_unit else "",
            "to_unit_name": to_unit.name if to_unit else "",
            "ratio": c.ratio, "level": c.level,
            "created_at": str(c.created_at)
        })
    return ResponseModel(data={
        "product_id": product_id,
        "base_unit": base_unit_name,
        "conversions": result
    })


@router.post("/convert", response_model=ResponseModel)
def convert_quantity(
    product_id: int = Query(...),
    quantity: float = Query(..., gt=0),
    from_unit_id: int = Query(...),
    to_unit_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """数量换算：从一个单位换算到另一个单位"""
    # 查找直接换算关系
    conv = db.query(UnitConversion).filter(
        UnitConversion.product_id == product_id,
        UnitConversion.from_unit_id == from_unit_id,
        UnitConversion.to_unit_id == to_unit_id
    ).first()
    if conv:
        return ResponseModel(data={
            "original_quantity": quantity,
            "converted_quantity": quantity * conv.ratio,
            "from_unit": db.query(Unit).get(from_unit_id).name,
            "to_unit": db.query(Unit).get(to_unit_id).name,
            "ratio": conv.ratio
        })
    # 尝试反向换算
    conv_reverse = db.query(UnitConversion).filter(
        UnitConversion.product_id == product_id,
        UnitConversion.from_unit_id == to_unit_id,
        UnitConversion.to_unit_id == from_unit_id
    ).first()
    if conv_reverse:
        return ResponseModel(data={
            "original_quantity": quantity,
            "converted_quantity": quantity / conv_reverse.ratio,
            "from_unit": db.query(Unit).get(from_unit_id).name,
            "to_unit": db.query(Unit).get(to_unit_id).name,
            "ratio": 1 / conv_reverse.ratio
        })
    # 尝试通过中间单位链式换算
    all_convs = db.query(UnitConversion).filter(UnitConversion.product_id == product_id).all()
    # 构建换算图
    graph = {}
    for c in all_convs:
        graph.setdefault(c.from_unit_id, []).append((c.to_unit_id, c.ratio))
        graph.setdefault(c.to_unit_id, []).append((c.from_unit_id, 1 / c.ratio))
    # BFS 寻找路径
    from collections import deque
    visited = {from_unit_id: 1.0}
    queue = deque([from_unit_id])
    while queue:
        current = queue.popleft()
        if current == to_unit_id:
            break
        for neighbor, ratio in graph.get(current, []):
            if neighbor not in visited:
                visited[neighbor] = visited[current] * ratio
                queue.append(neighbor)
    if to_unit_id in visited:
        total_ratio = visited[to_unit_id]
        return ResponseModel(data={
            "original_quantity": quantity,
            "converted_quantity": quantity * total_ratio,
            "from_unit": db.query(Unit).get(from_unit_id).name,
            "to_unit": db.query(Unit).get(to_unit_id).name,
            "ratio": total_ratio
        })
    raise HTTPException(status_code=400, detail="未找到换算关系")
