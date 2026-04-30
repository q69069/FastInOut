from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # CG+日期+序号
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    paid_amount = Column(Float, default=0)
    status = Column(Integer, default=0)  # 0=草稿 1=已确认 2=已入库 3=已关闭
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)  # 单价
    amount = Column(Float, default=0)  # 金额
    received_qty = Column(Float, default=0)  # 已入库数量


class PurchaseStockin(Base):
    __tablename__ = "purchase_stockins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # RK+日期+序号
    order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    status = Column(Integer, default=1)  # 1=已入库
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class PurchaseStockinItem(Base):
    __tablename__ = "purchase_stockin_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stockin_id = Column(Integer, ForeignKey("purchase_stockins.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)
    amount = Column(Float, default=0)


class PurchaseReturn(Base):
    __tablename__ = "purchase_returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # CT+日期+序号
    stockin_id = Column(Integer, ForeignKey("purchase_stockins.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    status = Column(Integer, default=0)  # 0=草稿 1=已确认
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)


class PurchaseReturnItem(Base):
    __tablename__ = "purchase_return_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(Integer, ForeignKey("purchase_returns.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)
    amount = Column(Float, default=0)
