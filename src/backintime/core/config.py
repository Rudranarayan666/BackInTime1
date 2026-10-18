"""Versioned JSON configuration and profile persistence."""

import hashlib
import json
import os
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

from backintime.core.exceptions import (
    ConfigurationConflictError,
    ConfigurationError,
    ValidationError,
)
from backintime.core.profile import Profile

CONFIG_VERSION = 1


@dataclass(frozen=True, slots=True)
class Configuration:
    """Application configuration, including unrecognized extension fields."""

    profiles: tuple[Profile, ...] = ()
    extensions: dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        seen_ids: set[str] = set()
        for profile in self.profiles:
            profile.validate()
            if profile.profile_id in seen_ids:
                raise ValidationError(f"Duplicate profile ID: {profile.profile_id!r}")
            seen_ids.add(profile.profile_id)


class ConfigStore:
    """Read and atomically persist the application configuration."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser()
        self._lock = RLock()

    @classmethod
    def default_path(cls) -> Path:
        """Return the XDG configuration path, with the standard home fallback."""
        configured_home = os.environ.get("XDG_CONFIG_HOME")
        config_home = (
            Path(configured_home).expanduser() if configured_home else Path.home() / ".config"
        )
        return cls(config_home / "backintime" / "config.json").path

    def load(self) -> Configuration:
        """Load and validate configuration; a missing file means no profiles."""
        try:
            raw_text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return Configuration()
        except OSError as exc:
            raise ConfigurationError(f"Cannot read configuration '{self.path}': {exc}") from exc

        try:
            raw = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Configuration '{self.path}' is not valid JSON: {exc.msg}."
            ) from exc
        if not isinstance(raw, dict):
            raise ConfigurationError("Configuration root must be a JSON object.")

        version = raw.get("version")
        if type(version) is not int or version != CONFIG_VERSION:
            raise ConfigurationError(
                f"Unsupported configuration version {version!r}; expected {CONFIG_VERSION}."
            )
        raw_profiles = raw.get("profiles", [])
        if not isinstance(raw_profiles, list):
            raise ConfigurationError("Configuration 'profiles' must be a list.")

        known_keys = {"version", "profiles"}
        profiles = tuple(_parse_profile(item) for item in raw_profiles)
        configuration = Configuration(
            profiles=profiles,
            extensions={key: value for key, value in raw.items() if key not in known_keys},
        )
        try:
            configuration.validate()
        except ValidationError as exc:
            raise ConfigurationError(f"Invalid configuration: {exc}") from exc
        return configuration

    def load_with_revision(self) -> tuple[Configuration, str]:
        """Load configuration and return its content hash for optimistic updates."""
        with self._lock:
            configuration = self.load()
            return configuration, self._revision_unlocked()

    def update(
        self,
        expected_revision: str,
        transform: Callable[[Configuration], Configuration],
    ) -> tuple[Configuration, str]:
        """Serialize a validated read-modify-write and reject stale revisions."""
        with self._lock:
            configuration, current_revision = self.load_with_revision()
            if current_revision != expected_revision:
                raise ConfigurationConflictError("Configuration changed since it was last read.")
            updated = transform(configuration)
            try:
                updated.validate()
            except ValidationError:
                raise
            self.save(updated)
            return updated, self._revision_unlocked()

    def save(self, configuration: Configuration) -> None:
        """Validate and atomically replace the configuration file."""
        with self._lock:
            self._save_locked(configuration)

    def _save_locked(self, configuration: Configuration) -> None:
        try:
            configuration.validate()
        except ValidationError as exc:
            raise ConfigurationError(f"Invalid configuration: {exc}") from exc

        data: dict[str, object] = {
            **configuration.extensions,
            "version": CONFIG_VERSION,
            "profiles": [_profile_to_dict(profile) for profile in configuration.profiles],
        }
        try:
            serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            file_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
            )
            temporary_path = Path(temporary_name)
            try:
                if os.name != "nt":
                    os.chmod(temporary_path, 0o600)
                with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(serialized)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary_path, self.path)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()
        except (OSError, TypeError, ValueError) as exc:
            raise ConfigurationError(f"Cannot write configuration '{self.path}': {exc}") from exc

    def _revision_unlocked(self) -> str:
        try:
            content = self.path.read_bytes()
        except FileNotFoundError:
            content = b""
        except OSError as exc:
            raise ConfigurationError(f"Cannot read configuration '{self.path}': {exc}") from exc
        return hashlib.sha256(content).hexdigest()


def _parse_profile(value: Any) -> Profile:
    if not isinstance(value, dict):
        raise ConfigurationError("Each profile must be a JSON object.")
    profile_id = value.get("profile_id")
    name = value.get("name")
    target = value.get("target")
    sources = value.get("sources")
    excludes = value.get("excludes", [])
    if not isinstance(profile_id, str) or not isinstance(name, str):
        raise ConfigurationError("Each profile must have string 'profile_id' and 'name' fields.")
    if not isinstance(target, str):
        raise ConfigurationError(f"Profile '{profile_id}' must have a string 'target' field.")
    if not isinstance(sources, list) or not all(isinstance(item, str) for item in sources):
        raise ConfigurationError(f"Profile '{profile_id}' 'sources' must be a list of strings.")
    if not isinstance(excludes, list) or not all(isinstance(item, str) for item in excludes):
        raise ConfigurationError(f"Profile '{profile_id}' 'excludes' must be a list of strings.")

    known_keys = {"profile_id", "name", "target", "sources", "excludes"}
    return Profile(
        profile_id=profile_id,
        name=name,
        sources=tuple(Path(item) for item in sources),
        target=Path(target),
        excludes=tuple(excludes),
        extensions={key: item for key, item in value.items() if key not in known_keys},
    )


def _profile_to_dict(profile: Profile) -> dict[str, object]:
    return {
        **profile.extensions,
        "profile_id": profile.profile_id,
        "name": profile.name,
        "sources": [str(source) for source in profile.sources],
        "target": str(profile.target),
        "excludes": list(profile.excludes),
    }
