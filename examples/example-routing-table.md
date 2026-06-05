| task_id | role | score | tier | agent_type | model | effort | fallback | confidence | flags |
|---|---|---:|---|---|---|---|---|---|---|
| task-line-1 | implementer | 1 | T1 | spc_quick | gpt-5.4-mini | low | spc_spark | medium | - |
| task-line-2 | implementer | 3 | T2 | spc_spark | gpt-5.3-codex-spark | medium | spc_standard | medium | - |
| task-line-3 | implementer | 8 | T4 | spc_deep | gpt-5.5 | high | spc_final_verifier | low | architecture, data, security |

## Dispatch headers

### task-line-1
```text
[sp-codex-select]
tier: T1
category: quick
agent_type: spc_quick
model: gpt-5.4-mini
model_reasoning_effort: low
sandbox_mode: workspace-write
fallback_agent_type: spc_spark
complexity_score: 1
confidence: medium
hard_flags: none
rationale: file_scope=1; diff_size=0; ambiguity=0; integration=0; risk=0; verification=0; role_adjust=0
rule: use the selected cheapest-capable tier; escalate rather than guessing.
[/sp-codex-select]
```

### task-line-2
```text
[sp-codex-select]
tier: T2
category: spark
agent_type: spc_spark
model: gpt-5.3-codex-spark
model_reasoning_effort: medium
sandbox_mode: workspace-write
fallback_agent_type: spc_standard
complexity_score: 3
confidence: medium
hard_flags: none
rationale: file_scope=1; diff_size=0; ambiguity=0; integration=1; risk=1; verification=0; role_adjust=0
rule: use the selected cheapest-capable tier; escalate rather than guessing.
[/sp-codex-select]
```

### task-line-3
```text
[sp-codex-select]
tier: T4
category: deep
agent_type: spc_deep
model: gpt-5.5
model_reasoning_effort: high
sandbox_mode: workspace-write
fallback_agent_type: spc_final_verifier
complexity_score: 8
confidence: low
hard_flags: architecture, data, security
rationale: file_scope=1; diff_size=0; ambiguity=1; integration=2; risk=3; verification=1; role_adjust=0
rule: use the selected cheapest-capable tier; escalate rather than guessing.
[/sp-codex-select]
```
