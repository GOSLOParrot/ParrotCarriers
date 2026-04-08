# Skill Seekers 操作索引

> 用途：Skill Seekers 拉取流程的操作清单与状态跟踪  
> 更新：2026-04-04  
> 注意：当前索引以本目录现有文件为准；历史归档未在本仓库保留

---

## 一、当前 Skill 状态（P0+P1+辅助）

| # | Skill 名称 | `.cursor/skills/` | `docs/references/` | 状态 |
|:--|:----------|:------------------|:-------------------|:-----|
| 1 | agent-starter-python | ✅ | `livekit/agent-starter-python/` | 已完成 |
| 2 | livekit-agents | ✅ | `livekit/agents/` | 已完成 |
| 3 | python-agents-examples | ✅ | `livekit/python-agents-examples/` | 已完成 |
| 4 | agents-example-unity | ✅ | `livekit/agents-example-unity/` | 已完成 |
| 5 | client-sdk-unity | ✅ | `livekit/client-sdk-unity/` | 已完成 |
| 6 | sva-vision-agents | ✅ | `sva/Vision-Agents/` | 已完成 |
| 7 | graphiti | ✅ | `memory/graphiti/` | 已完成 |
| 8 | nanobot | ✅（项目级窄路由） | `agent/nanobot/` | 已接入，建议显式调用 |
| 9 | ar-mapping (openteach) | ❌ | `ar/openteach/`（待拉） | **待补拉** |

`nanobot` 说明：

- 参考层：`docs/references/skill_seekers_output/agent/nanobot/`
- 路由层：`.cursor/skills/nanobot/`
- 使用方式：优先用于后台 Agent / 子任务 / 多实例 / heartbeat / cron / memory consolidation 审计
- 不建议把整包 `nanobot` 当作所有 Bus 任务的默认主 skill

**P2 按需（暂不拉）**：concept-graphs、spark-dsg、py-trees

---

## 二、SKILL.md description 优化状态

> 当前所有 SKILL.md 的 description 为通用语言，会影响 Cursor 智能触发准确率  
> 待全面审计后人工定制

| Skill | 当前 description | 建议改为 |
|:------|:----------------|:--------|
| livekit-agents | "Use when working with agents" | "Use when implementing AgentSession, RPC, DataChannel, or LiveKit voice pipeline" |
| agent-starter-python | 同上 | "Use when setting up LiveKit agent entry point, worker config, or uv environment" |
| python-agents-examples | 同上 | "Use when looking for LiveKit tool_calling, gemini, rpc, multimodal examples" |
| agents-example-unity | 同上 | "Use when building Unity + LiveKit RPC integration, RegisterRpcMethod, DataChannel" |
| client-sdk-unity | 同上 | "Use when working with Unity LiveKit SDK, PublishTrack, PerformRpc, Lossy packets" |
| sva-vision-agents | 同上 | "Use when implementing VideoProcessor, attach_agent, or frame handler pipeline" |
| graphiti | 同上 | "Use when implementing memory backend, group_id, add_episode, or build_communities" |

---

## 三、下一步操作

- [x] 接入 `HKUDS/nanobot`：
  - 已建立 `docs/references/skill_seekers_output/agent/nanobot/`
  - 已建立 `.cursor/skills/nanobot/SKILL.md`
  - 已建立 `NANOBOT_LOCATION_AND_ROUTING_REPORT.md`

- [ ] 补拉 `openteach`（P1）：
  ```
  skill-seekers github --repo aadhithya14/Open-Teach --output docs/references/skill_seekers_output/ar/openteach --code-analysis-depth medium
  ```
  然后手动将 SKILL.md 复制到 `.cursor/skills/ar-mapping/SKILL.md`

- [ ] 定制 7 个 SKILL.md 的 description（人工审计后执行）

- [ ] 后续视审计结果决定：
  - 是否把 `nanobot` 再拆成更窄的项目专用 skill
  - 是否补充 `nanobot-worker` 专用 tasks 路由

- [ ] P2 按需拉取（Phase 3 DSG 阶段才需要）：concept-graphs、spark-dsg、py-trees

---

## 四、参考资料

- **全面 Skill 清单**（含 P0/P1/P2 拉取命令）：`docs/InfoCollections/SkillSeekers/skill_list_comprehensive.md`
- **模型选择与 API 成本**：当前仓库未保留独立归档文档
- **脚本审计**：当前仓库未保留独立归档文档
- **详细参考数据**：`docs/references/skill_seekers_output/`
- **nanobot 路由说明**：`docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md`
