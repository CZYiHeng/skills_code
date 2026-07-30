# WorkBuddy Skill Chains

> Structured code development and documentation workflow for [WorkBuddy](https://www.codebuddy.cn/) — from requirement analysis to impact tracing, conversational incremental development, plus retrofitting headers onto existing code.

## What is this?

Two complementary skill chains plus a standalone conversational skill, all enforcing a **function-header-as-source-of-truth** discipline:

```
─── dev-flow chain (for NEW code) ───────────────────────────
dev-flow (master orchestrator — the ONLY entry point)
  ├─ Phase 1: req-analyst      → requirement analysis, temporary @business
  ├─ Phase 2: arch-designer    → function decomposition, DAG dependencies
  ├─ Phase 3: func-contract    → structured function headers + code
  └─ Phase 4: func-logger      → structured business logging
flow-tracer (standalone post-hoc analysis tool)

─── code-formatter chain (for EXISTING code) ────────────────
code-formatter (master orchestrator — the ONLY entry point)
  ├─ Phase 0: language detect + scope scan + confirm
  ├─ Phase 1: func-analyzer    → analyze existing code, extract 8-field contract
  ├─ Phase 2: header-injector  → generate + inject structured headers
  └─ Phase 3: consistency self-check (7 rules, self-contained)

─── req-to-code (standalone, conversational) ────────────────
req-to-code (self-contained — skeleton first, then fill)
  ├─ Round 1: skeleton (complete 8-field headers + placeholder bodies)
  ├─ Round 2+: incremental filling based on user feedback
  ├─ Direction changes: apply immediately, mark rework
  └─ Final round: full 7-rule consistency check
  Thinking discipline: thesis-driven (emerges through dialog) + 3 questions per proposal
```

**Core principle:** All durable architecture information lives in function headers/docstrings — not in standalone file-level blocks. The dev-flow chain creates headers alongside new code; the code-formatter chain retrofits headers onto existing code.

## Why?

- **Docs never drift from code** — the contract is *inside* the function, not in a separate wiki.
- **Impact analysis is deterministic** — trace any field change through `OWNS_FIELDS` and `DEPENDS_ON`.
- **Logging is consistent** — every function declares its logging intent in the `LOG` header section.
- **Works for new code AND modifications** — MODIFY mode reads existing headers, runs impact analysis, then applies changes.
- **Retrofit existing code** — code-formatter analyzes old code and injects structured headers without modifying logic.

## Install

### Option A: Clone directly

```bash
git clone https://github.com/<your-username>/skills_code.git
```

Then copy each skill folder into your WorkBuddy skills directory:

```
~/.workbuddy/skills/dev-flow/
~/.workbuddy/skills/req-analyst/
~/.workbuddy/skills/arch-designer/
~/.workbuddy/skills/func-contract/
~/.workbuddy/skills/func-logger/
~/.workbuddy/skills/flow-tracer/
~/.workbuddy/skills/code-formatter/
~/.workbuddy/skills/func-analyzer/
~/.workbuddy/skills/header-injector/
~/.workbuddy/skills/req-to-code/
```

### Option B: Upload via WorkBuddy UI

Open WorkBuddy → Skills Market → upload each skill folder's `SKILL.md`.

## Usage

### Start a new coding task

Simply describe what you want to build. WorkBuddy will invoke `$dev-flow` automatically:

```
> 帮我写一个员工花名册导入功能，输入是 Excel，需要清洗去重后写入数据库
```

The orchestrator will:
1. **req-analyst** — analyze the business context, produce a temporary `@business` block, and **ask you to confirm**.
2. **arch-designer** — design function decomposition with field ownership and DAG dependencies, and **ask you to confirm**.
3. **func-contract** — write each function with a structured header + implementation.
4. **func-logger** — add structured logs matching each function's `LOG` section.

### Modify existing code

```
> 把 find_effective_baseline 的 target_date 改成支持日期范围
```

If structured function headers are detected, dev-flow switches to **MODIFY mode**:
1. Reads existing headers.
2. Runs impact analysis (owner function → downstream consumers → affected logs).
3. Shows the impact report.
4. Applies changes and updates all affected headers.

### Trace data flow & impact

After code is written, use `flow-tracer` to analyze:

```
> 分析一下余额基线查找的数据流，如果改了 snapshot_date 字段会影响哪些函数？
```

Output includes:
- Module overview table
- Mermaid sequence diagrams per phase
- Log trace table with grep commands
- Field ownership table
- Impact analysis report

### Format existing code with structured headers

When you have existing code without structured headers, use `$code-formatter` to retrofit them:

```
> 帮我把 data_process.py 的代码格式化成有结构化函数头的
```

The orchestrator will:
1. **Phase 0** — detect language, scan functions, show scope summary, ask for confirmation.
2. **func-analyzer** — analyze each function's ROLE, DEPENDS_ON, IN, OUT, OWNS_FIELDS, SIDE, ERRORS, LOG.
3. **header-injector** — generate language-appropriate headers and inject into code.
4. **Phase 3** — run 7-rule consistency check to ensure headers match implementation.

Output: a new file `data_process_formatted.py` with structured headers, original file untouched.

Supports Python, JavaScript/TypeScript, C/C++, Java. Works on single files or entire directories.

### Build code iteratively with req-to-code

When requirements are fuzzy or evolving, use `$req-to-code` for conversational incremental development:

```
> 先搭个骨架，我要做一个 CSV 数据清洗工具，支持去重去空
```

Round 1 — the skill writes a minimal runnable skeleton (complete headers + placeholder bodies) and answers three questions (why this way / what's the downside / any conflicts):

```
骨架方案：read_file → clean_data → validate_rows → transform → write_output → main

为什么这样分：数据流驱动，经典 ETL 骨架
有什么缺点：假设单一文件输入；validate 和 clean 顺序可调
有没有冲突：无。OWNS_FIELDS 不重叠，DEPENDS_ON 线性无循环

ROUND 1 — 骨架
主旨：CSV 数据清洗工具，去重去空
函数数：6 | 头完整：6 | body 填充：0 | TODO：6
```

Round 2+ — say "继续" and the skill fills in bodies upstream-first, runs 7-rule consistency check on changed functions:

```
> 继续

ROUND 2 — 填充
主旨：CSV 数据清洗工具，去重去空
主旨对齐：✓
本轮填充：read_file, clean_data
一致性检查：2 checked, 0 STALE, 0 MISSING
```

Direction changes are applied immediately — affected functions revert to placeholders with `# TODO(round-N): rework`:

```
> 改成支持 JSON 输入

方向变更（round 3）
为什么改：输入格式从 CSV 改为 JSON
有什么缺点：read_file 和 transform 需要重写
有没有冲突：clean_data 和 validate_rows 不受影响
```

## Function Header Standard

Every generated or modified function carries a structured header:

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

| Field | Purpose |
|---|---|
| `ROLE` | One-line business responsibility |
| `DEPENDS_ON` | Upstream functions (forms a DAG) |
| `IN` | Input types and business meaning |
| `OUT` | Output type and business meaning |
| `OWNS_FIELDS` | Fields this function creates/normalizes/validates/persists |
| `SIDE` | Side effects (INSERT/UPDATE/DELETE/external call/file write); `None` if pure |
| `ERRORS` | Exception, fallback, or `None` return semantics |
| `LOG` | Logging intent summary |

## Logging Format

```
业务动作名 | 阶段 | key=value
```

| Stage | Level | When |
|---|---|---|
| `IN` | INFO | Key inputs for tracing |
| `OUT` | INFO | Key outputs or result summaries |
| `MAP` (single) | INFO | Business-critical field mappings |
| `MAP` (batch) | DEBUG | Bulk mappings, per-row details |
| `ERR` (recoverable) | WARNING | Fallback, skip, retry |
| `ERR` (fatal) | ERROR | Operation aborts |

## Skill Reference

### Dev-Flow Chain (new code)

| Skill | Phase | Invocation | Purpose |
|---|---|---|---|
| `dev-flow` | Orchestrator | `$dev-flow` (auto-triggered on code requests) | Mode detection, pipeline orchestration |
| `req-analyst` | Phase 1 | Internal only | Business context analysis, `@business` block |
| `arch-designer` | Phase 2 | Internal only | Function decomposition, DAG, field ownership |
| `func-contract` | Phase 3 | Internal only | Structured headers + code implementation |
| `func-logger` | Phase 4 | Internal only | Structured logging + `LOG` header updates |
| `flow-tracer` | Post-hoc | `$flow-tracer` | Data flow diagrams, log traces, impact analysis |

### Code-Formatter Chain (existing code)

| Skill | Phase | Invocation | Purpose |
|---|---|---|---|
| `code-formatter` | Orchestrator | `$code-formatter` | Language detection, scope, pipeline orchestration |
| `func-analyzer` | Phase 1 | Internal only | Analyze existing functions, extract 8-field contract |
| `header-injector` | Phase 2 | Internal only | Generate + inject structured headers, output new file |

### Req-To-Code (conversational incremental dev)

| Skill | Invocation | Purpose |
|---|---|---|
| `req-to-code` | `$req-to-code` | Conversational incremental development: skeleton first, then fill. Thesis-driven, 3 questions per proposal. Self-contained — no orchestrator, no sub-skills. |

> Phase skills are designed to be called **only** through their orchestrator. Do not invoke them directly. `req-to-code` is standalone — invoke directly.

## Project Structure

```
skills_code/
├── dev-flow/
│   ├── SKILL.md              # Master orchestrator (new code)
│   └── agents/openai.yaml
├── req-analyst/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── arch-designer/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── func-contract/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── func-logger/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── flow-tracer/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── code-formatter/
│   ├── SKILL.md              # Master orchestrator (existing code)
│   └── agents/openai.yaml
├── func-analyzer/
│   ├── SKILL.md              # Phase 1: analyze existing code
│   └── agents/openai.yaml
├── header-injector/
│   ├── SKILL.md              # Phase 2: inject structured headers
│   └── agents/openai.yaml
├── req-to-code/
│   ├── SKILL.md              # Conversational incremental dev (standalone)
│   └── agents/openai.yaml
├── data_process.py           # Example script (standalone CLI tool)
├── data_process_formatted.py # Example output (code-formatter result)
└── README.md
```

## Example: Full Flow

**User request:**
> 写一个 CSV 数据清洗工具，支持去重、去空、过滤

**Phase 1 — req-analyst output:**
```
@business:
  name:       CSV数据清洗
  purpose:    对 CSV/Excel 文件进行清洗去重去空并过滤
  input:      CSV/Excel 文件
  fields:     任意业务字段
  output:     清洗后的文件 + 统计摘要
  flow:       文件读取 → 过滤 → 清洗 → 输出
  complexity: medium
```

**Phase 2 — arch-designer output:**
```
@architecture:
  functions:
    - name: read_file
      role: 读取输入文件为 DataFrame
      depends_on: []
      ...
    - name: filter_rows
      role: 按条件过滤行
      depends_on: [read_file]
      ...
    - name: clean
      role: 去重去空
      depends_on: [filter_rows]
      ...
    - name: write_file
      role: 写入输出文件
      depends_on: [clean]
      ...
```

**Phase 3 — func-contract output:** (function headers + implementation)

**Phase 4 — func-logger output:** (structured logs added to each function)

## Compatibility

- **WorkBuddy** (CLI / VS Code extension / WeChat Mini Program)
- Skills are framework-agnostic — generated code follows the function header standard in any language

## License

MIT
