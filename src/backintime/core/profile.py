"""Backup profile model and validation."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from backintime.core.exceptions import ValidationError

_PROFILE_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}", re.ASCII)


@dataclass(frozen=True, slots=True)
class Profile:
    """Configuration for one independent backup destination and source set."""

    profile_id: str
    name: str
    sources: tuple[Path, ...]
    target: Path
    excludes: tuple[str, ...] = ()
    extensions: dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate profile values without touching source or target contents."""
        if not _PROFILE_ID.fullmatch(self.profile_id):
            raise ValidationError(
                "Profile ID must start with a lowercase letter or digit and contain "
                "only lowercase letters, digits, underscores, or hyphens (up to 64 "
                "characters)."
            )
        if not self.name.strip():
            raise ValidationError("Profile name must not be empty.")
        if not self.sources:
            raise ValidationError(f"Profile '{self.profile_id}' must have at least one source.")
        if "\x00" in str(self.target):
            raise ValidationError(f"Profile '{self.profile_id}' target contains an invalid path.")
        if not self.target.is_absolute():
            raise ValidationError(f"Profile '{self.profile_id}' target must be an absolute path.")

        resolved_sources: list[Path] = []
        for source in self.sources:
            if "\x00" in str(source):
                raise ValidationError(
                    f"Profile '{self.profile_id}' source contains an invalid path."
                )
            if not source.is_absolute():
                raise ValidationError(
                    f"Profile '{self.profile_id}' source must be an absolute path: {source}"
                )
            try:
                resolved_sources.append(source.expanduser().resolve(strict=False))
            except (OSError, RuntimeError, ValueError) as exc:
                raise ValidationError(
                    f"Cannot resolve profile '{self.profile_id}' source '{source}': {exc}"
                ) from exc

        try:
            resolved_target = self.target.expanduser().resolve(strict=False)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ValidationError(
                f"Cannot resolve profile '{self.profile_id}' target '{self.target}': {exc}"
            ) from exc
        for source in resolved_sources:
            if resolved_target == source or source in resolved_target.parents:
                raise ValidationError(
                    f"Profile '{self.profile_id}' target is inside source '{source}'."
                )

        if any("\x00" in rule for rule in self.excludes):
            raise ValidationError(f"Profile '{self.profile_id}' contains an invalid exclude rule.")
