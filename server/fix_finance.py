with open('routers/finance.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix pre-receipt creation: status=0 and use prepaid_balance
old1 = '''    receipt = Receipt(
        code=code, customer_id=req.customer_id, amount=req.amount,
        payment_method=req.payment_method, receipt_type="pre",
        status=1, remark=req.remark, confirmed_at=datetime.now(),
        created_by=user.id
    )
    db.add(receipt)
    # 预收款减少客户应收余额
    customer = db.query(Customer).get(req.customer_id)
    if customer:
        customer.receivable_balance = (customer.receivable_balance or 0) - req.amount'''

new1 = '''    receipt = Receipt(
        code=code, customer_id=req.customer_id, amount=req.amount,
        payment_method=req.payment_method, receipt_type="pre",
        status=0, remark=req.remark,
        created_by=user.id
    )
    db.add(receipt)
    # 预收款增加客户预收余额，不影响应收余额
    customer = db.query(Customer).get(req.customer_id)
    if customer:
        customer.prepaid_balance = (customer.prepaid_balance or 0) + req.amount'''

if old1 in content:
    content = content.replace(old1, new1)
    print("Fixed pre-receipt creation")
else:
    print("Could not find pre-receipt creation pattern")

# Fix pre-to-receivable: use prepaid_balance not receivable_balance
old2 = '''    receipt.amount -= req.amount
    customer = db.query(Customer).get(receipt.customer_id)
    if customer:
        customer.receivable_balance -= req.amount'''

new2 = '''    receipt.amount -= req.amount
    # 客户预收余额减少（应收余额已在销售出库时产生，此处只消耗预收不重复扣减）
    customer = db.query(Customer).get(receipt.customer_id)
    if customer:
        customer.prepaid_balance = (customer.prepaid_balance or 0) - req.amount'''

if old2 in content:
    content = content.replace(old2, new2)
    print("Fixed pre-to-receivable")
else:
    print("Could not find pre-to-receivable pattern")

# Add confirm_pre_receipt endpoint before pre-to-receivable
confirm_endpoint = '''

@router.post("/pre-receipt/{receipt_id}/confirm", response_model=ResponseModel)
def confirm_pre_receipt(receipt_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    """确认预收款单"""
    user = get_current_user(authorization, db)
    r = db.query(Receipt).get(receipt_id)
    if not r:
        raise HTTPException(status_code=404, detail="预收款单不存在")
    require_owner_or_admin(user, r.created_by, db, "无权操作此收款单")
    if r.status != 0:
        raise HTTPException(400, "只有待确认状态的预收款可以确认")
    r.status = 1
    r.confirmed_at = datetime.now()
    r.operator_id = user.id
    db.commit()
    return ResponseModel(message="预收款确认成功")


'''

# Insert before @router.post("/pre-to-receivable"
if '@router.post("/pre-to-receivable"' in content:
    content = content.replace('@router.post("/pre-to-receivable"', confirm_endpoint + '@router.post("/pre-to-receivable"')
    print("Added confirm_pre_receipt endpoint")
else:
    print("Could not find pre-to-receivable endpoint")

with open('routers/finance.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All done")