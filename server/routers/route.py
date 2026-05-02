"""
路线档案
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.route import Route
from models.employee_route import EmployeeRoute
from schemas import RouteCreate, RouteUpdate, RouteResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/routes", tags=["路线"])


@router.get("/", response_model=list[RouteResponse])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).order_by(Route.sort_order).all()
    return routes


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    return db.query(Route).filter(Route.id == route_id).first()


@router.post("/", response_model=RouteResponse)
def create_route(data: RouteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    route = Route(**data.model_dump())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.put("/{route_id}", response_model=RouteResponse)
def update_route(route_id: int, data: RouteUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise ValueError("路线不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return route


@router.delete("/{route_id}")
def delete_route(route_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise ValueError("路线不存在")
    db.delete(route)
    db.commit()
    return {"success": True}
