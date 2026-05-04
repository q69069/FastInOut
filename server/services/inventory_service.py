"""库存扣减/回滚统一入口 — Phase 0 services 层"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.inventory import Inventory


class InventoryService:
    @staticmethod
    def deduct(db: Session, product_id: int, warehouse_id: int, quantity: float):
        """扣库存，库存不足抛出异常"""
        if quantity <= 0:
            return
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        if not inv or inv.quantity < quantity:
            raise HTTPException(400, f"库存不足：商品{product_id} 仓库{warehouse_id}")
        inv.quantity -= quantity

    @staticmethod
    def restore(db: Session, product_id: int, warehouse_id: int, quantity: float):
        """回滚库存（作废/红冲时调用）"""
        if quantity <= 0:
            return
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        if inv:
            inv.quantity += quantity
        else:
            # 如果库存记录不存在，创建一条
            inv = Inventory(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(inv)

    @staticmethod
    def get_quantity(db: Session, product_id: int, warehouse_id: int) -> float:
        """查询某仓库某商品的库存数量"""
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        return inv.quantity if inv else 0
