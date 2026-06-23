---
name: arch-designer
description: >-
  [CHAIN POSITION: Phase 2 of dev-flow. Do NOT call directly — use $dev-flow instead.]
  Architecture designer that reads the confirmed temporary @business context and designs function decomposition:
  function responsibilities, IN/OUT types, owns_fields, depends_on DAG, side effects, and errors.
  Produces a temporary architecture plan for user confirmation, then hands off details to be embedded into each function header/docstring by func-contract.
  Supports linear chains, branches, and merges.
---

# Arch-Designer — Function Architecture Designer

Design the function structure before code is written. The architecture plan is temporary; the durable source of truth will be each function header/docstring.

## Chain Position

```
dev-flow orchestrator
  └─ Phase 1: req-analyst            → confirmed temporary @business
  └─ Phase 2: arch-designer (YOU)    → temporary architecture plan
  └─ Phase 3: func-contract          → function headers/docstrings + code
  └─ Phase 4: func-logger            → logs + LOG header sections
```

## Input

Read the confirmed business context:

```
@business:
  name:       <业务名称>
  flow:       <数据流向>
  fields:     <字段→含义映射>
  complexity: <simple|medium|complex>
```

## Workflow

### Step 1: Design Function Decomposition

Use one function per distinct business operation or data transformation. Keep I/O, parsing, validation, computation, persistence, and export responsibilities separate when they are non-trivial.

### Step 2: Assign Field Ownership

For each field that is created, normalized, validated, persisted, or materially transformed, assign exactly one owning function.

### Step 3: Define Dependencies

Use `depends_on` to declare upstream functions. Support:

- Linear chain: A → B → C
- Branch: A → B and A → C
- Merge: A + B → C

### Step 4: Produce Temporary Architecture Plan

Use this shape for confirmation and handoff:

```
@architecture:
  functions:
    - name:         <函数名>
      role:         <一句话职责>
      depends_on:   [上游函数名列表]
      in:           <输入类型和业务含义>
      out:          <输出类型和业务含义>
      owns_fields:  [字段列表]
      side:         <副作用；无则 None>
      errors:       <异常/降级/None 语义；无则 None>
```

### Step 5: Hand Off To Function Headers

After user confirmation, each architecture item must be copied into that function's header/docstring:

- `role` → `ROLE`
- `depends_on` → `DEPENDS_ON`
- `in` → `IN`
- `out` → `OUT`
- `owns_fields` → `OWNS_FIELDS`
- `side` → `SIDE`
- `errors` → `ERRORS`

Do not leave the architecture plan as the only durable documentation in code.

## Design Principles

- Flow-driven: each distinct transformation is a function.
- Field ownership is mandatory for mutable or derived fields.
- Dependencies are explicit through `DEPENDS_ON`.
- Function headers are the final architecture record.
- Keep functions focused and testable.