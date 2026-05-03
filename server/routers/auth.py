import json
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from models.role import Role
from models.module import Module
from models.role_module_permission import RoleModulePermission
from models.operation_permission import OperationPermission
from models.employee_role import EmployeeRole
from schemas.auth import LoginRequest, LoginResponse, CurrentUser
from schemas.common import ResponseModel
from utils.auth import verify_password, create_access_token, decode_access_token
from utils.cache import (
    get_permissions_cache, set_permissions_cache,
    invalidate_user_caches, PERMISSIONS_CACHE_TTL
)
from datetime import datetime, timedelta
import threading

router = APIRouter(prefix="/api/auth", tags=["认证"])

_login_failures = {}
_login_lock = threading.Lock()
MAX_FAILURES = 5
LOCKOUT_MINUTES = 15

_token_blacklist = set()
_blacklist_lock = threading.Lock()


def _check_login_lock(username: str):
    with _login_lock:
        if username not in _login_failures:
            return
        cutoff = datetime.now() - timedelta(minutes=LOCKOUT_MINUTES)
        _login_failures[username] = [t for t in _login_failures[username] if t > cutoff]
        if len(_login_failures[username]) >= MAX_FAILURES:
            remaining = (_login_failures[username][0] + timedelta(minutes=LOCKOUT_MINUTES) - datetime.now()).seconds // 60
            raise HTTPException(status_code=429, detail=f"登录失败次数过多，请{remaining + 1}分钟后再试")
        if not _login_failures[username]:
            del _login_failures[username]


def _record_login_failure(username: str):
    with _login_lock:
        if username not in _login_failures:
            _login_failures[username] = []
        _login_failures[username].append(datetime.now())


def _clear_login_failures(username: str):
    with _login_lock:
        _login_failures.pop(username, None)


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    with _blacklist_lock:
        if token in _token_blacklist:
            raise HTTPException(status_code=401, detail="token已失效，请重新登录")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user or user.status != 1:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


def _get_user_permissions(user: Employee, db: Session) -> tuple:
    """返回 (role_name, permissions_list)"""
    if not user.role_id:
        return None, []
    role = db.query(Role).get(user.role_id)
    if not role:
        return None, []
    try:
        perms = json.loads(role.permissions_json or "[]")
    except (json.JSONDecodeError, TypeError):
        perms = []
    return role.name, perms


def _build_user_permissions(user: Employee, db: Session, filter_role_id: int = None) -> dict:
    """构建完整的用户权限信息"""
    # 获取员工的所有角色
    emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
    role_ids = [er.role_id for er in emp_roles]
    if user.role_id and user.role_id not in role_ids:
        role_ids.append(user.role_id)

    # 如果指定了filter_role_id，只使用该角色
    if filter_role_id:
        if filter_role_id not in role_ids:
            return {"roles": [], "modules": [], "permissions": {}, "operations": [], "warehouse_ids": [], "route_ids": [], "bypass_audit": {}}
        role_ids = [filter_role_id]

    if not role_ids:
        return {"roles": [], "modules": [], "permissions": {}, "operations": [], "warehouse_ids": [], "route_ids": [], "bypass_audit": {}}

    # 获取角色信息
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    # 获取可见模块（并集）
    module_perms = db.query(RoleModulePermission).filter(
        RoleModulePermission.role_id.in_(role_ids),
        RoleModulePermission.can_view == True
    ).all()
    module_ids = set(mp.module_id for mp in module_perms)
    modules = db.query(Module).filter(Module.id.in_(module_ids)).all()
    module_keys = [m.module_key for m in modules]

    # 构建模块权限映射
    perm_map = {}
    for mp in module_perms:
        mod = next((m for m in modules if m.id == mp.module_id), None)
        if mod:
            perm_map[mod.module_key] = {
                "view": mp.can_view,
                "create": mp.can_create,
                "edit": mp.can_edit,
                "delete": mp.can_delete,
                "audit": mp.can_audit,
                "export": mp.can_export,
                "data_scope": mp.data_scope,
            }

    # 获取操作权限（去重）
    op_perms = db.query(OperationPermission).filter(
        OperationPermission.role_id.in_(role_ids),
        OperationPermission.allowed == True
    ).all()
    operations = list(set(op.operation_key for op in op_perms))

    # 解析仓库和路线
    warehouse_ids = []
    if user.warehouse_ids:
        try:
            warehouse_ids = [int(x.strip()) for x in str(user.warehouse_ids).split(",") if x.strip().isdigit()]
        except:
            warehouse_ids = []

    route_ids = []
    if user.route_ids:
        try:
            route_ids = [int(x.strip()) for x in str(user.route_ids).split(",") if x.strip().isdigit()]
        except:
            route_ids = []

    # 解析免审配置
    bypass_audit = {}
    if user.bypass_audit:
        try:
            bypass_audit = json.loads(user.bypass_audit) if isinstance(user.bypass_audit, str) else (user.bypass_audit or {})
        except:
            bypass_audit = {}

    # 构建角色信息
    role_infos = [{"id": r.id, "role_key": r.role_key, "name": r.name} for r in roles]

    return {
        "roles": role_infos,
        "modules": module_keys,
        "permissions": perm_map,
        "operations": operations,
        "warehouse_ids": warehouse_ids,
        "route_ids": route_ids,
        "bypass_audit": bypass_audit,
    }


@router.post("/login", response_model=ResponseModel)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    _check_login_lock(req.username)
    user = db.query(Employee).filter(Employee.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        _record_login_failure(req.username)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已禁用")
    _clear_login_failures(req.username)

    # 构建完整权限信息
    perms = _build_user_permissions(user, db)

    # 登录成功时清除旧缓存（确保权限变更生效）
    invalidate_user_caches(user.id)

    # 构造增强JWT payload
    token = create_access_token(
        {"user_id": user.id, "username": user.username},
        extra={
            "roles": perms["roles"],
            "modules": perms["modules"],
            "permissions": perms["permissions"],
            "operations": perms["operations"],
            "warehouse_ids": perms["warehouse_ids"],
            "route_ids": perms["route_ids"],
            "bypass_audit": perms["bypass_audit"],
        }
    )

    role_name, _ = _get_user_permissions(user, db)
    # 获取所有角色信息
    all_roles = perms.get("roles", [])
    # 主角色为第一个（优先级最高）
    primary_role = all_roles[0] if all_roles else None
    primary_role_id = primary_role.get("id") if primary_role else user.role_id
    primary_role_name = primary_role.get("name") if primary_role else role_name

    return ResponseModel(data=LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username,
        name=user.name,
        position=user.position,
        role_id=primary_role_id,
        role_name=primary_role_name,
        roles=all_roles,
        permissions=perms,
    ))


@router.post("/logout", response_model=ResponseModel)
def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        with _blacklist_lock:
            _token_blacklist.add(token)
    return ResponseModel(message="已退出")


@router.get("/current", response_model=ResponseModel)
def current_user(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    role_name, _ = _get_user_permissions(user, db)
    perms = _build_user_permissions(user, db)
    data = CurrentUser.model_validate(user)
    data.role_name = role_name
    # 获取所有角色信息
    all_roles = perms.get("roles", [])
    primary_role = all_roles[0] if all_roles else None
    data.role_id = primary_role.get("id") if primary_role else user.role_id
    data.roles = all_roles
    data.permissions = perms
    return ResponseModel(data=data)


@router.get("/permissions", response_model=ResponseModel)
def get_permissions(
    role_id: int = None,
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 如果指定了role_id，只返回该角色的权限
    if role_id:
        # 尝试从缓存获取
        cached = get_permissions_cache(user.id, role_id)
        if cached is not None:
            return ResponseModel(data=cached)
        role = db.query(Role).get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        perms = _build_user_permissions(user, db, filter_role_id=role_id)
        set_permissions_cache(user.id, perms, role_id=role_id, ttl=PERMISSIONS_CACHE_TTL)
        return ResponseModel(data=perms)
    # 否则返回所有角色的合并权限
    # 尝试从缓存获取
    cached = get_permissions_cache(user.id)
    if cached is not None:
        return ResponseModel(data=cached)
    perms = _build_user_permissions(user, db)
    set_permissions_cache(user.id, perms, ttl=PERMISSIONS_CACHE_TTL)
    return ResponseModel(data=perms)


@router.get("/modules", response_model=ResponseModel)
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).order_by(Module.sort_order).all()
    return ResponseModel(data=[{
        "id": m.id,
        "module_key": m.module_key,
        "name": m.name,
        "module_type": m.module_type,
        "pc_view": m.pc_view,
        "h5_tab": m.h5_tab,
        "icon": m.icon,
        "path": m.path,
    } for m in modules])
