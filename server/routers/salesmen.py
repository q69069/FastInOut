from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.salesman import Salesman
from models.employee import Employee
from models.sales import SalesOrder
from schemas.salesman import SalesmanCreate, SalesmanUpdate, SalesmanOut
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/salesmen", tags=["业务员"])


@router.get("", response_model=ResponseModel)
def list_salesmen(db: Session = Depends(get_db)):
    salesmen = db.query(Salesman).filter(Salesman.status == 1).all()
    result = []
    for s in salesmen:
        emp = db.query(Employee).get(s.employee_id)
        out = SalesmanOut.model_validate(s)
        out.employee_name = emp.name if emp else ""
        result.append(out)
    return ResponseModel(data=[r.model_dump() for r in result])


@router.post("", response_model=ResponseModel)
def create_salesman(req: SalesmanCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).get(req.employee_id)
    if not emp:
        raise HTTPException(status_code=400, detail="员工不存在")
    existing = db.query(Salesman).filter(Salesman.employee_id == req.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该员工已是业务员")
    salesman = Salesman(
        employee_id=req.employee_id,
        commission_rate=req.commission_rate,
        target_amount=req.target_amount
    )
    db.add(salesman)
    db.commit()
    db.refresh(salesman)
    out = SalesmanOut.model_validate(salesman)
    out.employee_name = emp.name
    return ResponseModel(data=out.model_dump())


@router.put("/{salesman_id}", response_model=ResponseModel)
def update_salesman(salesman_id: int, req: SalesmanUpdate, db: Session = Depends(get_db)):
    salesman = db.query(Salesman).get(salesman_id)
    if not salesman:
        raise HTTPException(status_code=404, detail="业务员不存在")
    data = req.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(salesman, k, v)
    db.commit()
    db.refresh(salesman)
    emp = db.query(Employee).get(salesman.employee_id)
    out = SalesmanOut.model_validate(salesman)
    out.employee_name = emp.name if emp else ""
    return ResponseModel(data=out.model_dump())


@router.get("/stats", response_model=ResponseModel)
def salesman_stats(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    salesmen = db.query(Salesman).filter(Salesman.status == 1).all()
    result = []
    for s in salesmen:
        emp = db.query(Employee).get(s.employee_id)
        q = db.query(SalesOrder).filter(
            SalesOrder.operator_id == s.employee_id,
            SalesOrder.status.in_([1, 2])  # 已确认/已出库
        )
        if start_date:
            q = q.filter(SalesOrder.created_at >= start_date)
        if end_date:
            q = q.filter(SalesOrder.created_at <= end_date + " 23:59:59")
        orders = q.all()
        total_amount = sum(o.total_amount or 0 for o in orders)
        order_count = len(orders)
        commission = total_amount * (s.commission_rate or 0)
        result.append({
            "salesman_id": s.id,
            "employee_id": s.employee_id,
            "employee_name": emp.name if emp else "",
            "commission_rate": s.commission_rate,
            "target_amount": s.target_amount,
            "actual_amount": total_amount,
            "order_count": order_count,
            "commission": round(commission, 2)
        })
    return ResponseModel(data=result)
