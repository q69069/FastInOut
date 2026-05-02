"""
车销相关表
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class VehicleSalesOut(Base):
    """车销出库单"""
    __tablename__ = "vehicle_sales_outs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, comment="单号")

    employee_id = Column(Integer, ForeignKey("employees.id"), comment="业务员ID")
    vehicle_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="车仓ID")

    total_amount = Column(Float, default=0, comment="总金额")
    remark = Column(Text, comment="备注")

    status = Column(String(20), default="draft", comment="状态 draft/confirmed")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    confirmed_at = Column(DateTime, comment="确认时间")


class VehicleReturn(Base):
    """车销回库单"""
    __tablename__ = "vehicle_returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, comment="单号")

    vehicle_sales_out_id = Column(Integer, ForeignKey("vehicle_sales_outs.id"), comment="原车销出库ID")
    employee_id = Column(Integer, ForeignKey("employees.id"), comment="业务员ID")

    total_amount = Column(Float, default=0, comment="总金额")
    remark = Column(Text, comment="备注")

    status = Column(String(20), default="draft", comment="状态 draft/confirmed")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    confirmed_at = Column(DateTime, comment="确认时间")


class VehicleLoss(Base):
    """车销报损单"""
    __tablename__ = "vehicle_losses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, comment="单号")

    vehicle_sales_out_id = Column(Integer, ForeignKey("vehicle_sales_outs.id"), comment="原车销出库ID")
    employee_id = Column(Integer, ForeignKey("employees.id"), comment="业务员ID")

    total_amount = Column(Float, default=0, comment="报损金额")
    reason = Column(Text, comment="报损原因")
    status = Column(String(20), default="draft", comment="状态 draft/confirmed")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    confirmed_at = Column(DateTime, comment="确认时间")
