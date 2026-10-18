"""Filesystem path validation helpers."""

from pathlib import Path

from backintime.core.exceptions import ValidationError


def validate_path_within(path: Path, root: Path, *, allow_root: bool = False) -> Path:
    """Resolve a path and ensure it remains within the resolved boundary."""
    if "\x00" in str(path) or "\x00" in str(root):
        raise ValidationError("Paths must not contain a null character.")
    try:
        candidate = path.expanduser().resolve(strict=False)
        boundary = root.expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValidationError(f"Cannot resolve path safely: {exc}") from exc

    try:
        relative = candidate.relative_to(boundary)
    except ValueError as exc:
        raise ValidationError(
            f"Path '{candidate}' is outside allowed directory '{boundary}'."
        ) from exc

    if not allow_root and not relative.parts:
        raise ValidationError(f"Path '{candidate}' must be inside, not equal to, '{boundary}'.")
    return candidate
