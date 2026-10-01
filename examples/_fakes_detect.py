from typing import Any

PHRASE = "ignore all previous instructions"


class PhraseScanner:
    """English-only stand-in for the real detector: scores 50 on one known phrase."""

    block_threshold = 45
    suspicious_threshold = 25

    def scan(self, text: str) -> dict[str, Any]:
        if PHRASE in text.lower():
            return {"verdict": "block", "score": 50,
                    "findings": [{"category": "instruction_override", "weight": 50,
                                  "match": PHRASE}]}
        return {"verdict": "safe", "score": 0, "findings": []}
