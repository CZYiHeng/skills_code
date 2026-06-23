---
name: func-logger
description: >-
  [CHAIN POSITION: Phase 4 of dev-flow. Do NOT call directly — use $dev-flow instead.]
  Structured function-level logging with severity-aware level strategy.
  Reads each function header/docstring, especially ROLE, IN, OUT, OWNS_FIELDS, SIDE, ERRORS, and LOG,
  then adds or updates structured logs using the format: 业务动作名 | 阶段(IN/MAP/ERR/OUT) | key=value.
  IN/OUT use INFO, key business MAP uses INFO, batch/details use DEBUG, recoverable errors use WARNING, fatal errors use ERROR.
  Updates the function header LOG section when logging behavior changes.
---

# Func-Logger — Structured Business Logging

Add structured logs that match the function header contract. The function header `LOG` section and the actual log statements must stay consistent.

## Chain Position

```
dev-flow orchestrator
  └─ Phase 1: req-analyst            → temporary @business
  └─ Phase 2: arch-designer          → temporary architecture plan
  └─ Phase 3: func-contract          → function headers/docstrings + code
  └─ Phase 4: func-logger (YOU)      → logs + LOG header sections
```

## Source Of Truth

Read the function header/docstring:

- `ROLE` gives the business action name.
- `IN` identifies key inputs to log.
- `OUT` identifies result summaries to log.
- `OWNS_FIELDS` identifies important mappings.
- `SIDE` identifies persistence/export/external-call logs.
- `ERRORS` identifies warning/error branches.
- `LOG` records the intended logging behavior and must be updated if logs change.

## Log Format

```
业务动作名 | 阶段 | key1=value1, key2=value2
```

Stages: `IN`, `MAP`, `ERR`, `OUT`

## Severity Strategy

| Stage | Level | Rule |
|---|---|---|
| IN | `INFO` | Key identifiers, counts, dates, target paths, safe request parameters |
| OUT | `INFO` | Counts, IDs, summaries, status |
| MAP single | `INFO` | Key business field mapping or important derived value |
| MAP batch/detail | `DEBUG` | Bulk mapping summaries, per-row details, internal state |
| MAP skipped | `INFO` | Skipped work that changes output |
| ERR recoverable | `WARNING` | Fallback, skip, retry, partial success |
| ERR fatal | `ERROR` | Operation aborts or caller must handle failure |

## Examples

```python
logger.info("余额基线查找 | IN | account_id=%s, target_date=%s", account_id, target_date)
logger.info("余额基线查找 | OUT | baseline_found=%s, snapshot_date=%s", baseline is not None, snapshot_date)
logger.warning("余额快照计算 | ERR | 汇率缺失，降级为原逻辑 currency=%s, month=%s", currency, month)
logger.error("余额基线新增 | ERR | DuplicateSnapshot account_id=%s, snapshot_date=%s", account_id, snapshot_date)
```

## What Not To Log

- Secrets, passwords, tokens, credentials, cookies, authorization headers.
- Full PII or full file contents.
- Per-row logs at INFO in tight loops.
- Large payloads; log counts, IDs, and summaries instead.

## Delivery Checklist

- [ ] Logs match each function's `LOG` header section.
- [ ] `IN` and `OUT` are covered for important functions.
- [ ] `SIDE` effects have success/failure logs.
- [ ] `ERRORS` branches use WARNING or ERROR correctly.
- [ ] Sensitive data is not logged.
- [ ] Header `LOG` section is updated when log behavior changes.