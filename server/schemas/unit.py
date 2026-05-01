from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 单位 ==========
class UnitCreate(BaseModel):
    name: str
    symbol: Optional[str] = None
    description: Optional[str] = None


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class UnitOut(BaseModel):
    id: int
    name: str
    symbol: Optional[str] = None
    description: Optional[str] = None
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 单位换算 ==========
class UnitConversionCreate(BaseModel):
    product_id: int
    from_unit_id: int
    to_unit_id: int
    ratio: float = Field(gt=0, description="换算比例必须大于0")
    level: int = Field(ge=1, le=10, default=1, description="层级：1=第一层，2=第二层...")


class UnitConversionOut(BaseModel):
    id: int
    product_id: int
    from_unit_id: int
    to_unit_id: int
    from_unit_name: Optional[str] = None
    to_unit_name: Optional[str] = None
    ratio: float
    level: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 商品单位配置（完整换算链） ==========
class ProductUnitConfig(BaseModel):
    """商品的完整单位换算链，如：1件=4中包，1中包=20支"""
    product_id: int
    base_unit_id: int  # 最小单位（支）
    base_unit_name: Optional[str] = None
    conversions: List[UnitConversionOut] = []  # 换算链
