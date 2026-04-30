from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.auth import hash_password

router = APIRouter(prefix="/api/employees", tags=["员工"])


@router.get("", response_model=PaginatedResponse)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Employee)
    if keyword:
        q = q.filter(Employee.name.contains(keyword) | Employee.code.contains(keyword) | Employee.username.contains(keyword))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        data=[EmployeeOut.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ResponseModel)
def create_employee(req: EmployeeCreate, db: Session = Depends(get_db)):
    if req.username:
        existing = db.query(Employee).filter(Employee.username == req.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
    data = req.model_dump()
    password = data.pop("password", None)
    emp = Employee(**data)
    if password:
        emp.password_hash = hash_password(password)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return ResponseModel(data=EmployeeOut.model_validate(emp))


@router.get("/{employee_id}", response_model=ResponseModel)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return ResponseModel(data=EmployeeOut.model_validate(emp))


@router.put("/{employee_id}", response_model=ResponseModel)
def update_employee(employee_id: int, req: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    data = req.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    if "username" in data and data["username"] != emp.username:
        existing = db.query(Employee).filter(Employee.username == data["username"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
    for k, v in data.items():
        setattr(emp, k, v)
    if password:
        emp.password_hash = hash_password(password)
    db.commit()
    db.refresh(emp)
    return ResponseModel(data=EmployeeOut.model_validate(emp))


@router.delete("/{employee_id}", response_model=ResponseModel)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    db.delete(emp)
    db.commit()
    return ResponseModel(message="删除成功")
