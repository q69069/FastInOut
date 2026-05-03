from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="员工ID")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")

    __table_args__ = (
        UniqueConstraint('employee_id', 'role_id', name='uq_employee_role'),
    )
