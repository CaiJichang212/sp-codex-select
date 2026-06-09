# sp-codex-select

`sp-codex-select` is a portable Agent Skill for cost-aware model/subagent routing in Superpowers + Codex workflows.

It turns a task or plan into a routing row: tier, Codex custom agent, model, reasoning effort, sandbox mode, fallback, and escalation triggers.

## Development reference

This repository tracks upstream Superpowers as a pinned git submodule at `third_party/superpowers/`.

- Development-time reference: `third_party/superpowers/`
- Upstream: `https://github.com/obra/superpowers.git`
- Current pinned commit: `6fd4507659784c351abbd2bc264c7162cfd386dc`

Initialize the checkout after cloning this repository:

```bash
git submodule update --init --recursive
```

Refresh the pinned reference intentionally, then commit the updated submodule pointer:

```bash
git submodule update --remote third_party/superpowers
git add third_party/superpowers .gitmodules
git commit -m "chore: bump superpowers submodule"
```

The submodule is for development-time source inspection, patch generation, and compatibility checks. Runtime integration remains no-fork: install this skill into the target Codex project and leave upstream Superpowers unchanged.

## Install into a Codex project

```bash
# From the parent directory containing sp-codex-select/
./sp-codex-select/scripts/install_codex_assets.sh /path/to/repo
```

The installer copies:

- the skill to `/path/to/repo/.agents/skills/sp-codex-select/`;
- custom-agent TOMLs to `/path/to/repo/.codex/agents/`.

Manual install:

```bash
mkdir -p .agents/skills .codex/agents
cp -R sp-codex-select .agents/skills/sp-codex-select
cp sp-codex-select/assets/codex-agents/*.toml .codex/agents/
cat sp-codex-select/assets/AGENTS.md-snippet.md >> AGENTS.md
```

## Install beside Superpowers

```bash
cp -R sp-codex-select /path/to/superpowers/skills/sp-codex-select
```

For a no-fork setup, keep the skill in `.agents/skills/` and paste `assets/AGENTS.md-snippet.md` into your project `AGENTS.md`.

## Use the router script

```bash
python3 sp-codex-select/scripts/route_tasks.py \
  --role implementer \
  --text "Fix typo in README and update changelog" \
  --format md
```

```bash
python3 sp-codex-select/scripts/route_tasks.py \
  --role implementer \
  --plan docs/implementation-plan.md \
  --format json
```

The script is deterministic and dependency-free. It is intentionally conservative: hard flags such as auth, migrations, concurrency, or prior failures route directly to GPT-5.5-backed deep agents.

## Validate

```bash
python3 sp-codex-select/scripts/validate_skill.py sp-codex-select
```
