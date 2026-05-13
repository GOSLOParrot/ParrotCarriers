# App/Web Chat Start Prompts (2026-05-13)

Owner: coordination
Status: active
Category: startup prompts
Scope: Unity App chat and Web Console chat handoff
Sources:
- `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
- `codex_workspace/app_web_parallel_workflow_20260513.md`
- `codex_workspace/codex_skills/MIGRATION_STATUS_20260513.md`
- `codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md`
- `codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md`

Use these prompts by copying one into a new Codex chat. The dedicated chat owns
its own TODO list, decisions, and implementation order after it starts.

## Unity App Chat Prompt

Inventory rule for this prompt: the formal Unity App center is
`unity/ArSpike/Assets/ParrotApp/**`. Do not recreate
`Assets/Scripts/ParrotApp/**`, top-level App-owned `Assets/Resources`,
top-level `Assets/UI`, top-level `Assets/Models`, or
`Assets/Scenes/SampleScene.unity`. The only allowed top-level
`Assets/Resources` content is the LiveKit SDK-generated
`LiveKitSdkVersionInfo.txt`.
After Unity directory, scene, resource, model, art, or Build Settings changes,
update the inventory SSOT and App TODO status in the same turn.
`Assets/ParrotApp/Runtime/Scripts/UI/AppV1MetaUiController.cs` is a legacy
Smoke/reference UI controller, not formal homepage completion evidence; use it
only after reading the inventory SSOT classification.

```text
你是 Unity App 前端线的 Codex。工作目录是 D:\GOSLOParrot\ParrotCarriers。

先读这些共享路线文件，不要跳过：
- codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md
- codex_workspace/app_web_parallel_workflow_20260513.md
- codex_workspace/codex_skills/MIGRATION_STATUS_20260513.md
- codex_workspace/design_workspace/backend_interface_map/app/unity_project_inventory_app_ssot_20260513.md
- .cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md
- codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md

必须显式使用/读取这些 direct Codex skills 或对应源技能后再写相关代码：
- ar-foundation-api
- ar-foundation-samples
- client-sdk-unity
- livekit-unity-lifecycle
- livekit-unity-video-publish
- graphiti（只在 App 触及 Ref/Graphiti UUID/记忆连接时）
- dsg-l2b-node-organization-options（只在 App 触及 Ref/Red String/Evidence Board/L2-B 关系时）

本 Chat 只负责 Unity App 线。你不要替 Web Console 定 TODO，也不要把 Web-only 管理接口写进 App DTO。

先和我确认 App 线的 Step 1 TODO，再写入：
- codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md 的 App lane
- codex_workspace/design_workspace/backend_interface_map/app/ 下的业务接口文件

第一阶段关注：
1. 启动页流程：RoomSetting、Maid Team、Line、Room/Profile、Persona/Model/Scene、画布菜单入口的边界。
2. 画布菜单：先复用核心选择/Ref/Edge 数据边界；不要把具体渲染器写死成唯一方案。
3. LiveKit 连接稳定性审计：已有策略、Room reconnect、pause/resume、token/secret 注入、HUD 状态。
4. 启动页前端设计和素材审计。
5. 简单进度条/加载动画占位。
6. 主页加载：启动页结束时主页需要已经准备好的模块、状态、资源、连接。
7. App 侧 Ref 连接：支持未来 2D 工作区/Red String/Evidence Board 的局部功能，但只通过共享候选接口，不直接写 Graphiti/FalkorDB。

如果发现共享核心接口缺失，只写到 core_interface_candidate_queue_20260513.md；不要直接改 .cursor/memory/architecture/Interface/**。核心接口必须等 App/Web 双线确认后再入 SSOT。

每次写文档遵守 app_web_parallel_workflow_20260513.md 的 Doc Hygiene：优先更新已有文件，新文件必须有 owner/status/category/scope/source。
```

## Web Console Chat Prompt

```text
你是 Web Console 前端/控制台线的 Codex。工作目录是 D:\GOSLOParrot\ParrotCarriers。

先读这些共享路线文件，不要跳过：
- codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md
- codex_workspace/app_web_parallel_workflow_20260513.md
- codex_workspace/codex_skills/MIGRATION_STATUS_20260513.md
- .cursor/memory/architecture/Interface/app_web_parallel_routes_agent_team_20260513.md
- codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md
- codex_workspace/design_workspace/backend_interface_map/web_console/graphiti_management_business_flow_20260513.md

必须显式使用/读取这些 direct Codex skills 或对应源技能后再写相关代码：
- graphiti
- dsg-rustworkx-master
- dsg-l1-5-l2a-conceptgraph-distilled
- dsg-l2b-node-organization-options
- dsg-attention-schema-papers（涉及 attention/decay/memory validity 时）
- py-trees
- nanobot
- nanobot-overview
- parrot-bus-orchestration
- livekit-agents（涉及 server-side agent/LiveKit Agents 时）

本 Chat 只负责 Web Console 线。你不要替 Unity App 定 TODO，也不要把 Web-only operator/admin 接口塞进 App DTO。

先和我确认 Web 线的 Step 1 TODO，再写入：
- codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md 的 Web lane
- codex_workspace/design_workspace/backend_interface_map/web_console/ 下的业务接口文件

第一阶段关注：
1. Web Console 需求概括、信息架构、美学方向、实现 TODOList。
2. ECS/module health 和 orchestrator /status 控制台骨架；注意有 PARROT_ORCH_SECRET 时 /status 需要 Bearer。
3. L1.5 管理、L2-B 可视化、节点 CRUD、照片管理。
4. Blackboard、IntentWorkspace、Plan/task、Scheduler、Nanobot、AgentTeam/Maid Team 状态监控。
5. GOSLO/Nanobot 协作、聊天室方案、任务调度器监控。
6. Graphiti/FalkorDB 管理：支持读、搜索、分区、可视化、Episode、Graphiti API 级节点/边/事实手术；FalkorDB 直写只做 Web operator 模式，带 dry-run/audit/backup 思路。
7. Web 版 Evidence/String Board：和 App 共用 Ref/Edge 数据模型，但 Web 渲染器可独立选择。

如果发现共享核心接口缺失，只写到 core_interface_candidate_queue_20260513.md；不要直接改 .cursor/memory/architecture/Interface/**。核心接口必须等 App/Web 双线确认后再入 SSOT。

每次写文档遵守 app_web_parallel_workflow_20260513.md 的 Doc Hygiene：优先更新已有文件，新文件必须有 owner/status/category/scope/source。
```
