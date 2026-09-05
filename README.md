# WorkBuddy Skill 集合

> 为 [WorkBuddy](https://www.codebuddy.cn/) 打造的结构化代码开发与文档工作流——从需求分析到影响追踪，从对话式渐进开发到给已有代码补结构化头。

## 这是什么？

两条互补的 skill 链 + 一个独立的对话式 skill，都遵循**函数头是架构唯一真实来源**的理念：

```
─── dev-flow 链（写新代码）───────────────────────────────────
dev-flow（主编排器 — 唯一入口）
  ├─ Phase 1: req-analyst      → 需求分析，临时 @business
  ├─ Phase 2: arch-designer    → 函数分解，DAG 依赖
  ├─ Phase 3: func-contract    → 结构化函数头 + 代码
  └─ Phase 4: func-logger      → 结构化业务日志
flow-tracer（独立事后分析工具）

─── code-formatter 链（给已有代码补头）──────────────────────
code-formatter（主编排器 — 唯一入口）
  ├─ Phase 0: 语言检测 + 范围扫描 + 确认
  ├─ Phase 1: func-analyzer    → 分析现有代码，提取 8 字段契约
  ├─ Phase 2: header-injector  → 生成 + 注入结构化头
  └─ Phase 3: 一致性自检（7 规则，自包含）

─── req-to-code（独立，对话式）──────────────────────────────
req-to-code（自包含 — 先搭骨架，再逐步填充）
  ├─ Round 1: 骨架（完整 8 字段头 + 占位符 body）
  ├─ Round 2+: 根据用户反馈增量填充
  ├─ 方向变更: 直接应用，标记 rework
  └─ 最终轮: 全量 7 规则一致性检查
  思考纪律: 主旨驱动（通过对话渐进涌现）+ 每个方案做方案评审（已集成 solution-review）

─── 表达层（方案评审与输出速览）────────────────────────────
solution-review（独立 — 方案三维度：是什么/为什么/优点与对比）
visual-digest（独立 — 把其他 skill 的输出提炼成图文速览：
              速览卡 / 流程图 / 对比表 / 进度仪表盘 / HTML 报告页）
```

**核心理念：** 所有持久的架构信息都放在函数头/文档字符串里——不是独立的文件级块。dev-flow 链在写新代码时创建头；code-formatter 链给已有代码补头；req-to-code 通过对话渐进式地构建带头的代码。

## 为什么？

- **文档不会和代码脱节**——契约在函数*内部*，不在独立的 wiki 里
- **影响分析是确定性的**——通过 `OWNS_FIELDS` 和 `DEPENDS_ON` 追踪任何字段变更
- **日志是一致的**——每个函数在 `LOG` 头字段里声明日志意图
- **新代码和修改都支持**——MODIFY 模式读取已有头，跑影响分析，再应用变更
- **给老代码补头**——code-formatter 分析旧代码并注入结构化头，不改业务逻辑
- **对话式渐进构建**——req-to-code 先搭骨架再逐步填充，适合模糊/演进中的需求

## 安装

### 方式 A：直接克隆

```bash
git clone https://github.com/CZYiHeng/skills_code.git
```

然后把每个 skill 文件夹复制到你的 WorkBuddy skills 目录：

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
~/.workbuddy/skills/solution-review/
~/.workbuddy/skills/visual-digest/
```

### 方式 B：通过 WorkBuddy UI 上传

打开 WorkBuddy → 技能市场 → 上传每个 skill 文件夹的 `SKILL.md`。

## 使用方式

### 开始一个新的编码任务

直接描述你想构建什么。WorkBuddy 会自动调用 `$dev-flow`：

```
> 帮我写一个员工花名册导入功能，输入是 Excel，需要清洗去重后写入数据库
```

编排器会：
1. **req-analyst** — 分析业务上下文，生成临时 `@business` 块，**请你确认**。
2. **arch-designer** — 设计函数分解、字段归属和 DAG 依赖，**请你确认**。
3. **func-contract** — 为每个函数写结构化头 + 实现代码。
4. **func-logger** — 添加匹配每个函数 `LOG` 字段的结构化日志。

### 修改已有代码

```
> 把 find_effective_baseline 的 target_date 改成支持日期范围
```

如果检测到已有结构化函数头，dev-flow 切换到 **MODIFY 模式**：
1. 读取已有头。
2. 跑影响分析（归属函数 → 下游消费者 → 受影响的日志）。
3. 展示影响报告。
4. 应用变更并更新所有受影响的头。

### 追踪数据流和影响

代码写完后，用 `flow-tracer` 分析：

```
> 分析一下余额基线查找的数据流，如果改了 snapshot_date 字段会影响哪些函数？
```

输出包括：
- 模块概览表
- 分阶段 Mermaid 时序图
- 日志追踪表（含 grep 命令）
- 字段归属表
- 影响分析报告

### 给已有代码补结构化头

当你有已有代码但没有结构化头时，用 `$code-formatter` 补上：

```
> 帮我把 data_process.py 的代码格式化成有结构化函数头的
```

编排器会：
1. **Phase 0** — 检测语言，扫描函数，展示范围摘要，请求确认。
2. **func-analyzer** — 分析每个函数的 ROLE、DEPENDS_ON、IN、OUT、OWNS_FIELDS、SIDE、ERRORS、LOG。
3. **header-injector** — 生成语言适配的头并注入代码。
4. **Phase 3** — 跑 7 规则一致性检查，确保头和实现匹配。

输出：新文件 `data_process_formatted.py`（带结构化头），原文件不动。

支持 Python、JavaScript/TypeScript、C/C++、Java。可处理单个文件或整个目录。

### 用 req-to-code 对话式渐进构建

当需求模糊或演进中时，用 `$req-to-code` 进行对话式渐进开发：

```
> 先搭个骨架，我要做一个 CSV 数据清洗工具，支持去重去空
```

Round 1 — skill 写出最小可运行骨架（完整头 + 占位符 body），并回答三个问题（为什么这样 / 有什么缺点 / 有没有冲突）：

```
骨架方案：read_file → clean_data → validate_rows → transform → write_output → main

为什么这样分：数据流驱动，经典 ETL 骨架
有什么缺点：假设单一文件输入；validate 和 clean 顺序可调
有没有冲突：无。OWNS_FIELDS 不重叠，DEPENDS_ON 线性无循环

ROUND 1 — 骨架
主旨：CSV 数据清洗工具，去重去空
函数数：6 | 头完整：6 | body 填充：0 | TODO：6
```

Round 2+ — 说"继续"，skill 按 upstream-first 顺序填充 body，对变更函数跑 7 规则一致性检查：

```
> 继续

ROUND 2 — 填充
主旨：CSV 数据清洗工具，去重去空
主旨对齐：✓
本轮填充：read_file, clean_data
一致性检查：2 个检查，0 STALE，0 MISSING
```

方向变更是直接应用的——受影响函数回退为占位符，标记 `# TODO(round-N): rework`：

```
> 改成支持 JSON 输入

方向变更（round 3）
为什么改：输入格式从 CSV 改为 JSON
有什么缺点：read_file 和 transform 需要重写
有没有冲突：clean_data 和 validate_rows 不受影响
```

## 函数头标准

每个生成或修改的函数都带结构化头：

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

| 字段 | 用途 |
|---|---|
| `ROLE` | 一句话业务职责 |
| `DEPENDS_ON` | 上游函数（构成 DAG） |
| `IN` | 输入类型和业务含义 |
| `OUT` | 输出类型和业务含义 |
| `OWNS_FIELDS` | 此函数创建/标准化/校验/持久化的字段 |
| `SIDE` | 副作用（INSERT/UPDATE/DELETE/外部调用/文件写入）；无则 `None` |
| `ERRORS` | 异常、降级或 `None` 返回语义 |
| `LOG` | 日志意图摘要 |

## 日志格式

```
业务动作名 | 阶段 | key=value
```

| 阶段 | 级别 | 何时使用 |
|---|---|---|
| `IN` | INFO | 关键输入用于追踪 |
| `OUT` | INFO | 关键输出或结果摘要 |
| `MAP`（单条） | INFO | 业务关键字段映射 |
| `MAP`（批量） | DEBUG | 批量映射、逐行细节 |
| `ERR`（可恢复） | WARNING | 降级、跳过、重试 |
| `ERR`（致命） | ERROR | 操作中断 |

## Skill 参考

### Dev-Flow 链（新代码）

| Skill | 阶段 | 调用方式 | 用途 |
|---|---|---|---|
| `dev-flow` | 编排器 | `$dev-flow`（代码请求时自动触发） | 模式检测，流水线编排 |
| `req-analyst` | Phase 1 | 仅内部调用 | 业务上下文分析，`@business` 块 |
| `arch-designer` | Phase 2 | 仅内部调用 | 函数分解，DAG，字段归属 |
| `func-contract` | Phase 3 | 仅内部调用 | 结构化头 + 代码实现 |
| `func-logger` | Phase 4 | 仅内部调用 | 结构化日志 + `LOG` 头更新 |
| `flow-tracer` | 事后分析 | `$flow-tracer` | 数据流图，日志追踪，影响分析 |

### Code-Formatter 链（已有代码）

| Skill | 阶段 | 调用方式 | 用途 |
|---|---|---|---|
| `code-formatter` | 编排器 | `$code-formatter` | 语言检测，范围，流水线编排 |
| `func-analyzer` | Phase 1 | 仅内部调用 | 分析已有函数，提取 8 字段契约 |
| `header-injector` | Phase 2 | 仅内部调用 | 生成 + 注入结构化头，输出新文件 |

### Req-To-Code（对话式渐进开发）

| Skill | 调用方式 | 用途 |
|---|---|---|
| `req-to-code` | `$req-to-code` | 对话式渐进开发：先搭骨架，再逐步填充。主旨驱动，每个方案做方案评审。自包含——无编排器，无子 skill。 |

### 表达层（独立 skill）

| Skill | 调用方式 | 用途 |
|---|---|---|
| `solution-review` | `$solution-review` | 方案三维度：是什么/为什么/优点与对比。已集成进 req-to-code 的方案输出环节，也可独立评审任意方案。 |
| `visual-digest` | `$visual-digest` | 输出速览：把其他 skill 的密集输出提炼成图文（速览卡/流程图/对比表/进度仪表盘/HTML 报告页），一屏看懂。 |

> Phase skill 只能通过编排器调用，不要直接调用。`req-to-code` / `solution-review` / `visual-digest` 是独立的——直接调用。

## 项目结构

```
skills_code/
├── dev-flow/
│   ├── SKILL.md              # 主编排器（新代码）
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
│   ├── SKILL.md              # 主编排器（已有代码）
│   └── agents/openai.yaml
├── func-analyzer/
│   ├── SKILL.md              # Phase 1: 分析已有代码
│   └── agents/openai.yaml
├── header-injector/
│   ├── SKILL.md              # Phase 2: 注入结构化头
│   └── agents/openai.yaml
├── req-to-code/
│   ├── SKILL.md              # 对话式渐进开发（独立）
│   └── agents/openai.yaml
├── solution-review/
│   ├── SKILL.md              # 方案三维度评审（独立，已集成进 req-to-code）
│   └── agents/openai.yaml
├── visual-digest/
│   ├── SKILL.md              # 输出速览：图文提炼（独立）
│   └── agents/openai.yaml
├── data_process.py           # 示例脚本（独立 CLI 工具）
├── data_process_formatted.py # 示例输出（code-formatter 结果）
└── README.md
```

## 示例：完整流程

**用户请求：**
> 写一个 CSV 数据清洗工具，支持去重、去空、过滤

**Phase 1 — req-analyst 输出：**
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

**Phase 2 — arch-designer 输出：**
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

**Phase 3 — func-contract 输出：**（函数头 + 实现代码）

**Phase 4 — func-logger 输出：**（为每个函数添加结构化日志）

## 兼容性

- **WorkBuddy**（CLI / VS Code 插件 / 微信小程序）
- Skill 与框架无关——生成的代码在任何语言中都遵循函数头标准

## 许可证

MIT
