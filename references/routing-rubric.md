# sp-codex-select routing rubric

The router uses a conservative cost-performance cascade.

## Dimensions

Score from 0 to 3 unless noted:

- `file_scope`: explicit file count and cross-package breadth.
- `diff_size`: expected size or rewrite breadth.
- `ambiguity`: how much behavior/design must be inferred.
- `integration`: number and risk of system boundaries.
- `risk`: API/data/auth/security/rollback impact.
- `verification`: 0 for exact tests, 1 for indirect checks, 2 for unclear/flaky checks.

## Hard flags

Any hard flag routes implementation to `spc_deep`:

- auth/security/permissions/secrets/payment/privacy;
- schema/migration/destructive/data integrity/rollback;
- concurrency/races/distributed consistency/idempotency;
- public API/backward compatibility/SDK compatibility;
- broad architecture/refactor/plugin extension point;
- unclear root cause or a previous lower-tier failure.

## Tier mapping

- Unknown files, no hard flag: `spc_explorer` first.
- Score 0-2: `spc_quick`.
- Score 3-6: `spc_spark`.
- Score 7-10: `spc_standard`.
- Score 11+ or hard flag: `spc_deep`.

Review routing is intentionally stronger than implementation routing.
