from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    detail: str
    status: int
    data: T | None
    meta: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(
        cls, detail: str = "Ok", data: T | None = None, **kwargs
    ) -> "BaseResponse":
        return cls(detail=detail, status=200, data=data or None, **kwargs)

    @classmethod
    def error(cls, detail: str, status: int = 500, **kwargs) -> "BaseResponse":
        return cls(detail=detail, status=status, data=None, **kwargs)
