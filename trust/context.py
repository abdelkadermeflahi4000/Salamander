from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class TrustLevel(str, Enum):
    UNKNOWN = "unknown"
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class ActionRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TrustContext:
    source: str = "unknown"
    origin: str = "unknown"

    agent_id: Optional[str] = None
    session_id: Optional[str] = None

    action: Optional[str] = None
    tool: Optional[str] = None

    trust_level: TrustLevel = TrustLevel.UNKNOWN
    action_risk: ActionRisk = ActionRisk.NONE

    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_untrusted(self) -> bool:
        return self.trust_level in {
            TrustLevel.UNKNOWN,
            TrustLevel.UNTRUSTED,
            TrustLevel.LOW,
        }
