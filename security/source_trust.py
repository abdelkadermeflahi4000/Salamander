from dataclasses import dataclass
from enum import Enum


class TrustLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SYSTEM = "system"


@dataclass(frozen=True)
class Source:
    kind: str
    identifier: str | None = None
    authenticated: bool = False
    verified: bool = False


class SourceTrust:
    DEFAULTS = {
        "web": TrustLevel.LOW,
        "email": TrustLevel.LOW,
        "file": TrustLevel.LOW,
        "user": TrustLevel.HIGH,
        "database": TrustLevel.MEDIUM,
        "internal_api": TrustLevel.HIGH,
        "system": TrustLevel.SYSTEM,
        "unknown": TrustLevel.VERY_LOW,
    }

    def evaluate(self, source: Source) -> TrustLevel:
        if source.verified and source.authenticated:
            return TrustLevel.HIGH

        return self.DEFAULTS.get(
            source.kind,
            TrustLevel.VERY_LOW,
        )
