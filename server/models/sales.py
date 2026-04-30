from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, func
from database import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # XS+日期+序号
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    paid_amount = Column(Float, default=0)
    status = Column(Integer, default=0)  # 0=草稿 1=已确认 2=已出库 3=已关闭
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)
    amount = Column(Float, default=0)
    delivered_qty = Column(Float, default=0)  # 已出库数量


class SalesStockout(Base):
    __tablename__ = "sales_stockouts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # CK+日期+序号
    order_id = Column(Integer, ForeignKey("sales_orders.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    status = Column(Integer, default=1)  # 1=已出库
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class SalesStockoutItem(Base):
    __tablename__ = "sales_stockout_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stockout_id = Column(Integer, ForeignKey("sales_stockouts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)
    amount = Column(Float, default=0)


class SalesReturn(Base):
    __tablename__ = "sales_returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # ST+日期+序号
    stockout_id = Column(Integer, ForeignKey("sales_stockouts.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    operator_id = Column(Integer, ForeignKey("employees.id"))
    total_amount = Column(Float, default=0)
    status = Column(Integer, default=0)  # 0=草稿 1=已确认
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)


class SalesReturnItem(Base):
    __tablename__ = "sales_return_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(Integer, ForeignKey("sales_returns.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=0)
    price = Column(Float, default=0)
    amount = Column(Float, default=0)
