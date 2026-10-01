"""DeepScanner: runs any base scanner over every evasion-resistant view.

Same interface as the base scanner (`.scan(text)` -> dict with verdict/score/findings),
so it plugs into the gate, MCP tools and CLI unchanged.
score = min(100, best view score + min(60, sum of structural signal weights))
"""
from __future__ import annotations

from typing import Any

from salamander.core.views import SIGNAL_WEIGHTS, Signal, expand

SIGNAL_CAP = 60
_VERDICT_SCORE = {"block": 100, "suspicious": 30, "safe": 0}


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return obj.get(name, default) if isinstance(obj, dict) else getattr(obj, name, default)


def _score(result: Any) -> int:
    value = _get(result, "score", None)
    if value is None:
        return _VERDICT_SCORE.get(str(_get(result, "verdict", "block")), 100)
    return int(value)


class DeepScanner:
    def __init__(self, base: Any, *, block_threshold: int | None = None,
                 suspicious_threshold: int | None = None) -> None:
        self.base = base
        self.block_threshold = (block_threshold if block_threshold is not None
                                else getattr(base, "block_threshold", 45))
        self.suspicious_threshold = (suspicious_threshold if suspicious_threshold is not None
                                     else getattr(base, "suspicious_threshold", 25))

    def scan(self, text: str) -> dict[str, Any]:
        expansion = expand(text)
        signals: list[Signal] = list(expansion.signals)
        scored: list[tuple[str, int, list[Any]]] = []
        for view in expansion.views:
            result = self.base.scan(view.text)
            scored.append((view.name, _score(result), list(_get(result, "findings", None) or [])))

        best_name, best_score, _ = max(scored, key=lambda item: item[1])
        direct = max((s for n, s, _ in scored if n in ("raw", "clean")), default=0)
        if (best_name.startswith("decoded:") and best_score >= self.suspicious_threshold
                and direct < self.suspicious_threshold):
            signals.append(Signal("encoding_evasion", SIGNAL_WEIGHTS["encoded_payload"],
                                  f"payload only visible after {best_name}"))

        signal_total = min(SIGNAL_CAP, sum(s.weight for s in signals))
        score = min(100, best_score + signal_total)
        verdict = ("block" if score >= self.block_threshold
                   else "suspicious" if score >= self.suspicious_threshold else "safe")

        findings: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        for name, view_score, view_findings in scored:
            if view_score <= 0:
                continue
            for f in view_findings:
                match = _get(f, "match") or _get(f, "matched") or _get(f, "text")
                key = (_get(f, "category"), match, name)
                if key in seen:
                    continue
                seen.add(key)
                findings.append({"category": _get(f, "category", "unknown"),
                                 "weight": _get(f, "weight", 0), "match": match, "view": name})
        for s in signals:
            findings.append({"category": s.category, "weight": s.weight, "match": None,
                             "view": "structure", "note": s.note})
        return {"verdict": verdict, "score": score, "findings": findings,
                "views": [v.name for v in expansion.views]}
