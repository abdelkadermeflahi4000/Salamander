#!/usr/bin/env python
"""Measure scanners on labelled data: precision / recall / F1 / FPR, overall and per language.

Data: JSONL, one object per line: {"text": str, "label": 0|1, "lang": "zh"|"latin"?, "kind": str?}
Usage:
  python scripts/evaluate.py --data data/eval/test.jsonl data/eval/zh_seed.jsonl
  python scripts/evaluate.py --data data/eval/test.jsonl \
      --scanners salamander salamander-deep llm-guard
Two operating points are reported: "block" (only block counts as detection) and
"flag" (suspicious or block). Never evaluate on data used for training.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def confusion_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == 0 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == 0 and p == 0)
    fn = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == 1 and p == 0)

    def div(a: float, b: float) -> float:
        return a / b if b else 0.0

    precision, recall = div(tp, tp + fp), div(tp, tp + fn)
    return {"n": len(y_true), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": precision, "recall": recall,
            "f1": div(2 * precision * recall, precision + recall),
            "fpr": div(fp, fp + tn), "accuracy": div(tp + tn, len(y_true))}


def _verdict(result: Any) -> str:
    v = result.get("verdict") if isinstance(result, dict) else getattr(result, "verdict", "block")
    return str(v)


def _base_scanner() -> Any:
    try:
        from salamander.core.detector import SalamanderHybrid

        return SalamanderHybrid()
    except Exception:
        from salamander import Salamander

        return Salamander()


def make_predictor(name: str) -> Callable[[str], str]:
    """Return text -> verdict ("safe" | "suspicious" | "block")."""
    if name == "salamander":
        scanner = _base_scanner()
        return lambda text: _verdict(scanner.scan(text))
    if name == "salamander-deep":
        from salamander.core.deep import DeepScanner

        scanner = DeepScanner(_base_scanner())
        return lambda text: _verdict(scanner.scan(text))
    if name == "llm-guard":
        try:
            from llm_guard.input_scanners import PromptInjection
        except ImportError as exc:  # optional, heavy dependency
            raise SystemExit("llm-guard not installed: pip install llm-guard") from exc
        guard = PromptInjection(threshold=0.5)

        def predict(text: str) -> str:
            _, is_valid, _ = guard.scan(text)
            return "safe" if is_valid else "block"

        return predict
    raise SystemExit(f"unknown scanner: {name}")


def evaluate(rows: list[dict[str, Any]], predictor: Callable[[str], str]) -> dict[str, Any]:
    verdicts = [predictor(r["text"]) for r in rows]
    labels = [int(r["label"]) for r in rows]
    out: dict[str, Any] = {}
    for point, positive in (("block", {"block"}), ("flag", {"suspicious", "block"})):
        preds = [1 if v in positive else 0 for v in verdicts]
        entry: dict[str, Any] = {"overall": confusion_metrics(labels, preds)}
        groups: dict[str, list[int]] = defaultdict(list)
        for i, r in enumerate(rows):
            groups[str(r.get("lang", "?"))].append(i)
        if len(groups) > 1:
            entry["by_lang"] = {g: confusion_metrics([labels[i] for i in idx],
                                                     [preds[i] for i in idx])
                                for g, idx in sorted(groups.items())}
        out[point] = entry
    return out


def _print(name: str, report: dict[str, Any]) -> None:
    print(f"\n== {name} ==")
    print(f"{'point':<8}{'group':<10}{'n':>5}{'prec':>8}{'recall':>8}{'F1':>8}{'FPR':>8}")
    for point, entry in report.items():
        rows = [("all", entry["overall"]), *entry.get("by_lang", {}).items()]
        for group, m in rows:
            print(f"{point:<8}{group:<10}{m['n']:>5}{m['precision']:>8.3f}{m['recall']:>8.3f}"
                  f"{m['f1']:>8.3f}{m['fpr']:>8.3f}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", nargs="+", required=True)
    parser.add_argument("--scanners", nargs="+", default=["salamander", "salamander-deep"])
    parser.add_argument("--json", help="write full report to this file")
    args = parser.parse_args(argv)

    rows = [r for path in args.data for r in load_jsonl(path)]
    if not rows:
        print("no data", file=sys.stderr)
        return 2
    print(f"{len(rows)} examples, {sum(int(r['label']) for r in rows)} injections")
    reports: dict[str, Any] = {}
    for name in args.scanners:
        reports[name] = evaluate(rows, make_predictor(name))
        _print(name, reports[name])
    if args.json:
        Path(args.json).write_text(json.dumps(reports, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
