from sqlalchemy.orm import Session
from models.module import Module
from models.role_module_permission import RoleModulePermission
from models.operation_permission import OperationPermission
from models.employee_role import EmployeeRole
from models.employee import Employee
from models.role import Role
from functools import lru_cache
from typing import Optional


class PermissionService:
    """权限查询服务（带缓存）"""

    @staticmethod
    def get_user_roles(user: Employee, db: Session) -> list[dict]:
        """获取用户所有角色信息"""
        emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
        role_ids = [er.role_id for er in emp_roles]
        if user.role_id and user.role_id not in role_ids:
            role_ids.append(user.role_id)
        if not role_ids:
            return []
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        return [{"id": r.id, "role_key": r.role_key, "name": r.name} for r in roles]

    @staticmethod
    def get_user_modules(user: Employee, db: Session) -> list[str]:
        """获取用户可见模块列表"""
        emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
        role_ids = [er.role_id for er in emp_roles]
        if user.role_id and user.role_id not in role_ids:
            role_ids.append(user.role_id)
        if not role_ids:
            return []
        perms = db.query(RoleModulePermission).filter(
            RoleModulePermission.role_id.in_(role_ids),
            RoleModulePermission.can_view == True
        ).all()
        module_ids = list(set(p.module_id for p in perms))
        if not module_ids:
            return []
        modules = db.query(Module).filter(Module.id.in_(module_ids)).all()
        return [m.module_key for m in modules]

    @staticmethod
    def get_user_permissions(user: Employee, db: Session) -> dict[str, dict]:
        """获取用户模块权限映射"""
        emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
        role_ids = [er.role_id for er in emp_roles]
        if user.role_id and user.role_id not in role_ids:
            role_ids.append(user.role_id)
        if not role_ids:
            return {}
        perms = db.query(RoleModulePermission).filter(
            RoleModulePermission.role_id.in_(role_ids)
        ).all()
        result = {}
        for p in perms:
            mod = db.query(Module).get(p.module_id)
            if mod:
                key = mod.module_key
                if key not in result:
                    result[key] = {
                        "view": False, "create": False, "edit": False,
                        "delete": False, "audit": False, "export": False,
                        "data_scope": "none"
                    }
                # 取并集（最宽松）
                if p.can_view:
                    result[key]["view"] = True
                if p.can_create:
                    result[key]["create"] = True
                if p.can_edit:
                    result[key]["edit"] = True
                if p.can_delete:
                    result[key]["delete"] = True
                if p.can_audit:
                    result[key]["audit"] = True
                if p.can_export:
                    result[key]["export"] = True
                # data_scope取最宽松
                scope_order = {"all": 5, "route": 4, "warehouse": 3, "self": 2, "none": 1}
                cur = scope_order.get(result[key]["data_scope"], 0)
                new = scope_order.get(p.data_scope or "all", 0)
                if new > cur:
                    result[key]["data_scope"] = p.data_scope
        return result

    @staticmethod
    def get_user_operations(user: Employee, db: Session) -> list[str]:
        """获取用户可执行操作列表"""
        emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
        role_ids = [er.role_id for er in emp_roles]
        if user.role_id and user.role_id not in role_ids:
            role_ids.append(user.role_id)
        if not role_ids:
            return []
        perms = db.query(OperationPermission).filter(
            OperationPermission.role_id.in_(role_ids),
            OperationPermission.allowed == True
        ).all()
        ops = set()
        for p in perms:
            if p.operation_key == "*":
                return ["*"]
            ops.add(p.operation_key)
        return list(ops)

    @staticmethod
    def can_operation(user: Employee, db: Session, operation: str) -> bool:
        """检查用户是否有某操作权限"""
        ops = PermissionService.get_user_operations(user, db)
        return "*" in ops or operation in ops

    @staticmethod
    def get_data_scope(user: Employee, db: Session, module_key: str) -> str:
        """获取用户在某模块的数据范围"""
        perms = PermissionService.get_user_permissions(user, db)
        if module_key in perms:
            return perms[module_key].get("data_scope", "none")
        return "none"
