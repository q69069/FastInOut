from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from schemas.auth import LoginRequest, LoginResponse, CurrentUser
from schemas.common import ResponseModel

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=ResponseModel)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(Employee).filter(Employee.username == req.username).first()
    if not user or user.password_hash != req.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已禁用")
    return ResponseModel(data=LoginResponse(
        token=f"token_{user.id}_{user.username}",
        user_id=user.id,
        username=user.username,
        name=user.name,
        position=user.position
    ))


@router.post("/logout", response_model=ResponseModel)
def logout():
    """退出登录"""
    return ResponseModel(message="已退出")


@router.get("/current", response_model=ResponseModel)
def current_user(db: Session = Depends(get_db)):
    """获取当前用户信息（简化版，后续加token验证）"""
    user = db.query(Employee).first()
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    return ResponseModel(data=CurrentUser.model_validate(user))
