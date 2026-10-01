if score > 50:
    block
return Verdict.BLOCK
import re
from dataclasses import dataclass

from .types import Severity


@dataclass(frozen=True)
class Pattern:
    name: str
    category: str
    regex: re.Pattern[str]
    severity: Severity
    confidence: float


PATTERNS = (
    Pattern(
        name="instruction_override",
        category="instruction_override",
        regex=re.compile(
            r"\bignore\s+(?:all\s+)?previous\s+instructions\b",
            re.I,
        ),
        severity=Severity.HIGH,
        confidence=0.95,
    ),

    Pattern(
        name="system_prompt_exfiltration",
        category="system_prompt_exfiltration",
        regex=re.compile(
            r"\breveal\s+(?:your\s+)?system\s+prompt\b",
            re.I,
        ),
        severity=Severity.HIGH,
        confidence=0.95,
    ),
)
