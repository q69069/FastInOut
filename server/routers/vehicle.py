"""
车销相关
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.vehicle import VehicleSalesOut, VehicleReturn, VehicleLoss
from schemas import VehicleSalesOutResponse, VehicleReturnResponse, VehicleLossResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/vehicle", tags=["车销"])


# 车销出库
@router.get("/sales-outs", response_model=list[VehicleSalesOutResponse])
def list_vehicle_sales_outs(db: Session = Depends(get_db)):
    return db.query(VehicleSalesOut).order_by(VehicleSalesOut.created_at.desc()).all()


@router.get("/sales-outs/{id}", response_model=VehicleSalesOutResponse)
def get_vehicle_sales_out(id: int, db: Session = Depends(get_db)):
    return db.query(VehicleSalesOut).filter(VehicleSalesOut.id == id).first()


@router.post("/sales-outs", response_model=VehicleSalesOutResponse)
def create_vehicle_sales_out(data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = VehicleSalesOut(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sales-outs/{id}", response_model=VehicleSalesOutResponse)
def update_vehicle_sales_out(id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(VehicleSalesOut).filter(VehicleSalesOut.id == id).first()
    if not obj:
        raise ValueError("记录不存在")
    for key, value in data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sales-outs/{id}")
def delete_vehicle_sales_out(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(VehicleSalesOut).filter(VehicleSalesOut.id == id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return {"success": True}


# 车销回库
@router.get("/returns", response_model=list[VehicleReturnResponse])
def list_vehicle_returns(db: Session = Depends(get_db)):
    return db.query(VehicleReturn).order_by(VehicleReturn.created_at.desc()).all()


@router.post("/returns", response_model=VehicleReturnResponse)
def create_vehicle_return(data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = VehicleReturn(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# 车销报损
@router.get("/losses", response_model=list[VehicleLossResponse])
def list_vehicle_losses(db: Session = Depends(get_db)):
    return db.query(VehicleLoss).order_by(VehicleLoss.created_at.desc()).all()


@router.post("/losses", response_model=VehicleLossResponse)
def create_vehicle_loss(data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = VehicleLoss(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
