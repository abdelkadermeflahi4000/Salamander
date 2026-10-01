from .types import Finding, RiskScore, Severity


SEVERITY_WEIGHT = {
    Severity.LOW: 0.15,
    Severity.MEDIUM: 0.35,
    Severity.HIGH: 0.70,
    Severity.CRITICAL: 1.00,
}


def calculate_risk(
    findings: tuple[Finding, ...],
) -> RiskScore:

    if not findings:
        return RiskScore(0.0)

    risk = 0.0
    reasons = []

    for finding in findings:
        weight = SEVERITY_WEIGHT[finding.severity]

        contribution = weight * finding.confidence

        risk = 1 - ((1 - risk) * (1 - contribution))

        reasons.append(finding.category)

    return RiskScore(
        value=min(risk, 1.0),
        reasons=tuple(reasons),
    )
