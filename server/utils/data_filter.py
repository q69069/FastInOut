from sqlalchemy.orm import Session
from models.employee import Employee


class DataFilter:
    """根据用户角色自动过滤数据的工具类"""

    @staticmethod
    def get_data_scope(user: Employee, db: Session, module_key: str = None) -> str:
        """获取用户的数据权限范围"""
        if not user:
            return "none"

        # 管理员看全部
        if user.role_id:
            from models.role import Role
            role = db.query(Role).get(user.role_id)
            if role and role.role_key == "admin":
                return "all"

        # 检查是否有模块权限决定数据范围
        # 简单逻辑：先检查user.route_ids和warehouse_ids
        if user.route_ids or user.warehouse_ids:
            # 有路线或仓库绑定，按route过滤
            return "route"
        return "self"

    @staticmethod
    def apply_scope(query, model, user: Employee, db: Session, scope_field: str = None, module_key: str = None):
        """
        根据 data_scope 自动添加 WHERE 条件

        scope_field: 过滤字段名，默认 route_id
        module_key: 模块key，用于确定权限
        """
        if not user:
            return query.filter(model.id == -1)  # 无用户返回空

        scope_field = scope_field or "route_id"
        data_scope = DataFilter.get_data_scope(user, db, module_key)

        if data_scope == "all":
            return query  # 全部数据

        elif data_scope == "route":
            route_ids = DataFilter._parse_ids(user.route_ids)
            if route_ids and hasattr(model, scope_field):
                return query.filter(getattr(model, scope_field).in_(route_ids))
            # fallback: 按创建人过滤
            return query.filter(model.created_by == user.id)

        elif data_scope == "warehouse":
            warehouse_ids = DataFilter._parse_ids(user.warehouse_ids)
            if warehouse_ids and hasattr(model, "warehouse_id"):
                return query.filter(model.warehouse_id.in_(warehouse_ids))
            return query.filter(model.created_by == user.id)

        elif data_scope == "self":
            return query.filter(model.created_by == user.id)

        elif data_scope == "none":
            return query.filter(model.id == -1)  # 返回空

        return query

    @staticmethod
    def _parse_ids(ids_str) -> list:
        """解析逗号分隔的ID字符串"""
        if not ids_str:
            return []
        try:
            return [int(x.strip()) for x in str(ids_str).split(",") if x.strip().isdigit()]
        except:
            return []