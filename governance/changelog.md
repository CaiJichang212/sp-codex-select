# sp-codex-select Changelog

## 0.2.2 - 2026-06-09

- Stop failing Pilot validation on local `.gitignore`-ignored artifacts such as `.DS_Store`, `__pycache__`, and `*.pyc`.
- Force public API and endpoint compatibility tasks to the `api` hard flag and `spc_deep`.
- Add governance metadata to `SKILL.md` frontmatter for Pilot review.
- Strengthen Pilot validation for frontmatter metadata, trigger eval balance, and model-map hard flags.
- Harden installer to copy only runtime skill files into target projects.
- Exclude development-only source materials such as `docs/`, `tests/`, `evals/`, `governance/`, `.git`, and `third_party/` from target installs.
- Reduce route false positives for JSON schema validation and Markdown plan filenames.
- Add near-miss trigger evals for ordinary Codex explanations and non-dispatch requests.
- Add validator checks for `agents/openai.yaml` UI metadata and model-map consistency.
- Add split fallback semantics to `references/model-map.json`.
- Fix clean error reporting for empty route JSONL analysis.
- Restore Chinese table-structure data-risk routing.
- Preserve route-header trigger behavior even when the request asks not to dispatch subagents.
- Add `validate_skill.py --stage runtime` for installed runtime skill copies.

## 0.2.1 - 2026-06-05

- Add non-destructive installer behavior with dry-run, force, and backup semantics.
- Add Pilot readiness eval suites for trigger boundaries and route outputs.
- Add governance package for risk assessment, review record, and change tracking.
- Add Draft/Pilot validation requirements.
- Clarify fallback semantics across implementation, review, and final verification.
- Clarify prompt injection handling for untrusted task and plan text.
- Pass local Draft/Pilot validation gate with eval, governance, installer safety, route tests, and observability checks.

## 0.2.0 - Current Baseline

- Deterministic router script exists.
- Codex custom-agent TOMLs exist.
- Basic smoke validator exists.
- Observability guidance exists as documentation.
