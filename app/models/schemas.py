from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    uptime: float
    environment: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: Optional[str] = None
