import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.role import Role
from models.employee import Employee
from schemas.role import RoleCreate, RoleUpdate, RoleOut, AssignRole
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/roles", tags=["角色管理"])

DEFAULT_ROLES = [
    {"name": "管理员", "description": "系统管理员，拥有所有权限", "permissions_json": '["*"]'},
    {"name": "业务员", "description": "销售业务人员", "permissions_json": '["sales","customers","products_view","reports_view"]'},
    {"name": "仓管", "description": "仓库管理人员", "permissions_json": '["inventory","warehouses","purchases","transfers"]'},
    {"name": "财务", "description": "财务人员", "permissions_json": '["finance","reports","customers_view","suppliers_view"]'},
]


def init_default_roles(db: Session):
    for role_data in DEFAULT_ROLES:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            db.add(Role(**role_data))
    db.commit()


def _role_to_out(role: Role) -> RoleOut:
    try:
        perms = json.loads(role.permissions_json or "[]")
    except (json.JSONDecodeError, TypeError):
        perms = []
    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=perms,
        created_at=role.created_at,
    )


@router.get("", response_model=PaginatedResponse)
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(Role)
    total = q.count()
    items = q.order_by(Role.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[_role_to_out(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/all", response_model=ResponseModel)
def list_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.id).all()
    return ResponseModel(data=[_role_to_out(r) for r in roles])


@router.post("", response_model=ResponseModel)
def create_role(req: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    role = Role(
        name=req.name,
        description=req.description,
        permissions_json=json.dumps(req.permissions, ensure_ascii=False),
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return ResponseModel(data=_role_to_out(role))


@router.put("/{role_id}", response_model=ResponseModel)
def update_role(role_id: int, req: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if req.name is not None:
        role.name = req.name
    if req.description is not None:
        role.description = req.description
    if req.permissions is not None:
        role.permissions_json = json.dumps(req.permissions, ensure_ascii=False)
    db.commit()
    db.refresh(role)
    return ResponseModel(data=_role_to_out(role))


@router.delete("/{role_id}", response_model=ResponseModel)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    used = db.query(Employee).filter(Employee.role_id == role_id).first()
    if used:
        raise HTTPException(status_code=400, detail="该角色下有员工，无法删除")
    db.delete(role)
    db.commit()
    return ResponseModel(message="删除成功")


@router.post("/assign", response_model=ResponseModel)
def assign_role(req: AssignRole, db: Session = Depends(get_db)):
    employee = db.query(Employee).get(req.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    role = db.query(Role).get(req.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    employee.role_id = req.role_id
    db.commit()
    return ResponseModel(message=f"已将 {employee.name} 分配为 {role.name}")
