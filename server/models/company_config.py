"""公司设置模型 — Phase C"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class CompanyConfig(Base):
    __tablename__ = "company_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(String(200))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
