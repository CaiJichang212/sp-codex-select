#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

sys.dont_write_bytecode = True


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

REQUIRED_SKILL_METADATA = [
    "org.owner",
    "org.version",
    "org.status",
    "org.risk_level",
    "org.last_reviewed",
]

VALID_STATUSES = {"draft", "pilot", "production", "deprecated"}
VALID_RISK_LEVELS = {"R0", "R1", "R2", "R3", "R4"}
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


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str, errors: List[str]) -> dict[str, object]:
    if not text.startswith("---\n"):
        errors.append("SKILL.md frontmatter must start with ---")
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        errors.append("SKILL.md frontmatter must end with ---")
        return {}
    frontmatter = text[4:end].splitlines()
    parsed: dict[str, object] = {}
    current_map: str | None = None
    for line_no, line in enumerate(frontmatter, start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  "):
            if current_map is None:
                errors.append(f"SKILL.md frontmatter line {line_no}: nested value without parent key")
                continue
            match = re.match(r"^\s{2}([A-Za-z0-9_.-]+):\s*(.*?)\s*$", line)
            if not match:
                errors.append(f"SKILL.md frontmatter line {line_no}: unsupported nested mapping syntax")
                continue
            container = parsed.setdefault(current_map, {})
            if not isinstance(container, dict):
                errors.append(f"SKILL.md frontmatter line {line_no}: {current_map} must be a mapping")
                continue
            container[match.group(1)] = unquote(match.group(2))
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if not match:
            errors.append(f"SKILL.md frontmatter line {line_no}: unsupported syntax")
            continue
        key, value = match.group(1), match.group(2)
        if value == "":
            parsed[key] = {}
            current_map = key
        else:
            parsed[key] = unquote(value)
            current_map = None
    return parsed


def check_required(root: Path, paths: Iterable[str], errors: List[str]) -> None:
    for relative in paths:
        if not (root / relative).exists():
            errors.append(f"missing required file: {relative}")


def check_skill(root: Path, errors: List[str], stage: str) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return
    skill = skill_path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(skill, errors)
    if frontmatter.get("name") != "sp-codex-select":
        errors.append("SKILL.md frontmatter must include name: sp-codex-select")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md frontmatter must include description")
    compatibility = frontmatter.get("compatibility")
    if compatibility is not None and not isinstance(compatibility, str):
        errors.append("SKILL.md frontmatter compatibility must be a string")
    metadata = frontmatter.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        errors.append("SKILL.md frontmatter metadata must be a string-to-string mapping")
    if isinstance(metadata, dict):
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append("SKILL.md frontmatter metadata must be a string-to-string mapping")
    if stage == "pilot":
        if not isinstance(metadata, dict):
            errors.append("SKILL.md frontmatter missing metadata")
            for key in REQUIRED_SKILL_METADATA:
                errors.append(f"SKILL.md frontmatter missing metadata.{key}")
        else:
            for key in REQUIRED_SKILL_METADATA:
                value = metadata.get(key)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"SKILL.md frontmatter missing metadata.{key}")
            status = metadata.get("org.status")
            if isinstance(status, str) and status not in VALID_STATUSES:
                errors.append(f"SKILL.md metadata.org.status must be one of {sorted(VALID_STATUSES)}")
            risk_level = metadata.get("org.risk_level")
            if isinstance(risk_level, str) and risk_level not in VALID_RISK_LEVELS:
                errors.append(f"SKILL.md metadata.org.risk_level must be one of {sorted(VALID_RISK_LEVELS)}")
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
        return
    if expected_suite == "queries":
        positive = sum(1 for case in cases if isinstance(case, dict) and case.get("expected_use_skill") is True)
        negative = sum(1 for case in cases if isinstance(case, dict) and case.get("expected_use_skill") is False)
        if positive < 10:
            errors.append(f"{relative} must contain at least 10 positive trigger cases")
        if negative < 10:
            errors.append(f"{relative} must contain at least 10 negative trigger cases")


def read_simple_yaml_keys(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return values


def check_openai_yaml(root: Path, errors: List[str]) -> None:
    path = root / "agents" / "openai.yaml"
    values = read_simple_yaml_keys(path)
    for field in ["name", "display_name", "short_description", "default_prompt"]:
        if not values.get(field):
            errors.append(f"agents/openai.yaml missing {field}")


def load_route_config(root: Path, errors: List[str]) -> dict | None:
    route_path = root / "scripts" / "route_tasks.py"
    if not route_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("sp_codex_select_route_tasks", route_path)
    if spec is None or spec.loader is None:
        errors.append("cannot load scripts/route_tasks.py for config consistency check")
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    config = getattr(module, "DEFAULT_CONFIG", None)
    if not isinstance(config, dict):
        errors.append("scripts/route_tasks.py missing DEFAULT_CONFIG")
        return None
    return config


def check_model_map_consistency(root: Path, errors: List[str]) -> None:
    payload = load_json(root, "references/model-map.json", errors)
    route_config = load_route_config(root, errors)
    if not isinstance(payload, dict) or route_config is None:
        return
    tiers = payload.get("tiers")
    models = route_config.get("models")
    if not isinstance(tiers, dict) or not isinstance(models, dict):
        errors.append("references/model-map.json tiers must match route_tasks DEFAULT_CONFIG models")
        return
    expected_hard_flags = route_config.get("hard_flags")
    if payload.get("hard_flags") != expected_hard_flags:
        errors.append(f"model-map hard_flags expected {expected_hard_flags!r} got {payload.get('hard_flags')!r}")
    fields = [
        "tier",
        "agent_type",
        "model",
        "reasoning_effort",
        "sandbox_mode",
        "fallback",
        "implementation_fallback",
        "review_fallback",
        "final_verification_policy",
    ]
    for category, model_cfg in models.items():
        map_cfg = tiers.get(category)
        if not isinstance(map_cfg, dict):
            errors.append(f"model-map missing tier category: {category}")
            continue
        for field in fields:
            if map_cfg.get(field) != model_cfg.get(field):
                errors.append(
                    f"model-map {category}.{field} expected {model_cfg.get(field)!r} got {map_cfg.get(field)!r}"
                )


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
    if stage in {"runtime", "pilot"}:
        check_openai_yaml(root, errors)
        check_model_map_consistency(root, errors)
    if stage == "pilot":
        check_required(root, PILOT_REQUIRED, errors)
        check_eval_suite(root, "evals/eval_queries.json", "queries", 30, errors)
        check_eval_suite(root, "evals/evals.json", "routes", 20, errors)
        check_installer_safety(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate sp-codex-select package readiness.")
    parser.add_argument("root", nargs="?", default=".", help="Skill package root.")
    parser.add_argument("--stage", choices=["smoke", "runtime", "draft", "pilot"], default="smoke")
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
