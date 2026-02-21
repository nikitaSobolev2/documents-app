from enum import Enum
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic_core import ErrorDetails


T = TypeVar("T")


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class AppBaseResponse(BaseModel, Generic[T]):
    status: int
    message: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    error_details: Optional[List[ErrorDetails]] = None
