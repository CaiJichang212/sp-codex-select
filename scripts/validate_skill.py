#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List


BASE_REQUIRED = [
    "SKILL.md",
    "scripts/route_tasks.py",
    "scripts/install_codex_assets.sh",
    "assets/AGENTS.md-snippet.md",
    "references/routing-rubric.md",
]

DRAFT_HEADINGS = [
    "When to use",
    "Do not use when",
    "Required inputs",
    "Output contract",
    "Tool contract",
    "Validation checklist",
    "Safety and permissions",
    "Failure handling",
]

PILOT_REQUIRED = [
    "evals/eval_queries.json",
    "evals/evals.json",
    "scripts/run_evals.py",
    "scripts/analyze_routes.py",
    "governance/risk_assessment.md",
    "governance/review_record.md",
    "governance/changelog.md",
    "tests/test_install_codex_assets.py",
    "tests/test_route_tasks.py",
    "tests/test_run_evals.py",
    "tests/test_validate_skill.py",
    "tests/test_analyze_routes.py",
]


def check_required(root: Path, paths: Iterable[str], errors: List[str]) -> None:
    for relative in paths:
        if not (root / relative).exists():
            errors.append(f"missing required file: {relative}")


def check_skill(root: Path, errors: List[str], stage: str) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return
    skill = skill_path.read_text(encoding="utf-8")
    if not skill.startswith("---"):
        errors.append("SKILL.md frontmatter must start with ---")
    if "name: sp-codex-select" not in skill:
        errors.append("SKILL.md frontmatter must include name: sp-codex-select")
    if "description:" not in skill:
        errors.append("SKILL.md frontmatter must include description")
    if len(skill.splitlines()) > 560:
        errors.append("SKILL.md should stay under 560 lines after audit sections")
    if stage in {"draft", "pilot"}:
        for heading in DRAFT_HEADINGS:
            if not re.search(rf"^## {re.escape(heading)}$", skill, re.M):
                errors.append(f"SKILL.md missing audit heading: {heading}")


def check_agents(root: Path, errors: List[str]) -> None:
    agent_dir = root / "assets" / "codex-agents"
    agents = sorted(agent_dir.glob("*.toml"))
    if len(agents) < 7:
        errors.append("expected at least 7 Codex agent TOML files")
    for agent in agents:
        text = agent.read_text(encoding="utf-8")
        for key in ["name", "description", "developer_instructions"]:
            if not re.search(rf"^\s*{key}\s*=", text, re.M):
                errors.append(f"{agent.relative_to(root)} missing {key}")


def load_json(root: Path, relative: str, errors: List[str]) -> object | None:
    path = root / relative
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{relative} invalid JSON: {exc}")
        return None


def check_eval_suite(root: Path, relative: str, expected_suite: str, min_cases: int, errors: List[str]) -> None:
    payload = load_json(root, relative, errors)
    if not isinstance(payload, dict):
        errors.append(f"{relative} must be a JSON object")
        return
    if payload.get("suite") != expected_suite:
        errors.append(f"{relative} suite must be {expected_suite}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < min_cases:
        errors.append(f"{relative} must contain at least {min_cases} cases")


def check_installer_safety(root: Path, errors: List[str]) -> None:
    installer = root / "scripts" / "install_codex_assets.sh"
    if not installer.exists():
        return
    text = installer.read_text(encoding="utf-8")
    if "--dry-run" not in text:
        errors.append("installer missing --dry-run support")
    if "--force" not in text:
        errors.append("installer missing --force support")
    if re.search(r'rm\s+-rf\s+"\$REPO/.agents/skills/sp-codex-select"', text):
        errors.append("installer still contains unsafe default rm -rf target deletion")
    if "backup-" not in text:
        errors.append("installer missing backup behavior for forced replacement")


def validate(root: Path, stage: str) -> List[str]:
    errors: List[str] = []
    check_required(root, BASE_REQUIRED, errors)
    check_skill(root, errors, stage)
    check_agents(root, errors)
    if stage == "pilot":
        check_required(root, PILOT_REQUIRED, errors)
        check_eval_suite(root, "evals/eval_queries.json", "queries", 30, errors)
        check_eval_suite(root, "evals/evals.json", "routes", 20, errors)
        check_installer_safety(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate sp-codex-select package readiness.")
    parser.add_argument("root", nargs="?", default=".", help="Skill package root.")
    parser.add_argument("--stage", choices=["smoke", "draft", "pilot"], default="smoke")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    errors = validate(root, args.stage)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.stage}: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
