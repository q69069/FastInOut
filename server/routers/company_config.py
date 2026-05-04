"""公司设置路由 — Phase C"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models.company_config import CompanyConfig
from models.employee import Employee
from schemas.common import ResponseModel
from utils.role_check import require_role

router = APIRouter(prefix="/api", tags=["公司设置"])


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


@router.get("/company-configs", response_model=ResponseModel)
def list_configs(authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    items = db.query(CompanyConfig).all()
    result = [{"id": c.id, "config_key": c.config_key, "config_value": c.config_value, "description": c.description} for c in items]
    return ResponseModel(data=result)


@router.put("/company-configs/{config_id}", response_model=ResponseModel)
def update_config(config_id: int, data: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user(authorization, db)
    require_role(user, db, "admin", message="只有管理员可以修改设置")
    config = db.query(CompanyConfig).get(config_id)
    if not config:
        raise HTTPException(404, "配置项不存在")
    config.config_value = data.get("config_value")
    db.commit()
    return ResponseModel(message="设置已保存")


@router.post("/company-configs/init", response_model=ResponseModel)
def init_configs(db: Session = Depends(get_db)):
    """初始化默认配置项"""
    defaults = [
        ("settlement_expense_auto_approve_limit", "500", "交账费用自动审批上限"),
        ("credit_limit_default", "10000", "默认赊账额度"),
        ("anomaly_price_deviation", "0.3", "单价异常偏差阈值"),
    ]
    for key, value, desc in defaults:
        existing = db.query(CompanyConfig).filter(CompanyConfig.config_key == key).first()
        if not existing:
            db.add(CompanyConfig(config_key=key, config_value=value, description=desc))
    db.commit()
    return ResponseModel(message="初始化完成")
