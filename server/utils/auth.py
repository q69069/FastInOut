import os
import hashlib
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "fastinout-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, pwd_hash = hashed_password.split("$", 1)
        return hashlib.sha256((salt + plain_password).encode()).hexdigest() == pwd_hash
    except (ValueError, AttributeError):
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
