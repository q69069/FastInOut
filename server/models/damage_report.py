"""报损单模型 — Phase C"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class DamageReport(Base):
    __tablename__ = "damage_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), unique=True, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    report_type = Column(String(20), default="general")  # vehicle/general
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="pending")  # pending/audited/adjusted
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())
    audited_at = Column(DateTime)


class DamageReportItem(Base):
    __tablename__ = "damage_report_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("damage_reports.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0)
    amount = Column(Float, default=0)
    reason = Column(String(200))
