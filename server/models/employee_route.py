"""
业务员-路线关联表
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base


class EmployeeRoute(Base):
    __tablename__ = "employee_routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="业务员ID")
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, comment="路线ID")

    __table_args__ = (
        UniqueConstraint('employee_id', 'route_id', name='uq_employee_route'),
    )
