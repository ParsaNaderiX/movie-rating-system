from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: int
    message: str


class SuccessResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: T


class FailureResponse(BaseModel):
    status: str = "failure"
    error: ErrorDetail
