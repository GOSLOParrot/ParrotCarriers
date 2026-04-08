# 23 · 目录审计、Cursor 路由方案与服务器更新

> 生成日期: 2026-03-02  
> 依据: 联网深度搜索 Cursor 2.0 官方文档/博客/社区、当时版本的 INDEX / output / 服务器决策资料  
> 目的: 为目录整理、Cursor rules 路由、active_context 填充提供行动依据
> 注: **历史审计文档**。其中“问题诊断 / 当前阶段”仅代表 2026-03-02 当时状态；当前以 `.cursor/memory/INDEX.md`、`.cursor/memory/active_context.md`、`.cursor/memory/architecture/module_division.md` 为准。

---

## 一、问题诊断

### 1.1 当前混乱点

| # | 问题 | 根因 | 影响 |
|:--|:-----|:-----|:-----|
| 1 | `output/` 目录存在于根目录 | Skill Seekers 跑时 `--output` 路径写错，未指向 `docs/references/skill_seekers_output/` | 与规划的存放位置不一致 |
| 2 | `.cursor/rules/` 为空 | 尚未创建任何 .mdc 规则 | Cursor 无全局路由指引，不知道去哪找上下文 |
| 3 | `.cursor/skills/` 不存在 | 尚未从 output 中迁移 SKILL.md | Cursor 无法自动发现领域技能 |
| 4 | `active_context.md` 为空 | INDEX 和 rules 中未说明其用途，导致填充失败 | 进度与下一步无处记录 |
| 5 | INDEX.md 中服务器信息过时 | 仍写香港+新加坡，实际已改为东京双节点 | Cursor 引用错误上下文 |
| 6 | `backend/` vs `agent/`、`unity_client` vs `unity-client` | 命名不统一 | INDEX 与实际目录不对齐 |

### 1.2 解决优先级

1. **先**：确定目录树 → 创建第一个 workspace.mdc → 更新 INDEX → 填充 active_context
2. **后**：迁移 output → 创建 skills → 补拉 openteach

---

## 二、Cursor 2.0 Rules 与 Skills 机制（联网调研 2026-03-02）

### 2.1 Rules（`.cursor/rules/*.mdc`）

> 来源: https://docs.cursor.com/en/context/rules · https://localskills.sh/blog/cursor-rules-guide

**核心机制**：Rules 是**持久化指令**，嵌入模型上下文起始位置，告诉 Cursor 如何为本项目写代码/做决策。

| 属性 | 说明 |
|:-----|:-----|
| **文件格式** | `.mdc`（Markdown Cursor）= YAML frontmatter + Markdown 正文 |
| **存放位置** | `.cursor/rules/`，应纳入版本控制 |
| **旧方案** | `.cursorrules` 已废弃（仍向后兼容），新项目不应使用 |

**四种激活模式**：

| 模式 | frontmatter 配置 | 何时生效 |
|:-----|:-----------------|:---------|
| **Always Apply** | `alwaysApply: true` | 每次会话 |
| **Intelligent** | `description` + `alwaysApply: false` | Agent 根据描述判断相关性 |
| **File-specific** | `globs: ["pattern"]` | 用户提及匹配文件时 |
| **Manual** | 空 frontmatter | 用户 `@规则名` 时 |

**最佳实践**：
- 每个 .mdc 控制在 500 行以内
- 按领域拆分（全局工作流、后端约定、Unity 约定）
- 具体写代码模式和禁止事项
- 引用文件路径而非复制内容

### 2.2 Skills（`.cursor/skills/<name>/SKILL.md`）

> 来源: https://cursor.com/docs/context/skills · https://www.mdskills.ai/specs/skill-md

**核心机制**：Skills 是**按需加载的领域知识包**，通过三阶段渐进式加载，避免上下文膨胀。

**三阶段加载**：

| 阶段 | 加载内容 | token 开销 |
|:-----|:---------|:-----------|
| **Discovery** | 仅 name + description | ~100 tokens |
| **Activation** | 完整 SKILL.md | <5000 tokens |
| **Execution** | 按需加载 references/、scripts/ | 按需 |

**自动发现位置**（优先级从高到低）：
1. `.agents/skills/<name>/SKILL.md` — 项目级
2. `.cursor/skills/<name>/SKILL.md` — 项目级
3. `~/.cursor/skills/<name>/SKILL.md` — 用户全局

**SKILL.md 格式**：

```markdown
---
name: livekit-agents
description: LiveKit Agents 框架 — AgentSession/RPC/DataChannel/Room 模型。构建总线骨架时使用。
---

# LiveKit Agents

## 何时使用
构建 ParrotCarriers 总线、配置 AgentSession/RPC 时激活。

## 参考
- `references/README.md`
- `references/file_structure.md`
```

**手动调用**：在 Agent 聊天中输入 `/skill-name`

### 2.3 Rules vs Skills 的区别

| 维度 | Rules | Skills |
|:-----|:------|:-------|
| **目的** | 指挥 Cursor「怎么做」 | 提供领域知识「做什么」 |
| **加载** | 静态（alwaysApply）或半静态 | 动态按需 |
| **位置** | `.cursor/rules/*.mdc` | `.cursor/skills/<name>/SKILL.md` |
| **token** | 始终占用（alwaysApply）或条件占用 | 仅匹配时加载 |
| **用途** | 编码约定、架构约束、工作流 | API 文档、仓库知识、部署指南 |

### 2.4 Dynamic Context Discovery（Cursor 官方博客 2026）

> 来源: https://cursor.com/blog/dynamic-context-discovery

Cursor 的核心哲学转向**动态上下文发现**：
- **减少静态上下文**，让 Agent 自行按需拉取
- **Skills、MCP、Terminal 输出** 都被当作文件处理
- Agent 用 grep/semantic search 自行发现所需上下文
- 长工具输出写入文件，Agent 用 `tail` 按需读取

**对 ParrotCarriers 的启示**：
- workspace.mdc 只写路由索引，不塞大量内容
- 详细信息放 INDEX.md / skills / references，让 Cursor 动态发现
- 不需要把所有知识都塞进 rules

---

## 三、服务器决策更新（东京双节点摘要）

### 3.1 变更：香港+新加坡 → 东京双节点

| 原决策 | 新决策 | 原因 |
|:-------|:-------|:-----|
| 香港 (区域 A) + 新加坡 (区域 B) | **东京 常驻城堡（当前 ecs.g9i.large）** + **东京 按需机甲 (A10)** | 抢不到香港 A10；东京靠近 Gemini API |

### 3.2 新物理拓扑

```
┌─────────────────────────────────────────────────────────────┐
│ 常驻城堡 (The Castle): 东京 ecs.g9i.large (2核8G, 常开)    │
│   LiveKit Server · Redis · Neo4j · Python Agent             │
│   (Gemini 逻辑 · Scheduler〔旧称 Dispatcher〕· Nanobot)     │
└──────────────────────────┬──────────────────────────────────┘
                           │ VPC 内网 (0.1ms)
                           │
┌──────────────────────────┴──────────────────────────────────┐
│ 按需机甲 (The Mecha): 东京 ecs.gn7i A10 (抢占式)            │
│   SAM2 + DINOv2 · DSG L1/L2-A (Stateless Worker)            │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 关键设计

| 维度 | 说明 |
|:-----|:-----|
| **控制面 vs 数据面** | `ecs.g9i.large` = 控制面（状态/路由/记忆）；A10 = 数据面（算力，可抛弃） |
| **VPC** | 同一可用区，内网 0.1ms |
| **视频流路径** | Unity (泉州) → LiveKit (Castle / ecs.g9i.large) → [内网] → SAM2 (A10) |
| **A10 无状态** | 启动时连接 Castle 内网 IP，释放无损失 |

### 3.4 需更新的文档

| 文档 | 位置 | 需更新内容 |
|:-----|:-----|:-----------|
| INDEX.md §三 | `.cursor/memory/INDEX.md` | 服务器从 HK+SG 改为 Tokyo 双节点 |
| legacy.md §三 | `docs/InfoCollections/HumanPlan/legacy.md` | 同步东京双节点摘要，并避免继续引用缺失文档 |
| active_context.md | `.cursor/memory/active_context.md` | 反映当前服务器决策 |

---

## 四、修正后的目录结构树

> 基于实际文件审计 + Cursor 2.0 机制 + 服务器新决策

```
ParrotCarriers/
│
│  ═══════════════════════ .cursor/ — 作战指挥室 ═══════════════
│
├── .cursor/
│   ├── memory/
│   │   ├── architecture/
│   │   │   ├── system_core.md       # 总架构图 v3
│   │   │   └── scene.md             # 家族拓扑与场景推演
│   │   ├── lore/                    # 可选：故事背景/人格设定
│   │   ├── INDEX.md                 # ★ 全局索引（唯一真相源）
│   │   └── active_context.md        # ★ 当前进度 + 下一步计划
│   │
│   ├── rules/                       # ★ Cursor 规则（.mdc 格式）
│   │   └── workspace.mdc            # ★ 第一个全局规则：路由 + 项目概述
│   │                                #    （alwaysApply: true）
│   │                                #    后续按需添加：
│   │                                #    backend-python.mdc (globs: agent/**)
│   │                                #    unity-client.mdc (globs: unity_client/**)
│   │                                #    architecture.mdc (description 触发)
│   │
│   └── skills/                      # ★ Skill Seekers 输出转存（按需加载）
│       ├── livekit-agents/          # 从 output/agents/ 迁移
│       │   └── SKILL.md
│       ├── agent-starter-python/    # 从 output/agent-starter-python/ 迁移
│       │   └── SKILL.md
│       ├── python-agents-examples/
│       │   └── SKILL.md
│       ├── agents-example-unity/
│       │   └── SKILL.md
│       ├── client-sdk-unity/
│       │   └── SKILL.md
│       ├── sva-vision-agents/       # 从 output/Vision-Agents/ 迁移
│       │   └── SKILL.md
│       └── graphiti/
│           └── SKILL.md
│
│  ═══════════════════════ docs/ — 皇家大图书馆 ═══════════════
│
├── docs/
│   ├── InfoCollections/             # 调研遗产与人类计划
│   │   ├── HumanPlan/
│   │   │   ├── plan.md              # 原始计划与调研需求
│   │   │   ├── legacy.md            # 调研决策（D1-D22）
│   │   │   └── legacy.md            # ★ 当前保留的服务器部署摘要入口
│   │   └── Opus/
│   │       ├── INDEX.md             # 22+1 个调研文档索引
│   │       ├── 01~22_*.md           # 旧项目调研遗产
│   │       └── 23_directory_audit_and_cursor_routing.md  # ★ 本文件
│   │
│   ├── references/                  # Skill Seekers 详细参考资料
│   │   ├── skill_seekers_output/    # ★ output/ 的正确归属位置
│   │   │   ├── livekit/             # agent-starter-python, agents, etc.
│   │   │   ├── sva/                 # Vision-Agents
│   │   │   ├── memory/              # graphiti
│   │   │   ├── ar/                  # openteach（待补拉）
│   │   │   ├── _raw/               # *_github_data.json
│   │   │   └── _configs/
│   │   ├── learning_projects_list.md
│   │   └── README.md
│   │
│   ├── design/                      # 设计草稿
│   │   └── README.md
│   │
│   └── specifications/              # 部署规格
│       └── README.md                # 阿里云/SRE 待补充
│
│  ═══════════════════════ 代码目录 ═══════════════════════════
│
├── agent/                           # Python 云端 Agent（当前为 backend/，需重命名）
├── unity_client/                    # Unity AR 客户端
├── infra/                           # Docker/LiveKit Server 配置
│
│  ═══════════════════════ 工具与输出 ═══════════════════════════
│
├── scripts/                         # Skill Seekers 等脚本
├── output/                          # ⚠ 临时：Skill Seekers 原始输出（待迁移后删除）
├── Report/                          # Composer 产出的报告（不修改，仅参考）
│
│  ═══════════════════════ 根文件 ═══════════════════════════════
│
├── .env
├── .gitignore
└── .venv/
```

### 各目录职责一览

| 目录 | 职责 | Cursor 消费方式 |
|:-----|:-----|:----------------|
| `.cursor/memory/` | 持久记忆：INDEX（唯一索引）、active_context（进度）、architecture（架构图） | workspace.mdc 路由指向 |
| `.cursor/rules/` | 持久指令：编码约定、路由导航、架构约束 | 自动/智能/globs 加载 |
| `.cursor/skills/` | 领域技能：LiveKit/SVA/Graphiti 等 SKILL.md | 三阶段动态发现 |
| `docs/InfoCollections/` | 人类调研遗产（Opus 22篇 + HumanPlan） | @doc 引用 |
| `docs/references/` | Skill Seekers 详细参考资料 | @doc 引用 |
| `docs/design/` | 设计草稿 | @doc 引用 |
| `docs/specifications/` | 部署规格（阿里云/SRE） | @doc 引用 |
| `agent/` | Python 云端 Agent 代码 | backend-python.mdc globs 触发 |
| `unity_client/` | Unity AR 客户端代码 | unity-client.mdc globs 触发 |
| `infra/` | Docker/LiveKit Server | 按需 |
| `scripts/` | 自动化脚本 | 按需 |
| `output/` | 临时（待迁移后清理） | — |
| `Report/` | Composer 历史报告（不修改） | 仅人类参考 |

## 三、待澄清问题集合 (2026-03-18 遗留)

以下问题在架构设计中暂未明确，需要在进入开发实现或 Phase 3 时进行确认：

### A. 架构与角色
- **A1**: Nanobot 与 Gemini 外部分身是否同时出现在同一聊天室？分工如何？
- **A2**: LobeChat 是否保留？若保留，与 Nanobot 的 Telegram/微信如何分工？
- **A3**: “口令”是指语音指令、密码/凭证，还是唤醒词？

### B. 数据流与同步
- **B1**: Drive 同步外部分身设定/状态：手动同步还是自动同步？
- **B2**: “物体常态信息”的具体范围？Obsidian 同步哪些类型的物体结点？
- **B3**: 资产目录结构、元数据存储，以及与 Drive 的同步策略？

### C. 视觉与 CV
- **C1**: 跨会话 ReID 的优先级？Phase 1 是否需要预留 DINOv2 embedding 持久化设计？
- **C2**: 按图搜图 / 按图联网：自建 embedding 还是只调用外部 API？
- **C3**: 笔记本哨兵的视频源：本机摄像头，还是主 Room 转发的视频流？

### D. Nanobot 改造
- **D1**: Nanobot 的 Scene / Preference 来源：MCP 调用 ParrotCarrier，还是调度器注入？
- **D2**: Nanobot 与任务调度器的具体集成接口与交互协议？

### E. 实施细节
- **E1**: YOLO 哨兵在 `EvidenceAccumulator` 中的具体权重设置？（例如 +0.05 vs +0.15）
- **E2**: DSG Sentinel 的 ModuleManifest 与具体部署方式？
- **E3**: “满血特殊补丁”的触发条件与使用场景是什么？

---

## 五、Cursor 路由方案

### 5.1 workspace.mdc — 第一个全局规则

这是**唯一的 alwaysApply 规则**，作为 Cursor 的 GPS 导航仪：

```yaml
---
description: ParrotCarriers 工作区全局路由与项目概述
globs:
alwaysApply: true
---
```

**内容应包含**：
1. 项目一句话定位
2. 当前阶段（指向 active_context.md）
3. 文件路由表（去哪找什么）
4. 关键约束（服务器在东京、DSG/调度器预留）

**不应包含**：大段架构细节、API 文档（让 Cursor 动态发现）

### 5.2 路由逻辑

```
workspace.mdc (alwaysApply: true)
    │
    ├─→ .cursor/memory/INDEX.md        # 全局索引
    ├─→ .cursor/memory/active_context.md # 当前进度
    │
    ├─→ .cursor/skills/                 # 领域技能（动态发现）
    │
    ├─→ docs/InfoCollections/           # 调研遗产（@doc）
    ├─→ docs/references/                # 参考资料（@doc）
    │
    └─→ 后续按需添加的 .mdc 规则
         ├── architecture.mdc           # 架构约束
         ├── backend-python.mdc         # agent/** 编码约定
         └── unity-client.mdc           # unity_client/** 约定
```

### 5.3 INDEX.md 定位

- **唯一真相源**：所有路径、目录用途、项目入口都以 INDEX.md 为准
- workspace.mdc 只指向 INDEX.md，不重复其内容
- INDEX.md 需同步更新：目录树、服务器决策、active_context 说明

---

## 六、迁移行动清单

### Phase 0：目录整理与路由配置（历史阶段）

| # | 行动 | 优先级 |
|:--|:-----|:-------|
| 1 | 创建 `.cursor/rules/workspace.mdc` | P0 |
| 2 | 更新 `.cursor/memory/INDEX.md`（目录树、服务器决策、路由说明） | P0 |
| 3 | 填充 `.cursor/memory/active_context.md`（当前进度与下一步） | P0 |
| 4 | 创建 `.cursor/skills/` 目录，从 output 迁移 7 个 SKILL.md | P1 |
| 5 | 迁移 output 详细数据 → `docs/references/skill_seekers_output/` 分类存放 | P1 |
| 6 | 重命名 `backend/` → `agent/`（或更新 INDEX 为 backend） | P1 |
| 7 | 补拉 openteach | P2 |
| 8 | 清理 output/ 临时目录 | P2 |

---

## 七、可溯源链接

| 链接 | 用途 | 时效性 |
|:-----|:-----|:-------|
| https://docs.cursor.com/en/context/rules | Cursor Rules 官方文档 | 2026 |
| https://cursor.com/docs/context/skills | Cursor Skills 官方文档 | 2026 |
| https://cursor.com/blog/dynamic-context-discovery | Dynamic Context Discovery 博客 | 2026 |
| https://www.mdskills.ai/specs/skill-md | SKILL.md 开放标准规范 | 2026 |
| https://localskills.sh/blog/cursor-rules-guide | Cursor Rules 2026 社区指南 | 2026 |
| https://forum.cursor.com/t/cursor-2-0-project-rule-mdc-files-with-glob-patterns-not-auto-loaded-in-conversations/140641 | Cursor 2.0 globs 加载 bug 讨论 | 2026 |
| https://dev.to/nedcodes/cursor-rules-vs-skills-whats-the-actual-difference-383b | Rules vs Skills 区别 | 2026 |
