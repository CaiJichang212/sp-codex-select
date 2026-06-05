#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$REPO/.agents/skills" "$REPO/.codex/agents"
rm -rf "$REPO/.agents/skills/sp-codex-select"
cp -R "$SKILL_DIR" "$REPO/.agents/skills/sp-codex-select"
cp "$SKILL_DIR"/assets/codex-agents/*.toml "$REPO/.codex/agents/"

printf 'Installed sp-codex-select skill to %s\n' "$REPO/.agents/skills/sp-codex-select"
printf 'Installed Codex custom agents to %s\n' "$REPO/.codex/agents"
printf 'Optional: append assets/AGENTS.md-snippet.md to your project AGENTS.md.\n'
