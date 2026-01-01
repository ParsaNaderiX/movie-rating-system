import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.http_exceptions import AppHTTPException

logger = logging.getLogger("movie_rating")


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
    request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    route = request.url.path
    if route.startswith("/api/v1/movies/") and route.endswith("/ratings"):
        movie_id = "-"
        rating = "-"
        parts = route.split("/")
        if len(parts) >= 6:
            movie_id = parts[4]
        try:
            body = await request.json()
            if isinstance(body, dict) and "score" in body:
                rating = body["score"]
        except Exception:
            pass
        logger.warning(
            "Invalid rating value",
            extra={"movie_id": movie_id, "rating": rating, "route": route},
        )
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return JSONResponse(
        status_code=status_code,
        content=_failure_payload(status_code, "Validation error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppHTTPException, app_http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
