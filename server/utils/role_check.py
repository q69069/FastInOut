"""统一角色检查工具 — 替代硬编码 role_id 判断

使用方式：
    from utils.role_check import require_role, is_admin, is_owner_or_admin

    # 检查是否为管理员
    if is_admin(user, db): ...

    # 检查是否有指定角色（支持多角色）
    require_role(user, db, "warehouse", "只有仓管可以确认")

    # 检查是否为管理员或创建人
    if not is_owner_or_admin(user, created_by, db): raise HTTPException(403)
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.employee import Employee

# 复用 utils.auth 中已有的基础函数
from utils.auth import has_role as _has_role, is_admin as _is_admin


def is_admin(user: Employee, db: Session) -> bool:
    """检查用户是否为管理员"""
    return _is_admin(user, db)


def has_role(user: Employee, db: Session, *role_keys: str) -> bool:
    """检查用户是否拥有指定角色中的任意一个"""
    return _has_role(user, db, list(role_keys))


def require_role(user: Employee, db: Session, *role_keys: str, message: str = "") -> None:
    """要求用户拥有指定角色，否则抛出 403"""
    if not has_role(user, db, *role_keys):
        roles_str = "/".join(role_keys)
        raise HTTPException(403, message or f"需要 {roles_str} 角色权限")


def is_owner_or_admin(user: Employee, created_by: int, db: Session) -> bool:
    """检查用户是否为管理员或创建人"""
    if _is_admin(user, db):
        return True
    return user.id == created_by


def require_owner_or_admin(user: Employee, created_by: int, db: Session, message: str = "") -> None:
    """要求管理员或创建人，否则抛出 403"""
    if not is_owner_or_admin(user, created_by, db):
        raise HTTPException(403, message or "只有管理员或创建人可以操作")
