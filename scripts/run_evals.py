#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from route_tasks import load_config, route_task  # noqa: E402


TRIGGER_TERMS = [
    "superpowers",
    "codex",
    "subagent",
    "custom agent",
    "spawn_agent",
    "spc_",
    "model tier",
    "routing",
    "route",
    "fallback",
    "review policy",
    "reviewer roles",
    "spec-review",
    "quality-review",
    "reasoning effort",
    "sandbox",
    "final verifier",
    "子代理",
    "派发",
    "路由",
    "模型层级",
    "回退",
    "审查策略",
]


def load_suite(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{path}: top-level JSON must be an object")
    if payload.get("suite") not in {"routes", "queries"}:
        raise SystemExit(f"{path}: suite must be routes or queries")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit(f"{path}: cases must be a non-empty list")
    return payload


def require(case: Dict[str, Any], key: str) -> Any:
    if key not in case:
        raise SystemExit(f"{case.get('id', '<missing id>')}: missing required field {key}")
    return case[key]


def should_use_skill(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in TRIGGER_TERMS)


def compare_expected(case_id: str, expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    for field, expected_value in expected.items():
        actual_value = actual.get(field)
        if field == "hard_flags":
            actual_value = sorted(actual_value or [])
            expected_value = sorted(expected_value or [])
        if actual_value != expected_value:
            failures.append(
                f"{case_id}: {field} expected={expected_value!r} actual={actual_value!r}"
            )
    return failures


def run_routes(cases: List[Dict[str, Any]], config_path: str | None) -> List[str]:
    cfg = load_config(config_path)
    failures: List[str] = []
    for case in cases:
        case_id = require(case, "id")
        text = require(case, "text")
        role = case.get("role", "auto")
        route = route_task(text, role, case.get("files"), cfg, task_id=case_id)
        actual = asdict(route)
        failures.extend(compare_expected(case_id, require(case, "expect"), actual))
    return failures


def run_queries(cases: List[Dict[str, Any]]) -> List[str]:
    failures: List[str] = []
    for case in cases:
        case_id = require(case, "id")
        text = require(case, "text")
        expected = require(case, "expected_use_skill")
        actual = should_use_skill(text)
        if actual != expected:
            failures.append(
                f"{case_id}: expected_use_skill expected={expected!r} actual={actual!r}"
            )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run sp-codex-select eval suites.")
    parser.add_argument("--suite", required=True, help="Path to eval JSON suite.")
    parser.add_argument("--config", help="Optional route_tasks JSON config override.")
    args = parser.parse_args(argv)

    suite_path = Path(args.suite)
    payload = load_suite(suite_path)
    cases = payload["cases"]
    failures = run_routes(cases, args.config) if payload["suite"] == "routes" else run_queries(cases)

    passed = len(cases) - len({failure.split(":", 1)[0] for failure in failures})
    print(f"suite={suite_path} cases={len(cases)} passed={passed} failed={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
