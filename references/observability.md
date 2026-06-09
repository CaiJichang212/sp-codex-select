# Observability and evaluation

Record one JSONL object for every dispatched task after route selection and final outcome.

## JSONL schema

Required fields:

- `task_id`: task or plan item id.
- `role`: routed role.
- `tier`: selected tier such as `T1`, `T4`, `R2`, or `R3`.
- `agent`: selected Codex custom agent.
- `model`: selected model id.
- `score`: numeric complexity score.
- `status`: final worker status such as `DONE`, `BLOCKED`, or `DONE_WITH_CONCERNS`.
- `review_pass`: boolean review result.
- `tests_pass`: boolean test result.
- `escalated`: boolean indicating whether the task required a stronger tier.

Example:

```json
{"task_id":"T3","role":"implementer","tier":"T2","agent":"spc_spark","model":"gpt-5.3-codex-spark","score":5,"status":"DONE","review_pass":true,"tests_pass":true,"escalated":false}
```

## Local analysis

Run:

```bash
python3 scripts/analyze_routes.py observability/routes.jsonl
```

The analyzer reports route count, tier counts, review failure rate, test failure rate, escalation rate, and false-cheap candidates.

## Pilot calibration rule

During Pilot, inspect route records before changing thresholds. Increase tier for task classes with repeated review failures, test failures, or escalations. Move a task class down only when tests and review consistently pass without rework.
