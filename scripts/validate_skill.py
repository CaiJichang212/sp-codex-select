#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

REQUIRED = [
    'SKILL.md',
    'scripts/route_tasks.py',
    'assets/AGENTS.md-snippet.md',
    'references/routing-rubric.md',
]

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
missing = [p for p in REQUIRED if not (root / p).exists()]
if missing:
    raise SystemExit('Missing required files: ' + ', '.join(missing))
skill = (root / 'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---') or 'name: sp-codex-select' not in skill or 'description:' not in skill:
    raise SystemExit('SKILL.md frontmatter must include name and description')
if len(skill.splitlines()) > 500:
    raise SystemExit('SKILL.md should stay under 500 lines')
agent_dir = root / 'assets' / 'codex-agents'
agents = sorted(agent_dir.glob('*.toml'))
if len(agents) < 7:
    raise SystemExit('Expected at least 7 Codex agent TOML files')
for agent in agents:
    text = agent.read_text(encoding='utf-8')
    for key in ['name', 'description', 'developer_instructions']:
        if not re.search(rf'^\s*{key}\s*=', text, re.M):
            raise SystemExit(f'{agent.name} missing {key}')
print(f'OK: {root}')
