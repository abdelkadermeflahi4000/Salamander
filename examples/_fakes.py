from typing import Any


class FakeScanner:
    """Deterministic scanner: returns a fixed verdict, optionally with match fragments."""

    def __init__(self, verdict: str = "safe", score: int = 0,
                 findings: list[dict[str, Any]] | None = None) -> None:
        self.verdict, self.score, self.findings = verdict, score, findings or []

    def scan(self, text: str) -> dict[str, Any]:
        return {"verdict": self.verdict, "score": self.score, "findings": self.findings}


class KeywordScanner:
    """Blocks when the word 'bad' appears; reports it as a removable match."""

    def scan(self, text: str) -> dict[str, Any]:
        if "bad" in text.lower():
            return {"verdict": "block", "score": 90,
                    "findings": [{"category": "instruction_override", "match": "bad"}]}
        return {"verdict": "safe", "score": 0, "findings": []}


class BrokenScanner:
    def scan(self, text: str) -> dict[str, Any]:
        raise RuntimeError("model file missing")
