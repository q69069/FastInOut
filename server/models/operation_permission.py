from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from database import Base


class OperationPermission(Base):
    __tablename__ = "operation_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    operation_key = Column(String(50), nullable=False, comment="操作标识")
    allowed = Column(Boolean, default=False, comment="是否允许")
    data_scope = Column(String(20), default="all", comment="数据范围")

    __table_args__ = (
        UniqueConstraint('role_id', 'operation_key', name='uq_role_operation'),
    )
