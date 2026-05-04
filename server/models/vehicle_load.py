"""装车单模型 — Phase B"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class VehicleLoad(Base):
    __tablename__ = "vehicle_loads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    load_no = Column(String(30), unique=True, nullable=False)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    vehicle_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    status = Column(String(20), default="draft")  # draft/pending/loaded/partial_return/returned
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, server_default=func.now())
    loaded_at = Column(DateTime)
    returned_at = Column(DateTime)


class VehicleLoadItem(Base):
    __tablename__ = "vehicle_load_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    load_id = Column(Integer, ForeignKey("vehicle_loads.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    returned_quantity = Column(Float, default=0)
