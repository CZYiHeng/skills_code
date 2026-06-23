---
name: func-contract
description: >-
  [CHAIN POSITION: Phase 3 of dev-flow. Do NOT call directly — use $dev-flow instead.]
  Function data-contract standard. Reads the confirmed temporary business and architecture context from dev-flow,
  then writes each function with a structured header/docstring containing ROLE, DEPENDS_ON, IN, OUT, OWNS_FIELDS, SIDE, ERRORS, and LOG.
  Function headers/docstrings are the durable source of truth for impact analysis; standalone @business/@architecture blocks are not.
  Uses business language and variable names that reveal the data transformation chain.
---

# Func-Contract — Function Header Contract Standard

Write code from the confirmed design and embed the local contract in each function header/docstring.

## Chain Position

```
dev-flow orchestrator
  └─ Phase 1: req-analyst            → temporary @business
  └─ Phase 2: arch-designer          → temporary architecture plan
  └─ Phase 3: func-contract (YOU)    → function headers/docstrings + code
  └─ Phase 4: func-logger            → logs + LOG header sections
```

## Header Template

Use language-native docstrings/comments. For Python:

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
      <副作用；无则 None>

    ERRORS:
      <异常、降级或 None 返回语义；无则 None>

    LOG:
      <本函数应记录的 IN/OUT/MAP/ERR 摘要>
    """
```

## Rules

- Write the function header before the body.
- Copy each architecture field into the matching header section.
- Use `OWNS_FIELDS: []` for read-only helper functions that own no fields.
- Use `SIDE: None` for pure/read-only functions.
- Use `ERRORS` to document exceptions, fallback behavior, and meaningful `None` returns.
- Use `LOG` to summarize logging intent even before func-logger inserts concrete log statements.
- Do not create file-level `@business` or `@architecture` as permanent code documentation.

## Naming

Intermediate variables must reveal the transformation chain:

```python
raw_headers -> cleaned_headers -> header_map
```

Never reuse one variable name for different semantic states.

## Delivery Checklist

- [ ] Every generated/modified function has a structured header/docstring.
- [ ] Header `ROLE/DEPENDS_ON/IN/OUT/OWNS_FIELDS/SIDE/ERRORS/LOG` matches implementation.
- [ ] Every mutable or derived field has exactly one owning function.
- [ ] `DEPENDS_ON` names real upstream functions.
- [ ] Variable names reveal the data chain.
- [ ] No stale standalone architecture block is left as the only source of truth.