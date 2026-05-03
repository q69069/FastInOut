from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from database import Base


class RoleModulePermission(Base):
    __tablename__ = "role_module_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, comment="模块ID")
    can_view = Column(Boolean, default=True, comment="可见")
    can_create = Column(Boolean, default=False, comment="新增")
    can_edit = Column(Boolean, default=False, comment="编辑")
    can_delete = Column(Boolean, default=False, comment="删除")
    can_audit = Column(Boolean, default=False, comment="审核")
    can_export = Column(Boolean, default=False, comment="导出")
    data_scope = Column(String(20), default="all", comment="数据范围: all/self/route/warehouse/none")

    __table_args__ = (
        UniqueConstraint('role_id', 'module_id', name='uq_role_module'),
    )
