"""审计日志查看 — Phase A Day 9-10

查看 http_audit_log 表中的 HTTP 请求审计记录。
注意：审批记录在 audit_logs 表（routers/audit.py），这里只看 HTTP 请求日志。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.http_audit_log import HttpAuditLog
from models.employee import Employee
from schemas.common import ResponseModel, PaginatedResponse
from utils.role_check import require_role
from pydantic import BaseModel, ConfigDict
from typing import Optional

router = APIRouter(prefix="/api", tags=["审计日志"])


class HttpAuditLogOut(BaseModel):
    id: int
    user_id: int
    method: str
    path: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


def get_current_user(authorization: str = None, db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    from utils.auth import decode_access_token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token格式错误")
    payload = decode_access_token(authorization.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="token无效")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.get("/audit-logs/http", response_model=PaginatedResponse)
def list_http_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None),
    method: str = Query(None),
    entity_type: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user(authorization, db)

    # 只有管理员可以查看审计日志
    require_role(user, db, "admin", message="只有管理员可以查看审计日志")

    q = db.query(HttpAuditLog)

    if user_id:
        q = q.filter(HttpAuditLog.user_id == user_id)
    if method:
        q = q.filter(HttpAuditLog.method == method)
    if entity_type:
        q = q.filter(HttpAuditLog.entity_type == entity_type)
    if start_date:
        q = q.filter(HttpAuditLog.created_at >= start_date)
    if end_date:
        q = q.filter(HttpAuditLog.created_at <= datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59))

    total = q.count()
    items = q.order_by(HttpAuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 补充用户名
    result = []
    for item in items:
        data = HttpAuditLogOut.model_validate(item).model_dump()
        emp = db.query(Employee).get(item.user_id)
        data["username"] = emp.name if emp else "未知"
        result.append(data)

    return PaginatedResponse(data=result, total=total, page=page, page_size=page_size)
