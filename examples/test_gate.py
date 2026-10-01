import json

import pytest

from salamander.integrations.gate import SUSPICIOUS_NOTE, scan_and_gate
from tests._fakes import BrokenScanner, FakeScanner, KeywordScanner

SECRET = "ATTACKER PAYLOAD"


def test_safe_content_passes_through() -> None:
    out = scan_and_gate("hello", scanner=FakeScanner("safe"))
    assert out["allowed"] and out["content"] == "hello"


def test_block_withholds_content() -> None:
    out = scan_and_gate(SECRET, scanner=FakeScanner("block", 90))
    assert not out["allowed"] and out["content"] is None
    assert SECRET not in json.dumps(out)


def test_suspicious_released_with_warning_by_default() -> None:
    out = scan_and_gate("hmm", scanner=FakeScanner("suspicious", 30))
    assert out["allowed"] and out["content"].startswith(SUSPICIOUS_NOTE)


def test_suspicious_withheld_when_strict() -> None:
    out = scan_and_gate("hmm", scanner=FakeScanner("suspicious", 30), allow_suspicious=False)
    assert not out["allowed"] and out["content"] is None


def test_scanner_error_fails_closed() -> None:
    out = scan_and_gate("anything", scanner=BrokenScanner())
    assert not out["allowed"] and out["content"] is None


def test_unknown_verdict_fails_closed() -> None:
    out = scan_and_gate("x", scanner=FakeScanner("weird"))
    assert not out["allowed"]


def test_oversize_input_is_refused() -> None:
    out = scan_and_gate("a" * 11, scanner=FakeScanner("safe"), max_chars=10)
    assert not out["allowed"]


def test_non_string_input_is_refused() -> None:
    assert not scan_and_gate(123, scanner=FakeScanner("safe"))["allowed"]  # type: ignore[arg-type]


def test_invalid_mode_raises() -> None:
    with pytest.raises(ValueError):
        scan_and_gate("x", mode="nope", scanner=FakeScanner())


def test_sanitize_removes_fragment_and_rescans_safe() -> None:
    out = scan_and_gate("hello BAD world", mode="sanitize", scanner=KeywordScanner())
    assert out["allowed"] and out["sanitized"]
    assert out["content"] == "hello [REMOVED] world"


def test_sanitize_refuses_when_nothing_removable() -> None:
    scanner = FakeScanner("block", 90, findings=[{"category": "x"}])
    out = scan_and_gate("whatever", mode="sanitize", scanner=scanner)
    assert not out["allowed"] and out["content"] is None


def test_categories_reported_without_matched_text() -> None:
    out = scan_and_gate("bad", scanner=KeywordScanner())
    assert out["categories"] == ["instruction_override"]
    assert "bad" not in json.dumps({k: v for k, v in out.items() if k != "reason"})
