"""
The trust envelope — forces explicit handling of untrusted content.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from salamander.core.detector import SalamanderHybrid, ScanResult, Verdict
from salamander.envelope.exceptions import UnsafeContentError

T = TypeVar("T")


@dataclass(slots=True)
class Envelope:
    """
    Wrapper around untrusted content.
    The agent must explicitly choose how to handle it.
    """

    raw: str
    result: ScanResult
    source: str = "unknown"

    def safe_content(self) -> str:
        """
        Return the content only if it is not blocked.
        Raises UnsafeContentError otherwise.
        """
        if self.result.verdict == Verdict.BLOCK:
            raise UnsafeContentError(
                f"Content from '{self.source}' was blocked "
                f"(score={self.result.score}, findings={len(self.result.findings)})",
                result=self.result,
            )
        return self.raw

    def content_or(self, default: str = "") -> str:
        """Return content if safe/suspicious, otherwise return default."""
        if self.result.verdict == Verdict.BLOCK:
            return default
        return self.raw

    def summary(self) -> str:
        """Safe summary for end users (never returns raw attacker text)."""
        if self.result.verdict == Verdict.BLOCK:
            return f"[Content blocked — score {self.result.score}]"
        if self.result.verdict == Verdict.SUSPICIOUS:
            return f"[Content flagged as suspicious — score {self.result.score}]"
        return f"[Content safe — length {len(self.raw)}]"

    @property
    def is_blocked(self) -> bool:
        return self.result.verdict == Verdict.BLOCK

    @property
    def is_safe(self) -> bool:
        return self.result.verdict == Verdict.SAFE


def wear(
    source: str = "unknown",
    detector: SalamanderHybrid | None = None,
) -> Callable[[Callable[..., str]], Callable[..., Envelope]]:
    """
    Decorator that wraps a function returning str → returns Envelope.
    """
    _detector = detector or SalamanderHybrid()

    def decorator(func: Callable[..., str]) -> Callable[..., Envelope]:
        def wrapper(*args: Any, **kwargs: Any) -> Envelope:
            raw = func(*args, **kwargs)
            if not isinstance(raw, str):
                raise TypeError(f"@wear expects the wrapped function to return str, got {type(raw)}")
            result = _detector.scan(raw)
            return Envelope(raw=raw, result=result, source=source)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
