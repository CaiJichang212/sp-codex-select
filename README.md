# sp-codex-select

`sp-codex-select` is a portable Agent Skill for cost-aware model/subagent routing in Superpowers + Codex workflows.

It turns a task or plan into a routing row: tier, Codex custom agent, model, reasoning effort, sandbox mode, fallback, and escalation triggers.

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
