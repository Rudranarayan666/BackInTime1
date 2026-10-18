"""FastAPI dependencies and application state accessors."""

from typing import Annotated

from fastapi import Depends, Request

from backintime.core.config import ConfigStore


def get_config_store(request: Request) -> ConfigStore:
    """Return the configured store for this app instance."""
    config_store = request.app.state.config_store
    if not isinstance(config_store, ConfigStore):
        raise RuntimeError("Application configuration store was not initialized.")
    return config_store


ConfigStoreDependency = Annotated[ConfigStore, Depends(get_config_store)]
