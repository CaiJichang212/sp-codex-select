#!/usr/bin/env python3
"""
sp-codex-select: deterministic cost-aware router for Superpowers + Codex subagents.

The script is dependency-free. It is an advisory router, not a substitute for review.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "0.2.0"

DEFAULT_CONFIG: Dict[str, Any] = {
    "models": {
        "explorer": {
            "tier": "T0",
            "agent_type": "spc_explorer",
            "model": "gpt-5.3-codex-spark",
            "reasoning_effort": "medium",
            "sandbox_mode": "read-only",
            "fallback": "spc_spark",
            "implementation_fallback": "spc_spark",
            "review_fallback": None,
            "final_verification_policy": "not-required",
        },
        "quick": {
            "tier": "T1",
            "agent_type": "spc_quick",
            "model": "gpt-5.4-mini",
            "reasoning_effort": "low",
            "sandbox_mode": "workspace-write",
            "fallback": "spc_spark",
            "implementation_fallback": "spc_spark",
            "review_fallback": None,
            "final_verification_policy": "not-required",
        },
        "spark": {
            "tier": "T2",
            "agent_type": "spc_spark",
            "model": "gpt-5.3-codex-spark",
            "reasoning_effort": "medium",
            "sandbox_mode": "workspace-write",
            "fallback": "spc_standard",
            "implementation_fallback": "spc_standard",
            "review_fallback": None,
            "final_verification_policy": "recommended-for-behavior-change",
        },
        "standard": {
            "tier": "T3",
            "agent_type": "spc_standard",
            "model": "gpt-5.4",
            "reasoning_effort": "high",
            "sandbox_mode": "workspace-write",
            "fallback": "spc_deep",
            "implementation_fallback": "spc_deep",
            "review_fallback": None,
            "final_verification_policy": "recommended-for-branch-gate",
        },
        "deep": {
            "tier": "T4",
            "agent_type": "spc_deep",
            "model": "gpt-5.5",
            "reasoning_effort": "high",
            "sandbox_mode": "workspace-write",
            "fallback": "spc_final_verifier",
            "implementation_fallback": None,
            "review_fallback": "spc_quality_reviewer",
            "final_verification_policy": "recommended-for-hard-flags",
        },
        "spec_review": {
            "tier": "R1",
            "agent_type": "spc_spec_reviewer",
            "model": "gpt-5.4",
            "reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "fallback": "spc_quality_reviewer",
            "implementation_fallback": None,
            "review_fallback": "spc_quality_reviewer",
            "final_verification_policy": "not-required",
        },
        "quality_review": {
            "tier": "R2",
            "agent_type": "spc_quality_reviewer",
            "model": "gpt-5.5",
            "reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "fallback": "spc_final_verifier",
            "implementation_fallback": None,
            "review_fallback": "spc_final_verifier",
            "final_verification_policy": "recommended-for-hard-flags",
        },
        "final_verify": {
            "tier": "R3",
            "agent_type": "spc_final_verifier",
            "model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "sandbox_mode": "read-only",
            "fallback": None,
            "implementation_fallback": None,
            "review_fallback": None,
            "final_verification_policy": "required-final-gate",
        },
    },
    "thresholds": {"quick_max": 2, "spark_max": 6, "standard_max": 10},
    "policy": {
        "unknown_files_first_use_explorer": True,
        "hard_flags_force_deep": True,
        "spec_review_on_behavior_change": True,
        "quality_review_on_hard_flags": True,
    },
}

# Phrases are matched with token/word boundaries for ASCII and substring matching for CJK.
KEYWORDS: Dict[str, List[str]] = {
    "trivial": [
        "typo", "spelling", "rename", "comment", "docstring", "format", "lint",
        "one-line", "single file", "clear spec", "mechanical", "boilerplate", "readme",
        "changelog", "拼写", "错别字", "注释", "格式化", "单文件", "机械", "文档修正",
    ],
    "exact": [
        "acceptance criteria", "exact", "unit test", "tests exist", "reproduce with",
        "given when then", "验收标准", "明确测试", "单元测试", "复现步骤", "输入输出明确",
    ],
    "ambiguity": [
        "unclear", "ambiguous", "unknown", "figure out", "infer", "investigate",
        "inferred",
        "explore", "discover", "root cause", "debug", "flaky", "intermittent",
        "cannot reproduce", "performance regression", "不明确", "未知", "推断", "调研",
        "探索", "定位", "根因", "为什么", "偶发", "难以复现", "性能回退",
    ],
    "integration": [
        "multi-file", "cross-module", "cross package", "monorepo", "integration",
        "backend", "frontend", "database", "db", "cache", "queue", "event",
        "webhook", "cli", "sdk", "protocol", "多个文件", "跨模块", "跨包", "集成",
        "接口", "前后端", "数据库", "缓存", "队列", "事件", "协议",
    ],
    "api": ["api", "public api", "endpoint", "graphql", "rest", "rpc", "sdk", "client compatibility", "公共api"],
    "security": [
        "auth", "authentication", "authorization", "permission", "security", "secret",
        "token", "oauth", "payment", "billing", "pii", "privacy", "crypto",
        "encryption", "signature", "xss", "csrf", "sql injection", "rce", "sandbox",
        "credential", "权限", "鉴权", "认证", "授权", "安全", "密钥", "令牌",
        "支付", "账单", "隐私", "加密", "签名", "凭证",
    ],
    "data": [
        "migration", "schema", "destructive", "delete", "data loss", "rollback",
        "transaction", "backfill", "consistency", "idempotent", "idempotency", "replication",
        "distributed", "race condition", "race", "deadlock", "concurrency", "并发",
        "迁移", "表结构", "删除", "数据丢失", "回滚", "事务", "回填", "一致性",
        "幂等", "复制", "分布式", "竞态", "死锁",
    ],
    "architecture": [
        "architecture", "architectural", "system design", "refactor", "rewrite",
        "breaking change", "backward compatibility", "compatibility", "abstraction",
        "framework", "plugin", "extension point", "long-term", "strategy", "tradeoff",
        "架构", "设计", "重构", "重写", "破坏性", "兼容", "抽象", "框架", "插件", "扩展点", "长期", "权衡",
    ],
    "prior_failure": [
        "previously failed", "failed once", "failed twice", "retry after failure",
        "blocked", "done_with_concerns", "review failed", "tests failed", "failing test",
        "失败过", "重试", "受阻", "审查失败", "测试失败",
    ],
    "verification": [
        "test", "tests", "unit test", "integration test", "e2e", "lint", "typecheck",
        "pytest", "jest", "vitest", "go test", "cargo test", "npm test", "pnpm test",
        "测试", "单测", "集成测试", "端到端", "类型检查",
    ],
}

ROLE_ALIASES = {
    "auto": "auto",
    "impl": "implementer",
    "implementation": "implementer",
    "coder": "implementer",
    "code": "implementer",
    "debug": "debugger",
    "debugger": "debugger",
    "qa": "quality-reviewer",
    "quality": "quality-reviewer",
    "quality-review": "quality-reviewer",
    "spec": "spec-reviewer",
    "spec-review": "spec-reviewer",
    "review": "quality-reviewer",
    "final": "final-verifier",
    "verify": "final-verifier",
    "verifier": "final-verifier",
    "map": "explorer",
    "explore": "explorer",
    "research": "explorer",
    "plan": "planner",
    "planner": "planner",
    "architect": "architect",
    "docs": "doc-writer",
    "doc": "doc-writer",
    "test": "test-writer",
    "tester": "test-writer",
}

PATH_RE = re.compile(
    r"(?:[\w.$@~+\-]+/)+[\w.$@~+\-]+\.(?:py|js|jsx|ts|tsx|mjs|cjs|go|rs|java|kt|swift|rb|php|cs|cpp|c|h|sql|md|json|ya?ml|toml|sh|tf|proto|vue|css|html)",
    re.I,
)
ASCII_RE = re.compile(r"^[\x00-\x7F]+$")


@dataclass
class Route:
    task_id: str
    role: str
    score: int
    tier: str
    category: str
    agent_type: str
    model: str
    reasoning_effort: str
    fallback_agent_type: Optional[str]
    implementation_fallback_agent_type: Optional[str]
    review_fallback_agent_type: Optional[str]
    final_verification_policy: str
    sandbox_mode: str
    confidence: str
    hard_flags: List[str]
    signals: Dict[str, Any]
    rationale: List[str]
    escalation: List[str]
    codex_spawn_hint: str
    superpowers_dispatch_header: str


def deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            deep_merge(dst[key], value)
        else:
            dst[key] = value
    return dst


def load_config(path: Optional[str]) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if path:
        deep_merge(cfg, json.loads(Path(path).read_text(encoding="utf-8")))
    return cfg


def phrase_hit(text: str, phrase: str) -> bool:
    phrase_l = phrase.lower()
    if ASCII_RE.match(phrase_l):
        # For ASCII, require token boundaries around the entire phrase.
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(phrase_l).replace(r"\ ", r"\s+") + r"(?![A-Za-z0-9_])"
        return re.search(pattern, text) is not None
    return phrase_l in text


def hits(text: str, key: str) -> List[str]:
    return [phrase for phrase in KEYWORDS[key] if phrase_hit(text, phrase)]


def normalize_role(role: str, text: str) -> str:
    role = (role or "auto").strip().lower().replace("_", "-")
    role = ROLE_ALIASES.get(role, role)
    if role != "auto":
        return role
    if any(x in text for x in ["final review", "final verifier", "final branch", "before release", "release review", "最终", "全量审查", "发布前"]):
        return "final-verifier"
    if any(x in text for x in ["spec review", "spec compliance", "规格", "需求符合"]):
        return "spec-reviewer"
    if any(x in text for x in ["code review", "quality review", "质量审查", "代码审查"]):
        return "quality-reviewer"
    if any(x in text for x in ["explore", "investigate", "map", "locate", "定位", "探索", "调查"]):
        return "explorer"
    if any(x in text for x in ["plan", "architecture", "方案", "架构"]):
        return "planner"
    if any(x in text for x in ["docs", "documentation", "readme", "文档"]):
        return "doc-writer"
    if any(x in text for x in ["test", "测试"]):
        return "test-writer"
    return "implementer"


def estimate_files(text: str, explicit: Optional[int]) -> Tuple[Optional[int], List[str], bool]:
    if explicit is not None:
        return max(0, explicit), [], False
    paths = sorted(set(PATH_RE.findall(text)))
    if paths:
        return len(paths), paths, False
    if any(x in text for x in ["affected files unknown", "unknown files", "find relevant files", "找相关文件", "未知文件"]):
        return None, [], True
    if any(x in text for x in ["single file", "one file", "1 file", "单文件", "一个文件"]):
        return 1, [], False
    if any(x in text for x in ["two files", "2 files", "两个文件"]):
        return 2, [], False
    if any(x in text for x in ["multiple files", "multi-file", "many files", "多个文件", "多文件"]):
        return 4, [], False
    return None, [], True


def loc_hint(text: str) -> int:
    nums = [int(m.group(1)) for m in re.finditer(r"(\d{1,5})\s*(?:loc|lines|行)", text)]
    if nums:
        return max(nums)
    # Prompt size is a weak proxy for expected scope. Keep this conservative.
    return max(0, len(re.findall(r"\w+", text)) // 4)


def score_task(text: str, role: str, explicit_files: Optional[int]) -> Tuple[int, List[str], Dict[str, Any], List[str]]:
    t = text.lower()
    file_count, paths, file_unknown = estimate_files(t, explicit_files)
    loc = loc_hint(t)
    hit = {key: hits(t, key) for key in KEYWORDS}

    hard_flags: List[str] = []
    if hit["security"]:
        hard_flags.append("security")
    if hit["data"]:
        hard_flags.append("data")
    if hit["architecture"]:
        hard_flags.append("architecture")
    if hit["prior_failure"]:
        hard_flags.append("prior_failure")
    if role in ["architect", "final-verifier"]:
        hard_flags.append(f"role:{role}")

    if file_unknown:
        file_scope = 1
    elif (file_count or 0) <= 1:
        file_scope = 0
    elif (file_count or 0) <= 3:
        file_scope = 1
    elif (file_count or 0) <= 7:
        file_scope = 2
    else:
        file_scope = 3

    if loc <= 80:
        diff_size = 0
    elif loc <= 250:
        diff_size = 1
    elif loc <= 800:
        diff_size = 2
    else:
        diff_size = 3

    ambiguity = 0
    if file_unknown:
        ambiguity += 1
    if hit["ambiguity"]:
        ambiguity += 2
    if hit["exact"]:
        ambiguity -= 1
    if hit["trivial"] and not hit["ambiguity"]:
        ambiguity -= 1
    ambiguity = max(0, min(3, ambiguity))

    integration = 0
    if hit["integration"] or hit["api"]:
        integration += 1
    if hit["data"]:
        integration += 2
    integration = max(0, min(3, integration))

    risk = 0
    if hit["api"]:
        risk += 1
    if hit["architecture"]:
        risk += 1
    if hit["security"]:
        risk += 2
    if hit["data"]:
        risk += 2
    if hit["prior_failure"]:
        risk += 2
    risk = max(0, min(3, risk))

    verification = 0
    if hit["prior_failure"] or any(p in t for p in ["flaky", "intermittent", "难以复现", "偶发"]):
        verification = 2
    elif hit["verification"]:
        verification = 0
    elif hit["trivial"]:
        verification = 0
    else:
        verification = 1

    role_adjust = {
        "doc-writer": -1,
        "test-writer": 0,
        "debugger": 2,
        "planner": 2,
        "architect": 4,
        "spec-reviewer": 2,
        "quality-reviewer": 3,
        "final-verifier": 4,
        "explorer": 0,
    }.get(role, 0)

    score = max(0, file_scope + diff_size + ambiguity + integration + risk + verification + role_adjust)
    signals = {
        "file_count": file_count,
        "file_unknown": file_unknown,
        "paths_detected": paths[:20],
        "loc_hint": loc,
        "keyword_hits": {k: v for k, v in hit.items() if v},
        "dimensions": {
            "file_scope": file_scope,
            "diff_size": diff_size,
            "ambiguity": ambiguity,
            "integration": integration,
            "risk": risk,
            "verification": verification,
            "role_adjust": role_adjust,
        },
    }
    rationale = [f"{k}={v}" for k, v in signals["dimensions"].items()]
    return score, sorted(set(hard_flags)), signals, rationale


def pick_category(score: int, role: str, hard_flags: List[str], signals: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    if role == "final-verifier":
        return "final_verify"
    if role == "quality-reviewer":
        return "quality_review"
    if role == "spec-reviewer":
        return "quality_review" if hard_flags else "spec_review"
    if role == "explorer":
        return "explorer"
    if role == "architect":
        return "deep"
    if role == "planner":
        return "deep" if hard_flags or score >= 8 else "standard"
    if role == "debugger" and (hard_flags or score >= 7):
        return "deep"
    if signals.get("file_unknown") and cfg["policy"].get("unknown_files_first_use_explorer") and not hard_flags:
        trivial = bool(signals.get("keyword_hits", {}).get("trivial"))
        exact = bool(signals.get("keyword_hits", {}).get("exact"))
        verification = signals.get("dimensions", {}).get("verification", 1)
        if trivial and score <= cfg["thresholds"]["quick_max"] and verification <= 1:
            return "quick"
        return "explorer"
    if hard_flags and cfg["policy"].get("hard_flags_force_deep"):
        return "deep"

    thresholds = cfg["thresholds"]
    if score <= thresholds["quick_max"]:
        return "quick"
    if score <= thresholds["spark_max"]:
        return "spark"
    if score <= thresholds["standard_max"]:
        return "standard"
    return "deep"


def confidence_for(score: int, category: str, hard_flags: List[str], signals: Dict[str, Any]) -> str:
    if signals.get("file_unknown") and category != "explorer":
        if category in {"spec_review", "quality_review", "final_verify"}:
            return "medium"
        if category == "quick" and signals.get("keyword_hits", {}).get("trivial"):
            return "medium"
        return "low"
    if hard_flags and category != "deep":
        return "low"
    if score in {3, 4, 6, 7, 10, 11}:
        return "medium"
    return "high"


def build_header(tier: str, category: str, model_cfg: Dict[str, Any], score: int, hard_flags: List[str], confidence: str, rationale: List[str]) -> str:
    return "\n".join([
        "[sp-codex-select]",
        f"tier: {tier}",
        f"category: {category}",
        f"agent_type: {model_cfg['agent_type']}",
        f"model: {model_cfg['model']}",
        f"model_reasoning_effort: {model_cfg['reasoning_effort']}",
        f"sandbox_mode: {model_cfg.get('sandbox_mode', 'workspace-write')}",
        f"fallback_agent_type: {model_cfg.get('fallback') or 'none'}",
        f"implementation_fallback_agent_type: {model_cfg.get('implementation_fallback') or 'none'}",
        f"review_fallback_agent_type: {model_cfg.get('review_fallback') or 'none'}",
        f"final_verification_policy: {model_cfg.get('final_verification_policy', 'not-required')}",
        f"complexity_score: {score}",
        f"confidence: {confidence}",
        f"hard_flags: {', '.join(hard_flags) if hard_flags else 'none'}",
        f"rationale: {'; '.join(rationale)}",
        "rule: use the selected cheapest-capable tier; escalate rather than guessing.",
        "[/sp-codex-select]",
    ])


def route_task(text: str, role_arg: str, explicit_files: Optional[int], cfg: Dict[str, Any], task_id: Optional[str] = None) -> Route:
    role = normalize_role(role_arg, text.lower())
    score, hard_flags, signals, rationale = score_task(text, role, explicit_files)
    category = pick_category(score, role, hard_flags, signals, cfg)
    model_cfg = cfg["models"][category]
    tier = model_cfg["tier"]
    confidence = confidence_for(score, category, hard_flags, signals)
    tid = task_id or "task-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    header = build_header(tier, category, model_cfg, score, hard_flags, confidence, rationale)
    implementation_fallback = model_cfg.get("implementation_fallback")
    review_fallback = model_cfg.get("review_fallback")
    final_verification_policy = model_cfg.get("final_verification_policy", "not-required")
    legacy_fallback = model_cfg.get("fallback")
    escalation = [
        "Escalate on BLOCKED caused by reasoning/design/debugging uncertainty.",
        "Escalate on correctness-related DONE_WITH_CONCERNS or failed review.",
        "Retry the same tier only once for missing context; never repeat the same prompt after material failure.",
    ]
    return Route(
        task_id=tid,
        role=role,
        score=score,
        tier=tier,
        category=category,
        agent_type=model_cfg["agent_type"],
        model=model_cfg["model"],
        reasoning_effort=model_cfg["reasoning_effort"],
        fallback_agent_type=legacy_fallback,
        implementation_fallback_agent_type=implementation_fallback,
        review_fallback_agent_type=review_fallback,
        final_verification_policy=final_verification_policy,
        sandbox_mode=model_cfg.get("sandbox_mode", "workspace-write"),
        confidence=confidence,
        hard_flags=hard_flags,
        signals=signals,
        rationale=rationale,
        escalation=escalation,
        codex_spawn_hint=f"spawn_agent(agent_type=\"{model_cfg['agent_type']}\", task_name=\"{tid}\", message=<task prompt with sp-codex-select header>)",
        superpowers_dispatch_header=header,
    )


def split_plan(text: str) -> List[Tuple[str, str]]:
    task_lines: List[Tuple[str, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^\s*(?:[-*]|\d+[.)])\s+(?:\[[ xX]?\]\s+)?(.{8,})$", line)
        if match:
            task_lines.append((f"task-line-{idx}", match.group(1).strip()))
    if len(task_lines) >= 2:
        return task_lines

    headings = list(re.finditer(r"(?m)^(#{2,4})\s+(.+?)\s*$", text))
    sections: List[Tuple[str, str]] = []
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = text[match.start():end].strip()
        title = re.sub(r"[^\w\u4e00-\u9fff]+", "-", match.group(2)).strip("-")[:48]
        if len(body) > 20:
            sections.append((f"task-{i + 1}-{title or 'untitled'}", body))
    return sections or [("task-1", text.strip())]


def route_many(text: str, mode: str, role: str, explicit_files: Optional[int], cfg: Dict[str, Any]) -> List[Route]:
    tasks = split_plan(text) if mode == "plan" else [(None, text.strip())]
    return [route_task(body, role, explicit_files, cfg, task_id=tid) for tid, body in tasks]


def print_markdown(routes: List[Route]) -> None:
    print("| task_id | role | score | tier | agent_type | model | effort | fallback | confidence | flags |")
    print("|---|---|---:|---|---|---|---|---|---|---|")
    for r in routes:
        flags = ", ".join(r.hard_flags) if r.hard_flags else "-"
        fallback = r.fallback_agent_type or "-"
        print(f"| {r.task_id} | {r.role} | {r.score} | {r.tier} | {r.agent_type} | {r.model} | {r.reasoning_effort} | {fallback} | {r.confidence} | {flags} |")
    print("\n## Dispatch headers")
    for r in routes:
        print(f"\n### {r.task_id}\n```text\n{r.superpowers_dispatch_header}\n```")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Route Superpowers/Codex subagent tasks to cost-effective model tiers.")
    parser.add_argument("--version", action="version", version=f"sp-codex-select {VERSION}")
    parser.add_argument("--text", help="Task text. If omitted, stdin is used unless --plan is supplied.")
    parser.add_argument("--plan", help="Plan file to split into task rows.")
    parser.add_argument("--task-file", "--file", dest="task_file", help="File containing a single task prompt.")
    parser.add_argument("--mode", choices=["task", "plan"], default=None, help="Force task/plan mode. Defaults to plan when --plan is used.")
    parser.add_argument("--role", default="auto", help="Task role: implementer, explorer, spec-reviewer, quality-reviewer, final-verifier, planner, architect, debugger, test-writer, doc-writer.")
    parser.add_argument("--files", type=int, help="Explicit estimated number of affected files.")
    parser.add_argument("--config", help="Optional JSON config override.")
    parser.add_argument("--format", choices=["json", "md", "markdown", "csv", "header"], default="json")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    if args.plan:
        text = Path(args.plan).read_text(encoding="utf-8")
        mode = args.mode or "plan"
    elif args.task_file:
        text = Path(args.task_file).read_text(encoding="utf-8")
        mode = args.mode or "task"
    elif args.text is not None:
        text = args.text
        mode = args.mode or "task"
    else:
        text = sys.stdin.read()
        mode = args.mode or "task"

    if not text.strip():
        raise SystemExit("No task or plan text provided.")

    routes = route_many(text, mode, args.role, args.files, cfg)

    if args.format == "json":
        payload: Any = asdict(routes[0]) if len(routes) == 1 else [asdict(route) for route in routes]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.format in {"md", "markdown"}:
        print_markdown(routes)
    elif args.format == "header":
        print("\n\n".join(route.superpowers_dispatch_header for route in routes))
    elif args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["task_id", "role", "score", "tier", "category", "agent_type", "model", "reasoning_effort", "fallback", "confidence", "hard_flags"])
        for r in routes:
            writer.writerow([r.task_id, r.role, r.score, r.tier, r.category, r.agent_type, r.model, r.reasoning_effort, r.fallback_agent_type or "", r.confidence, ";".join(r.hard_flags)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
