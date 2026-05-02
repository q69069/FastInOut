"""
操作日志写入工具
"""
from sqlalchemy.orm import Session
from models.operation_log import OperationLog
from datetime import datetime


def log_operation(
    db: Session,
    user_id: int,
    username: str,
    module: str,
    action: str,
    target_type: str = None,
    target_id: int = None,
    target_name: str = None,
    detail: str = None,
    ip_address: str = None
):
    """
    记录操作日志
    """
    log = OperationLog(
        user_id=user_id,
        username=username,
        module=module,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        detail=detail,
        ip_address=ip_address,
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    return log
