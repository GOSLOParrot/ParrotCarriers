# ParrotCarriers 全面 Skill 列表

> 生成日期: 2026-02-28  
> 来源: docs/InfoCollections/Opus/ 全量审计  
> 用途: Skill Seekers 拉取清单、模型分配、存放位置

---

## 一、审计依据

基于 Opus 22 个文档的交叉引用，重点来源：

| 文档 | 贡献 |
|:-----|:-----|
| `03_reference_projects.md` | 参考项目与 Skill 映射 |
| `07_skills_design.md` | 4 个核心 Skill 设计 |
| `17_dsg_node_and_trigger_design.md` | 各层学习对象、Phase 路线图 |
| `22_research_sources_and_traceability.md` | 待拉取仓库、溯源 URL |
| `06_goals_and_roadmap.md` | Phase 0–3 任务依赖 |

---

## 二、模型分配策略（已确定）

| 用途 | 模型 | 说明 |
|:-----|:-----|:-----|
| **Skill Seekers 跑仓库** | **Gemini 3.1 Pro** | 代码分析、架构理解、模式提取，质量最高 |
| **其他资源文档 / enhance** | Gemini 2.5 Flash | 成本低，文档增强、常规任务 |
| **直接 @doc 引用** | 无需 Skill | 放 `docs/references/`，按需引用 |

---

## 三、全面 Skill 列表（按 Phase 与优先级）

### 3.1 P0 — Phase 1 总线骨架（必生成）

| # | Skill 名称 | 仓库 | 作用 | 关键词 |
|:--|:----------|:-----|:-----|:-------|
| 1 | **agent-starter-python** | livekit-examples/agent-starter-python | 总线骨架起点、AGENTS.md、uv、Turn Detector | `agent.py` `console` `download-files` |
| 2 | **livekit-agents** | livekit/agents | AgentSession、Room、事件模型、RPC | `AgentSession` `Room` `event` |
| 3 | **python-agents-examples** | livekit-examples/python-agents-examples | 50+ demo、Tool Calling、RPC、Gemini Live Vision | `tool_calling` `gemini` `rpc` `multimodal` |
| 4 | **agents-example-unity** | livekit-examples/agents-example-unity | Unity + Agent、RPC 注册、DataChannel | `RegisterRpcMethod` `DataChannel` `Unity` |
| 5 | **client-sdk-unity** | livekit/client-sdk-unity | Unity SDK、PublishTrack、PerformRpc、Lossy | `PublishTrack` `PerformRpc` `Lossy` |

### 3.2 P1 — Phase 2/3 核心（应生成）

| # | Skill 名称 | 仓库 | 作用 | 关键词 |
|:--|:----------|:-----|:-----|:-------|
| 6 | **sva-vision-agents** | GetStream/Vision-Agents | Processor 模式、attach_agent、状态注入 | `VideoProcessor` `attach_agent` `add_frame_handler` |
| 7 | **graphiti** | getzep/graphiti | 记忆后端、group_id、build_communities、add_episode | `group_id` `add_episode` `build_communities` |
| 8 | **ar-mapping** | aadhithya14/Open-Teach | 坐标变换、手势格式、ZMQ/DataChannel 参考 | `keypoint_transform` `palm_normal` `moving_average` |

### 3.3 P2 — Phase 3 DSG（按需生成）

| # | Skill 名称 | 仓库 | 作用 | 关键词 |
|:--|:----------|:-----|:-----|:-------|
| 9 | **concept-graphs** | concept-graphs/concept-graphs | L2-A 多视角融合、class_id 投票、LLM 关系 | `clip_ft` `MapObjectList` `vote` |
| 10 | **spark-dsg** | MIT-SPARK/Spark-DSG | L2-A 节点继承、DsgLayers、Khronos | `NodeAttributes` `SemanticNodeAttributes` `DsgLayers` |
| 11 | **py-trees** | spooky-npc/py-trees | 行为树调度器、Selector、Blackboard | `Selector` `memory` `Blackboard` |

### 3.4 文档 / @doc 即可（不生成 Skill）

| 资源 | 形式 | 说明 |
|:-----|:-----|:-----|
| **gemini-realtime** | 文档 | 通过 LiveKit 插件使用，参考 python-agents-examples |
| **OpenClaw SOUL** | 文档 | ParrotSoul 人格设计，Phase 3 人格时参考 |
| **FROSS / GraphRAG / 3DSSG** | 概念 | 取设计思路，不拉仓库 |
| **AR Foundation / XR Hands** | Unity 文档 | 官方文档 @doc 引用 |
| **RustworkX** | 依赖库 | pip 安装，DSG 图实现用，无需 Skill |

---

## 四、Skill Seekers 拉取命令（Gemini 3.1 Pro enhance）

### 4.1 环境准备

```bash
pip install skill-seekers skill-seekers[gemini]
export GOOGLE_API_KEY=your_key
# 若用 Gemini 3.1 Pro，需在 enhance 时指定（Skill Seekers 若支持 --model）
```

### 4.2 P0 + P1 全拉（8 个 Skill）

```bash
cd D:\GOSLOParrot\ParrotCarriers

# P0
skill-seekers github --repo livekit-examples/agent-starter-python --output docs/references/skill_seekers_output/livekit/agent-starter-python --code-analysis-depth medium
skill-seekers github --repo livekit/agents --output docs/references/skill_seekers_output/livekit/agents --code-analysis-depth medium
skill-seekers github --repo livekit-examples/python-agents-examples --output docs/references/skill_seekers_output/livekit/python-agents-examples --code-analysis-depth medium
skill-seekers github --repo livekit-examples/agents-example-unity --output docs/references/skill_seekers_output/livekit/agents-example-unity --code-analysis-depth medium
skill-seekers github --repo livekit/client-sdk-unity --output docs/references/skill_seekers_output/livekit/client-sdk-unity --code-analysis-depth medium

# P1
skill-seekers github --repo GetStream/Vision-Agents --output docs/references/skill_seekers_output/sva/vision-agents --code-analysis-depth medium
skill-seekers github --repo getzep/graphiti --output docs/references/skill_seekers_output/memory/graphiti --code-analysis-depth medium
skill-seekers github --repo aadhithya14/Open-Teach --output docs/references/skill_seekers_output/ar/openteach --code-analysis-depth medium
```

### 4.3 P2 按需拉取（3 个 Skill）

```bash
skill-seekers github --repo concept-graphs/concept-graphs --output docs/references/skill_seekers_output/dsg/concept-graphs --code-analysis-depth surface
skill-seekers github --repo MIT-SPARK/Spark-DSG --output docs/references/skill_seekers_output/dsg/spark-dsg --code-analysis-depth surface
skill-seekers github --repo spooky-npc/py-trees --output docs/references/skill_seekers_output/scheduler/py-trees --code-analysis-depth surface
```

### 4.4 增强（enhance）— 使用 Gemini 3.1 Pro

```bash
# 若 Skill Seekers 支持 --provider google --model gemini-3.1-pro
skill-seekers enhance docs/references/skill_seekers_output/livekit/agent-starter-python --provider google --mode api
# ... 对每个 output 目录执行

# 或批量（需脚本）
for dir in docs/references/skill_seekers_output/livekit/* docs/references/skill_seekers_output/sva/* docs/references/skill_seekers_output/memory/* docs/references/skill_seekers_output/ar/*; do
  skill-seekers enhance "$dir" --provider google --mode api
done
```

### 4.5 打包为 Cursor 可用格式

```bash
# Markdown 通用（放 docs 用 @doc）
skill-seekers package docs/references/skill_seekers_output/livekit/agent-starter-python --target markdown

# Claude Skill 格式（转 .cursor/skills/）
skill-seekers package docs/references/skill_seekers_output/livekit/agent-starter-python --target claude
```

---

## 五、输出目录结构

```
docs/references/skill_seekers_output/
├── livekit/
│   ├── agent-starter-python/    # P0
│   ├── agents/                  # P0
│   ├── python-agents-examples/  # P0
│   ├── agents-example-unity/    # P0
│   └── client-sdk-unity/        # P0
├── sva/
│   └── vision-agents/           # P1
├── memory/
│   └── graphiti/                # P1
├── ar/
│   └── openteach/               # P1
├── dsg/                         # P2 按需
│   ├── concept-graphs/
│   └── spark-dsg/
└── scheduler/
    └── py-trees/                # P2 按需
```

---

## 六、数量汇总

| 类型 | 数量 | 说明 |
|:-----|:-----|:-----|
| **P0 必生成** | 5 | Phase 1 总线骨架 |
| **P1 应生成** | 3 | Phase 2/3 核心 |
| **P2 按需** | 3 | Phase 3 DSG 深入 |
| **合计** | **8–11** | 建议先完成 P0+P1 共 8 个 |

---

## 七、与 Opus 07_skills_design 的对应

| Opus 07 设计 | 本列表 | 说明 |
|:-------------|:-------|:-----|
| livekit-agents | livekit-agents + agent-starter-python + python-agents-examples + agents-example-unity + client-sdk-unity | 拆分为 5 个更细粒度 Skill |
| sva-processors | sva-vision-agents | 同义 |
| gemini-realtime | 文档 / python-agents-examples 内 | 不单独生成 |
| ar-mapping | ar-mapping (OpenTeach) | 同义 |
