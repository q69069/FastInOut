import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.print_template import PrintTemplate
from models.sales import SalesOrder, SalesOrderItem, SalesStockout, SalesStockoutItem
from models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseStockin, PurchaseStockinItem
from models.customer import Customer
from models.supplier import Supplier
from models.product import Product
from models.warehouse import Warehouse
from models.finance import Receipt, Payment
from models.company import Company
from schemas.print_template import PrintTemplateCreate, PrintTemplateUpdate, PrintTemplateOut
from schemas.common import ResponseModel, PaginatedResponse

router = APIRouter(prefix="/api/print-templates", tags=["打印模板"])

TEMPLATE_TYPES = {
    "sales": "销售单",
    "purchase": "采购单",
    "stockin": "入库单",
    "stockout": "出库单",
    "statement": "对账单",
    "receipt": "收款凭证",
}

DEFAULT_TEMPLATES = [
    {
        "name": "默认销售单(A4)",
        "template_type": "sales",
        "paper_size": "A4",
        "content": """<div class="print-page">
  <h2 style="text-align:center">{{company_name}}</h2>
  <h3 style="text-align:center">销售单</h3>
  <div style="display:flex;justify-content:space-between;margin:10px 0">
    <span>客户：{{customer_name}}</span>
    <span>单号：{{order_code}}</span>
    <span>日期：{{order_date}}</span>
  </div>
  <table style="width:100%;border-collapse:collapse">
    <thead>
      <tr style="background:#f5f5f5">
        <th style="border:1px solid #333;padding:6px">序号</th>
        <th style="border:1px solid #333;padding:6px">商品名称</th>
        <th style="border:1px solid #333;padding:6px">规格</th>
        <th style="border:1px solid #333;padding:6px">单位</th>
        <th style="border:1px solid #333;padding:6px">数量</th>
        <th style="border:1px solid #333;padding:6px">单价</th>
        <th style="border:1px solid #333;padding:6px">金额</th>
      </tr>
    </thead>
    <tbody>
      {{#items}}
      <tr>
        <td style="border:1px solid #333;padding:6px;text-align:center">{{index}}</td>
        <td style="border:1px solid #333;padding:6px">{{product_name}}</td>
        <td style="border:1px solid #333;padding:6px">{{spec}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:center">{{unit}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{quantity}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{price}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{amount}}</td>
      </tr>
      {{/items}}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="6" style="border:1px solid #333;padding:6px;text-align:right;font-weight:bold">合计：</td>
        <td style="border:1px solid #333;padding:6px;text-align:right;font-weight:bold">{{total_amount}}</td>
      </tr>
    </tfoot>
  </table>
  <div style="margin-top:30px;display:flex;justify-content:space-between">
    <span>制单人：________</span>
    <span>审核人：________</span>
    <span>收货人签字：________</span>
  </div>
</div>""",
        "is_default": True,
    },
    {
        "name": "默认采购单(A4)",
        "template_type": "purchase",
        "paper_size": "A4",
        "content": """<div class="print-page">
  <h2 style="text-align:center">{{company_name}}</h2>
  <h3 style="text-align:center">采购单</h3>
  <div style="display:flex;justify-content:space-between;margin:10px 0">
    <span>供应商：{{supplier_name}}</span>
    <span>单号：{{order_code}}</span>
    <span>日期：{{order_date}}</span>
  </div>
  <table style="width:100%;border-collapse:collapse">
    <thead>
      <tr style="background:#f5f5f5">
        <th style="border:1px solid #333;padding:6px">序号</th>
        <th style="border:1px solid #333;padding:6px">商品名称</th>
        <th style="border:1px solid #333;padding:6px">规格</th>
        <th style="border:1px solid #333;padding:6px">单位</th>
        <th style="border:1px solid #333;padding:6px">数量</th>
        <th style="border:1px solid #333;padding:6px">单价</th>
        <th style="border:1px solid #333;padding:6px">金额</th>
      </tr>
    </thead>
    <tbody>
      {{#items}}
      <tr>
        <td style="border:1px solid #333;padding:6px;text-align:center">{{index}}</td>
        <td style="border:1px solid #333;padding:6px">{{product_name}}</td>
        <td style="border:1px solid #333;padding:6px">{{spec}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:center">{{unit}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{quantity}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{price}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{amount}}</td>
      </tr>
      {{/items}}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="6" style="border:1px solid #333;padding:6px;text-align:right;font-weight:bold">合计：</td>
        <td style="border:1px solid #333;padding:6px;text-align:right;font-weight:bold">{{total_amount}}</td>
      </tr>
    </tfoot>
  </table>
  <div style="margin-top:30px;display:flex;justify-content:space-between">
    <span>制单人：________</span>
    <span>审核人：________</span>
    <span>供应商签字：________</span>
  </div>
</div>""",
        "is_default": True,
    },
    {
        "name": "默认收款凭证(58mm)",
        "template_type": "receipt",
        "paper_size": "58mm",
        "content": """<div class="print-page" style="width:58mm;padding:2mm;font-size:12px">
  <div style="text-align:center;font-weight:bold;font-size:14px">{{company_name}}</div>
  <div style="text-align:center;margin:4px 0">收款凭证</div>
  <div>客户：{{customer_name}}</div>
  <div>金额：¥{{amount}}</div>
  <div>方式：{{payment_method}}</div>
  <div>单号：{{receipt_code}}</div>
  <div>日期：{{receipt_date}}</div>
  <div>业务员：{{salesman}}</div>
  <div style="margin-top:10px">签字：_______</div>
  <div style="text-align:center;margin-top:6px">谢谢惠顾！</div>
</div>""",
        "is_default": True,
    },
    {
        "name": "默认对账单(A4)",
        "template_type": "statement",
        "paper_size": "A4",
        "content": """<div class="print-page">
  <h2 style="text-align:center">{{company_name}}</h2>
  <h3 style="text-align:center">客户对账单</h3>
  <div style="display:flex;justify-content:space-between;margin:10px 0">
    <span>客户：{{customer_name}}</span>
    <span>期间：{{start_date}} 至 {{end_date}}</span>
  </div>
  <table style="width:100%;border-collapse:collapse">
    <thead>
      <tr style="background:#f5f5f5">
        <th style="border:1px solid #333;padding:6px">日期</th>
        <th style="border:1px solid #333;padding:6px">单号</th>
        <th style="border:1px solid #333;padding:6px">类型</th>
        <th style="border:1px solid #333;padding:6px">销售</th>
        <th style="border:1px solid #333;padding:6px">退货</th>
        <th style="border:1px solid #333;padding:6px">收款</th>
        <th style="border:1px solid #333;padding:6px">余额</th>
      </tr>
    </thead>
    <tbody>
      {{#items}}
      <tr>
        <td style="border:1px solid #333;padding:6px">{{date}}</td>
        <td style="border:1px solid #333;padding:6px">{{code}}</td>
        <td style="border:1px solid #333;padding:6px">{{type}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{sales}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{returns}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{payments}}</td>
        <td style="border:1px solid #333;padding:6px;text-align:right">{{balance}}</td>
      </tr>
      {{/items}}
    </tbody>
  </table>
  <div style="margin-top:20px">
    <span>期初应收：¥{{opening_balance}}</span> &nbsp;&nbsp;
    <span>本期销售：¥{{total_sales}}</span> &nbsp;&nbsp;
    <span>本期收款：¥{{total_payments}}</span> &nbsp;&nbsp;
    <span style="font-weight:bold">期末应收：¥{{closing_balance}}</span>
  </div>
  <div style="margin-top:30px;display:flex;justify-content:space-between">
    <span>对账人：________</span>
    <span>客户确认签字：________</span>
  </div>
</div>""",
        "is_default": True,
    },
]


def init_default_templates(db: Session):
    for t in DEFAULT_TEMPLATES:
        existing = db.query(PrintTemplate).filter(
            PrintTemplate.template_type == t["template_type"],
            PrintTemplate.is_default == True
        ).first()
        if not existing:
            db.add(PrintTemplate(**t))
    db.commit()


@router.get("", response_model=PaginatedResponse)
def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    template_type: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(PrintTemplate)
    if template_type:
        q = q.filter(PrintTemplate.template_type == template_type)
    total = q.count()
    items = q.order_by(PrintTemplate.is_default.desc(), PrintTemplate.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[PrintTemplateOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/types", response_model=ResponseModel)
def get_template_types():
    return ResponseModel(data=[{"value": k, "label": v} for k, v in TEMPLATE_TYPES.items()])


@router.get("/{template_id}", response_model=ResponseModel)
def get_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(PrintTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    return ResponseModel(data=PrintTemplateOut.model_validate(t))


@router.post("", response_model=ResponseModel)
def create_template(req: PrintTemplateCreate, db: Session = Depends(get_db)):
    if req.template_type not in TEMPLATE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效模板类型: {req.template_type}")
    if req.is_default:
        db.query(PrintTemplate).filter(
            PrintTemplate.template_type == req.template_type
        ).update({"is_default": False})
    t = PrintTemplate(**req.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return ResponseModel(data=PrintTemplateOut.model_validate(t))


@router.put("/{template_id}", response_model=ResponseModel)
def update_template(template_id: int, req: PrintTemplateUpdate, db: Session = Depends(get_db)):
    t = db.query(PrintTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    update_data = req.model_dump(exclude_unset=True)
    if update_data.get("is_default"):
        db.query(PrintTemplate).filter(
            PrintTemplate.template_type == t.template_type,
            PrintTemplate.id != template_id
        ).update({"is_default": False})
    for k, v in update_data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return ResponseModel(data=PrintTemplateOut.model_validate(t))


@router.delete("/{template_id}", response_model=ResponseModel)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    t = db.query(PrintTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(t)
    db.commit()
    return ResponseModel(message="删除成功")


@router.get("/{template_id}/preview/{doc_type}/{doc_id}", response_model=ResponseModel)
def preview_print(template_id: int, doc_type: str, doc_id: int, db: Session = Depends(get_db)):
    """用指定模板渲染打印预览数据"""
    t = db.query(PrintTemplate).get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")

    company = db.query(Company).first()
    company_name = company.name if company else "公司名称"

    data = {"company_name": company_name}

    if doc_type == "sales":
        order = db.query(SalesOrder).get(doc_id)
        if not order:
            raise HTTPException(status_code=404, detail="销售订单不存在")
        customer = db.query(Customer).get(order.customer_id)
        items = db.query(SalesOrderItem).filter(SalesOrderItem.order_id == order.id).all()
        item_list = []
        for i, item in enumerate(items):
            product = db.query(Product).get(item.product_id)
            item_list.append({
                "index": i + 1,
                "product_name": product.name if product else "",
                "spec": product.spec if product else "",
                "unit": product.unit if product else "",
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.amount,
            })
        data.update({
            "customer_name": customer.name if customer else "",
            "order_code": order.code,
            "order_date": str(order.created_at)[:10],
            "total_amount": order.total_amount,
            "items": item_list,
        })

    elif doc_type == "purchase":
        order = db.query(PurchaseOrder).get(doc_id)
        if not order:
            raise HTTPException(status_code=404, detail="采购订单不存在")
        supplier = db.query(Supplier).get(order.supplier_id)
        items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order.id).all()
        item_list = []
        for i, item in enumerate(items):
            product = db.query(Product).get(item.product_id)
            item_list.append({
                "index": i + 1,
                "product_name": product.name if product else "",
                "spec": product.spec if product else "",
                "unit": product.unit if product else "",
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.amount,
            })
        data.update({
            "supplier_name": supplier.name if supplier else "",
            "order_code": order.code,
            "order_date": str(order.created_at)[:10],
            "total_amount": order.total_amount,
            "items": item_list,
        })

    elif doc_type == "receipt":
        r = db.query(Receipt).get(doc_id)
        if not r:
            raise HTTPException(status_code=404, detail="收款单不存在")
        customer = db.query(Customer).get(r.customer_id)
        data.update({
            "customer_name": customer.name if customer else "",
            "amount": r.amount,
            "payment_method": r.payment_method or "",
            "receipt_code": r.code,
            "receipt_date": str(r.created_at)[:10],
            "salesman": "",
        })

    elif doc_type == "statement":
        customer = db.query(Customer).get(doc_id)
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")
        data.update({
            "customer_name": customer.name,
            "opening_balance": customer.receivable_balance or 0,
            "total_sales": 0,
            "total_payments": 0,
            "closing_balance": customer.receivable_balance or 0,
            "start_date": "",
            "end_date": "",
            "items": [],
        })

    return ResponseModel(data={"template": t.content, "data": data})
