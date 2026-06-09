# Superpowers + Codex integration

## Development-time upstream reference

Use a pinned git submodule at `third_party/superpowers/` during development.

- Upstream repository: `https://github.com/obra/superpowers.git`
- Current pinned commit: `6fd4507659784c351abbd2bc264c7162cfd386dc`
- Purpose: inspect `skills/` source, validate assumptions against upstream behavior, and generate patch candidates without forking runtime integration

Recommended commands:

```bash
git submodule update --init --recursive
git submodule status
```

Do not edit Codex's cached plugin copy under `~/.codex/plugins/cache/...`. Treat the submodule as the only local upstream reference inside this repository.

## Recommended no-fork integration

1. Install the skill to `.agents/skills/sp-codex-select/`.
2. Install custom agent TOMLs to `.codex/agents/`.
3. Append `assets/AGENTS.md-snippet.md` to project `AGENTS.md`.
4. Keep upstream Superpowers unchanged.

This works because the project instructions tell Codex to run model routing before Superpowers SDD dispatch, while the skill provides the reusable rubric and script.

Runtime integration stays no-fork even when the submodule is present. The submodule is a development aid, not a deployed dependency.

## Superpowers fork integration

Copy this skill into the Superpowers `skills/` directory and insert `assets/superpowers-sdd-patch.md` into the SDD skill before implementation dispatch.

Only move to a fork or a vendored `third_party/` snapshot when CI or release engineering requires fully reproducible upstream-coupled tests inside this repository.

## Dispatch pattern

1. Parent reads plan.
2. Parent routes every task through `sp-codex-select`.
3. Parent dispatches selected custom agents.
4. Implementer reports status.
5. Spec reviewer verifies plan compliance.
6. Quality reviewer verifies correctness/risk when needed.
7. Parent escalates according to fallback policy.
