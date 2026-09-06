---
name: header-injector
description: >-
  [CHAIN POSITION: Phase 2 of code-formatter. Do NOT call directly — use $code-formatter instead.]
  Header generator and injector. Reads the function inventory from func-analyzer,
  generates language-appropriate structured headers (ROLE/DEPENDS_ON/IN/OUT/OWNS_FIELDS/SIDE/ERRORS/LOG),
  and injects them into the code without modifying business logic.
  Handles INSERT (no existing docstring), PREPEND (has plain docstring), FILL (partial structured header), SKIP (complete).
  Outputs to a new file <original>_formatted.<ext>.
---

# Header-Injector — Structured Header Generator & Injector

Generate structured function headers from the analysis inventory and inject them into existing code.
You do NOT modify business logic — you only add or update function header docstrings/comments.

## Chain Position

```
code-formatter orchestrator
  └─ Phase 1: func-analyzer          → function inventory
  └─ Phase 2: header-injector (YOU)  → structured headers + formatted code
```

## Input

The function inventory produced by `func-analyzer`. Each entry contains:

```
function_name(signature) -> return_type
  ROLE:         <business responsibility>
  DEPENDS_ON:   [upstream functions]
  IN:           <params and meaning>
  OUT:          <return value and meaning>
  OWNS_FIELDS:  [owned fields]
  SIDE:         <side effects; None if pure>
  ERRORS:       <error handling; None if no errors>
  LOG:          <recommended logging strategy>
```

Plus the original source code and the injection mode for each function (INSERT / PREPEND / FILL / SKIP).

## Workflow

### Step 1: Select Header Format (by language)

| Language | Format | Placement |
|---|---|---|
| Python | Triple-quote docstring `"""..."""` | After signature, before body |
| JavaScript / TypeScript | JSDoc block `/** ... */` | Before function declaration |
| C / C++ | Block comment `/* ... */` | Before function declaration |
| Java | Javadoc block `/** ... */` | Before method declaration |

### Step 2: Generate Header Content

<!-- SSOT: 8 字段函数头标准 v1（四语言模板）— 本文件是权威源，修改时同步 dev-flow / req-to-code / README 的副本 -->

For each function in the inventory, generate the 8-field header in the target language format.

#### Python

```python
def function_name(params) -> ReturnType:
    """
    ROLE:
      <business responsibility>

    DEPENDS_ON:
      [upstream_function_a, upstream_function_b]

    IN:
      <param: type — meaning>

    OUT:
      <type — meaning>

    OWNS_FIELDS:
      [field_a, field_b]

    SIDE:
      <side effects; None if pure>

    ERRORS:
      <error handling; None if no errors>

    LOG:
      <recommended logging strategy>
    """
```

#### JavaScript / TypeScript

```javascript
/**
 * ROLE:
 *   <business responsibility>
 *
 * DEPENDS_ON:
 *   [upstreamFunctionA, upstreamFunctionB]
 *
 * IN:
 *   <param: type — meaning>
 *
 * OUT:
 *   <type — meaning>
 *
 * OWNS_FIELDS:
 *   [fieldA, fieldB]
 *
 * SIDE:
 *   <side effects; None if pure>
 *
 * ERRORS:
 *   <error handling; None if no errors>
 *
 * LOG:
 *   <recommended logging strategy>
 */
function functionName(params) {
```

#### C / C++

```c
/*
 * ROLE:
 *   <business responsibility>
 *
 * DEPENDS_ON:
 *   [upstream_function_a, upstream_function_b]
 *
 * IN:
 *   <param: type — meaning>
 *
 * OUT:
 *   <type — meaning>
 *
 * OWNS_FIELDS:
 *   [field_a, field_b]
 *
 * SIDE:
 *   <side effects; None if pure>
 *
 * ERRORS:
 *   <error handling; None if no errors>
 *
 * LOG:
 *   <recommended logging strategy>
 */
int function_name(params) {
```

#### Java

```java
/**
 * ROLE:
 *   <business responsibility>
 *
 * DEPENDS_ON:
 *   [upstreamFunctionA, upstreamFunctionB]
 *
 * IN:
 *   <param: type — meaning>
 *
 * OUT:
 *   <type — meaning>
 *
 * OWNS_FIELDS:
 *   [fieldA, fieldB]
 *
 * SIDE:
 *   <side effects; None if pure>
 *
 * ERRORS:
 *   <error handling; None if no errors>
 *
 * LOG:
 *   <recommended logging strategy>
 */
public ReturnType functionName(params) {
```

### Step 3: Apply Injection Mode

For each function, apply the injection mode determined in Phase 0:

#### INSERT — No existing docstring

Insert the structured header directly. For Python, after the signature line. For C/Java, before the signature.

```python
# BEFORE:
def read_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()

# AFTER (INSERT):
def read_file(path: Path) -> pd.DataFrame:
    """
    ROLE:
      读取 CSV/Excel 文件为 DataFrame

    DEPENDS_ON:
      []

    IN:
      path: Path — 输入文件路径

    OUT:
      pd.DataFrame — 文件内容

    OWNS_FIELDS:
      []

    SIDE:
      None；只读文件

    ERRORS:
      不支持的文件格式抛 ValueError

    LOG:
      IN INFO (file path); ERR ERROR (unsupported format)
    """
    suffix = path.suffix.lower()
```

#### PREPEND — Has plain docstring (no ROLE/etc.)

Insert the structured header above the existing docstring. Keep the original docstring below as supplementary notes.

```python
# BEFORE:
def clean(df, drop_dup, drop_na):
    """Clean the dataframe by removing duplicates and nulls."""
    result = df.copy()

# AFTER (PREPEND):
def clean(df, drop_dup, drop_na):
    """
    ROLE:
      对 DataFrame 去重去空

    DEPENDS_ON:
      []

    IN:
      df: DataFrame — 原始数据
      drop_dup: bool — 是否去重
      drop_na: bool — 是否去空

    OUT:
      DataFrame — 清洗后的数据

    OWNS_FIELDS:
      []

    SIDE:
      stdout (print statistics)

    ERRORS:
      None

    LOG:
      OUT INFO (removed count); MAP INFO (duplicate/na count)

    ---
    Original docstring:
    Clean the dataframe by removing duplicates and nulls.
    """
    result = df.copy()
```

#### FILL — Has partial structured header (some fields missing)

Add only the missing fields to the existing structured header. Do not rewrite fields that already exist and are correct.

```python
# BEFORE (has ROLE and IN, missing the rest):
def filter_rows(df, column, op, value):
    """
    ROLE:
      按条件过滤 DataFrame 行

    IN:
      df: DataFrame; column: str; op: str; value: str
    """

# AFTER (FILL — added DEPENDS_ON, OUT, OWNS_FIELDS, SIDE, ERRORS, LOG):
def filter_rows(df, column, op, value):
    """
    ROLE:
      按条件过滤 DataFrame 行

    DEPENDS_ON:
      []

    IN:
      df: DataFrame; column: str; op: str; value: str

    OUT:
      DataFrame — 过滤后的数据

    OWNS_FIELDS:
      []

    SIDE:
      None

    ERRORS:
      列不存在抛 ValueError; 不支持的 operator 抛 ValueError

    LOG:
      IN INFO (column, op, value); OUT INFO (filtered row count)
    """
```

#### SKIP — Already has complete structured header

Do not modify. Leave the function as-is.

### Step 4: Output Formatted Code

Write the formatted code to a **new file**:

- File name: `<original_name>_formatted.<original_extension>`
- Example: `data_process.py` → `data_process_formatted.py`
- Original file is NOT modified
- For directory scope: generate `_formatted` file in the same directory as each source file

Preserve everything except function headers:
- All imports
- All decorators
- All type hints
- All existing comments (except where PREPEND merges)
- All code logic, indentation, blank lines
- Module-level docstrings and comments

## Injection Rules

- **Never modify business logic** — only add or update docstrings/comments.
- **Preserve all existing code** — imports, decorators, type hints, logic, formatting, blank lines.
- **Header placement**: Python — after signature, indented to match body. C/C++/Java — before signature, at column 0 or matching indentation.
- **Existing docstrings**: keep them. INSERT adds new header. PREPEND adds structured header above existing. FILL merges into existing.
- **Indentation**: match the function's indentation level. Python body indent (4 spaces) for docstring. C/Java — header at same indent as function.
- **Trivial functions**: even one-line functions get a full header. No exceptions — documentation completeness is the goal.
- **Async/generator functions**: treat the same as regular functions. The header describes the business contract, not the execution model.
- **Language consistency**: if the codebase uses Chinese comments/variables, write headers in Chinese. If English, write in English.

## Delivery Checklist

- [ ] Every function in scope has a structured header (8 fields).
- [ ] No business logic was changed — only headers added/updated.
- [ ] Existing docstrings preserved (PREPEND mode keeps original below structured header).
- [ ] Language-appropriate header format used (Python docstring / JS JSDoc / C block / Java Javadoc).
- [ ] Header placement correct (Python after signature, C/Java before signature).
- [ ] Indentation matches function body.
- [ ] Output written to `<original>_formatted.<ext>`, original file untouched.
- [ ] All imports, decorators, type hints, comments, and blank lines preserved.