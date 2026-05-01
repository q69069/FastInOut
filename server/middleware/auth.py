import json
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from models.role import Role
from routers.auth import get_current_user


def require_permission(permission: str):
    """权限校验依赖，用于 FastAPI 路由"""
    def dependency(
        current_user: Employee = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not current_user.role_id:
            raise HTTPException(status_code=403, detail="未分配角色，请联系管理员")
        role = db.query(Role).get(current_user.role_id)
        if not role:
            raise HTTPException(status_code=403, detail="角色不存在")
        try:
            permissions = json.loads(role.permissions_json)
        except (json.JSONDecodeError, TypeError):
            permissions = []
        if "*" in permissions:
            return current_user
        if permission not in permissions:
            raise HTTPException(status_code=403, detail=f"权限不足，需要: {permission}")
        return current_user
    return Depends(dependency)
