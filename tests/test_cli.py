from pathlib import Path

import pytest

from backintime.cli.main import main


def test_version_option(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    assert "backintime 0.1.0" in capsys.readouterr().out


def test_check_config_accepts_missing_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    result = main(["--config", str(tmp_path / "missing.json"), "check-config"])

    assert result == 0
    assert "Configuration is valid (0 profiles)." in capsys.readouterr().out
