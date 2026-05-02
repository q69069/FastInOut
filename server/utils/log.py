from sqlalchemy.orm import Session
from models.system import OperationLog


def write_log(db: Session, operator: str, action: str, target: str, detail: str = "", ip: str = ""):
    """写入操作日志"""
    log = OperationLog(
        operator=operator,
        action=action,
        target=target,
        detail=detail,
        ip=ip
    )
    db.add(log)
    db.commit()
