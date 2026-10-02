import json
import time
from pathlib import Path


class AuditLogger:

    def __init__(self, path="salamander_audit.jsonl"):
        self.path = Path(path)

    def log(self, event: dict):

        event = {
            "timestamp": time.time(),
            **event,
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(
                    event,
                    ensure_ascii=False,
                )
                + "\n"
            )
