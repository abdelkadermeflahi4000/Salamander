#!/usr/bin/env python
"""Build leak-free train/test splits from public + local data.

Sources:
  --hf NAME       a Hugging Face dataset with 'text' and 'label' columns
                  (e.g. deepset/prompt-injections; verify its label meaning and license first)
  --local FILE    JSONL with {"text","label"[, "lang"]}
Steps: normalise -> dedupe (so no text is in both splits) -> stratified split by
(label, lang) with a fixed seed -> write data/training/train.jsonl and data/eval/test.jsonl.
Requires `pip install datasets` only when --hf is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

_CJK = re.compile(r"[\u4e00-\u9fff]")


def fingerprint(text: str) -> str:
    norm = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).lower()).strip()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()


def guess_lang(text: str) -> str:
    cjk = len(_CJK.findall(text))
    return "zh" if cjk and cjk / max(1, len(text)) > 0.2 else "latin"


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for r in rows:
        seen.setdefault(fingerprint(r["text"]), r)  # first occurrence wins
    return list(seen.values())


def split(rows: list[dict[str, Any]], test_frac: float, seed: int
          ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    buckets: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[(int(r["label"]), r.get("lang", "latin"))].append(r)
    train: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    for key in sorted(buckets):
        items = buckets[key]
        rng.shuffle(items)
        k = max(1, round(len(items) * test_frac)) if len(items) > 1 else 0
        test.extend(items[:k])
        train.extend(items[k:])
    return train, test


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_hf(name: str) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("pip install datasets") from exc
    rows = []
    for split_name, ds in load_dataset(name).items():
        for item in ds:
            rows.append({"text": item["text"], "label": int(item["label"]),
                         "source": f"hf:{name}:{split_name}"})
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hf", nargs="*", default=[])
    p.add_argument("--local", nargs="*", default=[])
    p.add_argument("--test-frac", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--out-dir", default="data")
    args = p.parse_args(argv)

    rows: list[dict[str, Any]] = []
    for name in args.hf:
        rows += load_hf(name)
    for path in args.local:
        for line in open(path, encoding="utf-8"):
            if line.strip():
                rows.append({**json.loads(line), "source": f"local:{path}"})
    for r in rows:
        r.setdefault("lang", guess_lang(r["text"]))
    before = len(rows)
    rows = dedupe(rows)
    train, test = split(rows, args.test_frac, args.seed)
    out = Path(args.out_dir)
    write_jsonl(out / "training" / "train.jsonl", train)
    write_jsonl(out / "eval" / "test.jsonl", test)
    print(f"{before} rows -> {len(rows)} after dedupe; train={len(train)} test={len(test)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
