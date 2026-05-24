from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import get_db
from models.employee import Employee
from deps import require_reports_module
from models.product import Product
from models.customer import Customer
from models.supplier import Supplier
from models.inventory import Inventory, InventoryAlert
from models.sales import SalesOrder, SalesStockout, SalesStockoutItem
from models.purchase import PurchaseOrder, PurchaseStockin, PurchaseStockinItem
from models.finance import Receipt, Payment
from schemas.common import ResponseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/reports", tags=["报表"])


# ========== 经营看板 ==========
@router.get("/dashboard", response_model=ResponseModel)
def dashboard(user: Employee = Depends(require_reports_module), db: Session = Depends(get_db)):
    today = datetime.now().strftime("%Y-%m-%d")
    # 今日销售额
    today_sales = db.query(func.sum(SalesStockout.total_amount)).filter(
        SalesStockout.status == 2,
        SalesStockout.created_at >= today
    ).scalar() or 0
    # 今日采购额
    today_purchase = db.query(func.sum(PurchaseStockin.total_amount)).filter(
        PurchaseStockin.status == 2,
        PurchaseStockin.created_at >= today
    ).scalar() or 0
    # 今日回款
    today_receipt = db.query(func.sum(Receipt.amount)).filter(
        Receipt.status == 1,
        Receipt.created_at >= today
    ).scalar() or 0
    # 今日付款
    today_payment = db.query(func.sum(Payment.amount)).filter(
        Payment.status == 1,
        Payment.created_at >= today
    ).scalar() or 0
    # 库存总量
    invs = db.query(Inventory).all()
    total_stock_qty = sum(i.quantity for i in invs)
    total_stock_value = sum(i.quantity * i.cost_price for i in invs)
    # 应收/应付
    total_receivable = db.query(func.sum(Customer.receivable_balance)).filter(
        Customer.receivable_balance > 0
    ).scalar() or 0
    total_payable = db.query(func.sum(Supplier.payable_balance)).filter(
        Supplier.payable_balance > 0
    ).scalar() or 0
    # 本月订单数
    month_start = datetime.now().strftime("%Y-%m-01")
    month_orders = db.query(SalesOrder).filter(SalesOrder.created_at >= month_start).count()
    # 库存预警数
    alert_count = db.query(InventoryAlert).filter(InventoryAlert.is_handled == 0).count()
    return ResponseModel(data={
        "today_sales": today_sales,
        "today_purchase": today_purchase,
        "today_receipt": today_receipt,
        "today_payment": today_payment,
        "total_stock_qty": total_stock_qty,
        "total_stock_value": total_stock_value,
        "total_receivable": total_receivable,
        "total_payable": total_payable,
        "month_orders": month_orders,
        "alert_count": alert_count,
        "product_count": db.query(Product).count(),
        "customer_count": db.query(Customer).count(),
        "supplier_count": db.query(Supplier).count(),
    })


# ========== 销售报表 ==========
@router.get("/sales", response_model=ResponseModel)
def sales_report(
    group_by: str = Query("day"),  # day/week/month/year
    start_date: str = Query(None), end_date: str = Query(None),
    customer_id: int = Query(None), product_id: int = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date:
        q = q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if customer_id:
        q = q.filter(SalesStockout.customer_id == customer_id)
    stockouts = q.all()
    # 按日期分组统计
    stats = {}
    for so in stockouts:
        date_key = str(so.created_at)[:10]  # YYYY-MM-DD
        if group_by == "month":
            date_key = date_key[:7]
        elif group_by == "year":
            date_key = date_key[:4]
        if date_key not in stats:
            stats[date_key] = {"date": date_key, "order_count": 0, "total_amount": 0, "cost_amount": 0, "profit": 0}
        stats[date_key]["order_count"] += 1
        stats[date_key]["total_amount"] += so.total_amount
        # 计算成本
        items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == so.id).all()
        for item in items:
            if product_id and item.product_id != product_id:
                continue
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            cost = inv.cost_price if inv else 0
            stats[date_key]["cost_amount"] += item.quantity * cost
        stats[date_key]["profit"] = stats[date_key]["total_amount"] - stats[date_key]["cost_amount"]
    result = sorted(stats.values(), key=lambda x: x["date"])
    return ResponseModel(data=result)


# ========== 采购报表 ==========
@router.get("/purchase", response_model=ResponseModel)
def purchase_report(
    group_by: str = Query("day"),
    start_date: str = Query(None), end_date: str = Query(None),
    supplier_id: int = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    q = db.query(PurchaseStockin).filter(PurchaseStockin.status == 2)
    if start_date:
        q = q.filter(PurchaseStockin.created_at >= start_date)
    if end_date:
        q = q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    if supplier_id:
        q = q.filter(PurchaseStockin.supplier_id == supplier_id)
    stockins = q.all()
    stats = {}
    for si in stockins:
        date_key = str(si.created_at)[:10]
        if group_by == "month":
            date_key = date_key[:7]
        elif group_by == "year":
            date_key = date_key[:4]
        if date_key not in stats:
            stats[date_key] = {"date": date_key, "order_count": 0, "total_amount": 0}
        stats[date_key]["order_count"] += 1
        stats[date_key]["total_amount"] += si.total_amount
    result = sorted(stats.values(), key=lambda x: x["date"])
    return ResponseModel(data=result)


# ========== 库存报表 ==========
@router.get("/inventory", response_model=ResponseModel)
def inventory_report(warehouse_id: int = Query(None), user: Employee = Depends(require_reports_module), db: Session = Depends(get_db)):
    q = db.query(Inventory)
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    invs = q.all()
    result = []
    for inv in invs:
        product = db.query(Product).get(inv.product_id)
        from models.warehouse import Warehouse
        warehouse = db.query(Warehouse).get(inv.warehouse_id)
        result.append({
            "product_id": inv.product_id,
            "product_name": product.name if product else "",
            "product_code": product.code if product else "",
            "warehouse_name": warehouse.name if warehouse else "",
            "quantity": inv.quantity,
            "cost_price": inv.cost_price,
            "total_value": inv.quantity * inv.cost_price
        })
    total_value = sum(r["total_value"] for r in result)
    return ResponseModel(data={"items": result, "total_value": total_value})


# ========== 利润报表 ==========
@router.get("/profit", response_model=ResponseModel)
def profit_report(
    group_by: str = Query("day"),
    start_date: str = Query(None), end_date: str = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    # 销售收入
    sales_q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date:
        sales_q = sales_q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        sales_q = sales_q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    sales = sales_q.all()
    # 采购成本
    purchase_q = db.query(PurchaseStockin).filter(PurchaseStockin.status == 2)
    if start_date:
        purchase_q = purchase_q.filter(PurchaseStockin.created_at >= start_date)
    if end_date:
        purchase_q = purchase_q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    purchases = purchase_q.all()
    # 按日期分组
    stats = {}
    for so in sales:
        date_key = str(so.created_at)[:10]
        if group_by == "month":
            date_key = date_key[:7]
        if date_key not in stats:
            stats[date_key] = {"date": date_key, "sales_amount": 0, "cost_amount": 0, "profit": 0, "gross_rate": 0}
        stats[date_key]["sales_amount"] += so.total_amount
        items = db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == so.id).all()
        for item in items:
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            cost = inv.cost_price if inv else 0
            stats[date_key]["cost_amount"] += item.quantity * cost
    for si in purchases:
        date_key = str(si.created_at)[:10]
        if group_by == "month":
            date_key = date_key[:7]
        if date_key not in stats:
            stats[date_key] = {"date": date_key, "sales_amount": 0, "cost_amount": 0, "profit": 0, "gross_rate": 0}
    for key in stats:
        stats[key]["profit"] = stats[key]["sales_amount"] - stats[key]["cost_amount"]
        if stats[key]["sales_amount"] > 0:
            stats[key]["gross_rate"] = round(stats[key]["profit"] / stats[key]["sales_amount"] * 100, 2)
    result = sorted(stats.values(), key=lambda x: x["date"])
    return ResponseModel(data=result)


# ========== Excel导出 ==========
@router.get("/export/sales")
def export_sales(
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    from fastapi.responses import StreamingResponse
    from openpyxl import Workbook
    from io import BytesIO

    q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date:
        q = q.filter(SalesStockout.created_at >= start_date)
    if end_date:
        q = q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    orders = q.order_by(SalesStockout.created_at.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "销售报表"
    ws.append(["单号", "客户", "仓库", "金额", "日期"])

    from models.customer import Customer as Cust
    from models.warehouse import Warehouse as Wh
    customers_map = {c.id: c.name for c in db.query(Cust).all()}
    warehouses_map = {w.id: w.name for w in db.query(Wh).all()}

    for so in orders:
        ws.append([
            so.code,
            customers_map.get(so.customer_id, ""),
            warehouses_map.get(so.warehouse_id, ""),
            so.total_amount,
            str(so.created_at)[:19]
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sales_report.xlsx"}
    )


@router.get("/export/inventory")
def export_inventory(user: Employee = Depends(require_reports_module), db: Session = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    from openpyxl import Workbook
    from io import BytesIO

    invs = db.query(Inventory).all()
    products_map = {p.id: p for p in db.query(Product).all()}
    from models.warehouse import Warehouse as Wh
    warehouses_map = {w.id: w.name for w in db.query(Wh).all()}

    wb = Workbook()
    ws = wb.active
    ws.title = "库存报表"
    ws.append(["商品编码", "商品名称", "规格", "单位", "仓库", "数量", "成本价", "库存金额"])

    for inv in invs:
        p = products_map.get(inv.product_id)
        ws.append([
            p.code if p else "",
            p.name if p else "",
            p.spec if p else "",
            p.unit if p else "",
            warehouses_map.get(inv.warehouse_id, ""),
            inv.quantity,
            inv.cost_price,
            inv.quantity * inv.cost_price
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory_report.xlsx"}
    )


@router.get("/export/profit")
def export_profit(
    group_by: str = Query("day"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    from fastapi.responses import StreamingResponse
    from openpyxl import Workbook
    from io import BytesIO
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    THIN = Side(style='thin', color='999999')
    BORDER = Border(left=THIN, top=THIN, right=THIN, bottom=THIN)
    HEADER_FILL = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    HFONT = Font(color='FFFFFF', bold=True, size=11)
    CTR = Alignment(horizontal='center', vertical='center')

    def hdr(ws, headers, widths):
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = HFONT; c.fill = HEADER_FILL; c.alignment = CTR; c.border = BORDER
        for col, w in enumerate(widths, 1):
            ws.column_dimensions[chr(64+col)].width = w

    def row(ws, r, vals):
        for col, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=col, value=v)
            c.font = Font(size=10); c.border = BORDER
            if isinstance(v, (int, float)):
                c.alignment = Alignment(horizontal='right')
            else:
                c.alignment = CTR

    def m(v): return round(float(v or 0), 2)

    sales_q = db.query(SalesStockout).filter(SalesStockout.status == 2)
    if start_date: sales_q = sales_q.filter(SalesStockout.created_at >= start_date)
    if end_date: sales_q = sales_q.filter(SalesStockout.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    sales = sales_q.all()
    purchase_q = db.query(PurchaseStockin).filter(PurchaseStockin.status == 2)
    if start_date: purchase_q = purchase_q.filter(PurchaseStockin.created_at >= start_date)
    if end_date: purchase_q = purchase_q.filter(PurchaseStockin.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
    purchases = purchase_q.all()

    stats = {}
    for so in sales:
        dk = str(so.created_at)[:10]
        if group_by == "month": dk = dk[:7]
        if dk not in stats: stats[dk] = {"date": dk, "sales_amount": 0, "cost_amount": 0, "profit": 0, "gross_rate": 0}
        stats[dk]["sales_amount"] += so.total_amount
        for item in db.query(SalesStockoutItem).filter(SalesStockoutItem.stockout_id == so.id).all():
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            stats[dk]["cost_amount"] += item.quantity * (inv.cost_price if inv else 0)
    for si in purchases:
        dk = str(si.created_at)[:10]
        if group_by == "month": dk = dk[:7]
        if dk not in stats: stats[dk] = {"date": dk, "sales_amount": 0, "cost_amount": 0, "profit": 0, "gross_rate": 0}
    for key in stats:
        stats[key]["profit"] = stats[key]["sales_amount"] - stats[key]["cost_amount"]
        if stats[key]["sales_amount"] > 0:
            stats[key]["gross_rate"] = round(stats[key]["profit"] / stats[key]["sales_amount"] * 100, 2)

    result = sorted(stats.values(), key=lambda x: x["date"])

    wb = Workbook()
    ws = wb.active
    ws.title = "利润报表"
    hdr(ws, ['日期', '销售金额', '成本金额', '利润', '利润率(%)'], [14, 14, 14, 14, 12])
    ts = tc = 0
    for i, r in enumerate(result, 2):
        s, c = m(r["sales_amount"]), m(r["cost_amount"])
        p = m(r["profit"]); ts += s; tc += c
        row(ws, i, [r["date"], s, c, p, r["gross_rate"]])
    if result:
        tp = ts - tc; rate = round(tp/ts*100,2) if ts else 0
        row(ws, len(result)+2, ['合计', ts, tc, tp, rate])

    buf = BytesIO()
    wb.save(buf); buf.seek(0)
    fname = f"利润报表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    from urllib.parse import quote
    encoded_fname = quote(fname)
    return StreamingResponse(buf, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_fname}"})


@router.get("/export/finance")
def export_finance(
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    from fastapi.responses import StreamingResponse
    from openpyxl import Workbook
    from io import BytesIO

    wb = Workbook()
    # 收款
    ws1 = wb.active
    ws1.title = "收款记录"
    ws1.append(["单号", "客户", "金额", "日期"])

    rq = db.query(Receipt).filter(Receipt.status == 1)
    if start_date:
        rq = rq.filter(Receipt.created_at >= start_date)
    if end_date:
        rq = rq.filter(Receipt.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    customers_map = {c.id: c.name for c in db.query(Customer).all()}
    for r in rq.all():
        ws1.append([r.code, customers_map.get(r.customer_id, ""), r.amount, str(r.created_at)[:19]])

    # 付款
    ws2 = wb.create_sheet("付款记录")
    ws2.append(["单号", "供应商", "金额", "日期"])

    pq = db.query(Payment).filter(Payment.status == 1)
    if start_date:
        pq = pq.filter(Payment.created_at >= start_date)
    if end_date:
        pq = pq.filter(Payment.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    suppliers_map = {s.id: s.name for s in db.query(Supplier).all()}
    for p in pq.all():
        ws2.append([p.code, suppliers_map.get(p.supplier_id, ""), p.amount, str(p.created_at)[:19]])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=finance_report.xlsx"}
    )


# ========== 单据导出 ==========
@router.get("/export/documents")
def export_documents(
    type: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    keyword: str = Query(None),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    from fastapi.responses import StreamingResponse
    from openpyxl import Workbook
    from io import BytesIO
    from models.purchase import PurchaseOrder, PurchaseStockin, PurchaseReturn
    from models.sales import SalesOrder, SalesStockout, SalesReturn
    from models.purchase_receipt import PurchaseReceipt
    from models.sales_delivery import SalesDelivery
    from models.purchase_return_dlv import PurchaseReturnDelivery
    from models.inventory import InventoryTransfer, InventoryCheck
    from models.vehicle_load import VehicleLoad
    from models.damage_report import DamageReport
    from models.settlement import Settlement
    from models.warehouse import Warehouse as Wh
    from models.customer import Customer as Cust
    from models.supplier import Supplier as Sup

    # Bulk pre-fetch name lookups
    warehouses_map = {w.id: w.name for w in db.query(Wh).all()}
    customers_map = {c.id: c.name for c in db.query(Cust).all()}
    suppliers_map = {s.id: s.name for s in db.query(Sup).all()}

    def date_filter(q, model):
        if start_date:
            q = q.filter(model.created_at >= start_date)
        if end_date:
            q = q.filter(model.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        return q

    def code_filter(q, model, col):
        if keyword:
            q = q.filter(col.contains(keyword))
        return q

    rows = []

    # 1. 采购订单
    if not type or type == 'purchase_order':
        q = db.query(PurchaseOrder)
        q = date_filter(q, PurchaseOrder)
        if keyword:
            q = q.filter(PurchaseOrder.code.contains(keyword))
        for o in q.order_by(PurchaseOrder.created_at.desc()).all():
            rows.append(["采购订单", o.code, suppliers_map.get(o.supplier_id, ""), warehouses_map.get(o.warehouse_id, ""), o.total_amount or 0, {0:"草稿",1:"已确认",2:"已入库",3:"已冲红"}.get(o.status, str(o.status)), str(o.created_at)[:19], o.remark or ""])

    # 2. 采购单
    if not type or type == 'purchase_receipt':
        q = db.query(PurchaseReceipt)
        q = date_filter(q, PurchaseReceipt)
        if keyword:
            q = q.filter(PurchaseReceipt.receipt_no.contains(keyword))
        for r in q.order_by(PurchaseReceipt.created_at.desc()).all():
            rows.append(["采购单", r.receipt_no, suppliers_map.get(r.supplier_id, ""), warehouses_map.get(r.warehouse_id, ""), r.total_amount or 0, {"pending":"草稿","confirmed":"已入库","cancelled":"已取消","reversed":"已冲红"}.get(r.status, r.status), str(r.created_at)[:19], r.remark or ""])

    # 3. 入库单
    if not type or type == 'purchase_stockin':
        q = db.query(PurchaseStockin)
        q = date_filter(q, PurchaseStockin)
        if keyword:
            q = q.filter(PurchaseStockin.code.contains(keyword))
        for si in q.order_by(PurchaseStockin.created_at.desc()).all():
            rows.append(["入库单", si.code, suppliers_map.get(si.supplier_id, ""), warehouses_map.get(si.warehouse_id, ""), si.total_amount or 0, {0:"草稿",1:"已入库",2:"已入库",3:"已冲红"}.get(si.status, str(si.status)), str(si.created_at)[:19], si.remark or ""])

    # 4. 采购退货订单
    if not type or type == 'purchase_return_order':
        q = db.query(PurchaseReturn)
        q = date_filter(q, PurchaseReturn)
        if keyword:
            q = q.filter(PurchaseReturn.code.contains(keyword))
        for r in q.order_by(PurchaseReturn.created_at.desc()).all():
            rows.append(["采购退货订单", r.code, suppliers_map.get(r.supplier_id, ""), warehouses_map.get(r.warehouse_id, ""), r.total_amount or 0, {0:"草稿",1:"已确认",2:"已出库",3:"已冲红"}.get(r.status, str(r.status)), str(r.created_at)[:19], r.remark or ""])

    # 5. 采购退货
    if not type or type == 'purchase_return_dlv':
        q = db.query(PurchaseReturnDelivery)
        q = date_filter(q, PurchaseReturnDelivery)
        if keyword:
            q = q.filter(PurchaseReturnDelivery.return_dlv_no.contains(keyword))
        for d in q.order_by(PurchaseReturnDelivery.created_at.desc()).all():
            rows.append(["采购退货", d.return_dlv_no, suppliers_map.get(d.supplier_id, ""), warehouses_map.get(d.warehouse_id, ""), d.total_amount or 0, {"pending":"草稿","warehouse_confirmed":"已出库","finance_confirmed":"已结算","settled":"已结算","reversed":"已冲红"}.get(d.status, d.status), str(d.created_at)[:19], d.remark or ""])

    # 6. 销售订单
    if not type or type == 'sales_order':
        q = db.query(SalesOrder)
        q = date_filter(q, SalesOrder)
        if keyword:
            q = q.filter(SalesOrder.code.contains(keyword))
        for o in q.order_by(SalesOrder.created_at.desc()).all():
            rows.append(["销售订单", o.code, customers_map.get(o.customer_id, ""), warehouses_map.get(o.warehouse_id, ""), o.total_amount or 0, {0:"草稿",1:"已确认",2:"已出库",3:"已冲红"}.get(o.status, str(o.status)), str(o.created_at)[:19], o.remark or ""])

    # 7. 销售单
    if not type or type == 'sales_delivery':
        q = db.query(SalesDelivery)
        q = date_filter(q, SalesDelivery)
        if keyword:
            q = q.filter(SalesDelivery.delivery_no.contains(keyword))
        for sd in q.order_by(SalesDelivery.created_at.desc()).all():
            rows.append(["销售单", sd.delivery_no, customers_map.get(sd.customer_id, ""), warehouses_map.get(sd.warehouse_id, ""), sd.total_amount or 0, {"pending":"草稿","confirmed":"已出库","settled":"已结算","voided":"已作废","reversed":"已冲红"}.get(sd.status, sd.status), str(sd.created_at)[:19], sd.remark or ""])

    # 8. 出库单
    if not type or type == 'sales_stockout':
        q = db.query(SalesStockout)
        q = date_filter(q, SalesStockout)
        if keyword:
            q = q.filter(SalesStockout.code.contains(keyword))
        for so in q.order_by(SalesStockout.created_at.desc()).all():
            rows.append(["出库单", so.code, customers_map.get(so.customer_id, ""), warehouses_map.get(so.warehouse_id, ""), so.total_amount or 0, {0:"草稿",1:"已出库",2:"已出库",3:"已冲红"}.get(so.status, str(so.status)), str(so.created_at)[:19], so.remark or ""])

    # 9. 退货订单
    if not type or type == 'sales_return_order':
        q = db.query(SalesReturn).filter(SalesReturn.doc_type == "return_order")
        q = date_filter(q, SalesReturn)
        if keyword:
            q = q.filter(SalesReturn.code.contains(keyword))
        for r in q.order_by(SalesReturn.created_at.desc()).all():
            rows.append(["退货订单", r.code, customers_map.get(r.customer_id, ""), warehouses_map.get(r.warehouse_id, ""), r.total_amount or 0, {0:"草稿",1:"已确认",2:"已入库",3:"已冲红"}.get(r.status, str(r.status)), str(r.created_at)[:19], r.remark or ""])

    # 10. 退货单
    if not type or type == 'return_delivery':
        q = db.query(SalesReturn).filter(SalesReturn.doc_type == "return_delivery")
        q = date_filter(q, SalesReturn)
        if keyword:
            q = q.filter(SalesReturn.code.contains(keyword))
        for r in q.order_by(SalesReturn.created_at.desc()).all():
            rows.append(["退货单", r.code, customers_map.get(r.customer_id, ""), warehouses_map.get(r.warehouse_id, ""), r.total_amount or 0, {0:"草稿",1:"已入库",2:"已入库",3:"已结算"}.get(r.status, str(r.status)), str(r.created_at)[:19], r.remark or ""])

    # 11. 库存调拨
    if not type or type == 'transfer':
        q = db.query(InventoryTransfer)
        q = date_filter(q, InventoryTransfer)
        if keyword:
            q = q.filter(InventoryTransfer.code.contains(keyword))
        for t in q.order_by(InventoryTransfer.created_at.desc()).all():
            rows.append(["库存调拨", t.code, warehouses_map.get(t.from_warehouse_id, ""), warehouses_map.get(t.to_warehouse_id, ""), "", {1:"调拨中",2:"已确认",3:"已取消"}.get(t.status, str(t.status)), str(t.created_at)[:19], t.remark or ""])

    # 12. 盘点单
    if not type or type == 'stocktaking':
        q = db.query(InventoryCheck)
        q = date_filter(q, InventoryCheck)
        if keyword:
            q = q.filter(InventoryCheck.code.contains(keyword))
        for s in q.order_by(InventoryCheck.created_at.desc()).all():
            rows.append(["盘点单", s.code, warehouses_map.get(s.warehouse_id, ""), warehouses_map.get(s.warehouse_id, ""), "", {1:"盘点中",2:"已审核",3:"已调整",4:"已作废"}.get(s.status, str(s.status)), str(s.created_at)[:19], s.remark or ""])

    # 13. 装车单
    if not type or type == 'vehicle_load':
        q = db.query(VehicleLoad)
        q = date_filter(q, VehicleLoad)
        if keyword:
            q = q.filter(VehicleLoad.load_no.contains(keyword))
        for v in q.order_by(VehicleLoad.created_at.desc()).all():
            rows.append(["装车单", v.load_no, warehouses_map.get(v.from_warehouse_id, ""), warehouses_map.get(v.vehicle_warehouse_id, ""), "", {"draft":"草稿","loaded":"已装车","returned":"已退库"}.get(v.status, v.status), str(v.created_at)[:19], v.remark or ""])

    # 14. 报损单
    if not type or type == 'damage_report':
        q = db.query(DamageReport)
        q = date_filter(q, DamageReport)
        if keyword:
            q = q.filter(DamageReport.code.contains(keyword))
        for d in q.order_by(DamageReport.created_at.desc()).all():
            rows.append(["报损单", d.code, warehouses_map.get(d.warehouse_id, ""), warehouses_map.get(d.warehouse_id, ""), d.total_amount or 0, {"pending":"草稿","adjusted":"已调整"}.get(d.status, d.status), str(d.created_at)[:19], d.remark or ""])

    # 15. 交账单
    if not type or type == 'settlement':
        q = db.query(Settlement)
        q = date_filter(q, Settlement)
        if keyword:
            q = q.filter(Settlement.settlement_no.contains(keyword))
        for s in q.order_by(Settlement.created_at.desc()).all():
            rows.append(["交账单", s.settlement_no, s.employee_name or "", "", s.total_sales or 0, {"pending":"草稿","audited":"已通过","rejected":"已驳回"}.get(s.status, s.status), str(s.created_at)[:19], s.remark or ""])

    wb = Workbook()
    ws = wb.active
    ws.title = "单据导出"
    ws.append(["单据类型", "单号", "客户/供应商", "仓库", "金额", "状态", "创建时间", "备注"])

    for row in rows:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=documents_export_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )


# ========== 趋势图 ==========
@router.get("/trend", response_model=ResponseModel)
def trend_report(
    trend_type: str = Query("sales"),  # sales/purchase
    period: str = Query("month"),  # month/quarter
    months: int = Query(12, ge=1, le=24),
    user: Employee = Depends(require_reports_module),
    db: Session = Depends(get_db)
):
    """采购/销售趋势数据（按月/季度）"""
    from collections import OrderedDict
    now = datetime.now()
    data = OrderedDict()

    if trend_type == "sales":
        # 查询已确认的销售出库单
        records = db.query(SalesStockout).filter(SalesStockout.status == 2).all()
        for r in records:
            dt = r.created_at
            if not dt:
                continue
            if period == "month":
                key = dt.strftime("%Y-%m")
            elif period == "quarter":
                q = (dt.month - 1) // 3 + 1
                key = f"{dt.year}-Q{q}"
            else:
                key = dt.strftime("%Y-%m")
            if key not in data:
                data[key] = {"amount": 0, "count": 0}
            data[key]["amount"] += r.total_amount or 0
            data[key]["count"] += 1
    else:
        records = db.query(PurchaseStockin).filter(PurchaseStockin.status == 2).all()
        for r in records:
            dt = r.created_at
            if not dt:
                continue
            if period == "month":
                key = dt.strftime("%Y-%m")
            elif period == "quarter":
                q = (dt.month - 1) // 3 + 1
                key = f"{dt.year}-Q{q}"
            else:
                key = dt.strftime("%Y-%m")
            if key not in data:
                data[key] = {"amount": 0, "count": 0}
            data[key]["amount"] += r.total_amount or 0
            data[key]["count"] += 1

    # 填充空月份/季度
    result = []
    if period == "month":
        for i in range(months - 1, -1, -1):
            dt = now - timedelta(days=i * 30)
            key = dt.strftime("%Y-%m")
            d = data.get(key, {"amount": 0, "count": 0})
            result.append({"period": key, "amount": round(d["amount"], 2), "count": d["count"]})
    else:
        for i in range(months // 3):
            dt = now - timedelta(days=i * 90)
            q = (dt.month - 1) // 3 + 1
            key = f"{dt.year}-Q{q}"
            if key not in [r["period"] for r in result]:
                d = data.get(key, {"amount": 0, "count": 0})
                result.insert(0, {"period": key, "amount": round(d["amount"], 2), "count": d["count"]})

    return ResponseModel(data=result)
