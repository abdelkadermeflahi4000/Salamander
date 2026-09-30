"""
Core detection engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

from salamander.core.normalize import normalize
from salamander.core.patterns import ALL_PATTERNS, Pattern


class Verdict(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCK = "block"


@dataclass(frozen=True, slots=True)
class Finding:
    pattern_id: str
    category: str
    weight: int
    matched_text: str
    language: str


@dataclass(slots=True)
class ScanResult:
    text: str
    normalized_text: str
    score: int
    verdict: Verdict
    findings: list[Finding] = field(default_factory=list)

    @property
    def is_blocked(self) -> bool:
        return self.verdict == Verdict.BLOCK

    @property
    def is_safe(self) -> bool:
        return self.verdict == Verdict.SAFE


class Salamander:
    """Pattern-only detector."""

    def __init__(
        self,
        block_threshold: int = 45,
        suspicious_threshold: int = 25,
        patterns: list[Pattern] | None = None,
    ) -> None:
        self.block_threshold = block_threshold
        self.suspicious_threshold = suspicious_threshold
        self.patterns = patterns or ALL_PATTERNS

    def scan(self, text: str) -> ScanResult:
        if not text or not text.strip():
            return ScanResult(
                text=text,
                normalized_text=text,
                score=0,
                verdict=Verdict.SAFE,
            )

        normalized = normalize(text)
        findings: list[Finding] = []

        for p in self.patterns:
            for match in p.pattern.finditer(normalized):
                findings.append(
                    Finding(
                        pattern_id=p.id,
                        category=p.category,
                        weight=p.weight,
                        matched_text=match.group(0),
                        language=p.language,
                    )
                )

        # Sum weights (cap at 100)
        score = min(100, sum(f.weight for f in findings))

        if score >= self.block_threshold:
            verdict = Verdict.BLOCK
        elif score >= self.suspicious_threshold:
            verdict = Verdict.SUSPICIOUS
        else:
            verdict = Verdict.SAFE

        return ScanResult(
            text=text,
            normalized_text=normalized,
            score=score,
            verdict=verdict,
            findings=findings,
        )


class SalamanderHybrid(Salamander):
    """
    Pattern + ML hybrid.
    ML is treated as an additional weighted finding (weight 35)
    only when probability >= 0.6.
    """

    def __init__(
        self,
        block_threshold: int = 45,
        suspicious_threshold: int = 25,
        ml_weight: int = 35,
        ml_prob_threshold: float = 0.6,
        **kwargs,
    ) -> None:
        super().__init__(block_threshold=block_threshold, suspicious_threshold=suspicious_threshold, **kwargs)
        self.ml_weight = ml_weight
        self.ml_prob_threshold = ml_prob_threshold
        self._ml_classifier = None  # lazy load

    def _get_ml(self):
        if self._ml_classifier is None:
            try:
                from salamander.ml.classifier import MLClassifier
                self._ml_classifier = MLClassifier()
            except Exception:
                # Graceful degradation if ML is unavailable
                self._ml_classifier = False
        return self._ml_classifier

    def scan(self, text: str) -> ScanResult:
        result = super().scan(text)

        ml = self._get_ml()
        if ml and ml is not False:
            prob = ml.predict_proba(result.normalized_text)
            if prob >= self.ml_prob_threshold:
                # Add ML as an extra finding
                result.findings.append(
                    Finding(
                        pattern_id="ml_statistical_signal",
                        category="ml_signal",
                        weight=self.ml_weight,
                        matched_text=f"ml_prob={prob:.3f}",
                        language="xx",
                    )
                )
                # Recalculate score
                new_score = min(100, sum(f.weight for f in result.findings))
                if new_score >= self.block_threshold:
                    new_verdict = Verdict.BLOCK
                elif new_score >= self.suspicious_threshold:
                    new_verdict = Verdict.SUSPICIOUS
                else:
                    new_verdict = Verdict.SAFE

                # Create updated result (because frozen dataclass would be better,
                # but we keep it simple here)
                result = ScanResult(
                    text=result.text,
                    normalized_text=result.normalized_text,
                    score=new_score,
                    verdict=new_verdict,
                    findings=result.findings,
                )

        return result
