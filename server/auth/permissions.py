from fastapi import Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from utils.auth import decode_access_token


class PermissionContext:
    """从JWT解析的用户权限上下文"""
    def __init__(self, payload: dict):
        self.user_id = payload.get("user_id")
        self.username = payload.get("username")
        self.roles = payload.get("roles", [])
        self.modules = payload.get("modules", [])
        self.permissions = payload.get("permissions", {})
        self.operations = payload.get("operations", [])
        self.warehouse_ids = payload.get("warehouse_ids", [])
        self.route_ids = payload.get("route_ids", [])
        self.bypass_audit = payload.get("bypass_audit", {})

    @property
    def is_admin(self):
        return any(r.get("role_key") == "admin" for r in self.roles)


def get_permission_context(authorization: str = Header(None)) -> PermissionContext:
    """从Authorization头解析权限上下文"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    return PermissionContext(payload)


class PermissionChecker:
    """统一权限检查器"""

    def __init__(self, module_key: str = None, operation: str = None):
        self.module_key = module_key
        self.operation = operation

    async def __call__(self, request: Request, ctx: PermissionContext = Depends(get_permission_context)):
        # 检查模块权限
        if self.module_key and self.module_key not in ctx.modules and not ctx.is_admin:
            raise HTTPException(status_code=403, detail=f"无权访问模块: {self.module_key}")
        # 检查操作权限
        if self.operation and self.operation not in ctx.operations and not ctx.is_admin:
            raise HTTPException(status_code=403, detail=f"无权执行操作: {self.operation}")
        return ctx


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
