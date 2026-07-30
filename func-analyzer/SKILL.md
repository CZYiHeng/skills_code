---
name: func-analyzer
description: >-
  [CHAIN POSITION: Phase 1 of code-formatter. Do NOT call directly — use $code-formatter instead.]
  Function analyzer for existing code. Reads source code, extracts function signatures,
  builds a call graph, and determines each function's ROLE, DEPENDS_ON, IN, OUT, OWNS_FIELDS,
  SIDE, ERRORS, and LOG by analyzing the actual implementation.
  Produces a structured function inventory for header-injector to consume.
  Supports Python, JavaScript/TypeScript, C/C++, Java.
---

# Func-Analyzer — Existing Code Function Analyzer

Analyze existing code to extract the contract information that will become structured function headers.
You do NOT write or modify code — you only read and analyze, producing a function inventory.

## Chain Position

```
code-formatter orchestrator
  └─ Phase 1: func-analyzer (YOU)    → function inventory
  └─ Phase 2: header-injector        → generate + inject structured headers
```

## Input

Source code in any supported language. May be:
- A single file
- Multiple files
- A directory (recursive)
- Pasted code snippet

The scope (single file vs directory) determines call-graph tracking depth:
- **Single file** → track calls within the same file only
- **Directory** → scan all source files first, build a function-name → file-location index, then track cross-file calls

## Analysis Workflow

### Step 1: Extract Function Inventory

Parse function signatures from the source code. Identify by language-specific patterns:

| Language | Function Definition Patterns |
|---|---|
| Python | `def name(...)` / `async def name(...)` |
| JavaScript | `function name(...)` / `const name = (...) =>` / `name(...) {` (method) |
| TypeScript | Same as JS + `function name(...): RetType` |
| C | `ret_type name(...)` (top-level, not macro) |
| C++ | Same as C + `ret_type ClassName::name(...)` (method) |
| Java | `ret_type name(...)` (inside class), `public/private/protected` modifiers |

For each function, record:
- Function name
- Parameters (name, type if annotated, default value)
- Return type (if annotated)
- Line range (start-end)
- Whether it has an existing docstring/comment

### Step 2: Build Call Graph

Scan each function body for calls to other functions **within the same codebase**:

- **Single file scope**: track calls to other functions defined in the same file
- **Directory scope**: first scan ALL source files to build a global function index `function_name → file_path`, then track cross-file calls

Only record calls to functions that exist in the codebase. Ignore:
- Standard library calls (`print`, `len`, `open`, `Math.floor`, etc.)
- Third-party library calls (`pd.read_csv`, `requests.get`, etc.)
- Built-in language constructs

Output: for each function, a `DEPENDS_ON` list of upstream function names.

### Step 3: Analyze Each Function's 8-Field Contract

For each function, determine the 8 header fields by analyzing its actual implementation:

#### ROLE — Business Responsibility

Infer from:
- Function name (verb + noun pattern)
- Primary return value or output
- Context within the call graph

Write in business language, one line.

**Example**: `read_file` → "读取 CSV/Excel 文件为 DataFrame"

#### DEPENDS_ON — Upstream Functions

From the call graph built in Step 2. List function names this function calls.

**Example**: `DEPENDS_ON: [read_file, filter_rows]`

If no upstream dependencies: `DEPENDS_ON: []`

#### IN — Input Parameters

Read from the function signature. For each parameter:
- Name
- Type (from annotation or inferred from usage)
- Business meaning (inferred from how it's used in the body)

**Example**:
```
IN:
  path: Path — 输入文件路径
```

#### OUT — Return Value

Analyze all `return` statements in the function body:
- Return type (from annotation or inferred from expression)
- Business meaning of the returned value
- `None` return semantics if applicable

**Example**:
```
OUT:
  pd.DataFrame — 文件内容
```

If the function has no `return` (void): `OUT: None`

#### OWNS_FIELDS — Owned Fields

Scan the function body for fields that this function:
- **Creates** — assigns a new field/key/column (`df['new_col'] = ...`, `dict['key'] = ...`, `obj.field = ...`)
- **Normalizes** — transforms or cleans a field value (`df['col'] = df['col'].str.lower()`)
- **Validates** — checks and potentially rejects based on field value
- **Persists** — writes a field to DB/file/external store

Only record **business fields**, not:
- Temporary variables (`result`, `temp`, `buf`)
- Loop counters (`i`, `idx`)
- Internal state (`self._cache`)

**Example**: `OWNS_FIELDS: [cleaned_data, duplicate_count]`

If the function owns no fields (read-only helper): `OWNS_FIELDS: []`

#### SIDE — Side Effects

Scan the function body for:
- **Database operations**: INSERT, UPDATE, DELETE, SQL execution, ORM save
- **File I/O**: file write, file delete, directory creation
- **External calls**: HTTP request, API call, message queue publish
- **Stdout/stderr output**: `print()`, `console.log()`, `fprintf(stderr, ...)`
- **Subprocess**: `os.system()`, `subprocess.run()`, `exec()`

Describe concisely. If none: `SIDE: None`

**Examples**:
- `SIDE: None；只读文件` (reads a file but doesn't modify anything)
- `SIDE: file write (output_path)` (writes to a file)
- `SIDE: stdout (print statistics)` (prints to stdout)
- `SIDE: DB INSERT (employees table)` (inserts into DB)

#### ERRORS — Error Handling

Scan for:
- `raise` / `throw` statements
- `try/except` / `try/catch` blocks
- Error code returns (`return -1`, `return None` on failure)
- Fallback behavior (default values, empty results)

Describe the error semantics concisely.

**Examples**:
- `ERRORS: 不支持的文件格式抛 ValueError`
- `ERRORS: 找不到基线时返回 None，不抛异常`
- `ERRORS: None` (no error handling, no exceptions)
- `ERRORS: DB 异常向上传播；重复键返回 None`

#### LOG — Recommended Logging Strategy

Describe the **recommended** structured logging for this function, based on its ROLE, IN, OUT, SIDE, and ERRORS — even if the code currently only uses `print()` or has no logging at all.

Follow the func-logger severity strategy:

| Stage | Level | When |
|---|---|---|
| IN | INFO | Key inputs for tracing |
| OUT | INFO | Key outputs or result summaries |
| MAP (single) | INFO | Business-critical field mappings |
| MAP (batch) | DEBUG | Bulk mappings, per-row details |
| ERR (recoverable) | WARNING | Fallback, skip, retry |
| ERR (fatal) | ERROR | Operation aborts |

Format: `LOG: <stage> <level> (what to log); ...`

**Examples**:
- `LOG: IN INFO (file path); ERR ERROR (unsupported format)`
- `LOG: OUT INFO (removed count); MAP INFO (duplicate/na count)`
- `LOG: IN INFO (account_id, target_date); OUT INFO (baseline_found, snapshot_date); ERR ERROR (DB exception)`

If the function is too trivial to need logging: `LOG: None`

### Step 4: Output Function Inventory

Produce a structured inventory for header-injector to consume:

```
FUNCTION INVENTORY
══════════════════

File: data_process.py
Language: Python

1. read_file(path: Path) -> pd.DataFrame
   ROLE:         读取 CSV/Excel 文件为 DataFrame
   DEPENDS_ON:   []
   IN:           path: Path — 输入文件路径
   OUT:          pd.DataFrame — 文件内容
   OWNS_FIELDS:  []
   SIDE:         None；只读文件
   ERRORS:       不支持的文件格式抛 ValueError
   LOG:          IN INFO (file path); ERR ERROR (unsupported format)

2. clean(df: DataFrame, drop_dup: bool, drop_na: bool) -> DataFrame
   ROLE:         对 DataFrame 去重去空
   DEPENDS_ON:   []
   IN:           df: DataFrame — 原始数据; drop_dup: bool — 是否去重; drop_na: bool — 是否去空
   OUT:          DataFrame — 清洗后的数据
   OWNS_FIELDS:  []
   SIDE:         stdout (print statistics)
   ERRORS:       None
   LOG:          OUT INFO (removed count); MAP INFO (duplicate/na count)

3. ...
```

## Analysis Rules

- **Read-only**: do not modify any code.
- **LOG is aspirational**: describe recommended structured logging, not current `print()` behavior.
- **DEPENDS_ON scope**: only record calls to functions in the same codebase (same file or same directory), not standard library or third-party calls.
- **OWNS_FIELDS**: only record business fields, not temporary variables.
- **SIDE**: `print()` / `console.log()` counts as a side effect (stdout write). Reading a file does not count as a side effect unless it modifies the file.
- **Trivial functions**: even one-line getters must be analyzed — at minimum provide ROLE and IN/OUT.
- **Ambiguity**: if a function's behavior is unclear (obfuscated, minified, dynamically dispatched), note the uncertainty in the inventory rather than guessing.
- **Business language**: write ROLE, IN, OUT, SIDE, ERRORS descriptions in the user's language (Chinese if the codebase uses Chinese comments/variables, English otherwise).