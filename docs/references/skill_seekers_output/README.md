# Skill Seekers 拉取输出目录

> 用途: 存放 Skill Seekers 从各参考仓库抓取的结构化知识  
> 全面 Skill 列表见 `Report/skill_list_comprehensive.md`  
> 模型: **Gemini 3.1 Pro** 跑仓库

---

## 目录结构

```
skill_seekers_output/
├── README.md                    # 本文件
├── agent/
│   └── nanobot/                 # 辅助参考: 后台 Agent / 子任务 / 多实例 / heartbeat / cron
├── livekit/
│   ├── agent-starter-python/    # P0: 总线骨架起点
│   ├── agents/                  # P0: 核心框架
│   ├── python-agents-examples/  # P0: 50+ Python 示例
│   ├── agents-example-unity/    # P0: Unity Agent 起步模板
│   └── client-sdk-unity/        # P0: Unity SDK
├── sva/
│   └── vision-agents/           # P1: Processor 模式
├── memory/
│   └── graphiti/                # P1: 记忆后端
├── ar/
│   └── openteach/               # P1: 坐标/手势
└── _configs/                    # 拉取配置（可选）
```

---

## 拉取清单（分类 · 作用 · 关键词）

> 完整列表见 `Report/skill_list_comprehensive.md`

### P0 — Phase 1 总线骨架

| 子目录 | 仓库 | 作用 | 拉取关键词 |
|:-------|:-----|:-----|:-----------|
| `livekit/agent-starter-python` | livekit-examples/agent-starter-python | 总线骨架、AGENTS.md、uv、Turn Detector | agent.py, console, download-files |
| `livekit/agents` | livekit/agents | AgentSession、Room、事件模型 | AgentSession, Room, event |
| `livekit/python-agents-examples` | livekit-examples/python-agents-examples | 50+ demo，tool_calling、gemini | tool_calling, gemini, rpc, multimodal |
| `livekit/agents-example-unity` | livekit-examples/agents-example-unity | Unity + Agent、RPC、DataChannel | RegisterRpcMethod, DataChannel, Unity |
| `livekit/client-sdk-unity` | livekit/client-sdk-unity | Unity SDK API | PublishTrack, PerformRpc, Lossy |

### 辅助参考 — 后台 Agent 模式

| 子目录 | 仓库 | 作用 | 拉取关键词 |
|:-------|:-----|:-----|:-----------|
| `agent/nanobot` | HKUDS/nanobot | 后台复杂任务、子代理、多实例、heartbeat、cron、memory consolidation | subagent, gateway, cron, heartbeat, multiple instances |

说明：

- `nanobot` 当前在本项目中是**辅助参考源**
- 主要服务于未来 `nanobot-worker` 的职责审计
- 当前不应取代 LiveKit / Unity / DSG 主技能路线

### P1 — Phase 2/3 核心

| 子目录 | 仓库 | 作用 | 拉取关键词 |
|:-------|:-----|:-----|:-----------|
| `sva/vision-agents` | GetStream/Vision-Agents | Processor 模式、状态注入 | VideoProcessor, attach_agent, add_frame_handler |
| `memory/graphiti` | getzep/graphiti | 记忆后端 | group_id, add_episode, build_communities |
| `ar/openteach` | aadhithya14/Open-Teach | 坐标变换、手势格式 | keypoint_transform, palm_normal, moving_average |

### P2 — Phase 3 DSG 按需

| 子目录 | 仓库 | 作用 |
|:-------|:-----|:-----|
| `dsg/concept-graphs` | concept-graphs/concept-graphs | L2-A 多视角融合 |
| `dsg/spark-dsg` | MIT-SPARK/Spark-DSG | L2-A 节点继承 |
| `scheduler/py-trees` | spooky-npc/py-trees | 行为树调度器 |

---

## 运行命令

需先安装：`pip install skill-seekers skill-seekers[gemini]`  
增强用 **Gemini 3.1 Pro**，见 `Report/usage_and_api_guide.md`

```bash
# 进入项目根目录
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

### 若使用 unified 多源（文档+代码）

```bash
skill-seekers unified --repo-url https://github.com/livekit-examples/agents-example-unity --depth basic --output-dir docs/references/skill_seekers_output/livekit/agents-example-unity
```

### 打包为 Cursor 可用格式

```bash
# 打包为 markdown（通用，放 docs 用 @doc 引用）
skill-seekers package docs/references/skill_seekers_output/livekit/agents-example-unity --target markdown
```

---

## 注意事项

- `multimodal-agent-python` 已归档 (2025-10)，不拉取
- `examples/multimodal-agent` 若在 python-agents-examples 内，会随该仓库一并抓取
- 首次运行建议用 `--code-analysis-depth surface` 快速验证（1–2 分钟）
- `nanobot` 当前已接入主仓路由，但应优先显式调用，不建议作为所有任务的默认主 skill
