from dataclasses import dataclass

from salamander.risk.engine import RiskEngine
from salamander.policy.engine import PolicyEngine
from salamander.trust.context import TrustContext
from salamander.trust.provenance import Provenance


@dataclass
class TrustDecision:
    decision: str
    risk: float
    reason: str
    provenance_id: str


class SalamanderRuntime:

    def __init__(
        self,
        detector,
        risk_engine=None,
        policy_engine=None,
    ):
        self.detector = detector
        self.risk_engine = risk_engine or RiskEngine()
        self.policy_engine = policy_engine or PolicyEngine()

    def inspect(
        self,
        content: str,
        context: TrustContext,
    ) -> TrustDecision:

        provenance = Provenance.create(
            content=content,
            source=context.source,
            origin=context.origin,
        )

        # Adapter layer:
        # This assumes your existing detector exposes scan().
        result = self.detector.scan(content)

        detection_score = getattr(
            result,
            "risk_score",
            getattr(result, "score", 0.0),
        )

        risk = self.risk_engine.calculate(
            detection_score=detection_score,
            context=context,
        )

        decision = self.policy_engine.decide(risk)

        return TrustDecision(
            decision=decision.value,
            risk=risk.final_risk,
            reason=risk.reason,
            provenance_id=provenance.content_id,
        )
