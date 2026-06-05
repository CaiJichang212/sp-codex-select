# Optional patch for Superpowers `subagent-driven-development/SKILL.md`

Insert this section before implementation dispatch:

```md
## Cost-aware model routing

Before every subagent dispatch, use `sp-codex-select` to select the subagent category/model.

For each task, produce:
Task, Role, Score, Tier, Agent, Model, Reasoning, Sandbox, Fallback, Reason.

If Codex custom agents are available, spawn the selected `agent_type` such as `spc_quick`, `spc_spark`, `spc_standard`, `spc_deep`, `spc_spec_reviewer`, `spc_quality_reviewer`, or `spc_final_verifier`.

If custom agents are unavailable, include the selected model and reasoning effort in the worker prompt.

Escalate one tier on BLOCKED due to reasoning/design/debugging uncertainty, correctness-related DONE_WITH_CONCERNS, failed quality review, or repeated spec-review failure. Never retry the same prompt on the same tier after a material failure.
```

A no-fork alternative is to append `assets/AGENTS.md-snippet.md` to the target project's `AGENTS.md`.
