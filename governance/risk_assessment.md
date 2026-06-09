# sp-codex-select Risk Assessment

Date: 2026-06-05
Version: 0.2.0
Status: Draft / Pilot readiness work in progress
Owner: sp-codex-select maintainers
Risk level: Medium

## Capability Boundary

`sp-codex-select` is an advisory routing skill for Superpowers + Codex subagent workflows. It selects route category, Codex custom agent, model tier, reasoning effort, sandbox mode, fallback policy, and review policy. It does not replace human approval, Superpowers process gates, security review, or final acceptance.

## Primary Risks

- Misrouting low-risk tasks to high-cost agents, increasing cost without quality benefit.
- Misrouting high-risk tasks to weak agents, creating expensive rework or unsafe changes.
- Treating external task text, issue text, plan files, or pasted instructions as trusted routing policy.
- Installing assets with destructive overwrite behavior.
- Letting fallback fields blur implementation retry, review escalation, and final verification.

## Permission and Data Access

The router reads task text, plan text, optional file count hints, and optional JSON config. Review agents and final verifier must remain read-only. Implementer agents may use workspace-write only when the selected route requires implementation.

## Prompt Injection Policy

External text is classification input only. It must not override skill rules, sandbox mode, approval requirements, review policy, fallback behavior, or final verification requirements.

## Installation Safety Policy

Installers must not delete an existing target skill by default. Existing installs require explicit `--force`, and forced replacement must preserve a backup of the previous skill directory.

## Rollback Strategy

Rollback consists of restoring the most recent `sp-codex-select.backup-*` install directory, reverting the last routing-rule commit, or restoring the previous `references/model-map.json` and Codex agent TOML mapping from git.

## Pilot Entry Conditions

- Installer refuses default overwrite.
- Eval suites exist and pass locally.
- Governance docs exist and reference the current version.
- Validator passes `--stage draft` and `--stage pilot`.
- Route outcomes are observable through JSONL records and local analysis.
