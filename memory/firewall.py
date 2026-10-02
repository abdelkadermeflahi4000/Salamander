from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryRecord:
    value: Any

    trust_score: float
    source: str

    verified: bool = False


class MemoryFirewall:

    def __init__(
        self,
        minimum_trust: float = 0.60,
    ):
        self.minimum_trust = minimum_trust

    def validate(
        self,
        value: Any,
        trust_score: float,
        source: str,
    ) -> MemoryRecord:

        verified = trust_score >= self.minimum_trust

        return MemoryRecord(
            value=value,
            trust_score=trust_score,
            source=source,
            verified=verified,
        )

    def allow_write(
        self,
        record: MemoryRecord,
    ) -> bool:

        return record.verified
