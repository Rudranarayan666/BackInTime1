"""Strict parsing and ordering for timestamped snapshot identifiers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from backintime.core.exceptions import ValidationError

_SNAPSHOT_ID = re.compile(r"([0-9]{8}-[0-9]{6})-([0-9]{3})", re.ASCII)
_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"


@dataclass(frozen=True, order=True, slots=True)
class SnapshotID:
    """A validated local snapshot identifier."""

    value: str

    def __post_init__(self) -> None:
        match = _SNAPSHOT_ID.fullmatch(self.value)
        if match is None:
            raise ValidationError(f"Invalid snapshot ID: {self.value!r}")
        try:
            parsed = datetime.strptime(match.group(1), _TIMESTAMP_FORMAT)
        except ValueError as exc:
            raise ValidationError(f"Invalid snapshot ID timestamp: {self.value!r}") from exc
        if parsed.strftime(_TIMESTAMP_FORMAT) != match.group(1):
            raise ValidationError(f"Invalid snapshot ID timestamp: {self.value!r}")

    @classmethod
    def parse(cls, value: str) -> SnapshotID:
        """Parse an ID and report malformed values as application validation errors."""
        return cls(value)

    @property
    def timestamp(self) -> datetime:
        """Return the timezone-naive timestamp encoded in this ID."""
        return datetime.strptime(self.value[:15], _TIMESTAMP_FORMAT)

    def __str__(self) -> str:
        return self.value
