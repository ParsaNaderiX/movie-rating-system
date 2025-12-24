from fastapi import status


class AppHTTPException(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundError(AppHTTPException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class ValidationError(AppHTTPException):
    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, message)
