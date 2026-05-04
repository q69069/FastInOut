"""采购退货出库单（PurchaseReturnDelivery）— Phase A+

独立于现有 PurchaseReturn（订单层），这是单据层：
- 状态流转：pending → warehouse_confirmed → finance_confirmed → settled
- 仓管确认：扣减库存
- 财务确认：冲减供应商应付
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class PurchaseReturnDelivery(Base):
    __tablename__ = "purchase_return_deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_dlv_no = Column(String(30), unique=True, nullable=False)  # CT-20260504-001
    purchase_return_id = Column(Integer, ForeignKey("purchase_returns.id"), nullable=True)  # 关联退货订单
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    total_amount = Column(Float, default=0)
    status = Column(String(20), default="pending")
    # pending → warehouse_confirmed → finance_confirmed → settled

    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    wh_confirmed_by = Column(Integer, ForeignKey("employees.id"))
    wh_confirmed_at = Column(DateTime)
    fin_confirmed_by = Column(Integer, ForeignKey("employees.id"))
    fin_confirmed_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    remark = Column(Text)


class PurchaseReturnDeliveryItem(Base):
    __tablename__ = "purchase_return_delivery_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_dlv_id = Column(Integer, ForeignKey("purchase_return_deliveries.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, default=0)
    unit_price = Column(Float, default=0)
    amount = Column(Float, default=0)
