import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.role import Role
from models.module import Module
from models.role_module_permission import RoleModulePermission
from models.operation_permission import OperationPermission
from models.employee import Employee
from models.employee_role import EmployeeRole
from schemas.role import RoleCreate, RoleUpdate, RoleOut, AssignRole
from schemas.common import ResponseModel, PaginatedResponse
from utils.cache import invalidate_user_caches

router = APIRouter(prefix="/api/roles", tags=["角色管理"])


def _invalidate_role_users_cache(db: Session, role_id: int):
    """清除角色关联用户的权限缓存"""
    employees = db.query(Employee).filter(Employee.role_id == role_id).all()
    for emp in employees:
        invalidate_user_caches(emp.id)


DEFAULT_ROLES = [
    {"role_key": "admin", "name": "老板/管理员", "description": "全部功能+系统设置", "permissions_json": '["*"]'},
    {"role_key": "supervisor", "name": "主管/文员", "description": "档案+采购+销售+报表", "permissions_json": '["supervisor"]'},
    {"role_key": "sales", "name": "业务员", "description": "销售业务人员", "permissions_json": '["sales"]'},
    {"role_key": "finance", "name": "财务", "description": "财务人员", "permissions_json": '["finance"]'},
    {"role_key": "warehouse", "name": "库管", "description": "仓库管理人员", "permissions_json": '["warehouse"]'},
]

DEFAULT_MODULES = [
    {"module_key": "home", "name": "首页", "module_type": "page", "pc_view": True, "h5_tab": "首页", "path": "/home", "icon": "HomeFilled", "sort_order": 1},
    {"module_key": "dashboard", "name": "数据看板", "module_type": "page", "pc_view": True, "h5_tab": "看板", "path": "/dashboard", "icon": "DataAnalysis", "sort_order": 2},
    {"module_key": "customers", "name": "客户管理", "module_type": "page", "pc_view": True, "h5_tab": "客户", "path": "/customers", "icon": "User", "sort_order": 3},
    {"module_key": "sales", "name": "销售订单", "module_type": "page", "pc_view": True, "h5_tab": "销售", "path": "/sales", "icon": "ShoppingCart", "sort_order": 4},
    {"module_key": "inventory", "name": "库存管理", "module_type": "page", "pc_view": True, "h5_tab": "库存", "path": "/inventory", "icon": "Box", "sort_order": 5},
    {"module_key": "purchases", "name": "采购管理", "module_type": "page", "pc_view": True, "path": "/purchases", "icon": "Truck", "sort_order": 6},
    {"module_key": "suppliers", "name": "供应商", "module_type": "page", "pc_view": True, "path": "/suppliers", "icon": "Store", "sort_order": 7},
    {"module_key": "finance", "name": "财务管理", "module_type": "page", "pc_view": True, "path": "/finance", "icon": "Money", "sort_order": 8},
    {"module_key": "employees", "name": "员工管理", "module_type": "page", "pc_view": True, "path": "/employees", "icon": "UserFilled", "sort_order": 9},
    {"module_key": "roles", "name": "角色权限", "module_type": "page", "pc_view": True, "path": "/roles", "icon": "Key", "sort_order": 10},
    {"module_key": "products", "name": "商品管理", "module_type": "page", "pc_view": True, "path": "/products", "icon": "Goods", "sort_order": 11},
    {"module_key": "warehouses", "name": "仓库管理", "module_type": "page", "pc_view": True, "path": "/warehouses", "icon": "OfficeBuilding", "sort_order": 12},
    {"module_key": "batches", "name": "批次管理", "module_type": "page", "pc_view": True, "path": "/batches", "icon": "Barcode", "sort_order": 13},
    {"module_key": "promotions", "name": "促销管理", "module_type": "page", "pc_view": True, "path": "/promotions", "icon": "Gift", "sort_order": 14},
    {"module_key": "reports", "name": "报表统计", "module_type": "page", "pc_view": True, "path": "/reports", "icon": "TrendCharts", "sort_order": 15},
    {"module_key": "system", "name": "系统设置", "module_type": "page", "pc_view": True, "path": "/system", "icon": "Setting", "sort_order": 16},
    {"module_key": "performance", "name": "业绩查看", "module_type": "page", "pc_view": True, "h5_tab": "业绩", "path": "/performance", "icon": "TrendCharts", "sort_order": 17},
    {"module_key": "tools", "name": "工具", "module_type": "page", "pc_view": True, "h5_tab": "工具", "path": "/tools", "icon": "Tools", "sort_order": 18},
    {"module_key": "profile", "name": "我的", "module_type": "page", "pc_view": False, "h5_tab": "我的", "path": "/profile", "icon": "User", "sort_order": 19},
]

DEFAULT_ROLE_PERMISSIONS = {
    "admin": {
        "home": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "dashboard": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "customers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "sales": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "inventory": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "purchases": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "suppliers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "finance": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "employees": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "roles": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "products": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "warehouses": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "batches": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "promotions": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "reports": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "system": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "performance": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "tools": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "profile": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
    },
    "sales": {
        "home": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "dashboard": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "self"},
        "customers": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "route"},
        "sales": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "self"},
        "inventory": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "reports": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "self"},
        "performance": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
        "tools": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
        "profile": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
    },
    "warehouse": {
        "home": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "inventory": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "warehouses": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "batches": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "products": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "tools": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "warehouse"},
        "profile": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
    },
    "finance": {
        "home": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "dashboard": {"can_view": True, "can_create": True, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "customers": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "finance": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": True, "can_audit": True, "can_export": True, "data_scope": "all"},
        "reports": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "products": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "tools": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
        "profile": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
    },
    "supervisor": {
        "home": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "dashboard": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "all"},
        "customers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": True, "can_export": True, "data_scope": "warehouse"},
        "sales": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": True, "can_export": True, "data_scope": "warehouse"},
        "inventory": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "purchases": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": True, "can_export": True, "data_scope": "warehouse"},
        "suppliers": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": True, "can_export": True, "data_scope": "warehouse"},
        "products": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "warehouses": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "batches": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "promotions": {"can_view": True, "can_create": True, "can_edit": True, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "reports": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": True, "data_scope": "warehouse"},
        "tools": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
        "profile": {"can_view": True, "can_create": False, "can_edit": False, "can_delete": False, "can_audit": False, "can_export": False, "data_scope": "self"},
    },
}

DEFAULT_OPERATIONS = {
    "admin": ["*"],
    "sales": ["sales:create", "sales:edit", "customers:create", "customers:edit", "inventory:view", "reports:view", "performance:view"],
    "warehouse": ["inventory:view", "inventory:adjust", "inventory:transfer", "warehouse:view", "batches:view"],
    "finance": ["finance:view", "finance:create", "finance:audit", "reports:view", "customers:view"],
    "supervisor": ["customers:create", "customers:edit", "customers:view", "sales:create", "sales:edit", "sales:view", "sales:audit", "inventory:view", "purchases:view", "suppliers:view", "reports:view"],
}


def init_default_roles(db: Session):
    ROLE_KEY_MAP = {
        "管理员": "admin",
        "业务员": "sales",
        "仓管": "warehouse",
        "财务": "finance",
    }
    for role_data in DEFAULT_ROLES:
        # 先按 role_key 查
        existing = db.query(Role).filter(Role.role_key == role_data["role_key"]).first()
        if existing:
            # 更新旧数据
            if not existing.role_key:
                existing.role_key = role_data["role_key"]
            continue
        # 再按 name 查（兼容旧数据）
        existing_by_name = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing_by_name:
            existing_by_name.role_key = role_data["role_key"]
            continue
        db.add(Role(**role_data))
    db.commit()


def init_modules(db: Session):
    for m in DEFAULT_MODULES:
        existing = db.query(Module).filter(Module.module_key == m["module_key"]).first()
        if not existing:
            db.add(Module(**m))
    db.commit()


def init_role_permissions(db: Session):
    for role_key, module_perms in DEFAULT_ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.role_key == role_key).first()
        if not role:
            continue
        for mod_key, perm in module_perms.items():
            module = db.query(Module).filter(Module.module_key == mod_key).first()
            if not module:
                continue
            existing = db.query(RoleModulePermission).filter(
                RoleModulePermission.role_id == role.id,
                RoleModulePermission.module_id == module.id
            ).first()
            if not existing:
                db.add(RoleModulePermission(role_id=role.id, module_id=module.id, **perm))
    db.commit()

    for role_key, operations in DEFAULT_OPERATIONS.items():
        role = db.query(Role).filter(Role.role_key == role_key).first()
        if not role:
            continue
        for op_key in operations:
            existing = db.query(OperationPermission).filter(
                OperationPermission.role_id == role.id,
                OperationPermission.operation_key == op_key
            ).first()
            if not existing:
                allowed = True if op_key == "*" else False
                data_scope = "all" if op_key == "*" else "self"
                db.add(OperationPermission(role_id=role.id, operation_key=op_key, allowed=allowed, data_scope=data_scope))
    db.commit()


def _role_to_out(role: Role, db: Session) -> RoleOut:
    # 获取模块权限
    module_perms = db.query(RoleModulePermission).filter(
        RoleModulePermission.role_id == role.id
    ).all()
    module_permissions = []
    for mp in module_perms:
        mod = db.query(Module).get(mp.module_id)
        if mod:
            module_permissions.append({
                "module_key": mod.module_key,
                "can_view": mp.can_view,
                "can_create": mp.can_create,
                "can_edit": mp.can_edit,
                "can_delete": mp.can_delete,
                "can_audit": mp.can_audit,
                "can_export": mp.can_export,
                "data_scope": mp.data_scope,
            })

    # 获取操作权限
    op_perms = db.query(OperationPermission).filter(
        OperationPermission.role_id == role.id,
        OperationPermission.allowed == True
    ).all()
    operations = [op.operation_key for op in op_perms]

    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        role_key=role.role_key,
        module_permissions=module_permissions,
        operations=operations,
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
        data=[_role_to_out(i, db) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/all", response_model=ResponseModel)
def list_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.id).all()
    return ResponseModel(data=[_role_to_out(r, db) for r in roles])


@router.post("", response_model=ResponseModel)
def create_role(req: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    role = Role(
        name=req.name,
        description=req.description,
        role_key=req.role_key,
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    # 保存模块权限
    for mp in req.module_permissions:
        mod = db.query(Module).filter(Module.module_key == mp.module_key).first()
        if mod:
            db.add(RoleModulePermission(
                role_id=role.id,
                module_id=mod.id,
                can_view=mp.can_view,
                can_create=mp.can_create,
                can_edit=mp.can_edit,
                can_delete=mp.can_delete,
                can_audit=mp.can_audit,
                can_export=mp.can_export,
                data_scope=mp.data_scope,
            ))

    # 保存操作权限
    for op_key in req.operations:
        db.add(OperationPermission(
            role_id=role.id,
            operation_key=op_key,
            allowed=True,
        ))

    db.commit()
    return ResponseModel(data=_role_to_out(role, db))


@router.put("/{role_id}", response_model=ResponseModel)
def update_role(role_id: int, req: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if req.name is not None:
        role.name = req.name
    if req.description is not None:
        role.description = req.description
    db.commit()

    # 更新模块权限
    if req.module_permissions is not None:
        # 删除旧的
        db.query(RoleModulePermission).filter(RoleModulePermission.role_id == role_id).delete()
        # 添加新的
        for mp in req.module_permissions:
            mod = db.query(Module).filter(Module.module_key == mp.module_key).first()
            if mod:
                db.add(RoleModulePermission(
                    role_id=role.id,
                    module_id=mod.id,
                    can_view=mp.can_view,
                    can_create=mp.can_create,
                    can_edit=mp.can_edit,
                    can_delete=mp.can_delete,
                    can_audit=mp.can_audit,
                    can_export=mp.can_export,
                    data_scope=mp.data_scope,
                ))

    # 更新操作权限
    if req.operations is not None:
        # 删除旧的
        db.query(OperationPermission).filter(OperationPermission.role_id == role_id).delete()
        # 添加新的
        for op_key in req.operations:
            db.add(OperationPermission(
                role_id=role.id,
                operation_key=op_key,
                allowed=True,
            ))

    db.commit()
    # 清除该角色关联的所有用户的权限缓存
    _invalidate_role_users_cache(db, role_id)
    return ResponseModel(data=_role_to_out(role, db))


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
    # 清除该员工的权限缓存
    invalidate_user_caches(req.employee_id)
    return ResponseModel(message=f"已将 {employee.name} 分配为 {role.name}")
