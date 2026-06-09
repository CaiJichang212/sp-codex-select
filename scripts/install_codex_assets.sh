#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
FORCE=0
REPO="."

usage() {
  cat <<'EOF'
Usage: install_codex_assets.sh [--dry-run] [--force] [REPO]

Copies sp-codex-select into REPO/.agents/skills/ and Codex custom agents into
REPO/.codex/agents/.

Options:
  --dry-run   Print planned actions without writing files.
  --force     Replace an existing skill install after backing it up.
  -h, --help  Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      REPO="$1"
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [[ "$REPO" == "/" ]]; then
  REPO_ABS="/"
else
  REPO_ABS="$(cd "$(dirname "$REPO")" && pwd)/$(basename "$REPO")"
fi

case "$REPO_ABS" in
  "/"|"")
    printf 'Refusing unsafe target: %s\n' "$REPO_ABS" >&2
    exit 2
    ;;
esac

TARGET_SKILL="$REPO_ABS/.agents/skills/sp-codex-select"
TARGET_SKILLS_DIR="$REPO_ABS/.agents/skills"
TARGET_AGENTS_DIR="$REPO_ABS/.codex/agents"

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'DRY RUN:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

copy_skill_runtime() {
  local target="$1"
  run mkdir -p "$target"
  run cp "$SKILL_DIR/SKILL.md" "$target/"
  run cp "$SKILL_DIR/README.md" "$target/"

  for dir in scripts assets references agents; do
    run mkdir -p "$target/$dir"
    run cp -R "$SKILL_DIR/$dir/." "$target/$dir/"
  done
}

if [[ -e "$TARGET_SKILL" && "$FORCE" -ne 1 ]]; then
  printf 'Install target already exists: %s\n' "$TARGET_SKILL" >&2
  printf 'Use --force to replace it after a backup, or --dry-run to inspect actions.\n' >&2
  exit 1
fi

run mkdir -p "$TARGET_SKILLS_DIR" "$TARGET_AGENTS_DIR"

if [[ -e "$TARGET_SKILL" && "$FORCE" -eq 1 ]]; then
  BACKUP="$TARGET_SKILL.backup-$(date +%Y%m%d%H%M%S)"
  run mv "$TARGET_SKILL" "$BACKUP"
  printf 'Backed up existing skill to %s\n' "$BACKUP"
fi

copy_skill_runtime "$TARGET_SKILL"
run cp "$SKILL_DIR"/assets/codex-agents/*.toml "$TARGET_AGENTS_DIR/"

printf 'Installed sp-codex-select skill to %s\n' "$TARGET_SKILL"
printf 'Installed Codex custom agents to %s\n' "$TARGET_AGENTS_DIR"
printf 'Optional: append assets/AGENTS.md-snippet.md to your project AGENTS.md.\n'
