import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import secrets as _secrets
    SECRET_KEY = _secrets.token_urlsafe(32)
    import warnings
    warnings.warn("SECRET_KEY 环境变量未设置，已生成临时密钥。请设置环境变量 SECRET_KEY！")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, AttributeError):
        return False


def create_access_token(data: dict, extra: dict = None) -> str:
    to_encode = data.copy()
    if extra:
        to_encode.update(extra)
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_role_ids(user, db) -> list[int]:
    """获取用户所有角色ID（employee_roles + employee.role_id 并集）"""
    from models.employee_role import EmployeeRole
    emp_roles = db.query(EmployeeRole).filter(EmployeeRole.employee_id == user.id).all()
    role_ids = [er.role_id for er in emp_roles]
    if user.role_id and user.role_id not in role_ids:
        role_ids.append(user.role_id)
    return role_ids


def has_role(user, db, role_keys: list[str]) -> bool:
    """检查用户是否拥有指定角色中的任意一个（多角色并集）"""
    from models.role import Role
    role_ids = get_user_role_ids(user, db)
    if not role_ids:
        return False
    roles = db.query(Role).filter(Role.id.in_(role_ids), Role.role_key.in_(role_keys)).count()
    return roles > 0


def is_admin(user, db) -> bool:
    """检查用户是否为管理员"""
    return has_role(user, db, ["admin"])
