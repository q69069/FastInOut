import os

# ========== 路径配置 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "fastinout.db")

# ========== 数据库配置 ==========
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# ========== JWT 配置 ==========
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import secrets as _secrets
    import warnings

    SECRET_KEY = _secrets.token_urlsafe(32)
    warnings.warn("SECRET_KEY 环境变量未设置，已生成临时密钥。请设置环境变量 SECRET_KEY！")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
