"""
操作日志查询
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.operation_log import OperationLog
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from routers.auth import get_current_user

router = APIRouter(prefix="/operation-logs", tags=["日志"])


class OperationLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_name: Optional[str] = None
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=list[OperationLogResponse])
def list_operation_logs(
    module: str = None,
    action: str = None,
    target_type: str = None,
    target_id: int = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(OperationLog)

    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    if target_id:
        query = query.filter(OperationLog.target_id == target_id)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)

    query = query.order_by(OperationLog.created_at.desc())
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()
