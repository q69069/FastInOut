"""
权限检查中间件和工具
"""
from functools import wraps
from fastapi import HTTPException


def require_permissions(*required_permissions):
    """
    装饰器：检查用户是否具有所需权限
    用法：@require_permissions("sales.create", "sales.delete")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 current_user
            current_user = kwargs.get('current_user')
            if not current_user:
                # 如果没有 current_user 参数，尝试从 request 获取
                request = kwargs.get('request')
                if request:
                    from routers.auth import get_current_user_from_request
                    current_user = await get_current_user_from_request(request)

            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")

            # 检查权限
            user_permissions = get_user_permissions(current_user)
            for perm in required_permissions:
                if perm not in user_permissions and current_user.role_type != 'admin':
                    raise HTTPException(status_code=403, detail=f"缺少权限: {perm}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(user) -> list:
    """
    获取用户的权限列表
    从 role.permissions_json 或 role_type 推导
    """
    permissions = set()

    # admin 具有所有权限
    if getattr(user, 'role_type', None) == 'admin':
        return '*'

    # 根据 role_type 添加基础权限
    role_type = getattr(user, 'role_type', None)
    if role_type == 'sales':
        permissions.update([
            'sales.read', 'sales.create', 'sales.update', 'sales.delete',
            'customer.read', 'customer.create', 'customer.update',
            'order.read', 'order.create', 'order.update',
        ])
    elif role_type == 'warehouse':
        permissions.update([
            'inventory.read', 'inventory.update',
            'stock.read', 'stock.update',
            'warehouse.read',
        ])
    elif role_type == 'finance':
        permissions.update([
            'finance.read', 'finance.create', 'finance.update',
            'customer.read', 'supplier.read',
            'report.read',
        ])

    # 如果有 role.permissions_json，解析并添加
    role_perms = getattr(user, 'permissions_json', None) or getattr(user, 'role', None, None)
    if role_perms:
        import json
        try:
            extra_perms = json.loads(role_perms) if isinstance(role_perms, str) else role_perms
            permissions.update(extra_perms)
        except (json.JSONDecodeError, TypeError):
            pass

    return list(permissions)


def check_module_permission(user, module: str, action: str = 'read') -> bool:
    """
    检查用户对某个模块是否有指定操作的权限
    """
    if getattr(user, 'role_type', None) == 'admin':
        return True

    permission = f"{module}.{action}"
    user_permissions = get_user_permissions(user)

    return permission in user_permissions or '*' in user_permissions
