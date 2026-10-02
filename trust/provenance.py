from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import uuid


@dataclass
class Provenance:
    content_id: str
    source: str
    origin: str

    created_at: str

    parent_id: Optional[str] = None

    transformations: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    content_hash: Optional[str] = None

    @classmethod
    def create(
        cls,
        content: str,
        source: str,
        origin: str,
        parent_id: Optional[str] = None,
    ):
        digest = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        return cls(
            content_id=str(uuid.uuid4()),
            source=source,
            origin=origin,
            created_at=datetime.now(timezone.utc).isoformat(),
            parent_id=parent_id,
            content_hash=digest,
        )

    def add_transformation(self, name: str):
        self.transformations.append(name)
