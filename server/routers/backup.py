import os
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from config import DB_PATH, DATA_DIR
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/backup", tags=["数据备份"])


@router.get("/export")
def export_backup():
    """导出数据库备份文件"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="数据库文件不存在")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fastinout_backup_{timestamp}.db"

    return FileResponse(
        path=DB_PATH,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.post("/import", response_model=ResponseModel)
async def import_backup(file: UploadFile = File(...)):
    """导入数据库备份文件，覆盖现有数据库"""
    # 验证文件扩展名
    if not file.filename.endswith('.db'):
        raise HTTPException(status_code=400, detail="请上传 .db 格式的数据库文件")

    # 读取上传文件内容
    content = await file.read()

    # 验证文件不为空
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="上传的文件为空")

    # 验证文件是有效的 SQLite 数据库（检查文件头）
    if not content[:16].startswith(b'SQLite format 3'):
        raise HTTPException(status_code=400, detail="上传的文件不是有效的 SQLite 数据库")

    # 备份当前数据库（以防万一）
    backup_dir = os.path.join(DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    if os.path.exists(DB_PATH):
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"fastinout_before_import_{backup_timestamp}.db")
        shutil.copy2(DB_PATH, backup_path)

    # 写入新数据库文件
    with open(DB_PATH, "wb") as f:
        f.write(content)

    return ResponseModel(message="数据库导入成功，请刷新页面以加载新数据")
