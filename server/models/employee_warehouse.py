"""
业务员-仓库关联表
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base


class EmployeeWarehouse(Base):
    __tablename__ = "employee_warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="业务员ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")

    __table_args__ = (
        UniqueConstraint('employee_id', 'warehouse_id', name='uq_employee_warehouse'),
    )
