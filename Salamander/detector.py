"""
Salamander: a lightweight, dependency-free prompt-injection detector
for English and Chinese text, meant to sit in front of an AI agent as
a first line of defense before a tool call, retrieved document, or
user message reaches the model.

This is a pattern + heuristic layer (fast, explainable, zero external
calls). It is deliberately NOT a silver bullet — pair it with model-
based classification for higher recall on novel attacks.
"""

from dataclasses import dataclass, field

from .normalize import normalize
from .patterns import ALL_PATTERNS


@dataclass
class Finding:
    category: str
    weight: int
    matched_text: str


@dataclass
class ScanResult:
    text: str
    score: int
    verdict: str  # "safe" | "suspicious" | "block"
    findings: list[Finding] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Truthy when the text is flagged (suspicious or block)."""
        return self.verdict != "safe"

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "verdict": self.verdict,
            "findings": [
                {"category": f.category, "weight": f.weight, "matched_text": f.matched_text}
                for f in self.findings
            ],
        }


class Salamander:
    """Scans text for prompt-injection attempts targeting AI agents.

    Usage:
        guard = Salamander()
        result = guard.scan(incoming_text)
        if result.verdict == "block":
            raise ValueError("blocked: possible prompt injection")
    """

    def __init__(self, suspicious_threshold: int = 25, block_threshold: int = 45):
        self.suspicious_threshold = suspicious_threshold
        self.block_threshold = block_threshold
        self.patterns = ALL_PATTERNS

    def scan(self, text: str) -> ScanResult:
        if not text:
            return ScanResult(text=text or "", score=0, verdict="safe")

        normalized = normalize(text)
        findings: list[Finding] = []
        score = 0

        for regex, category, weight in self.patterns:
            match = regex.search(normalized)
            if match:
                findings.append(Finding(category=category, weight=weight, matched_text=match.group(0)))
                score += weight

        score = min(score, 100)

        if score >= self.block_threshold:
            verdict = "block"
        elif score >= self.suspicious_threshold:
            verdict = "suspicious"
        else:
            verdict = "safe"

        return ScanResult(text=text, score=score, verdict=verdict, findings=findings)

    def is_safe(self, text: str) -> bool:
        return self.scan(text).verdict == "safe"


class SalamanderHybrid(Salamander):
    """Salamander + a statistical (ML) second pass.

    The regex layer stays authoritative for explainability (you can show
    a user/auditor exactly which pattern fired). The ML layer adds recall
    on paraphrased attacks the regex layer misses, contributing to the
    score but never on its own to the explanation list unless it fires
    strongly.

    NOTE: the bundled model is trained on a small (~90 example) starter
    dataset — see salamander/training_data.py. Treat its signal as
    advisory, not authoritative, until retrained on more data.
    """

    def __init__(
        self,
        suspicious_threshold: int = 25,
        block_threshold: int = 45,
        ml_weight: int = 35,
        ml_trigger_proba: float = 0.6,
    ):
        super().__init__(suspicious_threshold, block_threshold)
        from .ml_classifier import MLClassifier
        self._ml = MLClassifier()
        self.ml_weight = ml_weight
        self.ml_trigger_proba = ml_trigger_proba

    def scan(self, text: str) -> ScanResult:
        result = super().scan(text)
        if not text:
            return result

        proba = self._ml.predict_proba(text)
        if proba >= self.ml_trigger_proba:
            result.findings.append(
                Finding(category="ml_statistical_signal",
                        weight=self.ml_weight,
                        matched_text=f"p={proba:.2f}")
            )
            result.score = min(result.score + self.ml_weight, 100)
            if result.score >= self.block_threshold:
                result.verdict = "block"
            elif result.score >= self.suspicious_threshold:
                result.verdict = "suspicious"

        return result
