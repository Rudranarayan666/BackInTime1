import json
from pathlib import Path

import pytest

from backintime.core.exceptions import ValidationError
from backintime.core.repository import Repository
from backintime.core.snapshot_id import SnapshotID
from backintime.core.validation import validate_path_within


def _write_snapshot(root: Path, snapshot_id: str, *, state: str = "complete") -> Path:
    snapshot_path = root / snapshot_id
    snapshot_path.mkdir(parents=True)
    (snapshot_path / "info.json").write_text(
        json.dumps({"snapshot_id": snapshot_id, "state": state}),
        encoding="utf-8",
    )
    return snapshot_path


def test_repository_lists_only_healthy_snapshots_by_default(tmp_path: Path) -> None:
    _write_snapshot(tmp_path, "20240101-000000-001")
    _write_snapshot(tmp_path, "20240102-000000-001", state="failed")
    (tmp_path / "20240103-000000-001").mkdir()
    (tmp_path / "not-a-snapshot").mkdir()

    records = Repository(tmp_path).list_snapshots()

    assert [str(record.snapshot_id) for record in records] == ["20240101-000000-001"]
    assert records[0].healthy


def test_repository_can_include_incomplete_snapshots(tmp_path: Path) -> None:
    incomplete_id = "20240102-000000-001"
    _write_snapshot(tmp_path, incomplete_id, state="failed")
    (tmp_path / "20240103-000000-001").mkdir()

    records = Repository(tmp_path).list_snapshots(include_incomplete=True)

    assert [str(record.snapshot_id) for record in records] == [
        "20240103-000000-001",
        incomplete_id,
    ]
    assert all(not record.healthy for record in records)


def test_repository_ignores_symlinked_snapshot_directories(tmp_path: Path) -> None:
    target = tmp_path / "outside"
    target.mkdir()
    _write_snapshot(target, "20240101-000000-001")
    link = tmp_path / "20240102-000000-001"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Directory symlinks unavailable: {exc}")

    assert Repository(tmp_path).list_snapshots(include_incomplete=True) == []


def test_snapshot_path_uses_only_validated_identifier(tmp_path: Path) -> None:
    repository = Repository(tmp_path)

    assert repository.snapshot_path(SnapshotID("20240101-000000-001")) == (
        tmp_path / "20240101-000000-001"
    )


def test_validate_path_within_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "root"

    with pytest.raises(ValidationError, match="outside allowed directory"):
        validate_path_within(tmp_path / "outside", root)


def test_validate_path_within_allows_nested_path(tmp_path: Path) -> None:
    root = tmp_path / "root"
    nested = root / "nested"

    assert validate_path_within(nested, root) == nested


def test_validate_path_within_rejects_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    link = root / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Directory symlinks unavailable: {exc}")

    with pytest.raises(ValidationError, match="outside allowed directory"):
        validate_path_within(link / "file", root)
