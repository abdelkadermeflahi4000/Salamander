from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCK = "block"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Finding:
    category: str
    severity: Severity
    confidence: float
    source: str
    description: str
    matched_text: str | None = None


@dataclass(frozen=True)
class RiskScore:
    value: float
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class SecurityContext:
    source: str = "unknown"
    source_trust: float = 0.0
    session_id: str | None = None
    user_id: str | None = None
    tool_name: str | None = None
    action_risk: float = 0.0
    turn_index: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScanResult:
    verdict: Verdict
    risk: RiskScore
    findings: tuple[Finding, ...]
    normalized: str | None = None
