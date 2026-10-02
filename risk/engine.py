from dataclasses import dataclass
from typing import Iterable

from salamander.trust.context import (
    ActionRisk,
    TrustContext,
)


@dataclass
class RiskDecision:
    content_risk: float
    context_risk: float
    action_risk: float
    final_risk: float

    reason: str


ACTION_WEIGHTS = {
    "none": 0.00,
    "read": 0.05,
    "search": 0.10,
    "write": 0.35,
    "write_file": 0.45,
    "database_write": 0.70,
    "execute": 0.80,
    "send_email": 0.85,
    "financial": 1.00,
}


TRUST_WEIGHTS = {
    "unknown": 0.50,
    "untrusted": 0.80,
    "low": 0.60,
    "medium": 0.30,
    "high": 0.10,
    "verified": 0.00,
}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


class RiskEngine:

    def calculate(
        self,
        detection_score: float,
        context: TrustContext,
    ) -> RiskDecision:

        content_risk = clamp(detection_score)

        context_risk = TRUST_WEIGHTS.get(
            context.trust_level.value,
            0.50,
        )

        action_risk = ACTION_WEIGHTS.get(
            context.action or "none",
            0.50,
        )

        # Content is the primary signal.
        # Context and action amplify the consequence.
        final = (
            content_risk * 0.55
            + context_risk * 0.20
            + action_risk * 0.25
        )

        final = clamp(final)

        if final >= 0.85:
            reason = "critical combined risk"
        elif final >= 0.65:
            reason = "high combined risk"
        elif final >= 0.40:
            reason = "medium combined risk"
        else:
            reason = "low combined risk"

        return RiskDecision(
            content_risk=content_risk,
            context_risk=context_risk,
            action_risk=action_risk,
            final_risk=final,
            reason=reason,
        )
