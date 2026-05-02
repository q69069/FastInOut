"""
仓库-路线关联表
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from database import Base


class WarehouseRoute(Base):
    __tablename__ = "warehouse_routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, comment="仓库ID")
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, comment="路线ID")

    __table_args__ = (
        UniqueConstraint('warehouse_id', 'route_id', name='uq_warehouse_route'),
    )
