from enum import Enum

from salamander.risk.engine import RiskDecision


class Decision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


class PolicyEngine:

    def decide(self, risk: RiskDecision) -> Decision:

        if risk.final_risk >= 0.85:
            return Decision.BLOCK

        if risk.final_risk >= 0.55:
            return Decision.REVIEW

        return Decision.ALLOW
