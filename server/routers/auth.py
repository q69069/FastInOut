from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models.employee import Employee
from schemas.auth import LoginRequest, LoginResponse, CurrentUser
from schemas.common import ResponseModel
from utils.auth import verify_password, create_access_token, decode_access_token
from datetime import datetime, timedelta
import threading

router = APIRouter(prefix="/api/auth", tags=["认证"])

# M1: 登录暴力破解防护 - 记录失败尝试
_login_failures = {}  # {username: [timestamp, ...]}
_login_lock = threading.Lock()
MAX_FAILURES = 5
LOCKOUT_MINUTES = 15

# M3: Token 黑名单
_token_blacklist = set()  # 存储已登出的 token
_blacklist_lock = threading.Lock()


def _check_login_lock(username: str):
    """检查用户是否被锁定"""
    with _login_lock:
        if username not in _login_failures:
            return
        # 清理过期记录
        cutoff = datetime.now() - timedelta(minutes=LOCKOUT_MINUTES)
        _login_failures[username] = [t for t in _login_failures[username] if t > cutoff]
        if len(_login_failures[username]) >= MAX_FAILURES:
            remaining = (_login_failures[username][0] + timedelta(minutes=LOCKOUT_MINUTES) - datetime.now()).seconds // 60
            raise HTTPException(status_code=429, detail=f"登录失败次数过多，请{remaining + 1}分钟后再试")
        if not _login_failures[username]:
            del _login_failures[username]


def _record_login_failure(username: str):
    """记录一次登录失败"""
    with _login_lock:
        if username not in _login_failures:
            _login_failures[username] = []
        _login_failures[username].append(datetime.now())


def _clear_login_failures(username: str):
    """清除用户的失败记录（登录成功时调用）"""
    with _login_lock:
        _login_failures.pop(username, None)


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    # M3: 检查 token 是否在黑名单中
    with _blacklist_lock:
        if token in _token_blacklist:
            raise HTTPException(status_code=401, detail="token已失效，请重新登录")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    user = db.query(Employee).get(payload.get("user_id"))
    if not user or user.status != 1:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


@router.post("/login", response_model=ResponseModel)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # M1: 检查是否被锁定
    _check_login_lock(req.username)
    user = db.query(Employee).filter(Employee.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        _record_login_failure(req.username)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已禁用")
    # M1: 登录成功，清除失败记录
    _clear_login_failures(req.username)
    token = create_access_token({"user_id": user.id, "username": user.username})
    return ResponseModel(data=LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username,
        name=user.name,
        position=user.position
    ))


@router.post("/logout", response_model=ResponseModel)
def logout(authorization: str = Header(None)):
    # M3: 将 token 加入黑名单
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        with _blacklist_lock:
            _token_blacklist.add(token)
    return ResponseModel(message="已退出")


@router.get("/current", response_model=ResponseModel)
def current_user(user: Employee = Depends(get_current_user)):
    return ResponseModel(data=CurrentUser.model_validate(user))
