# Superpowers + Codex integration

## Recommended no-fork integration

1. Install the skill to `.agents/skills/sp-codex-select/`.
2. Install custom agent TOMLs to `.codex/agents/`.
3. Append `assets/AGENTS.md-snippet.md` to project `AGENTS.md`.
4. Keep upstream Superpowers unchanged.

This works because the project instructions tell Codex to run model routing before Superpowers SDD dispatch, while the skill provides the reusable rubric and script.

## Superpowers fork integration

Copy this skill into the Superpowers `skills/` directory and insert `assets/superpowers-sdd-patch.md` into the SDD skill before implementation dispatch.

## Dispatch pattern

1. Parent reads plan.
2. Parent routes every task through `sp-codex-select`.
3. Parent dispatches selected custom agents.
4. Implementer reports status.
5. Spec reviewer verifies plan compliance.
6. Quality reviewer verifies correctness/risk when needed.
7. Parent escalates according to fallback policy.
