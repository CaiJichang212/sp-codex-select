#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_FIELDS = [
    "task_id",
    "role",
    "tier",
    "agent",
    "model",
    "score",
    "status",
    "review_pass",
    "tests_pass",
    "escalated",
]


def load_records(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        for field in REQUIRED_FIELDS:
            if field not in record:
                raise SystemExit(f"{path}:{line_no}: missing required field {field}")
        records.append(record)
    if not records:
        raise SystemExit(f"{path}: no route records found")
    return records


def rate(count: int, total: int) -> str:
    return f"{count / total:.2f}" if total else "0.00"


def summarize(records: List[Dict[str, Any]]) -> str:
    total = len(records)
    tier_counts = Counter(str(record["tier"]) for record in records)
    review_failures = sum(1 for record in records if record.get("review_pass") is False)
    test_failures = sum(1 for record in records if record.get("tests_pass") is False)
    escalations = sum(1 for record in records if record.get("escalated") is True)
    false_cheap = [
        str(record["task_id"])
        for record in records
        if str(record.get("tier")) in {"T1", "T2"} and (record.get("review_pass") is False or record.get("escalated") is True)
    ]
    lines = [
        f"route_count={total}",
        "tier_counts=" + ",".join(f"{tier}:{count}" for tier, count in sorted(tier_counts.items())),
        f"review_failure_rate={rate(review_failures, total)}",
        f"test_failure_rate={rate(test_failures, total)}",
        f"escalation_rate={rate(escalations, total)}",
        "false_cheap_candidates=" + (",".join(false_cheap) if false_cheap else "none"),
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze sp-codex-select route JSONL records.")
    parser.add_argument("jsonl", help="Path to route JSONL log.")
    args = parser.parse_args(argv)
    records = load_records(Path(args.jsonl))
    print(summarize(records))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            raise SystemExit(1)
        raise
