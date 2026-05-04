"""异常交易监控路由 — Phase D

检测：
1. 作废复开：同客户同日作废后重开
2. 单价异常：单价偏离均价超过30%
3. 赊账比例：赊账占比超过阈值
4. 多单退款：同客户短期多次退货
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models.sales_delivery import SalesDelivery, SalesDeliveryItem
from models.sales import SalesReturn
from models.customer import Customer
from models.product import Product
from models.employee import Employee
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/monitor", tags=["异常监控"])


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    from utils.auth import decode_access_token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.get("/anomalies", response_model=ResponseModel)
def detect_anomalies(
    days: int = Query(7), threshold: float = Query(0.3),
    authorization: str = Header(None), db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)
    anomalies = []
    since = datetime.now() - timedelta(days=days)

    # 1. 作废复开：同客户同日作废后重开
    voided = db.query(SalesDelivery).filter(
        SalesDelivery.status == "voided",
        SalesDelivery.created_at >= since
    ).all()
    for v in voided:
        reopened = db.query(SalesDelivery).filter(
            SalesDelivery.customer_id == v.customer_id,
            SalesDelivery.created_by == v.created_by,
            SalesDelivery.status.in_(["pending", "locked", "settled"]),
            SalesDelivery.created_at > v.created_at,
            SalesDelivery.created_at <= v.created_at + timedelta(days=1)
        ).first()
        if reopened:
            cust = db.query(Customer).get(v.customer_id)
            anomalies.append({
                "type": "void_reopen",
                "desc": f"客户{cust.name if cust else ''}同日作废后重开",
                "severity": "high",
                "detail": f"作废单:{v.delivery_no} → 重开单:{reopened.delivery_no}",
                "created_at": str(v.created_at)
            })

    # 2. 单价异常
    items = db.query(SalesDeliveryItem).join(SalesDelivery).filter(
        SalesDelivery.created_at >= since
    ).all()
    product_prices = {}
    for item in items:
        if item.product_id not in product_prices:
            product_prices[item.product_id] = []
        product_prices[item.product_id].append(item.unit_price or 0)
    for pid, prices in product_prices.items():
        if len(prices) < 3:
            continue
        avg = sum(prices) / len(prices)
        if avg == 0:
            continue
        for p in prices:
            if abs(p - avg) / avg > threshold:
                prod = db.query(Product).get(pid)
                anomalies.append({
                    "type": "price_deviation",
                    "desc": f"商品{prod.name if prod else ''}单价偏离均价{abs(p-avg)/avg*100:.0f}%",
                    "severity": "medium",
                    "detail": f"单价:{p} 均价:{avg:.2f}",
                    "created_at": ""
                })
                break

    # 3. 赊账比例过高
    deliveries = db.query(SalesDelivery).filter(
        SalesDelivery.created_at >= since,
        SalesDelivery.status.in_(["pending", "locked", "settled"])
    ).all()
    for d in deliveries:
        if d.total_amount and d.total_amount > 0:
            credit_ratio = (d.credit_amount or 0) / d.total_amount
            if credit_ratio > 0.8:
                cust = db.query(Customer).get(d.customer_id)
                anomalies.append({
                    "type": "high_credit",
                    "desc": f"销售单{d.delivery_no}赊账比例{credit_ratio*100:.0f}%",
                    "severity": "medium",
                    "detail": f"客户:{cust.name if cust else ''} 总额:{d.total_amount} 赊账:{d.credit_amount}",
                    "created_at": str(d.created_at)
                })

    # 4. 同客户短期多次退货
    returns = db.query(SalesReturn).filter(SalesReturn.created_at >= since).all()
    customer_returns = {}
    for r in returns:
        key = r.customer_id
        if key not in customer_returns:
            customer_returns[key] = []
        customer_returns[key].append(r)
    for cid, rets in customer_returns.items():
        if len(rets) >= 3:
            cust = db.query(Customer).get(cid)
            total = sum(r.total_amount or 0 for r in rets)
            anomalies.append({
                "type": "multi_return",
                "desc": f"客户{cust.name if cust else ''}{days}天内退货{len(rets)}次",
                "severity": "high",
                "detail": f"退货总额:{total:.2f}",
                "created_at": str(rets[0].created_at)
            })

    return ResponseModel(data={"count": len(anomalies), "items": anomalies})
