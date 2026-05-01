from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base


class Promotion(Base):
    """促销方案"""
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # 促销名称
    promo_type = Column(String(20), nullable=False)  # threshold(满减) / discount(折扣)
    threshold_amount = Column(Float, default=0)  # 满减门槛金额
    discount_value = Column(Float, default=0)  # 满减金额 或 折扣比例(0.85=八五折)
    start_date = Column(DateTime)  # 开始时间
    end_date = Column(DateTime)  # 结束时间
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
