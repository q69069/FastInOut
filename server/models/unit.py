from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class Unit(Base):
    """单位定义，如：件、箱、瓶、支、包等"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # 单位名称
    symbol = Column(String(20))  # 单位符号，如 kg、瓶
    description = Column(String(200))  # 描述
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    created_at = Column(DateTime, server_default=func.now())


class UnitConversion(Base):
    """单位换算关系，支持多层：件→中包→支"""
    __tablename__ = "unit_conversions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # 关联商品
    from_unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)  # 源单位（大单位）
    to_unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)  # 目标单位（小单位）
    ratio = Column(Float, nullable=False)  # 换算比例：1个from = ratio个to
    level = Column(Integer, default=1)  # 层级：1=第一层（件→中包），2=第二层（中包→支）
    created_at = Column(DateTime, server_default=func.now())
