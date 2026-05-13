---
status: ratified
category: codex-handoff
last_reviewed: 2026-05-12
ai_priority: high
ai_audience: "Codex agent (in codex_workspace/) — 文档搬迁 + Unity 前端落地 + 持续维护清单"
parent_doc: "INDEX.md"
related:
  - "../ecs_orchestrator_lifecycle_completion_20260512.md (升级完成报告 — 先读这份再读本文件)"
  - "../ecs_audit_prompt_for_castle_20260512.md (ECS 端审计 prompt — 不归你管，仅作上下文参考)"
  - "../backend_interface_refinement_20260507.md (Brain Core SSOT — 你需要往里加 §X)"
  - "audit_log_index_20260511.md (Round 5 五轮审计索引 — 你需要往里加一行 ECS 升级条目)"
  - "../../INDEX.md (顶层索引 — §1.1 active 表你需要登记一行新文档)"
  - "menu_design_complete_20260507.md (菜单设计 SSOT — Tier UI 渲染规范要并入)"
---

# Codex 指导：ECS Orchestrator 升级落地 + SSOT 搬迁（2026-05-12）

> **你的任务（Codex）**：
> 1. **读** `ecs_orchestrator_lifecycle_completion_20260512.md`（升级背景）+ `Interface/audit_log_index_20260511.md`（前置 Round 5）
> 2. **搬迁** §A — 把本次升级的协议 / 接口字段并入 4 份 SSOT
> 3. **前端落地** §B — Unity App 启动页 + 菜单 Tier 渲染 + Web monitor 拼装
> 4. **持续维护** §C — 标 P3 待办 / 列回归 chat 必读清单
>
> **本文档不修改 Phase 4 §8 wire 13 锁、ADR-L1.5-001、cs_parity 4/4。** 只动控制面。

---

## §A 文档搬迁清单（Codex 必做）

### A-1 在 `Interface/INDEX.md` 注册新文档

往 `## Active Interface Docs` 表加 1 行（保持字母序或贴在 `app_v1_brain_cold_start_line_lifecycle_audit_20260511.md` 下）：

```markdown
| `../ecs_orchestrator_lifecycle_completion_20260512.md` | active / completion-report | ECS Orchestrator + Tier 化设置 + systemd 升级完成报告（控制面，Round 5 后续阶段；与 audit_log_index_20260511.md 同源） |
| `ecs_orchestrator_codex_guidance_20260512.md` | active / codex-handoff | 本文件 — 搬迁清单 + Unity 前端落地清单 + 持续维护清单 |
```

把 `INDEX.md` frontmatter 的 `last_reviewed` 改成 `2026-05-12`。

### A-2 在 `audit_log_index_20260511.md` 加一行后续条目

`## 1. 五轮审计入口` 表后面加 §1.bis：

```markdown
## 1.bis Round 5 后续阶段（控制面升级，2026-05-12）

| 阶段 | 焦点 | 文档 |
|:---|:---|:---|
| Phase 1-5 | ECS Orchestrator + Tier 化设置 + systemd + 容器化 + 失败传播路径硬化 | [`../ecs_orchestrator_lifecycle_completion_20260512.md`](../ecs_orchestrator_lifecycle_completion_20260512.md) |

Round 5 暴露的 Bug L/M/N/O 是**症状**；Phase 1-5 是把"没有控制面"这个**结构性根因**补上：runtime_config.json 配置层级、setting_change_tier 注册表、orchestrator HTTP API + Bearer、systemd 托管、限频重启、boot preflight、crash hook、forceUnityReconnect RPC。
```

### A-3 在 `backend_interface_refinement_20260507.md` 加 §6（Brain 控制面公开 API）

放在文件末尾、`§5 L2-B baseline` 之后。要写的内容：

```markdown
## §6 Brain Control-Plane API（2026-05-12 新增 — Phase 1-5）

### §6.1 配置层级（file > BB > env > default）

| 层 | 入口 | 谁写 | 谁读 |
|:---|:---|:---|:---|
| file | `data/runtime_config.json` | `parrot.castle.runtime_config.write_runtime_config(...)`（仅 orchestrator） | `parrot.castle.runtime_config.resolve_runtime_config()` |
| BB | `global/brain_runtime_snapshot` | Brain 启动时 `write_brain_runtime_snapshot()` | Brain `_resolve_pipeline()`、orchestrator `/status` |
| env | `.env` `PARROT_LLM_PIPELINE` | 运维（fallback only） | `_resolve_pipeline()` 兜底 |
| default | `line_a` + 默认 LineProfile | 代码 | 兜底 |

**重要**：`running_line_id()` 故意忽略 BB（避免 Round 5 Bug O）；`active_line_id()` 仍 BB-first（用户面）。

### §6.2 新 RPC

| RPC name | Owner | Caller | 用途 |
|:---|:---|:---|:---|
| `forceUnityReconnect` | Brain (room.local_participant) | orchestrator → BB marker → Brain self-call | Tier 1 触发 LiveKit room disconnect → Unity 拿新 token 重连，新 entrypoint 读到新 line_id / room_profile_id |

返回结构：
```json
{
  "status": "ok",
  "reason": "<orchestrator 传入>",
  "request_id": "<可选>",
  "next": { "line_id": "...", "line_profile_id": "...", "room_profile_id": "..." },
  "note": "..."
}
```

### §6.3 Setting Change Tier 注册表

`data/registries/setting_change_tier.json` — 24 项 setting × Tier 0-3。Brain 端通过 `parrot.brain.setting_change_tier`：

```python
from parrot.brain.setting_change_tier import (
    tier_for, tier_label, tier_summary, tier_ui_action,
    line_switch_tier_for_profile,
)
```

`RoomSettingService.compatibility()` 已暴露 `tier` / `tier_label` / `tier_summary` / `tier_ui_action` 字段，前端可直接渲染。

### §6.4 BB 新 key

| key | 写者 | 内容 |
|:---|:---|:---|
| `global/brain_runtime_snapshot` | Brain entrypoint / disconnect | `{pid, room_name, started_at, line_id, line_profile_id, room_profile_id}` |
| `global/brain_boot_preflight` | `parrot.brain.boot_preflight` | `{redis_ok, photo_upload_port_in_use, runtime_config_valid, started_at}` |
| `global/brain_last_crash` | `parrot.brain.crash_hook` | `{exception_type, message, traceback, ts, pid, kind: "sync"|"async"}` |
| `global/orchestrator_force_reconnect_marker` | orchestrator `/force_unity_reconnect` | `{request_id, reason, ts}` — Brain 轮询触发本地 RPC |

### §6.5 Castle Orchestrator HTTP API

见 `ecs_orchestrator_lifecycle_completion_20260512.md` §3。Python 客户端：

```python
from parrot.castle.orchestrator.client import OrchestratorClient
client = OrchestratorClient(base_url="http://localhost:7890", secret=os.getenv("PARROT_ORCH_SECRET"))
client.set_active_line("line_b")
status = client.status()
```
```

### A-4 在 `menu_design_complete_20260507.md` 加 Tier UI 章节

放在 §"启动页 / 主菜单" 末尾（如果你的章节命名不同，往最后加亦可）：

```markdown
## §X Setting Change Tier 渲染规范（2026-05-12 新增）

每个菜单项决定执行时，前端必须读 `RoomSettingService.compatibility()` 返回的 `tier` 字段，按下表渲染：

| Tier | tier_ui_action | UI 行为 |
|:---:|:---|:---|
| 0 | `silent_apply` | 写完 BB 后 toast "已应用"；不弹窗 |
| 1 | `confirm_reconnect` | 弹"切换需要重连，预计 3-5s 不可用"对话框 → 用户确认后写 runtime_config.json + 调 `forceUnityReconnect` → 监听 room reconnected → toast "切换完成" |
| 2 | `confirm_process_restart` | 弹"切换需要重启 Brain，预计 5-10s 不可用"对话框 → 用户确认后调 orchestrator `/restart_component` → 轮询 `/status.processes.brain.alive` → toast |
| 3 | `block` | 弹"此设置需要运维操作 ECS"非阻塞提示 → 不允许在 App 内触发 |

C# 镜像与决策映射：`unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/SettingChangeTierDto.cs`（已就位，含 `SettingChangeTierUiHelper.Decide()`）。
```

### A-5 在顶层 `.cursor/memory/INDEX.md` §1.1 active 表加一行

按硬规则（H2）登记新顶层文档：

```markdown
| `architecture/ecs_orchestrator_lifecycle_completion_20260512.md` | **ECS Orchestrator + Lifecycle 升级完成报告（2026-05-12）** — Tier 化设置 / orchestrator :7890 / systemd / 容器化 / boot preflight / crash hook / 限频重启；Round 5 后续阶段（控制面） |
```

`active_context.md` 头部建议加一段（不强制）：

```markdown
> **🟢 2026-05-12**：ECS Orchestrator + Lifecycle Audit Phase 1-5 落地 — runtime_config.json 配置层级 + setting_change_tier 注册表 + orchestrator (:7890) HTTP API + Bearer + systemd 5 unit + Brain 容器化（profile-gated）+ boot preflight + crash hook + 限频重启。详见 [`architecture/ecs_orchestrator_lifecycle_completion_20260512.md`](architecture/ecs_orchestrator_lifecycle_completion_20260512.md) + [`architecture/Interface/ecs_orchestrator_codex_guidance_20260512.md`](architecture/Interface/ecs_orchestrator_codex_guidance_20260512.md)。Round 5 18 bug + 1 gap 之后的下一阶段控制面收口；数据面零漂移。
```

### A-6 不要碰的（保留）

- Phase 4 §8 wire 13 锁
- ADR-L1.5-001 决策
- `protocol_snapshot_p4.md` enum / topic 主体（控制面不进协议）
- `bus_v4.md` 拓扑（Bus topology 没变）
- `cs_parity` 4/4 守护
- `frontend_workspace_boundary.md`（边界规则没变；本次改动属于 H1 范畴：动了 `src/parrot/**` 公开签名 — Brain 加 `forceUnityReconnect` RPC、Brain 加 `parrot.brain.setting_change_tier` 模块。理由已在 commit msg + 完成报告 §8 写明）

---

## §B Unity 前端落地清单（你 / Codex 主导）

按优先级降序：

### B-1 启动页 Line / RoomProfile 选择 → orchestrator API 接通【**P2.5 必做**】

**当前现状**（Round 4）：启动页 RPC `applyRoomProfile` 走 Brain 直连；切线在 Round 5 之前是改 .env 重启 Brain。
**升级后期望**：
- 启动页用户选 Line / RoomProfile → 调 orchestrator `/set_active_line` 或 `/apply_room_profile`（用 `parrot_config.json` 里的 orchestrator URL + Bearer）
- 渲染 tier 弹窗（按 §A-4 表）
- Tier 1 走 confirm_reconnect → 等 LiveKit room reconnected → 进入 HUD
- Tier 2 走 confirm_process_restart → 调 `/restart_component` → 轮询 `/status` 直到 brain.alive

**新核心接口（要写入你的 SSOT）**：
- `OrchestratorClient.SetActiveLineAsync(string lineId)` (C#)
- `OrchestratorClient.ApplyRoomProfileAsync(string roomProfileId, ...)` (C#)
- `OrchestratorClient.GetStatusAsync()` (C#)
- `OrchestratorClient.RestartComponentAsync(string component)` (C#)

**Resources/parrot_config.json 字段**（建议新增）：
```json
{
  "orchestrator_url": "http://<castle-ip>:7890",
  "orchestrator_secret": "<from build-time env>"
}
```

> 安全注意：`orchestrator_secret` 不要硬编码到 Resources；后续考虑跟 mint_secret 一样走 build-time 注入或开发期 .gitignore 占位。

### B-2 主菜单 Tier UI 渲染【**P2.5 必做**】

把 §A-4 的 tier × ui_action 表落到 Unity menu canvas 上：
- 读 `RoomSettingService.compatibility()` 的 `tier` 字段（已有 RPC）
- 按 tier 切换 `MenuItemView` 的执行行为（silent / confirm_reconnect / confirm_process_restart / block）
- C# 决策辅助类已就位：`SettingChangeTierUiHelper.Decide(SettingChangeTierDto)`

**Codex 你要做的具体事**：
- 设计 4 种 tier 弹窗 prefab（无需新 wire；只读 BB + 调 orchestrator API）
- 把 `MenuItemView` 的 `OnSelected()` 接 tier 决策
- HUD 里加一个常驻"当前运行中 line / profile"badge，数据源 `/status.brain_runtime_snapshot`

### B-3 Web monitor / 调试面板【**P3 P3 期 Web Console chat 接管**】

`/status` 端点已经聚合好所有运维需要的字段。Web 控制台 chat（已在 `chat_launches/web_console_launch_20260509.md`）应该把：
- `runtime_config` / `brain_runtime_snapshot` / `selection_drift` 三件套
- `processes` 心跳表
- `containers` docker compose ps 解析
- `brain_boot_preflight` + `brain_last_crash` + `restart_stats`

做成只读 dashboard。**不**要在 Web monitor 暴露写操作（Bearer 漏出风险），写操作走 Cursor / Cursor agent CLI。

### B-4 Phone 真连测试【**P2.5 必做 — 你或我 + 真机**】

升级后必须真机验证一次：
1. 启动页选 Line A → 进 HUD → 切到 Line B → 看到 tier 1 弹窗 → 确认 → reconnect → HUD 重出现 + GOSLO 用 Line B 行为响应
2. 启动页选已保存的 RoomProfile → 进 HUD → 看 HUD badge 是否反映正确 line/profile
3. 故意让 Brain crash（kill -9）→ orchestrator 5/300s 内会自动 systemd restart Brain → Unity 自动 reconnect → 看 `/status.brain_last_crash` 有 traceback

---

## §C 持续维护 / 后续审查【Cursor + Codex 联手】

### C-1 安全 hardening（待 P2.5 末或 P3 初）

- `orchestrator_secret` 不要走 Resources 明文 → 与 `mint_secret` 同等待遇（build-time 注入或安卓 keystore）
- `LIVEKIT_URL` 内外分流：拆 `LIVEKIT_PUBLIC_URL`（手机）/ `LIVEKIT_INTERNAL_URL`（Brain），减少 Brain 穿一次 NAT 的延迟。**待 P3 网络优化 chat 接管**。

### C-2 滚动重启完善（P3）

`parrot-brain@.service` 模板已就位 + `/rolling_restart_brain` API 就位，但**实际场景下双 Brain 同 Room 抢 identity**。需要一个 client_router：
- LiveKit dispatch agent_name 改成 `parrot-brain-1` / `parrot-brain-2`
- token-mint 在签发时按当前活跃版本路由
- 完整无停机升级是 P3 任务，当前是"轻 downtime"模式

### C-3 Nanobot 容器化（P3）

Maid + GOSLO Chat 当前走 systemd + Python venv。docker-compose.yml 暂未定义 maid / goslo-chat profile。如果 P3 要做 nanobot 隔离 / k8s 化，需要：
- 给 nanobot fork 写 Dockerfile
- docker-compose.yml 加 `maid` / `goslo-chat` profile
- 手机不连这两个，所以风险低，按需推进

### C-4 回归 chat 入场必读清单

任何后续触及 `src/parrot/castle/**` / `src/parrot/brain/{boot_preflight,crash_hook,setting_change_tier,room_setting,line_status}.py` / `infra/{systemd,docker-compose.yml}` / `data/runtime_config.json` / `data/registries/setting_change_tier.json` 的 chat **入场必读**：

1. `ecs_orchestrator_lifecycle_completion_20260512.md`（升级背景）
2. 本文件 §A 搬迁清单 + §B 前端落地状态
3. `audit_log_index_20260511.md` Round 5（前置 audit）
4. `infra/systemd/README.md`（unit 设计意图）

不读这四份就动相关代码 = 大概率重复 Round 5 之前的"没有控制面"问题。

### C-5 测试守护（你帮看）

Cursor 端 176 castle/brain 测试已绿。但如果你（Codex）在 Unity 端改 `SettingChangeTierDto` / `OrchestratorClient` C# 实现，**请同步**：
- `tests/test_castle/test_setting_change_tier.py` — 看 `RoomCompatibilityReport.tier_*` 字段名是否一致
- `tests/test_castle/test_runtime_config.py` — 看 `forceUnityReconnect` RPC 返回结构

如果字段名漂移，请回 Cursor 这边的 audit chat 报一下，我会在下一轮 Round 6 audit 里收口。

---

## §D 总结：你（Codex）这一轮的产出物

完成本指导后，**新增/改动**清单：

- ✏️ 改 `Interface/INDEX.md`（注册 2 份新文档）
- ✏️ 改 `Interface/audit_log_index_20260511.md`（加 §1.bis 后续阶段）
- ✏️ 改 `backend_interface_refinement_20260507.md`（加 §6 Brain Control-Plane API）
- ✏️ 改 `Interface/menu_design_complete_20260507.md`（加 §X Tier UI 渲染规范）
- ✏️ 改 `.cursor/memory/INDEX.md` §1.1（登记新文档）
- ✏️ 改 `active_context.md` 头部（加 2026-05-12 标记，可选）
- ➕ 新建 Unity C# OrchestratorClient + 4 种 tier 弹窗 prefab + HUD badge
- ➕ 接 启动页 / 菜单 → orchestrator API
- 🟡 标 P3 待办（C-1/C-2/C-3）

**不需要碰**：Cursor 端 Python 代码、Phase 4 §8 锁、协议 wire、ADR、cs_parity 守护。

读完本文件后请**先读** `ecs_orchestrator_lifecycle_completion_20260512.md`（200 行报告）再动手。

— end —

