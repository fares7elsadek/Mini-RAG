from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} '{identifier}' not found.",
        )


class ValidationException(AppException):
    """Client-provided data is invalid (422)."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
        )


class FileProcessingException(AppException):
    """File could not be processed (400)."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
        )


class DuplicateException(AppException):
    """Conflict / duplicate resource (409)."""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"{resource} '{identifier}' already exists.",
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Convert AppException subclasses into a uniform JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )
