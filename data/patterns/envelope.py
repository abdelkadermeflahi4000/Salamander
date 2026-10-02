"""
Salamander (焰甲) — the universal envelope.

This is the "coat" layer: a framework-agnostic wrapper that any agent
(Claude, GPT, a LangChain agent, a raw API call — anything) can put on
before it touches content from the "furnace": the untrusted outside
world (web pages, emails, files, tool results, other agents' output).

Design principle: the agent NEVER receives raw untrusted text directly.
It always receives an Envelope, which forces an explicit decision:
  - .content        -> the raw text (available, but reading it directly
                        is the agent's own choice, not the default path)
  - .safe_content()  -> the text ONLY if verdict == "safe", else raises
  - .content_or(default) -> the text if safe, else a fallback value
  - .summary()       -> a description of the risk, safe to show a user

This does not require every user of the library to know about
Salamander/SalamanderHybrid internals — they just call `wear(guard)` around
whatever function fetches untrusted content, and get an Envelope back.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Callable, TypeVar

from .detector import Salamander, ScanResult

T = TypeVar("T")


class UnsafeContentError(Exception):
    """Raised when code tries to use blocked content without acknowledging the risk."""


@dataclass
class Envelope:
    content: str
    result: ScanResult
    source: str = "unknown"

    @property
    def verdict(self) -> str:
        return self.result.verdict

    @property
    def score(self) -> int:
        return self.result.score

    def safe_content(self) -> str:
        """Return the content, but only if it passed the scan clean."""
        if self.result.verdict == "block":
            raise UnsafeContentError(
                f"Blocked content from '{self.source}' (score={self.score}): "
                f"{[f.category for f in self.result.findings]}"
            )
        return self.content

    def content_or(self, default: str) -> str:
        """Return the content if safe/suspicious, or `default` if blocked."""
        if self.result.verdict == "block":
            return default
        return self.content

    def summary(self) -> str:
        if self.result.verdict == "safe":
            return "No known injection pattern detected."
        cats = ", ".join(sorted({f.category for f in self.result.findings}))
        return f"{self.result.verdict} (score={self.score}) — flags: {cats}"


def wear(guard: Salamander | None = None, source: str = "unknown"):
    """Decorator: wrap any function that returns untrusted text so its
    result always arrives as an Envelope instead of raw text.

    Works with ANY agent framework because it only touches plain
    functions and strings — no dependency on a specific agent SDK.

    Example:
        @wear(source="web_fetch")
        def fetch_page(url: str) -> str:
            return requests.get(url).text

        envelope = fetch_page("https://example.com")
        text = envelope.safe_content()   # raises if the page tried to
                                          # inject instructions
    """
    _guard = guard or Salamander()

    def decorator(fn: Callable[..., str]) -> Callable[..., Envelope]:
        @functools.wraps(fn)
        def wrapped(*args, **kwargs) -> Envelope:
            raw = fn(*args, **kwargs)
            result = _guard.scan(raw)
            return Envelope(content=raw, result=result, source=source)
        return wrapped

    return decorator
