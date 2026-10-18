"""FastAPI application factory for loopback-hosted local management."""

import logging
from collections.abc import Awaitable, Callable, Mapping
from contextvars import ContextVar
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backintime.api.routes import router
from backintime.api.schemas import ErrorDetail, ErrorResponse
from backintime.core.config import ConfigStore

_request_id: ContextVar[str] = ContextVar("backintime_request_id", default="-")
_logger = logging.getLogger("backintime.api")


def create_app(*, config_store: ConfigStore | None = None) -> FastAPI:
    """Create an API application with an injectable configuration store."""
    app = FastAPI(
        title="BackInTime API",
        version="0.1.0",
        description="Loopback-local API for the independent BackInTime application.",
    )
    app.state.config_store = config_store or ConfigStore(ConfigStore.default_path())
    app.include_router(router)

    @app.middleware("http")
    async def attach_request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid4().hex
        token = _request_id.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            _request_id.reset(token)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        del request
        if isinstance(exc.detail, Mapping):
            code = str(exc.detail.get("code", "HTTP_ERROR"))
            message = str(exc.detail.get("message", "Request failed."))
        else:
            code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
            message = str(exc.detail)
        if code == "CONFIGURATION_INVALID":
            _logger.error("Configuration failure (request_id=%s): %s", _request_id.get(), message)
            message = "The application configuration could not be loaded or validated."
        return _error_response(exc.status_code, code, message)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        del request
        fields = ", ".join(".".join(str(part) for part in error["loc"]) for error in exc.errors())
        message = f"Request validation failed{f' for {fields}' if fields else ''}."
        return _error_response(422, "REQUEST_INVALID", message)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        _logger.exception(
            "Unhandled API error for %s %s (request_id=%s)",
            request.method,
            request.url.path,
            _request_id.get(),
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return _error_response(500, "INTERNAL_ERROR", "An unexpected server error occurred.")

    return app


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            request_id=_request_id.get(),
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers={"X-Request-ID": _request_id.get()},
    )


app = create_app()
