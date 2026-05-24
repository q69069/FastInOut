from fastapi import HTTPException
from models.unit import UnitConversion
from models.product import Product
from collections import deque


def resolve_by_unit_level(product_id, unit_level, unit_quantity, unit_conv_rate, db):
    """基于产品三单位体系的换算，返回 (base_qty, conv_rate)。

    unit_level: 'small' / 'medium' / 'large'
    unit_quantity: 用户选择的单位下的数量
    unit_conv_rate: 前端传来的换算率（1个该单位 = N个基本单位）
    """
    if not unit_level or unit_level == 'small':
        return unit_quantity, 1.0

    product = db.query(Product).get(product_id)
    if not product:
        return unit_quantity, 1.0

    # 优先用前端传来的 conv_rate（已经基于产品配置计算好了）
    if unit_conv_rate and unit_conv_rate > 0:
        return unit_quantity * unit_conv_rate, unit_conv_rate

    # 回退：从产品字段取
    if unit_level == 'medium' and product.medium_conv_rate:
        return unit_quantity * product.medium_conv_rate, product.medium_conv_rate
    if unit_level == 'large' and product.large_conv_rate:
        return unit_quantity * product.large_conv_rate, product.large_conv_rate

    return unit_quantity, 1.0


def find_conversion_rate(product_id, from_unit_id, to_unit_id, db):
    """BFS 查找从 from_unit 到 to_unit 的累积换算率。未找到返回 None。"""
    if from_unit_id == to_unit_id:
        return 1.0

    all_convs = db.query(UnitConversion).filter(
        UnitConversion.product_id == product_id
    ).all()

    graph = {}
    for c in all_convs:
        graph.setdefault(c.from_unit_id, []).append((c.to_unit_id, c.ratio))
        graph.setdefault(c.to_unit_id, []).append((c.from_unit_id, 1 / c.ratio))

    visited = {from_unit_id: 1.0}
    queue = deque([from_unit_id])
    while queue:
        current = queue.popleft()
        if current == to_unit_id:
            return visited[current]
        for neighbor, ratio in graph.get(current, []):
            if neighbor not in visited:
                visited[neighbor] = visited[current] * ratio
                queue.append(neighbor)
    return None


def resolve_unit_conversion(product_id, unit_id, unit_quantity, db):
    """将选中单位数量换算为基本单位数量。返回 (base_qty, conv_rate)。"""
    if not unit_id:
        return unit_quantity, 1.0
    product = db.query(Product).get(product_id)
    if not product or not product.base_unit_id or unit_id == product.base_unit_id:
        return unit_quantity, 1.0
    rate = find_conversion_rate(product_id, unit_id, product.base_unit_id, db)
    if not rate:
        raise HTTPException(status_code=400, detail="未找到该单位到基本单位的换算关系")
    return unit_quantity * rate, rate


def get_product_available_units(product_id, db):
    """返回商品所有可用单位及到基本单位的换算率列表。"""
    from models.unit import Unit
    product = db.query(Product).get(product_id)
    if not product:
        return []

    result = []
    base_unit_id = product.base_unit_id
    if base_unit_id:
        base_unit = db.query(Unit).get(base_unit_id)
        result.append({
            "unit_id": base_unit_id,
            "unit_name": base_unit.name if base_unit else product.unit,
            "is_base": True,
            "conv_rate": 1.0
        })
    elif product.unit:
        result.append({
            "unit_id": None,
            "unit_name": product.unit,
            "is_base": True,
            "conv_rate": 1.0
        })

    if not base_unit_id:
        return result

    all_convs = db.query(UnitConversion).filter(
        UnitConversion.product_id == product_id
    ).all()

    graph = {}
    for c in all_convs:
        graph.setdefault(c.from_unit_id, []).append((c.to_unit_id, c.ratio))
        graph.setdefault(c.to_unit_id, []).append((c.from_unit_id, 1 / c.ratio))

    visited = {base_unit_id: 1.0}
    queue = deque([base_unit_id])
    while queue:
        current = queue.popleft()
        for neighbor, ratio in graph.get(current, []):
            if neighbor not in visited:
                visited[neighbor] = visited[current] * ratio
                queue.append(neighbor)

    for uid, rate_to_base in visited.items():
        if uid == base_unit_id:
            continue
        unit = db.query(Unit).get(uid)
        if unit:
            result.append({
                "unit_id": uid,
                "unit_name": unit.name,
                "is_base": False,
                "conv_rate": 1.0 / rate_to_base if rate_to_base else 1.0
            })

    return result
