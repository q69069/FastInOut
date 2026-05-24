from datetime import datetime
from sqlalchemy import text, Column, Integer, String, ForeignKey, DateTime, func
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(200), nullable=False)
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class CustomerCategory(Base):
    __tablename__ = "customer_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class SupplierCategory(Base):
    __tablename__ = "supplier_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
