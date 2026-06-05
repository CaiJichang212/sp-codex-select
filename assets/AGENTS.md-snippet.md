## sp-codex-select model router

When using Superpowers `subagent-driven-development`, Codex `spawn_agent`, or parallel code-agent delegation, route every subtask through `sp-codex-select` before dispatch.

Required behavior:

1. Create a Model Routing Table row for each subtask: score, tier, agent_type, model, reasoning effort, sandbox, fallback, and reason.
2. Prefer Codex custom agents by name (`spc_quick`, `spc_spark`, `spc_standard`, `spc_deep`, reviewers) rather than generic workers.
3. Unknown affected files should first go to `spc_explorer` unless the task already has a hard escalation flag.
4. Use the cheapest-capable tier expected to pass implementation + tests + review, not the cheapest first call.
5. Implementers may be cheap; reviewers should be stronger. Use `spc_spec_reviewer` for spec compliance and `spc_quality_reviewer` for correctness/safety/data/security/concurrency concerns.
6. On BLOCKED due to reasoning/design/debugging uncertainty, failed quality review, or repeated spec-review failure, escalate one tier. Do not retry the same prompt on the same tier after a material failure.
7. For high-risk or final branch acceptance, use `spc_final_verifier` read-only.
