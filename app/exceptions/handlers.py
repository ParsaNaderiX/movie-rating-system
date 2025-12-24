from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.http_exceptions import AppHTTPException


def _failure_payload(status_code: int, message: str) -> dict:
    return {
        "status": "failure",
        "error": {"code": status_code, "message": message},
    }


async def app_http_exception_handler(
    _request: Request,
    exc: AppHTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_failure_payload(exc.status_code, exc.message),
    )


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=_failure_payload(exc.status_code, message),
    )


async def validation_exception_handler(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return JSONResponse(
        status_code=status_code,
        content=_failure_payload(status_code, "Validation error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppHTTPException, app_http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
