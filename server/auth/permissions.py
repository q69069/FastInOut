from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from auth.permission_service import PermissionService


class PermissionChecker:
    """统一权限检查器"""

    def __init__(self, module_key: str = None, operation: str = None):
        self.module_key = module_key
        self.operation = operation

    async def __call__(self, request: Request, current_user: Employee = Depends(get_db.__self__), db: Session = Depends(get_db)):
        # 注：这里简化处理，实际需要通过get_current_user获取current_user
        pass


def require_module(module_key: str):
    """模块权限检查装饰器"""
    def decorator(func):
        func._require_module = module_key
        return func
    return decorator


def require_operation(operation: str):
    """操作权限检查装饰器"""
    def decorator(func):
        func._require_operation = operation
        return func
    return decorator


class DataFilter:
    """数据权限过滤器"""

    @staticmethod
    def apply_scope(query, model, user, db: Session, scope_field: str = None, module_key: str = None):
        """根据 data_scope 自动添加 WHERE 条件"""
        if not user:
            return query.filter(model.id == -1)  # 无用户返回空

        data_scope = PermissionService.get_data_scope(user, db, module_key or "")
        scope_field = scope_field or "route_id"

        if data_scope == "all":
            return query  # 全部数据

        elif data_scope == "route":
            route_ids = []
            if user.route_ids:
                try:
                    route_ids = [int(x.strip()) for x in str(user.route_ids).split(",") if x.strip().isdigit()]
                except:
                    pass
            if route_ids and hasattr(model, scope_field):
                return query.filter(getattr(model, scope_field).in_(route_ids))
            return query.filter(model.created_by == user.id)  # fallback

        elif data_scope == "warehouse":
            warehouse_ids = []
            if user.warehouse_ids:
                try:
                    warehouse_ids = [int(x.strip()) for x in str(user.warehouse_ids).split(",") if x.strip().isdigit()]
                except:
                    pass
            if warehouse_ids and hasattr(model, "warehouse_id"):
                return query.filter(model.warehouse_id.in_(warehouse_ids))
            return query.filter(model.created_by == user.id)

        elif data_scope == "self":
            return query.filter(model.created_by == user.id)

        elif data_scope == "none":
            return query.filter(model.id == -1)  # 返回空

        return query
