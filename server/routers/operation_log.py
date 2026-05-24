from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.operation_log import OperationLog
from models.employee import Employee
from schemas.system import OperationLogOut
from schemas.common import PaginatedResponse
from deps import get_current_user

router = APIRouter(prefix="/api/operation-logs", tags=["日志"])


@router.get("/", response_model=PaginatedResponse)
def list_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    module: str = Query(None),
    action: str = Query(None),
    target_type: str = Query(None),
    target_id: int = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(OperationLog)
    if module:
        q = q.filter(OperationLog.module == module)
    if action:
        q = q.filter(OperationLog.action == action)
    if target_type:
        q = q.filter(OperationLog.target_type == target_type)
    if target_id:
        q = q.filter(OperationLog.target_id == target_id)
    if start_date:
        q = q.filter(OperationLog.created_at >= start_date)
    if end_date:
        q = q.filter(OperationLog.created_at <= end_date)
    total = q.count()
    items = q.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[OperationLogOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)
