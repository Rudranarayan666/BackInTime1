"""Validated API request and response models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class ProfileCreateRequest(BaseModel):
    """Client-supplied values for creating a profile."""

    model_config = ConfigDict(extra="forbid")

    profile_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    name: str = Field(min_length=1)
    sources: list[str] = Field(min_length=1)
    target: str = Field(min_length=1)
    excludes: list[str] = Field(default_factory=list)


class ProfilePatchRequest(BaseModel):
    """Partial editable fields for an existing profile."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    sources: list[str] | None = Field(default=None, min_length=1)
    target: str | None = Field(default=None, min_length=1)
    excludes: list[str] | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> ProfilePatchRequest:
        if not self.model_fields_set:
            raise ValueError("At least one profile field must be provided.")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Profile fields must not be null.")
        return self


class ErrorDetail(BaseModel):
    """Stable API error fields."""

    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    """Consistent API error envelope."""

    error: ErrorDetail
