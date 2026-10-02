from dataclasses import dataclass, field
from typing import Set


@dataclass
class AgentIdentity:

    agent_id: str

    trust_score: float = 0.5

    capabilities: Set[str] = field(
        default_factory=set
    )

    def can(self, capability: str) -> bool:
        return capability in self.capabilities
