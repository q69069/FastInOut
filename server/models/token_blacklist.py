from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_hash = Column(String(64), unique=True, index=True)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
