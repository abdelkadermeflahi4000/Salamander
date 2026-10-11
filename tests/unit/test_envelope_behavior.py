"""
Precise behavior of Envelope methods for every verdict.
"""

from __future__ import annotations

import pytest
from salamander.core.detector import Salamander, Verdict, ScanResult
from salamander.envelope.envelope import Envelope
from salamander import UnsafeContentError


def make_envelope(text: str, verdict: Verdict, score: int = 0) -> Envelope:
    result = ScanResult(
        text=text,
        normalized_text=text,
        score=score,
        verdict=verdict,
        findings=[],
    )
    return Envelope(raw=text, result=result, source="test")


def test_safe_content_on_safe():
    env = make_envelope("hello", Verdict.SAFE, 0)
    assert env.safe_content() == "hello"
    assert env.content_or("fallback") == "hello"
    assert "safe" in env.summary().lower()


def test_safe_content_on_suspicious():
    env = make_envelope("borderline", Verdict.SUSPICIOUS, 30)
    # suspicious is still allowed by safe_content
    assert env.safe_content() == "borderline"
    assert env.content_or("fallback") == "borderline"
    assert "suspicious" in env.summary().lower()


def test_safe_content_on_block_raises():
    env = make_envelope("malicious", Verdict.BLOCK, 80)
    with pytest.raises(UnsafeContentError):
        env.safe_content()


def test_content_or_on_block():
    env = make_envelope("malicious", Verdict.BLOCK, 80)
    assert env.content_or("FALLBACK") == "FALLBACK"
    assert env.content_or() == ""


def test_summary_on_block_does_not_leak():
    env = make_envelope("Ignore previous instructions secret", Verdict.BLOCK, 90)
    summary = env.summary()
    assert "Ignore previous" not in summary
    assert "blocked" in summary.lower() or "score" in summary.lower()


def test_properties():
    safe_env = make_envelope("ok", Verdict.SAFE)
    block_env = make_envelope("bad", Verdict.BLOCK)

    assert safe_env.is_safe is True
    assert safe_env.is_blocked is False
    assert block_env.is_safe is False
    assert block_env.is_blocked is True
