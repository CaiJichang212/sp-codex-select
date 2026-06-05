# Codex installation notes

Codex repository skills should be placed under `.agents/skills/`.
Project-scoped custom agents should be placed under `.codex/agents/`.
Project `AGENTS.md` should include the model-routing enforcement snippet if you want the behavior to apply even when the skill is not explicitly mentioned.

Run:

```bash
./sp-codex-select/scripts/install_codex_assets.sh /path/to/repo
```

Then ask Codex to use `$sp-codex-select` or mention `sp-codex-select` in the prompt.
