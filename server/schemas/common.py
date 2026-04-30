from pydantic import BaseModel
from typing import Optional, List, Any


class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
    total: int = 0
    page: int = 1
    page_size: int = 20
