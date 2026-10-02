from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TrustEdge:
    source: str
    target: str
    trust: float


class TrustGraph:

    def __init__(self):
        self.edges: Dict[tuple[str, str], TrustEdge] = {}

    def add_edge(
        self,
        source: str,
        target: str,
        trust: float,
    ):
        trust = max(0.0, min(1.0, trust))

        self.edges[(source, target)] = TrustEdge(
            source=source,
            target=target,
            trust=trust,
        )

    def get_trust(
        self,
        source: str,
        target: str,
    ) -> float:

        edge = self.edges.get((source, target))

        if edge is None:
            return 0.0

        return edge.trust
