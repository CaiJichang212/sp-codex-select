# Observability and evaluation

Append one JSONL record per routed task:

```json
{"task_id":"T3","role":"implementer","tier":"T2","agent":"spc_spark","model":"gpt-5.3-codex-spark","score":5,"status":"DONE","review_pass":true,"tests_pass":true,"escalated":false,"elapsed_sec":93}
```

Use 50-200 task outcomes to tune thresholds:

- increase tier for task classes with repeated review/test failures;
- decrease tier only when tests and review consistently pass without rework;
- keep high-risk review on stronger models even if implementation succeeds cheaply;
- track false-cheap cases separately: cheap first call but expensive total rework.
