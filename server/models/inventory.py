from datetime import datetime
from sqlalchemy import text, Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, default=0)
    cost_price = Column(Float, default=0)  # 成本价
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class InventoryCheck(Base):
    __tablename__ = "inventory_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # PD+日期+序号
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    checker_id = Column(Integer, ForeignKey("employees.id"))  # 复核人（轮岗盘点）
    status = Column(Integer, default=1)  # 1=盘点中 2=已确认 3=已作废
    remark = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime)


class InventoryCheckItem(Base):
    __tablename__ = "inventory_check_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey("inventory_checks.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    system_qty = Column(Float, default=0)  # 系统库存
    actual_qty = Column(Float, default=0)  # 实际库存
    diff_qty = Column(Float, default=0)  # 差异
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    unit_quantity = Column(Float, default=1)
    unit_conv_rate = Column(Float, default=1)


class InventoryTransfer(Base):
    __tablename__ = "inventory_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # DB+日期+序号
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    status = Column(Integer, default=1)  # 1=调拨中 2=已确认 3=已取消
    audit_status = Column(String(20), default="pending", comment="审核状态 pending/approved/rejected")
    auditor_id = Column(Integer, ForeignKey("employees.id"), comment="审核人ID")
    audit_time = Column(DateTime, comment="审核时间")
    audit_comment = Column(Text, comment="审核意见")
    remark = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime)


class InventoryTransferItem(Base):
    __tablename__ = "inventory_transfer_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(Integer, ForeignKey("inventory_transfers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    unit_quantity = Column(Float, default=1)
    unit_conv_rate = Column(Float, default=1)


class InventoryAlert(Base):
    __tablename__ = "inventory_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    current_qty = Column(Float, default=0)
    min_qty = Column(Float, default=0)
    max_qty = Column(Float, default=0)
    alert_type = Column(String(20))  # "low" or "high"
    is_handled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class OtherInventoryLog(Base):
    __tablename__ = "other_inventory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    type = Column(String(10))  # in/out
    quantity = Column(Float, default=0)
    reason = Column(String(50))
    remark = Column(String(200))
    created_by = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, default=datetime.now)
