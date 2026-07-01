---
name: dev-flow
description: >-
  Master orchestrator for the full development workflow — both NEW code and MODIFY existing code.
  When the user requests ANY code generation or modification, invoke $dev-flow FIRST.
  Orchestrates requirement analysis, architecture design, function contracts, implementation, and logging.
  Final code must place business, architecture, contract, dependency, side-effect, error, and logging intent in each function header/docstring, not in standalone file-level @business/@architecture blocks.
  Detects existing function-header contracts to switch between "create mode" and "modify mode".
  Evaluates task complexity to skip architecture expansion for simple tasks.
  Supports non-linear data-flow topologies via depends_on DAG.
  This is the ONLY entry point for code generation and modification.
---

# Dev-Flow — Development Workflow Orchestrator

You are the master orchestrator. Every code generation or modification request goes through you.

Core rule: **all durable design information belongs in function headers/docstrings.** Temporary `@business` and `@architecture` blocks may be shown during discussion and confirmation, but the committed code must not rely on standalone file-level architecture blocks.

## Function Header Standard

Every generated or modified function must carry a structured header/docstring containing the relevant local contract.

Use the language-native style when possible:

```python
def function_name(...):
    """
    ROLE:
      <一句话业务职责>

    DEPENDS_ON:
      [upstream_function_a, upstream_function_b]

    IN:
      <输入类型和业务含义>

    OUT:
      <输出类型和业务含义>

    OWNS_FIELDS:
      [field_a, field_b]

    SIDE:
      <INSERT/UPDATE/DELETE/外部调用/文件写入等；无副作用写 None>

    ERRORS:
      <异常、降级或 None 返回语义>

    LOG:
      IN/OUT 使用 INFO；关键业务 MAP 使用 INFO；批量细节使用 DEBUG；可恢复异常 WARNING；中断性异常 ERROR。
    """
```

Keep function headers concise but complete. If a field is owned, a side effect exists, a fallback exists, or a downstream function depends on this result, it must be stated in the relevant function header.

## Mode Detection

Before starting, check the target code:

| Detected | Mode | Behavior |
|---|---|---|
| No structured function headers | **CREATE** | Full or simplified pipeline |
| Has structured function headers with `ROLE` / `DEPENDS_ON` / `OWNS_FIELDS` | **MODIFY** | Impact analysis → modify → update headers |

If old standalone `@business` or `@architecture` blocks exist, treat them as legacy context. Migrate their durable information into function headers while making the requested change.

---

# CREATE MODE

## Phase 1: Requirement Analysis

Act as `req-analyst`:

1. Assess business context completeness.
2. If unclear → ask clarifying questions, do not proceed.
3. If clear → draft a temporary `@business` block for confirmation only:

```
@business:
  name:       <业务名称>
  purpose:    <业务目的>
  input:      <输入数据结构和含义>
  fields:     <字段→含义映射>
  output:     <输出用途>
  flow:       <数据流向: A → B → C → D>
  complexity: <simple | medium | complex>
```

4. Request user confirmation:
   > 以上是我对需求的理解，是否正确？确认后继续。

Do not proceed without explicit user approval.

## Phase 2: Architecture Design

Use complexity to decide how much design is needed:

| complexity | Action |
|---|---|
| `simple` | Skip expanded architecture. Create one function header with complete local contract. |
| `medium` / `complex` | Produce a temporary architecture plan with function decomposition and DAG dependencies. |

For medium/complex tasks, design one function per distinct flow step:

```
@architecture:
  functions:
    - name:         <函数名，业务语言>
      role:         <一句话职责>
      depends_on:   [上游函数名列表]
      in:           <输入类型和含义>
      out:          <输出类型和含义>
      owns_fields:  [字段列表]
      side:         <副作用，无则 None>
      errors:       <异常/降级/None 语义，无则 None>
```

Show the temporary architecture to the user for confirmation. After confirmation, transfer each function's architecture into that function's header/docstring.

## Phase 3: Code Generation

For each function:

1. Write the full function header/docstring first.
2. Implement the function immediately below its header.
3. Keep function body focused; target ≤30 lines unless the language/framework requires otherwise.
4. Use pipeline-style names that show transformation stages.
5. Do not create or preserve standalone top-level `@business` / `@architecture` blocks as the source of truth.

Example:

```python
def find_effective_baseline(account_id: int, target_date: date) -> SnapshotOut | None:
    """
    ROLE:
      查找某账户在目标日期之前最近的一条余额基线。

    DEPENDS_ON:
      []

    IN:
      account_id: 账户 ID
      target_date: 查询截止日期

    OUT:
      SnapshotOut | None；None 表示无可用基线。

    OWNS_FIELDS:
      []

    SIDE:
      None；只读。

    ERRORS:
      找不到基线时返回 None，不抛异常。

    LOG:
      IN/OUT 使用 INFO；未找到基线使用 INFO；数据库异常使用 ERROR。
    """
```

## Phase 4: Logging

Add structured logs with level-appropriate severity. Logging intent must also be summarized in the function header `LOG` section.

| Stage | Default Level | When to use |
|---|---|---|
| IN | INFO | Key inputs for tracing |
| OUT | INFO | Key outputs or result summaries |
| MAP single | INFO | Business-critical field mappings |
| MAP batch/detail | DEBUG | Bulk mappings, per-row details, internal state |
| ERR recoverable | WARNING | Can continue with fallback/skip |
| ERR fatal | ERROR | Operation aborts or must be surfaced |

Log format: `业务动作名 | 阶段 | key=value`

### Post-Step: Header Consistency Self-Check

After logging is added, run the 7-rule consistency check defined in `flow-tracer` Section -1 on every generated function. Any STALE or MISSING issue must be fixed before declaring the task complete — a freshly written header that already disagrees with its body is a bug, not a drift.

The 7 rules: `OWNS_FIELDS_MATCH`, `DEPENDS_ON_MATCH`, `SIDE_MATCH`, `IN_MATCH`, `OUT_MATCH`, `LOG_MATCH`, `ERRORS_MATCH`. See `flow-tracer/SKILL.md` Section -1 for the full definition.

---

# MODIFY MODE

When target code already has structured function headers.

## Phase 1: Understand the Change

1. Read existing function headers/docstrings.
2. Identify the requested field, behavior, dependency, side effect, or error-policy change.
3. Summarize to user:
   > 当前代码处理的是【业务名/函数职责】，你希望修改【具体变更】，我来分析影响范围。

## Phase 2: Impact Analysis

1. Locate owning function by `OWNS_FIELDS`, `ROLE`, and implementation references.
2. Trace downstream by `DEPENDS_ON`.
3. Check affected `IN`, `OUT`, `SIDE`, `ERRORS`, and `LOG` sections.
4. Produce impact report:

```
IMPACT ANALYSIS: 修改 "<字段名/行为>"
═══════════════════════════════════
OWNER FUNCTION:
  <函数名>
  └─ OWNS_FIELDS: [受影响字段]
  └─ HEADER: 需要更新 ROLE/IN/OUT/SIDE/ERRORS/LOG 中的 <具体项>

DOWNSTREAM:
  └─ <函数名>: DEPENDS_ON=[OWNER]
     └─ 需验证: <具体验证点>

AFFECTED LOGS:
  grep "<关键词>"  ← 需同步更新
```

Show impact report. Do not modify until user confirms when the change is broad or behaviorally risky. For small obvious edits, proceed and clearly state the impact checked.

## Phase 3: Apply Changes

Update:

- Owning function implementation.
- Downstream functions that consume changed output or behavior.
- Each affected function header/docstring.
- Logs and error handling that mention changed fields or rules.

If legacy top-level `@business` / `@architecture` blocks exist, migrate only the relevant durable details into function headers and remove stale duplicated architecture comments when safe.

## Phase 4: Final Verification

Before finishing, run the 7-rule Header Consistency Check defined in `flow-tracer` Section -1 on every changed function:

| Rule | Check |
|---|---|
| `OWNS_FIELDS_MATCH` | body-operated fields vs declared `OWNS_FIELDS` |
| `DEPENDS_ON_MATCH` | body-called functions vs declared `DEPENDS_ON` |
| `SIDE_MATCH` | body side effects vs declared `SIDE` |
| `IN_MATCH` | signature params vs declared `IN` |
| `OUT_MATCH` | actual returns vs declared `OUT` |
| `LOG_MATCH` | log statements vs declared `LOG` |
| `ERRORS_MATCH` | `try/except/raise` vs declared `ERRORS` |

Any STALE or MISSING result must be resolved before the task is declared complete — either update the header to match the new implementation, or revert the implementation if it drifted from the confirmed design. Then:

- Confirm every changed field has exactly one owning function.
- Confirm logs do not expose secrets.
- Run relevant tests/checks when available.

---

## Rules

- Function headers/docstrings are the durable source of truth.
- Temporary `@business` and `@architecture` blocks are for conversation and confirmation only.
- Do not scatter architecture across file-level comments, markdown blocks, and function headers.
- Keep business language throughout.
- Skip expanded architecture for simple tasks.
- For medium/complex tasks, preserve DAG dependencies through `DEPENDS_ON`.
- Update headers whenever implementation behavior changes.
- INFO logs tell the business trace; DEBUG logs hold detail; WARNING/ERROR represent recoverable/fatal errors.