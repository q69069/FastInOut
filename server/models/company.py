from datetime import datetime
from sqlalchemy import text, Column, Integer, String, DateTime, func
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    logo = Column(String(500))
    phone = Column(String(50))
    address = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
