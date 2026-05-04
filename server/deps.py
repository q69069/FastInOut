"""统一认证依赖 — 所有 router 共用

使用方式：
    from deps import get_current_user, require_admin, require_module

    @router.get("/xxx")
    def xxx(user: Employee = Depends(get_current_user)):
        ...

    @router.post("/xxx")
    def xxx(user: Employee = Depends(require_module("purchases"))):
        ...
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from utils.auth import decode_access_token, has_role, is_admin


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    """从 Authorization 头解析当前登录用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee | None:
    """可选认证：未登录返回 None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        return None
    return db.query(Employee).get(payload.get("user_id"))


def _make_role_dep(*role_keys: str):
    """创建角色检查依赖"""
    async def dep(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)) -> Employee:
        if is_admin(user, db):
            return user
        if not has_role(user, db, list(role_keys)):
            roles_str = "/".join(role_keys)
            raise HTTPException(403, f"需要 {roles_str} 角色权限")
        return user
    return dep


def _make_module_dep(module_key: str):
    """创建模块权限检查依赖"""
    async def dep(user: Employee = Depends(get_current_user), db: Session = Depends(get_db)) -> Employee:
        from auth.permission_service import PermissionService
        modules = PermissionService.get_user_modules(user, db)
        if module_key not in modules and not is_admin(user, db):
            raise HTTPException(403, f"无权访问模块: {module_key}")
        return user
    return dep


# 预定义常用角色依赖
require_admin_dep = _make_role_dep("admin")
require_sales_dep = _make_role_dep("sales", "admin")
require_warehouse_dep = _make_role_dep("warehouse", "admin")
require_finance_dep = _make_role_dep("finance", "admin")
require_sales_or_clerk_dep = _make_role_dep("sales", "clerk", "admin")
require_warehouse_or_clerk_dep = _make_role_dep("warehouse", "clerk", "admin")


def require_role(user: Employee, db: Session, *role_keys: str, message: str = ""):
    """命令式角色检查（用于函数内部）"""
    if is_admin(user, db):
        return
    if not has_role(user, db, list(role_keys)):
        roles_str = "/".join(role_keys)
        raise HTTPException(403, message or f"需要 {roles_str} 角色权限")


def require_owner_or_admin(user: Employee, created_by: int, db: Session, message: str = ""):
    """命令式：管理员或创建人"""
    if is_admin(user, db):
        return
    if user.id != created_by:
        raise HTTPException(403, message or "只有管理员或创建人可以操作")
