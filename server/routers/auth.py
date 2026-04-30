from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from schemas.auth import LoginRequest, LoginResponse, CurrentUser
from schemas.common import ResponseModel
from utils.auth import verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user or user.status != 1:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


@router.post("/login", response_model=ResponseModel)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已禁用")
    token = create_access_token({"user_id": user.id, "username": user.username})
    return ResponseModel(data=LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username,
        name=user.name,
        position=user.position
    ))


@router.post("/logout", response_model=ResponseModel)
def logout():
    return ResponseModel(message="已退出")


@router.get("/current", response_model=ResponseModel)
def current_user(user: Employee = Depends(get_current_user)):
    return ResponseModel(data=CurrentUser.model_validate(user))
