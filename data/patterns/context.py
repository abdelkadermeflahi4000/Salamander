from dataclasses import replace

from .types import RiskScore, SecurityContext


class ContextAnalyzer:

    def adjust_risk(
        self,
        risk: RiskScore,
        context: SecurityContext,
    ) -> RiskScore:

        value = risk.value
        reasons = list(risk.reasons)

        # Low-trust sources increase risk.
        if context.source_trust < 0.3:
            value += 0.10
            reasons.append("low_trust_source")

        # Dangerous actions increase risk.
        if context.action_risk >= 0.8:
            value += 0.20
            reasons.append("high_risk_action")

        return RiskScore(
            value=min(value, 1.0),
            reasons=tuple(reasons),
        )
