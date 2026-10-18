from pathlib import Path

import pytest

from backintime.core.exceptions import ValidationError
from backintime.core.profile import Profile


def test_profile_accepts_absolute_source_and_separate_target(tmp_path: Path) -> None:
    profile = Profile(
        profile_id="documents",
        name="Documents",
        sources=(tmp_path / "source",),
        target=tmp_path / "backup",
    )

    profile.validate()


def test_profile_rejects_relative_paths(tmp_path: Path) -> None:
    profile = Profile("documents", "Documents", (Path("relative"),), tmp_path / "backup")

    with pytest.raises(ValidationError, match="absolute path"):
        profile.validate()


def test_profile_rejects_null_characters_in_paths(tmp_path: Path) -> None:
    profile = Profile(
        "documents",
        "Documents",
        (Path(f"{tmp_path}\x00invalid"),),
        tmp_path / "backup",
    )

    with pytest.raises(ValidationError, match="invalid path"):
        profile.validate()


def test_profile_rejects_target_inside_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    profile = Profile("documents", "Documents", (source,), source / "backup")

    with pytest.raises(ValidationError, match="inside source"):
        profile.validate()


def test_profile_rejects_unsafe_identifier(tmp_path: Path) -> None:
    profile = Profile("../escape", "Documents", (tmp_path / "source",), tmp_path / "backup")

    with pytest.raises(ValidationError, match="Profile ID"):
        profile.validate()
