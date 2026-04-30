from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # 商品编码
    barcode = Column(String(50))  # 条码
    name = Column(String(200), nullable=False)
    spec = Column(String(200))  # 规格
    unit = Column(String(20))  # 单位
    category_id = Column(Integer, ForeignKey("categories.id"))
    purchase_price = Column(Float, default=0)  # 进价
    retail_price = Column(Float, default=0)  # 零售价
    member_price = Column(Float, default=0)  # 会员价
    cost_price = Column(Float, default=0)  # 成本价
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    stock_min = Column(Float, default=0)  # 库存下限
    stock_max = Column(Float, default=0)  # 库存上限
    image = Column(String(500))  # 图片路径
    status = Column(Integer, default=1)  # 1=启用 0=禁用
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
