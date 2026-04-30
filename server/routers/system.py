from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.system import OperationLog, Message, BackupRecord
from models.employee import Employee
from schemas.system import OperationLogOut, MessageCreate, MessageOut, BackupRecordOut
from schemas.common import ResponseModel, PaginatedResponse
from utils.auth import hash_password
from datetime import datetime

router = APIRouter(prefix="/api/system", tags=["系统"])


@router.get("/check", response_model=ResponseModel)
def check_init(db: Session = Depends(get_db)):
    admin = db.query(Employee).filter(Employee.username == "admin").first()
    return ResponseModel(data={"initialized": admin is not None})


@router.post("/init", response_model=ResponseModel)
def init_system(db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.username == "admin").first()
    if existing:
        raise HTTPException(status_code=400, detail="系统已初始化")
    admin = Employee(
        code="EMP001",
        name="管理员",
        username="admin",
        password_hash=hash_password("admin123"),
        position="系统管理员",
        status=1
    )
    db.add(admin)
    db.commit()
    return ResponseModel(message="初始化成功，管理员账号：admin / admin123")


@router.get("/logs", response_model=PaginatedResponse)
def list_logs(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(OperationLog)
    total = q.count()
    items = q.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[OperationLogOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.get("/messages", response_model=PaginatedResponse)
def list_messages(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    is_read: int = Query(None), db: Session = Depends(get_db)
):
    q = db.query(Message)
    if is_read is not None:
        q = q.filter(Message.is_read == is_read)
    total = q.count()
    items = q.order_by(Message.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[MessageOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.put("/messages/{msg_id}/read", response_model=ResponseModel)
def mark_read(msg_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).get(msg_id)
    if msg:
        msg.is_read = 1
        msg.read_at = datetime.now()
        db.commit()
    return ResponseModel(message="已标记已读")


@router.post("/upload/image", response_model=ResponseModel)
def upload_image():
    return ResponseModel(message="功能开发中")


@router.post("/backup", response_model=ResponseModel)
def create_backup(db: Session = Depends(get_db)):
    return ResponseModel(message="功能开发中")


@router.get("/backup/list", response_model=ResponseModel)
def list_backups(db: Session = Depends(get_db)):
    items = db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()
    return ResponseModel(data=[BackupRecordOut.model_validate(i) for i in items])


@router.post("/backup/restore", response_model=ResponseModel)
def restore_backup():
    return ResponseModel(message="功能开发中")
