"""
审核记录
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.audit import AuditLog
from schemas import AuditLogResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["审核"])


@router.get("/", response_model=list[AuditLogResponse])
def list_audit_logs(target_type: str = None, target_id: int = None, db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    if target_id:
        query = query.filter(AuditLog.target_id == target_id)
    return query.order_by(AuditLog.created_at.desc()).all()


@router.post("/", response_model=AuditLogResponse)
def create_audit_log(data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = AuditLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
