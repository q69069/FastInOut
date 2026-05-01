from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryOut(CategoryBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerCategoryBase(BaseModel):
    name: str
    sort_order: int = 0


class CustomerCategoryCreate(CustomerCategoryBase):
    pass


class CustomerCategoryUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None


class CustomerCategoryOut(CustomerCategoryBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SupplierCategoryBase(BaseModel):
    name: str
    sort_order: int = 0


class SupplierCategoryCreate(SupplierCategoryBase):
    pass


class SupplierCategoryUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None


class SupplierCategoryOut(SupplierCategoryBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
