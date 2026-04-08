# Context 路由审计：旧 Context Bank vs Cursor 原生 + Skill Seeker

> 生成日期: 2026-02-24
> 用途: 评估旧项目的 `.specify/context/` Context Bank 机制，对比 Cursor 2.0+ 原生能力，为新项目选择最优方案

---

## 1. 旧方案审计：Context Bank

### 1.1 机制描述

旧项目在 `.specify/context/` 下维护了一套手工策展的知识库：

```
.specify/context/
├── INDEX.md              # 索引入口
├── 00_versions.md        # 版本锁定
├── 01_graphiti_core.md   # Graphiti API 签名
├── 02_langgraph_flow.md  # LangGraph 用法
├── 03_sensor_io.md       # YOLO/VAD I/O
├── 04_neo4j_schema.md    # Neo4j 配置
└── 05_prior_knowledge.md # 先验知识库
```

配合 `.cursor/rules/00-project-guardrails.mdc` 中的硬规则：
> "API 签名以 Context Bank 为准：当编写 Graphiti/LangGraph/YOLO/VAD 代码时，必须参考 `.specify/context/*.md`，不信任训练数据。"

### 1.2 旧方案的问题

| 问题 | 影响 |
|:-----|:-----|
| **静态加载** | `alwaysApply: true` 使 guardrails 每次都注入全部规则，浪费 tokens |
| **手工维护成本高** | 每次依赖升级需手动更新 context 文件、标注 Source/Date |
| **_vendor/ 源码验证笨重** | 下载整个仓库源码到本地做 API 签名验证，占空间且难以持续 |
| **路由不够智能** | 无论任务是什么，所有 context 规则都被注入，缺乏按需加载 |
| **与 Cursor 原生能力重复** | Cursor 2.0+ 已支持 Dynamic Context Discovery，手工策展的价值降低 |
| **可扩展性差** | 新增学习项目(如 LiveKit/SVA)时需要为每个库重新手写 context 文件 |

---

## 2. Cursor 2.0+ 原生方案

### 2.1 Dynamic Context Discovery (2026年1月发布)

Cursor 现在支持五种动态上下文发现机制：

1. **长响应转文件**: 大输出写入文件，Agent 按需增量读取
2. **对话历史引用**: 上下文窗口满时可回溯历史文件
3. **Agent Skills 支持**: 按需发现领域特定能力
4. **MCP 工具高效加载**: 仅在需要时加载必要的 MCP 工具
5. **终端会话文件化**: 终端输出可按需引用

### 2.2 Agent Skills 机制

Skills 是 Cursor 的按需知识加载机制：

```
~/.cursor/skills-cursor/          # 全局 Skills（跨项目）
.cursor/skills/                    # 项目级 Skills
```

每个 Skill 包含：
- `SKILL.md`: 主指令文件（标题、描述、步骤）
- 可选: `EXAMPLES.md`, `REFERENCE.md`, `TEMPLATE.md`

**核心优势**: Agent 根据任务描述自动匹配 Skill，仅在需要时读取，不污染全局上下文。

### 2.3 Cursor Rules 最佳实践 (2026)

```
.cursor/rules/
├── workspace.mdc       # 全局工作流规则 (alwaysApply: true)
├── architecture.mdc    # 架构决策 (alwaysApply: false, 按 glob 匹配)
├── backend.mdc         # 后端约定 (globs: ["**/*.py"])
├── unity.mdc           # Unity 约定 (globs: ["**/*.cs"])
└── testing.mdc         # 测试约定
```

**关键原则**:
- `alwaysApply: true` 仅用于极少的全局规则（语言、工作流）
- 其他规则通过 `globs` 按文件类型自动匹配
- 保持每个规则文件 < 500 行
- 描述具体，附带正确/错误示例

---

## 3. 方案对比与结论

| 维度 | 旧 Context Bank | Cursor Skills + Rules | 胜出 |
|:-----|:----------------|:---------------------|:-----|
| **Token 效率** | 全量注入，浪费大 | 按需加载，精准 | Skills |
| **维护成本** | 手工策展，需标注日期和来源 | 一次编写，Agent 自动匹配 | Skills |
| **可扩展性** | 每个库一个 md 文件 | 每个学习项目一个 Skill | Skills |
| **版本追踪** | 需要 _vendor/ 或手工记录 | 依赖 `pyproject.toml` + lock file | Skills |
| **智能路由** | 无（全量注入） | 基于任务描述自动匹配 | Skills |
| **知识深度** | 可以非常详细 | 可以同样详细 | 平局 |
| **离线备份** | 天然在 git 中 | 天然在 git 中 | 平局 |

### 结论: 新项目应采用 **Cursor Skills + 精简 Rules** 方案

**具体策略**:

1. **全局 Rules** (`.cursor/rules/`):
   - `workspace.mdc`: 语言、工作流、Git 规范
   - `architecture.mdc`: 架构约束、分层原则
   - `backend-python.mdc`: Python 后端约定
   - `unity-client.mdc`: Unity C# 约定

2. **项目 Skills** (`.cursor/skills/`):
   - `livekit-agents/SKILL.md`: LiveKit Agent 开发参考
   - `sva-processors/SKILL.md`: SVA Processor 模式参考
   - `gemini-realtime/SKILL.md`: Gemini Realtime API 参考
   - `openteach-mapping/SKILL.md`: OpenTeach AR 映射参考

3. **@docs 引用**: 仓库级文档通过 `@` 引用按需获取，不预加载

4. **备份策略**: Skills 和 Rules 都在 `.cursor/` 下，随 git 版本控制

---

## 4. 迁移清单

| 旧项目资产 | 迁移动作 | 新项目位置 |
|:-----------|:---------|:----------|
| `.specify/context/INDEX.md` | **废弃** | 不迁移 |
| `.specify/context/00_versions.md` | 用 `pyproject.toml` 替代 | `pyproject.toml` |
| `.specify/context/01_graphiti_core.md` | 如继续用 Graphiti，转为 Skill | `.cursor/skills/graphiti/SKILL.md` |
| `.specify/context/02_langgraph_flow.md` | **废弃**，不再使用 LangGraph | 不迁移 |
| `.specify/context/03_sensor_io.md` | 重写为新视觉栈 Skill | `.cursor/skills/vision-pipeline/SKILL.md` |
| `.specify/context/04_neo4j_schema.md` | 如继续用 Neo4j，转为 Skill | `.cursor/skills/graphiti/SKILL.md` |
| `.specify/context/05_prior_knowledge.md` | 有价值的方法论保留到架构文档 | `doc/architecture.md` |
| `.cursor/rules/00-project-guardrails.mdc` | 重写为精简的新 rules | `.cursor/rules/*.mdc` |
| `.specify/audit/` | **废弃** | 不迁移 |
| `guide/` | 有价值的设计思想提炼到新架构文档 | `doc/` |
