import json
from pathlib import Path

import pytest

from backintime.core.config import ConfigStore, Configuration
from backintime.core.exceptions import ConfigurationConflictError, ConfigurationError
from backintime.core.profile import Profile


def _profile(tmp_path: Path) -> Profile:
    return Profile(
        profile_id="home",
        name="Home",
        sources=(tmp_path / "source",),
        target=tmp_path / "backup",
        excludes=("*.cache",),
        extensions={"future_profile_option": True},
    )


def test_missing_config_loads_empty_configuration(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == Configuration()


def test_config_save_and_load_preserves_extensions(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    configuration = Configuration(
        profiles=(_profile(tmp_path),),
        extensions={"future_setting": {"enabled": True}},
    )

    store.save(configuration)

    assert store.load() == configuration


def test_config_update_rejects_a_stale_revision(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    initial_revision = store.load_with_revision()[1]
    store.update(initial_revision, lambda configuration: configuration)

    with pytest.raises(ConfigurationConflictError):
        store.update(initial_revision, lambda configuration: configuration)


def test_failed_atomic_config_write_preserves_existing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "config.json"
    store = ConfigStore(config_path)
    store.save(Configuration())
    original_content = config_path.read_bytes()

    def fail_replace(source: str | bytes, destination: str | bytes) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr("backintime.core.config.os.replace", fail_replace)

    with pytest.raises(ConfigurationError, match="simulated replace failure"):
        store.save(Configuration(profiles=(_profile(tmp_path),)))

    assert config_path.read_bytes() == original_content
    assert list(tmp_path.glob(".config.json.*.tmp")) == []


def test_invalid_config_is_not_replaced_with_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="not valid JSON"):
        ConfigStore(config_path).load()
    assert config_path.read_text(encoding="utf-8") == "{invalid"


def test_unsupported_config_version_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"version": 99}), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Unsupported configuration version"):
        ConfigStore(config_path).load()


def test_duplicate_profile_ids_are_rejected(tmp_path: Path) -> None:
    profile = _profile(tmp_path)
    store = ConfigStore(tmp_path / "config.json")

    with pytest.raises(ConfigurationError, match="Duplicate profile ID"):
        store.save(Configuration(profiles=(profile, profile)))


def test_default_path_uses_xdg_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert ConfigStore.default_path() == tmp_path / "backintime" / "config.json"
