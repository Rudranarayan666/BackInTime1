"""Read-only API routes backed by core services."""

import platform
import shutil

from fastapi import APIRouter, HTTPException

from backintime import __version__
from backintime.api.dependencies import ConfigStoreDependency
from backintime.api.schemas import (
    HealthResponse,
    ProfileListResponse,
    ProfileResponse,
    SystemInfoResponse,
)
from backintime.core.exceptions import ConfigurationError

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the API process is responsive without inspecting user config."""
    return HealthResponse(status="ok", version=__version__)


@router.get("/system/info", response_model=SystemInfoResponse)
def system_info() -> SystemInfoResponse:
    """Report runtime capabilities without exposing filesystem locations."""
    return SystemInfoResponse(
        platform=platform.system(),
        python_version=platform.python_version(),
        rsync_available=shutil.which("rsync") is not None,
    )


@router.get("/profiles", response_model=ProfileListResponse)
def list_profiles(config_store: ConfigStoreDependency) -> ProfileListResponse:
    """List validated configured profiles using the existing core ConfigStore."""
    try:
        configuration = config_store.load()
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "CONFIGURATION_INVALID", "message": str(exc)},
        ) from exc

    return ProfileListResponse(
        profiles=[
            ProfileResponse(
                profile_id=profile.profile_id,
                name=profile.name,
                sources=[str(path) for path in profile.sources],
                target=str(profile.target),
                excludes=list(profile.excludes),
            )
            for profile in configuration.profiles
        ]
    )


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str, config_store: ConfigStoreDependency) -> ProfileResponse:
    """Return one configured profile by its stable identifier."""
    try:
        configuration = config_store.load()
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "CONFIGURATION_INVALID", "message": str(exc)},
        ) from exc

    for profile in configuration.profiles:
        if profile.profile_id == profile_id:
            return ProfileResponse(
                profile_id=profile.profile_id,
                name=profile.name,
                sources=[str(path) for path in profile.sources],
                target=str(profile.target),
                excludes=list(profile.excludes),
            )
    raise HTTPException(
        status_code=404,
        detail={"code": "PROFILE_NOT_FOUND", "message": "The selected profile does not exist."},
    )
