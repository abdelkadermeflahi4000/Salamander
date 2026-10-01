normalize
   ↓
patterns
   ↓
ML
   ↓
findings
from .normalize import normalize
from .patterns import PATTERNS
from .types import Finding


class Detector:

    def detect(self, text: str) -> tuple[Finding, ...]:
        normalized = normalize(text)
        findings: list[Finding] = []

        for pattern in PATTERNS:
            match = pattern.regex.search(normalized)

            if not match:
                continue

            findings.append(
                Finding(
                    category=pattern.category,
                    severity=pattern.severity,
                    confidence=pattern.confidence,
                    source="pattern",
                    description=pattern.name,
                    matched_text=match.group(0),
                )
            )

        return tuple(findings)
