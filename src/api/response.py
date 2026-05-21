import uuid
from typing import Any

from pydantic import BaseModel, Field


class Meta(BaseModel):
    traceId: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    meta: Meta = Field(default_factory=Meta)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    meta: Meta = Field(default_factory=Meta)


def ok(data: Any) -> SuccessResponse:
    return SuccessResponse(data=data)


def fail(code: str, message: str) -> ErrorResponse:
    return ErrorResponse(error=ErrorDetail(code=code, message=message))
