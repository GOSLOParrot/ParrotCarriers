# Web Console Environment Switch Prompt (2026-05-18)

Use this prompt in the Web Console chat when adding settings / connection
support for public ECS vs laptop Castle.

```text
你负责 Web Console 线。先读：

1. codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md
2. codex_workspace/app_web_parallel_workflow_20260513.md
3. codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md
4. codex_workspace/design_workspace/backend_interface_map/app/local_laptop_castle_app_env_20260518.md
5. codex_workspace/design_workspace/backend_interface_map/app/unity_livekit_ecp_sva_data_flow_map_20260515.md
6. codex_workspace/design_workspace/backend_interface_map/web_console/

目标：给 Web Console 增加“环境/连接配置”能力，明确区分 public ECS 和 laptop Castle，不要把 Unity App 的 parrot_config 切换误当成 Web Console 环境切换。

背景事实：
- Unity App 现在有两个测试环境：
  - public ECS: LiveKit `ws://8.216.45.45:7880`, token-mint `:7888`, orchestrator `:7890`, App API `:8790`, room 通常是 `parrot-main`。
  - laptop Castle: LiveKit `ws://192.168.2.4:17880`, token-mint `:17888`, orchestrator `:17890`, App API `:18790`, room `parrot-laptop-main`。
- Unity active config 是 `unity/ArSpike/Assets/ParrotApp/Resources/parrot_config.json`，是 Android build-time 输入，不是运行时热切换。
- Web Console / Obsidian scan / setting-file 管理 / Graphiti-FalkorDB 目标必须由 Web 侧自己的环境配置决定，不能从 Unity phone config 推断。
- local laptop runtime data 在 `codex_workspace/local_runtime/castle_laptop/**`，是 gitignored local lab；public ECS runtime data 在 ECS 上。不要混写。
- secrets 只允许在 server/BFF env 中存在，浏览器 UI 只能显示脱敏 URL、状态和 profile 名称，不能暴露 bearer secret。

请先审计现有 Web Console 配置、后端 BFF、App API facade、Obsidian/setting-file/Graphiti 相关入口，然后生成 TODOList，再实现。

推荐实现顺序：
1. 建立 Web Console server-side environment registry/profile：
   - `ecs`
   - `laptop`
   - profile 里包含 App API base URL、orchestrator URL、token-mint URL、LiveKit URL、room hint、Graphiti/Falkor/Obsidian scan target hint。
   - secrets 只从 env 读取，不进前端 bundle，不进 docs。
2. Web UI 增加环境状态/切换入口：
   - 当前 profile；
   - App API health；
   - RoomSetting snapshot probe；
   - line-profiles/personas probe；
   - orchestrator health / write-auth availability；
   - token-mint probe 只通过 BFF 做脱敏检查；
   - LiveKit URL/room 只显示脱敏摘要，不在浏览器暴露 mint secret。
3. 设置/设定文件/Obsidian scan 操作必须在提交前显示目标环境，防止 local lab 和 ECS 混写。
4. 保持职责分离：
   - RoomSetting/menu CRUD 继续走 App HTTP。
   - LiveKit RPC 只用于 in-room 指令、低延迟状态、ECP/Brain/GOSLO 相关事件，不要重新加入旧 RoomSetting RPC。
   - Web Console 不修改 Unity `parrot_config.json`；Unity config 切换由 App chat 的 `infra/switch-unity-app-config.ps1` 负责。
5. 更新 Web Console 接口文档和共享 TODO，写明 ECS/laptop 两环境差异、测试证据和未完成项。

验收：
- 浏览器看不到任何 bearer secret。
- `ecs` 和 `laptop` profile 的 health/probe 结果清楚可见。
- Web Console 改 RoomSetting / setting refs / Obsidian scan 时能确认目标环境。
- 文档更新到 `backend_interface_map/web_console/` 与共享 TODO。
```
