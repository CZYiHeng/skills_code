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
  SELF-CONTAINED: Phase 1-4 content (requirement analysis, architecture design,
  function contracts, logging) is inlined here as the single source of truth —
  there are no separate phase skills to load.
---

# Dev-Flow — Development Workflow Orchestrator

You are the master orchestrator. Every code generation or modification request goes through you.

Core rule: **all durable design information belongs in function headers/docstrings.** Temporary `@business` and `@architecture` blocks may be shown during discussion and confirmation, but the committed code must not rely on standalone file-level architecture blocks.

## Function Header Standard

<!-- SSOT: 8 字段函数头标准 v1（Python）— 四语言模板权威源 header-injector，修改时同步所有副本 -->

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

> 本章已合并原 `req-analyst` 全部内容，是 Phase 1 的唯一权威源。

### 评估维度

| Dimension | Check | Example |
|---|---|---|
| name | What is this business process called? | 员工花名册导入 |
| purpose | What business problem does it solve? | 将 HR 花名册导入系统 |
| input | What is the input data shape? | Excel 表含姓名/工号/部门 |
| fields | What are the key fields and meanings? | 姓名→name, 工号→employee_id |
| output | What is the output used for? | 标准化员工记录 |
| flow | What is the high-level data flow? | 文件→解析→清洗→写入 |
| complexity | How complex is the task? | simple / medium / complex |

任一高影响维度缺失 → 问一轮聚焦问题再继续。不要问实现细节，除非它影响业务行为。

### 复杂度判定

| Level | Criteria | Downstream behavior |
|---|---|---|
| `simple` | ≤2 flow steps, ≤3 key fields, one function is enough | Skip expanded architecture; one function header contract |
| `medium` | 3-4 flow steps or multiple functions | Full pipeline |
| `complex` | 5+ steps, branches, merges, multiple outputs, risky side effects | Full pipeline with detailed DAG |

### 步骤

1. Assess business context completeness（用上面的维度表）。
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

Do not proceed without explicit user approval. Never write code in this phase.

## Phase 2: Architecture Design

> 本章已合并原 `arch-designer` 全部内容，是 Phase 2 的唯一权威源。

Use complexity to decide how much design is needed:

| complexity | Action |
|---|---|
| `simple` | Skip expanded architecture. Create one function header with complete local contract. |
| `medium` / `complex` | Produce a temporary architecture plan with function decomposition and DAG dependencies. |

### 分解原则

Use one function per distinct business operation or data transformation. Keep I/O, parsing, validation, computation, persistence, and export responsibilities separate when they are non-trivial.

### 字段归属

For each field that is created, normalized, validated, persisted, or materially transformed, assign exactly one owning function.

### 依赖拓扑

Use `depends_on` to declare upstream functions. Support:

- Linear chain: A → B → C
- Branch: A → B and A → C
- Merge: A + B → C

### 输出临时架构

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

Show the temporary architecture to the user for confirmation.

### 交接：架构字段 → 函数头

After user confirmation, copy each architecture item into that function's header/docstring:

- `role` → `ROLE`
- `depends_on` → `DEPENDS_ON`
- `in` → `IN`
- `out` → `OUT`
- `owns_fields` → `OWNS_FIELDS`
- `side` → `SIDE`
- `errors` → `ERRORS`

Do not leave the architecture plan as the only durable documentation in code.

### 设计原则

- Flow-driven: each distinct transformation is a function.
- Field ownership is mandatory for mutable or derived fields.
- Dependencies are explicit through `DEPENDS_ON`.
- Function headers are the final architecture record.
- Keep functions focused and testable.

## Phase 3: Code Generation

> 本章已合并原 `func-contract` 全部内容，是 Phase 3 的唯一权威源。

### 步骤

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

### 头字段规则

- Copy each architecture field into the matching header section.
- Use `OWNS_FIELDS: []` for read-only helper functions that own no fields.
- Use `SIDE: None` for pure/read-only functions.
- Use `ERRORS` to document exceptions, fallback behavior, and meaningful `None` returns.
- Use `LOG` to summarize logging intent even before Phase 4 inserts concrete log statements.
- Do not create file-level `@business` or `@architecture` as permanent code documentation.

### 命名

Intermediate variables must reveal the transformation chain:

```python
raw_headers -> cleaned_headers -> header_map
```

Never reuse one variable name for different semantic states.

### 交付清单

- [ ] Every generated/modified function has a structured header/docstring.
- [ ] Header `ROLE/DEPENDS_ON/IN/OUT/OWNS_FIELDS/SIDE/ERRORS/LOG` matches implementation.
- [ ] Every mutable or derived field has exactly one owning function.
- [ ] `DEPENDS_ON` names real upstream functions.
- [ ] Variable names reveal the data chain.
- [ ] No stale standalone architecture block is left as the only source of truth.

## Phase 4: Logging

> 本章已合并原 `func-logger` 全部内容，是 Phase 4 的唯一权威源。

Add structured logs with level-appropriate severity. Logging intent must also be summarized in the function header `LOG` section.

### 头的哪些字段决定日志

Read the function header/docstring:

- `ROLE` gives the business action name.
- `IN` identifies key inputs to log.
- `OUT` identifies result summaries to log.
- `OWNS_FIELDS` identifies important mappings.
- `SIDE` identifies persistence/export/external-call logs.
- `ERRORS` identifies warning/error branches.
- `LOG` records the intended logging behavior and must be updated if logs change.

### 格式与级别

<!-- SSOT: 日志级别表 v1 — 权威源：本文件 Phase 4（原 func-logger 已并入），修改时同步所有副本 -->

Log format: `业务动作名 | 阶段 | key1=value1, key2=value2`

Stages: `IN`, `MAP`, `ERR`, `OUT`

| Stage | Level | Rule |
|---|---|---|
| IN | `INFO` | Key identifiers, counts, dates, target paths, safe request parameters |
| OUT | `INFO` | Counts, IDs, summaries, status |
| MAP single | `INFO` | Key business field mapping or important derived value |
| MAP batch/detail | `DEBUG` | Bulk mapping summaries, per-row details, internal state |
| MAP skipped | `INFO` | Skipped work that changes output |
| ERR recoverable | `WARNING` | Fallback, skip, retry, partial success |
| ERR fatal | `ERROR` | Operation aborts or caller must handle failure |

### 示例

```python
logger.info("余额基线查找 | IN | account_id=%s, target_date=%s", account_id, target_date)
logger.info("余额基线查找 | OUT | baseline_found=%s, snapshot_date=%s", baseline is not None, snapshot_date)
logger.warning("余额快照计算 | ERR | 汇率缺失，降级为原逻辑 currency=%s, month=%s", currency, month)
logger.error("余额基线新增 | ERR | DuplicateSnapshot account_id=%s, snapshot_date=%s", account_id, snapshot_date)
```

### 禁止记录

- Secrets, passwords, tokens, credentials, cookies, authorization headers.
- Full PII or full file contents.
- Per-row logs at INFO in tight loops.
- Large payloads; log counts, IDs, and summaries instead.

### 交付清单

- [ ] Logs match each function's `LOG` header section.
- [ ] `IN` and `OUT` are covered for important functions.
- [ ] `SIDE` effects have success/failure logs.
- [ ] `ERRORS` branches use WARNING or ERROR correctly.
- [ ] Sensitive data is not logged.
- [ ] Header `LOG` section is updated when log behavior changes.

### Post-Step: Header Consistency Self-Check

<!-- SSOT: 7 规则一致性检查 v1 — 权威源 flow-tracer Section -1，修改时同步所有副本 -->

After logging is added, run the 7-rule consistency check on every generated function. Any STALE or MISSING issue must be fixed before declaring the task complete — a freshly written header that already disagrees with its body is a bug, not a drift.

| # | Rule | What it checks | STALE（头多声明了） | MISSING（头少声明了） |
|---|---|---|---|---|
| 1 | `OWNS_FIELDS_MATCH` | body 创建/修改/持久化的字段 vs `OWNS_FIELDS` | 声明的字段 body 没操作 | body 操作了未声明的字段 |
| 2 | `DEPENDS_ON_MATCH` | body 调用的函数 vs `DEPENDS_ON` | 声明的依赖没调用 | body 调用了未声明的**结构化**函数 |
| 3 | `SIDE_MATCH` | body 副作用 vs `SIDE` | 声明的副作用没执行 | body 有 DB/file/API/**stdout** 写操作但 `SIDE: None` |
| 4 | `IN_MATCH` | 函数签名参数 vs `IN` 描述 | 描述的参数不在签名里 | 签名参数没描述 |
| 5 | `OUT_MATCH` | 实际 `return` vs `OUT` 声明 | 声明的返回形状从没返回 | 返回了未声明的形状 |
| 6 | `LOG_MATCH` | 实际日志语句 vs `LOG` | 描述的日志没有对应语句 | 有日志语句但 `LOG` 没描述 |
| 7 | `ERRORS_MATCH` | `try/except/raise` vs `ERRORS` | 描述的异常没有对应代码 | body 抛出/处理了未声明的异常 |

状态：✅ OK — 头与实现一致；⚠️ STALE — 头声明了代码不做的事，更新或删除声明；❌ MISSING — 代码做了头没声明的事，补声明。

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

<!-- SSOT: 7 规则一致性检查 v1 — 权威源 flow-tracer Section -1，修改时同步所有副本 -->

Before finishing, run the 7-rule Header Consistency Check on every changed function:

| # | Rule | What it checks | STALE（头多声明了） | MISSING（头少声明了） |
|---|---|---|---|---|
| 1 | `OWNS_FIELDS_MATCH` | body 创建/修改/持久化的字段 vs `OWNS_FIELDS` | 声明的字段 body 没操作 | body 操作了未声明的字段 |
| 2 | `DEPENDS_ON_MATCH` | body 调用的函数 vs `DEPENDS_ON` | 声明的依赖没调用 | body 调用了未声明的**结构化**函数 |
| 3 | `SIDE_MATCH` | body 副作用 vs `SIDE` | 声明的副作用没执行 | body 有 DB/file/API/**stdout** 写操作但 `SIDE: None` |
| 4 | `IN_MATCH` | 函数签名参数 vs `IN` 描述 | 描述的参数不在签名里 | 签名参数没描述 |
| 5 | `OUT_MATCH` | 实际 `return` vs `OUT` 声明 | 声明的返回形状从没返回 | 返回了未声明的形状 |
| 6 | `LOG_MATCH` | 实际日志语句 vs `LOG` | 描述的日志没有对应语句 | 有日志语句但 `LOG` 没描述 |
| 7 | `ERRORS_MATCH` | `try/except/raise` vs `ERRORS` | 描述的异常没有对应代码 | body 抛出/处理了未声明的异常 |

状态：✅ OK — 头与实现一致；⚠️ STALE — 头声明了代码不做的事，更新或删除声明；❌ MISSING — 代码做了头没声明的事，补声明。

Any STALE or MISSING result must be resolved before the task is declared complete — either update the header to match the new implementation, or revert the implementation if it drifted from the confirmed design. Then:

- Confirm every changed field has exactly one owning function.
- Confirm logs do not expose secrets.
- Run relevant tests/checks when available.

---

## Rules

- Function headers/docstrings are the durable source of truth.
- Temporary `@business` and `@architecture` blocks are for conversation and confirmation only.
- **This skill is self-contained** — Phase 1-4 content is inlined above. Do not expect separate phase skills to be loaded.
- Never write code before Phase 1 confirmation.
- Do not scatter architecture across file-level comments, markdown blocks, and function headers.
- Keep business language throughout.
- Skip expanded architecture for simple tasks.
- For medium/complex tasks, preserve DAG dependencies through `DEPENDS_ON`.
- Update headers whenever implementation behavior changes.
- INFO logs tell the business trace; DEBUG logs hold detail; WARNING/ERROR represent recoverable/fatal errors.
- `print()` / `console.log()` counts as a side effect (stdout write) and must be declared in `SIDE`.