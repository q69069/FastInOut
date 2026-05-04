"""装车单路由 — Phase B

装车 = 普通仓库→车仓的库存转移。
审核装车：扣减普通仓库库存，增加车仓库存。
退库：扣减车仓库存，增加普通仓库库存。
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.vehicle_load import VehicleLoad, VehicleLoadItem
from models.warehouse import Warehouse
from models.product import Product
from models.inventory import Inventory
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.status import VehicleLoadStatus

router = APIRouter(prefix="/api", tags=["装车单"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    from utils.auth import decode_access_token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def _gen_load_no(db):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"ZC{today}"
    last = db.query(VehicleLoad).filter(VehicleLoad.load_no.like(f"{prefix}%")).order_by(VehicleLoad.id.desc()).first()
    seq = int(last.load_no[-4:]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


def _update_inventory(db, warehouse_id, product_id, qty_change):
    inv = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.product_id == product_id
    ).first()
    if qty_change > 0:
        if inv:
            inv.quantity += qty_change
        else:
            inv = Inventory(warehouse_id=warehouse_id, product_id=product_id, quantity=qty_change)
            db.add(inv)
    else:
        if not inv or inv.quantity < abs(qty_change):
            raise HTTPException(400, f"仓库库存不足")
        inv.quantity += qty_change


@router.get("/vehicle-loads", response_model=PaginatedResponse)
def list_vehicle_loads(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None), authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    q = db.query(VehicleLoad)
    if status:
        q = q.filter(VehicleLoad.status == status)
    total = q.count()
    items = q.order_by(VehicleLoad.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for load in items:
        fw = db.query(Warehouse).get(load.from_warehouse_id)
        vw = db.query(Warehouse).get(load.vehicle_warehouse_id)
        emp = db.query(Employee).get(load.employee_id) if load.employee_id else None
        load_items = db.query(VehicleLoadItem).filter(VehicleLoadItem.load_id == load.id).all()
        item_list = []
        for li in load_items:
            prod = db.query(Product).get(li.product_id)
            item_list.append({
                "id": li.id, "product_id": li.product_id,
                "product_name": prod.name if prod else "",
                "quantity": li.quantity, "returned_quantity": li.returned_quantity
            })
        result.append({
            "id": load.id, "load_no": load.load_no,
            "from_warehouse_id": load.from_warehouse_id,
            "from_warehouse_name": fw.name if fw else "",
            "vehicle_warehouse_id": load.vehicle_warehouse_id,
            "vehicle_warehouse_name": vw.name if vw else "",
            "employee_id": load.employee_id,
            "employee_name": emp.name if emp else "",
            "status": load.status, "remark": load.remark,
            "created_at": str(load.created_at),
            "loaded_at": str(load.loaded_at) if load.loaded_at else None,
            "returned_at": str(load.returned_at) if load.returned_at else None,
            "items": item_list
        })
    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)


@router.post("/vehicle-loads", response_model=ResponseModel)
def create_vehicle_load(data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    if not data.get("from_warehouse_id") or not data.get("vehicle_warehouse_id"):
        raise HTTPException(400, "请选择来源仓库和目标车仓")
    if not data.get("items"):
        raise HTTPException(400, "请添加装车明细")
    load = VehicleLoad(
        load_no=_gen_load_no(db),
        from_warehouse_id=data["from_warehouse_id"],
        vehicle_warehouse_id=data["vehicle_warehouse_id"],
        employee_id=data.get("employee_id"),
        status="draft",
        remark=data.get("remark"),
        created_by=user.id
    )
    db.add(load)
    db.flush()
    for item in data["items"]:
        db.add(VehicleLoadItem(
            load_id=load.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        ))
    db.commit()
    return ResponseModel(message="装车单创建成功", data={"id": load.id, "load_no": load.load_no})


@router.get("/vehicle-loads/{load_id}", response_model=ResponseModel)
def get_vehicle_load(load_id: int, db: Session = Depends(get_db)):
    load = db.query(VehicleLoad).get(load_id)
    if not load:
        raise HTTPException(404, "装车单不存在")
    fw = db.query(Warehouse).get(load.from_warehouse_id)
    vw = db.query(Warehouse).get(load.vehicle_warehouse_id)
    emp = db.query(Employee).get(load.employee_id) if load.employee_id else None
    items = db.query(VehicleLoadItem).filter(VehicleLoadItem.load_id == load_id).all()
    item_list = []
    for li in items:
        prod = db.query(Product).get(li.product_id)
        item_list.append({
            "id": li.id, "product_id": li.product_id,
            "product_name": prod.name if prod else "",
            "quantity": li.quantity, "returned_quantity": li.returned_quantity
        })
    return ResponseModel(data={
        "id": load.id, "load_no": load.load_no,
        "from_warehouse_id": load.from_warehouse_id,
        "from_warehouse_name": fw.name if fw else "",
        "vehicle_warehouse_id": load.vehicle_warehouse_id,
        "vehicle_warehouse_name": vw.name if vw else "",
        "employee_id": load.employee_id,
        "employee_name": emp.name if emp else "",
        "status": load.status, "remark": load.remark,
        "created_at": str(load.created_at),
        "loaded_at": str(load.loaded_at) if load.loaded_at else None,
        "returned_at": str(load.returned_at) if load.returned_at else None,
        "items": item_list
    })


@router.post("/vehicle-loads/{load_id}/confirm", response_model=ResponseModel)
def confirm_vehicle_load(load_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """审核装车 — 扣减普通仓库库存，增加车仓库存"""
    user = get_current_user(authorization, db)
    load = db.query(VehicleLoad).get(load_id)
    if not load:
        raise HTTPException(404, "装车单不存在")
    if load.status != "draft":
        raise HTTPException(400, f"当前状态 {load.status} 不允许审核")
    items = db.query(VehicleLoadItem).filter(VehicleLoadItem.load_id == load_id).all()
    for item in items:
        _update_inventory(db, load.from_warehouse_id, item.product_id, -item.quantity)
        _update_inventory(db, load.vehicle_warehouse_id, item.product_id, item.quantity)
    load.status = "loaded"
    load.loaded_at = datetime.now()
    db.commit()
    return ResponseModel(message="装车确认成功，库存已转移")


@router.post("/vehicle-loads/{load_id}/return", response_model=ResponseModel)
def return_vehicle_load(load_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """退库 — 扣减车仓库存，增加普通仓库库存"""
    user = get_current_user(authorization, db)
    load = db.query(VehicleLoad).get(load_id)
    if not load:
        raise HTTPException(404, "装车单不存在")
    if load.status != "loaded":
        raise HTTPException(400, f"当前状态 {load.status} 不允许退库")
    items = db.query(VehicleLoadItem).filter(VehicleLoadItem.load_id == load_id).all()
    for item in items:
        return_qty = item.quantity - (item.returned_quantity or 0)
        if return_qty > 0:
            _update_inventory(db, load.vehicle_warehouse_id, item.product_id, -return_qty)
            _update_inventory(db, load.from_warehouse_id, item.product_id, return_qty)
            item.returned_quantity = item.quantity
    load.status = "returned"
    load.returned_at = datetime.now()
    db.commit()
    return ResponseModel(message="退库成功，库存已回退")
