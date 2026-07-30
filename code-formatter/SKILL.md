---
name: code-formatter
description: >-
  Master orchestrator for retrofitting structured function headers onto existing code.
  When the user wants to ADD or FORMAT structured headers (ROLE/DEPENDS_ON/IN/OUT/OWNS_FIELDS/SIDE/ERRORS/LOG)
  onto existing code that lacks them, invoke $code-formatter.
  Detects language, scopes the work, orchestrates analysis and injection.
  Supports Python, JavaScript/TypeScript, C/C++, Java.
  Preserves all existing business logic; only adds or updates function header docstrings.
  This is the ONLY entry point for code formatting.
---

# Code-Formatter — Structured Header Retrofit Orchestrator

You are the orchestrator for retrofitting structured function headers onto existing code.
Your job is to take code that has NO structured headers and produce code WITH structured headers —
without changing any business logic.

Core rule: **never modify business logic. Only add or update function header docstrings/comments.**

## When To Use

- User has existing code and wants to add structured function headers
- User wants to "format" or "standardize" code to match the dev-flow header standard
- User wants to retrofit headers for flow-tracer analysis
- User pastes code and says "format this" / "add headers" / "standardize this"

## When NOT To Use

- Writing new code from scratch → use `$dev-flow` instead
- Modifying existing code that ALREADY has complete structured headers → use `$dev-flow` MODIFY mode
- Only analyzing code that already has headers → use `$flow-tracer`

## Function Header Standard

Every function must carry a structured header/docstring containing the local contract.
Use the language-native style:

### Python

```python
def function_name(...):
    """
    ROLE:
      <one-line business responsibility>

    DEPENDS_ON:
      [upstream_function_a, upstream_function_b]

    IN:
      <input types and business meaning>

    OUT:
      <output type and business meaning>

    OWNS_FIELDS:
      [field_a, field_b]

    SIDE:
      <INSERT/UPDATE/DELETE/external call/file write; None if pure>

    ERRORS:
      <exceptions, fallbacks, or None return semantics; None if no errors>

    LOG:
      <IN/OUT INFO; key MAP INFO; batch DEBUG; recoverable WARNING; fatal ERROR>
    """
```

### JavaScript / TypeScript

```javascript
function functionName(...) {
    /**
     * ROLE:
     *   <one-line business responsibility>
     *
     * DEPENDS_ON:
     *   [upstreamFunctionA, upstreamFunctionB]
     *
     * IN:
     *   <input types and business meaning>
     *
     * OUT:
     *   <output type and business meaning>
     *
     * OWNS_FIELDS:
     *   [fieldA, fieldB]
     *
     * SIDE:
     *   <INSERT/UPDATE/DELETE/external call/file write; None if pure>
     *
     * ERRORS:
     *   <exceptions, fallbacks, or null/undefined return semantics; None if no errors>
     *
     * LOG:
     *   <IN/OUT INFO; key MAP INFO; batch DEBUG; recoverable WARN; fatal ERROR>
     */
```

### C / C++

```c
/* ROLE:
 *   <one-line business responsibility>
 *
 * DEPENDS_ON:
 *   [upstream_function_a, upstream_function_b]
 *
 * IN:
 *   <input types and business meaning>
 *
 * OUT:
 *   <output type and business meaning>
 *
 * OWNS_FIELDS:
 *   [field_a, field_b]
 *
 * SIDE:
 *   <INSERT/UPDATE/DELETE/external call/file write; None if pure>
 *
 * ERRORS:
 *   <error codes, fallbacks, or NULL return semantics; None if no errors>
 *
 * LOG:
 *   <IN/OUT INFO; key MAP INFO; batch DEBUG; recoverable WARN; fatal ERROR>
 */
int function_name(...) {
```

### Java

```java
/**
 * ROLE:
 *   <one-line business responsibility>
 *
 * DEPENDS_ON:
 *   [upstreamFunctionA, upstreamFunctionB]
 *
 * IN:
 *   <input types and business meaning>
 *
 * OUT:
 *   <output type and business meaning>
 *
 * OWNS_FIELDS:
 *   [fieldA, fieldB]
 *
 * SIDE:
 *   <INSERT/UPDATE/DELETE/external call/file write; None if pure>
 *
 * ERRORS:
 *   <exceptions, fallbacks, or null return semantics; None if no errors>
 *
 * LOG:
 *   <IN/OUT INFO; key MAP INFO; batch DEBUG; recoverable WARN; fatal ERROR>
 */
public ReturnType functionName(...) {
```

## Workflow

### Phase 0: Scope & Language Detection

1. Identify the target:
   - File path(s)
   - Directory (recursive scan)
   - Pasted code snippet
2. Detect language by file extension or syntax:

| Extension(s) | Language | Header Style |
|---|---|---|
| `.py` | Python | Triple-quote docstring |
| `.js`, `.jsx`, `.mjs` | JavaScript | JSDoc block `/** */` |
| `.ts`, `.tsx` | TypeScript | JSDoc block `/** */` |
| `.c`, `.h` | C | Block comment `/* */` |
| `.cpp`, `.cc`, `.hpp` | C++ | Block comment `/* */` |
| `.java` | Java | Javadoc block `/** */` |

3. Determine scope:

| Scope | Action |
|---|---|
| Single file | Process all functions in that file |
| Directory | Recursively find all source files, process each |
| Specific functions | Process only the named functions |

4. Check each function for existing structured headers:

| Existing State | Action |
|---|---|
| No docstring/comment | Mark as `INSERT` — will add new header |
| Plain docstring (no ROLE/etc.) | Mark as `PREPEND` — will add structured header above existing |
| Partial structured header (some fields) | Mark as `FILL` — will add missing fields |
| Complete structured header | Mark as `SKIP` — already formatted (or `REFRESH` if user requests) |

5. Present scope summary to user:

```
FORMAT SCOPE
════════════
Language:  Python
Files:     3
Functions: 12 total
  INSERT:  8  (no existing header)
  PREPEND: 3  (has plain docstring)
  FILL:    1  (partial structured header)
  SKIP:    0  (already complete)

OUTPUT:    生成新文件 (xxx_formatted.py)，原文件不动
DEPENDS_ON: 同文件内追踪 (单文件 scope) / 跨文件追踪 (目录 scope)

Proceed? (yes / adjust scope / specific functions only)
```

### Phase 1: Analyze (func-analyzer)

Hand off to `func-analyzer` to analyze every function in scope:

1. Extract function signatures (name, params, return type)
2. Build call graph (which functions call which, within the codebase)

   DEPENDS_ON 追踪范围:
   - 单文件 scope → 仅追踪同文件内函数调用
   - 目录 scope → 跨文件追踪，先全量扫描建立函数名→文件位置索引，再分析依赖

3. For each function, determine:
   - `ROLE` — business responsibility (inferred from name, body, context)
   - `DEPENDS_ON` — upstream functions called within the same codebase
   - `IN` — input params, types, business meaning
   - `OUT` — return values, types, business meaning
   - `OWNS_FIELDS` — fields created, normalized, validated, or persisted
   - `SIDE` — side effects (DB writes, file I/O, external calls, print/stdout)
   - `ERRORS` — exceptions raised/caught, error codes, fallback returns
   - `LOG` — existing logging statements and their levels

4. Produce a function inventory for Phase 2.

### Phase 2: Inject (header-injector)

Hand off to `header-injector` to generate and inject structured headers:

1. Generate language-appropriate header for each function based on the inventory.
2. Handle existing comments per the Phase 0 action plan (INSERT / PREPEND / FILL / SKIP).
3. Preserve all existing code: imports, decorators, type hints, logic, formatting.
4. Output the formatted code to a **new file**: `<原文件名>_formatted.<原扩展名>`
   - 例：`data_process.py` → `data_process_formatted.py`
   - 原文件不动
   - 目录 scope：在每个文件同目录下生成对应的 `_formatted` 文件

### Phase 3: Post-Injection Consistency Check

After injection, verify that each function's header matches its actual implementation.
This is self-contained — no external skill dependency required.

Check these 7 rules on every formatted function:

| # | Rule | What it checks | STALE (header over-declares) | MISSING (header under-declares) |
|---|---|---|---|---|
| 1 | `OWNS_FIELDS_MATCH` | fields created/modified/persisted in body vs `OWNS_FIELDS` | declared field not operated in body | body operates a field not declared |
| 2 | `DEPENDS_ON_MATCH` | functions called in body vs `DEPENDS_ON` | declared dependency not called | body calls a function not declared |
| 3 | `SIDE_MATCH` | side effects in body vs `SIDE` | declared side effect not executed | body has DB/file/API/stdout write but `SIDE: None` |
| 4 | `IN_MATCH` | function signature parameters vs `IN` | described param not in signature | signature param not described |
| 5 | `OUT_MATCH` | actual `return` statements vs `OUT` | declared return shape never returned | returns a shape not declared |
| 6 | `LOG_MATCH` | actual log/print statements vs `LOG` | described log behavior has no corresponding statement | log/print exists but not described in `LOG` |
| 7 | `ERRORS_MATCH` | `try/except/raise` or error returns vs `ERRORS` | described exception has no corresponding code | body raises/handles an exception not described |

Status values:
- `OK` — header and implementation agree.
- `STALE` — header declares something the code doesn't do. Fix the header.
- `MISSING` — code does something the header never declared. Add the declaration.

A freshly injected header that already disagrees with its body is a documentation bug.
Fix all STALE and MISSING issues before delivery.

Output format:

```
CONSISTENCY CHECK
═════════════════

| Function | Rule | Status | Detail |
|---|---|---|---|
| read_file | OWNS_FIELDS | OK | [] matches |
| read_file | DEPENDS_ON | OK | no calls |
| clean | SIDE | MISSING | has print() but SIDE: None |
| ...

SUMMARY: 12 checked, 10 OK, 1 STALE, 1 MISSING
```

Fix all issues, then deliver the final formatted code.

## Delivery Checklist

- [ ] Every function in scope has a structured header.
- [ ] Header fields (ROLE/DEPENDS_ON/IN/OUT/OWNS_FIELDS/SIDE/ERRORS/LOG) match implementation.
- [ ] No business logic was changed — only headers added/updated.
- [ ] Existing docstrings preserved (prepended or merged, not deleted).
- [ ] Language-appropriate header format used.
- [ ] Consistency check passed with zero STALE / MISSING.
- [ ] Every mutable or derived field has exactly one owning function.
- [ ] `DEPENDS_ON` names real upstream functions in the same codebase.

## Rules

- Function headers/docstrings are the durable source of truth.
- Never change business logic — only add or update headers.
- Preserve all existing code structure (imports, decorators, type hints, formatting).
- Use business language throughout headers.
- Generate headers that accurately reflect ACTUAL code behavior, not aspirational design.
- Run consistency check after injection; fix all issues before delivery.
- For directories, process files one by one and report progress.
- If a function is too trivial (e.g., one-line getter), still add a minimal header with ROLE and IN/OUT.
- If code is obfuscated or minified, ask the user before proceeding.