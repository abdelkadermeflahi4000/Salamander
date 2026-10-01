import json
from pathlib import Path

import pytest

from salamander import cli
from tests._fakes import FakeScanner


def _use(monkeypatch: pytest.MonkeyPatch, verdict: str, score: int = 0) -> None:
    monkeypatch.setattr(cli, "default_scanner", lambda *a, **k: FakeScanner(verdict, score))


def _file(tmp_path: Path, text: str = "some text") -> str:
    path = tmp_path / "sample.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_safe_file_exits_zero(tmp_path, monkeypatch, capsys) -> None:
    _use(monkeypatch, "safe")
    assert cli.main(["scan", _file(tmp_path)]) == 0
    assert "verdict:    safe" in capsys.readouterr().out


def test_block_exits_one(tmp_path, monkeypatch) -> None:
    _use(monkeypatch, "block", 90)
    assert cli.main(["scan", _file(tmp_path)]) == 1


def test_suspicious_passes_by_default_but_fails_in_strict(tmp_path, monkeypatch) -> None:
    _use(monkeypatch, "suspicious", 30)
    assert cli.main(["scan", _file(tmp_path)]) == 0
    assert cli.main(["scan", _file(tmp_path), "--fail-on", "suspicious"]) == 1


def test_fail_on_never(tmp_path, monkeypatch) -> None:
    _use(monkeypatch, "block", 90)
    assert cli.main(["scan", _file(tmp_path), "--fail-on", "never"]) == 0


def test_json_output_and_no_content_echo(tmp_path, monkeypatch, capsys) -> None:
    _use(monkeypatch, "block", 90)
    cli.main(["scan", _file(tmp_path, "ATTACKER PAYLOAD"), "--json"])
    out = capsys.readouterr().out
    assert json.loads(out)["verdict"] == "block"
    assert "ATTACKER PAYLOAD" not in out


def test_missing_file_exits_two(tmp_path, monkeypatch) -> None:
    _use(monkeypatch, "safe")
    assert cli.main(["scan", str(tmp_path / "nope.txt")]) == 2


def test_requires_exactly_one_source(tmp_path, monkeypatch) -> None:
    _use(monkeypatch, "safe")
    with pytest.raises(SystemExit) as exc:
        cli.main(["scan"])
    assert exc.value.code == 2
    with pytest.raises(SystemExit):
        cli.main(["scan", _file(tmp_path), "--url", "http://example.com"])


def test_url_to_private_address_exits_two(monkeypatch) -> None:
    _use(monkeypatch, "safe")
    assert cli.main(["scan", "--url", "http://127.0.0.1/"]) == 2
