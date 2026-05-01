from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, func
from database import Base


class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_no = Column(String(50), nullable=False)  # 批次号
    production_date = Column(Date)  # 生产日期
    expire_date = Column(Date)  # 过期日期
    quantity = Column(Float, default=0)  # 当前数量
    cost_price = Column(Float, default=0)  # 成本价
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    status = Column(String(20), default="active")  # active=正常, expired=过期, used=用完
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
