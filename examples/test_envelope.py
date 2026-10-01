"""envelope + @wear: unsafe use must require an explicit choice."""
import pytest

from salamander import UnsafeContentError, wear
from tests._util import INJECTION_EN, INJECTION_STACKED, SAFE_EN


@wear(source="test")
def fetch_safe() -> str:
    return SAFE_EN


@wear(source="test")
def fetch_blocked() -> str:
    return INJECTION_STACKED


def test_safe_content_returns_text_for_safe_input() -> None:
    assert fetch_safe().safe_content() == SAFE_EN


def test_safe_content_raises_on_blocked_input() -> None:
    with pytest.raises(UnsafeContentError):
        fetch_blocked().safe_content()


def test_content_or_returns_default_when_blocked() -> None:
    assert fetch_blocked().content_or("[removed]") == "[removed]"


def test_content_or_returns_text_when_safe() -> None:
    assert fetch_safe().content_or("[removed]") == SAFE_EN


def test_summary_never_echoes_attacker_text() -> None:
    summary = fetch_blocked().summary()
    assert isinstance(summary, str)
    assert INJECTION_EN.lower() not in summary.lower()
    assert "evil.example" not in summary


def test_wrapped_function_keeps_arguments() -> None:
    @wear(source="test")
    def echo(x: str, *, suffix: str = "") -> str:
        return x + suffix

    assert echo("hello", suffix="!").safe_content() == "hello!"


def test_wear_does_not_return_plain_string() -> None:
    assert not isinstance(fetch_safe(), str)
