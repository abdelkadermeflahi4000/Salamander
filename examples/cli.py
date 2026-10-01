"""Command line: `salamander scan FILE` / `salamander scan --url URL`.

Exit codes: 0 = passed, 1 = verdict reached --fail-on level, 2 = usage or I/O error.
The scanned text is never printed, only the verdict, score and categories.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from salamander.integrations.fetch import FetchError, fetch_text
from salamander.integrations.gate import default_scanner, summarize_result

LEVELS = {"safe": 0, "suspicious": 1, "block": 2}
FAIL_AT = {"suspicious": 1, "block": 2, "never": 99}
MAX_FILE_BYTES = 5_000_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="salamander", description="Prompt-injection scanner")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="scan a file, stdin ('-'), or a URL")
    scan.add_argument("file", nargs="?", help="path to a text file, or '-' for stdin")
    scan.add_argument("--url", help="fetch and scan a public http(s) URL")
    scan.add_argument("--json", action="store_true", help="machine-readable output")
    scan.add_argument("--fail-on", choices=list(FAIL_AT), default="block")
    scan.add_argument("--block-threshold", type=int)
    scan.add_argument("--suspicious-threshold", type=int)
    return parser


def _read_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.url:
        return fetch_text(args.url), args.url
    if args.file == "-":
        return sys.stdin.read(), "stdin"
    path = Path(args.file)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise OSError("file too large")
    return path.read_bytes().decode("utf-8", errors="replace"), str(path)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if bool(args.file) == bool(args.url):
        parser.error("provide exactly one of FILE or --url")

    try:
        text, source = _read_input(args)
    except (FetchError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    scanner = default_scanner(args.block_threshold, args.suspicious_threshold)
    verdict, score, categories = summarize_result(scanner.scan(text))

    if args.json:
        print(json.dumps({"source": source, "verdict": verdict, "score": score,
                          "categories": categories}, ensure_ascii=False))
    else:
        print(f"source:     {source}")
        print(f"verdict:    {verdict}")
        print(f"score:      {score}")
        print(f"categories: {', '.join(categories) or '-'}")

    return 1 if LEVELS[verdict] >= FAIL_AT[args.fail_on] else 0


if __name__ == "__main__":
    raise SystemExit(main())
