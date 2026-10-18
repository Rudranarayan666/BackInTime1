from datetime import datetime

import pytest

from backintime.core.exceptions import ValidationError
from backintime.core.snapshot_id import SnapshotID


@pytest.mark.parametrize(
    "value",
    [
        "20240229-235959-007",
        "20000101-000000-000",
    ],
)
def test_snapshot_id_accepts_valid_identifiers(value: str) -> None:
    assert str(SnapshotID.parse(value)) == value


@pytest.mark.parametrize(
    "value",
    [
        "20230229-120000-001",
        "20240101-240000-001",
        "20240101-120000-01",
        "20240101-120000-001-extra",
        "../20240101-120000-001",
    ],
)
def test_snapshot_id_rejects_invalid_identifiers(value: str) -> None:
    with pytest.raises(ValidationError):
        SnapshotID.parse(value)


def test_snapshot_ids_sort_chronologically() -> None:
    identifiers = [
        SnapshotID("20240102-000000-000"),
        SnapshotID("20231231-235959-999"),
        SnapshotID("20240102-000000-001"),
    ]

    assert [str(value) for value in sorted(identifiers)] == [
        "20231231-235959-999",
        "20240102-000000-000",
        "20240102-000000-001",
    ]
    assert SnapshotID("20240102-030405-006").timestamp == datetime(2024, 1, 2, 3, 4, 5)
