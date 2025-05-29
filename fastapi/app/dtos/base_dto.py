from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponseDTO(BaseModel, Generic[T]):
    success: bool
    code: int
    message: str
    data: Optional[T] = None


class BaseWebSocketDTO(BaseModel, Generic[T]):
    type: str
    data: Optional[T] = None


class TimeMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
