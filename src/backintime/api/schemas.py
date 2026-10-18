"""Validated API request and response models."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Liveness response."""

    status: str
    version: str


class SystemInfoResponse(BaseModel):
    """Non-sensitive runtime capability information."""

    platform: str
    python_version: str
    rsync_available: bool


class ProfileResponse(BaseModel):
    """Read-only view of a configured backup profile."""

    model_config = ConfigDict(frozen=True)

    profile_id: str
    name: str
    sources: list[str]
    target: str
    excludes: list[str]


class ProfileListResponse(BaseModel):
    """Configured profiles."""

    profiles: list[ProfileResponse]


class ErrorDetail(BaseModel):
    """Stable API error fields."""

    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    """Consistent API error envelope."""

    error: ErrorDetail
