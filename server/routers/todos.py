"""
待办任务路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from utils.data_filter import DataFilter
from routers.auth import get_current_user
from models.sales import SalesOrder
from models.purchase import PurchaseOrder

router = APIRouter(prefix="/api/todos", tags=["待办"])


class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    status: str
    type: str


@router.get("", response_model=List[TodoItem])
def list_todos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    todos = []

    # 获取待审核的销售订单（应用数据权限过滤）
    q = db.query(SalesOrder).filter(SalesOrder.status == 0)
    q = DataFilter.apply_scope(q, SalesOrder, current_user, db, scope_field="route_id", module_key="sales")
    pending_sales = q.all()
    for so in pending_sales:
        todos.append(TodoItem(
            id=f"sales_{so.id}",
            title=f"销售订单待审核: {so.code}",
            description=f"客户ID: {so.customer_id}, 金额: {so.total_amount}",
            status="待处理",
            type="sales"
        ))

    # 获取待审核的采购订单（应用数据权限过滤）
    q = db.query(PurchaseOrder).filter(PurchaseOrder.status == 0)
    q = DataFilter.apply_scope(q, PurchaseOrder, current_user, db, scope_field="route_id", module_key="purchases")
    pending_purchases = q.all()
    for po in pending_purchases:
        todos.append(TodoItem(
            id=f"purchase_{po.id}",
            title=f"采购订单待审核: {po.code}",
            description=f"供应商ID: {po.supplier_id}, 金额: {po.total_amount}",
            status="待处理",
            type="purchase"
        ))

    return todos