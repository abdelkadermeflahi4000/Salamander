from .types import Verdict, RiskScore


class Policy:

    def decide(self, risk: RiskScore) -> Verdict:

        if risk.value >= 0.80:
            return Verdict.BLOCK

        if risk.value >= 0.40:
            return Verdict.SUSPICIOUS

        return Verdict.SAFE
class Policy:

    def decide(
        self,
        risk: RiskScore,
        context: SecurityContext,
    ) -> Verdict:

        if context.action_risk >= 0.95 and risk.value >= 0.40:
            return Verdict.BLOCK

        if risk.value >= 0.80:
            return Verdict.BLOCK

        if risk.value >= 0.40:
            return Verdict.SUSPICIOUS

        return Verdict.SAFE
