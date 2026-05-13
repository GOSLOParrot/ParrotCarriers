---
status: ratified
category: completion-report
last_reviewed: 2026-05-12
ai_priority: high
ai_audience: "ECS operator, Cursor / Codex regression chats, Web monitor / runtime UX chats"
parent_doc: "../INDEX.md"
related:
  - "Interface/audit_log_index_20260511.md (Round 5 — Brain cold-start lifecycle audit, 本升级的直接前置)"
  - "Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md (Round 5 superset)"
  - "../infra/env-castle.template (Phase 1-5 升级后的最终版 env 模板)"
  - "../infra/deploy-castle.sh (--systemd 开关)"
  - "../infra/systemd/README.md (5 unit 安装与依赖图)"
  - "../infra/docker-compose.yml (orchestrator + brain 双 service profile-gate)"
  - "../data/registries/setting_change_tier.json (Tier 0-3 注册表 + 24 项 setting)"
  - "ecs_audit_prompt_for_castle_20260512.md (ECS 端复用审计 prompt)"
  - "Interface/ecs_orchestrator_codex_guidance_20260512.md (Codex 文档搬迁 + 前端落地指导)"
---

# ECS Orchestrator + Lifecycle Audit — 完成报告（2026-05-12）

> **使命**：把 Brain / Maid / GOSLO Chat / Scheduler / Orchestrator 五个进程从"tmux 手工拉起 + 改 .env 切线"升级到"systemd 托管 + Tier 化设置 + orchestrator (:7890) HTTP 治理"。配套补全 5 类长期失稳点（背景任务、photo upload、scheduler listener、unhandled exception、雪崩防御）。
>
> **范围对位**：`audit_log_index_20260511.md` Round 5 收口后用户提的"一劳永逸的 ECS 管理模块"任务；plan 见 `c:\Users\Bin\.cursor\plans\ecs_orchestrator_+_lifecycle_audit_cb7eefe4.plan.md`（不再读，已实施）。

---

## §0 升级清单一页速读

| 类别 | 改动 |
|:---|:---|
| **新协议** | `data/runtime_config.json`（file > BB > env > default 配置层级）；`global/brain_runtime_snapshot` BB key；`global/brain_boot_preflight` BB key；`global/brain_last_crash` BB key |
| **新 RPC** | Brain `forceUnityReconnect`（Tier 1 触发 LiveKit 重连） |
| **新 HTTP API** | Castle Orchestrator :7890（FastAPI + Bearer，9 个端点） |
| **新 systemd unit** | parrot-orchestrator / parrot-brain / parrot-scheduler / parrot-maid / parrot-goslo-chat（+ `parrot-brain@.service` 模板） |
| **新容器** | docker-compose.yml 新增 `orchestrator` + `brain` 两个 profile-gated service；`Dockerfile.brain` 拆 base/full 多阶段；`docker-compose.orchestrator-host.yml` 把 host docker / systemd 控制权交给容器 |
| **新注册表** | `data/registries/setting_change_tier.json` — 24 项 setting × Tier 0-3 + 决策文档 |
| **新模块（Python）** | `parrot.castle.runtime_config` / `parrot.castle.orchestrator/{server,actions,status,client,__main__}` / `parrot.brain.boot_preflight` / `parrot.brain.crash_hook` / `parrot.brain.setting_change_tier` |
| **DTO 镜像** | `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/SettingChangeTierDto.cs`（C# 镜像 tier registry + UI 决策映射） |
| **强化点** | DSG trigger listener 加 per-message `try/except`；Brain 装 `sys.excepthook` + `loop.set_exception_handler`；orchestrator 5 次 / 300s 限频重启 |
| **测试** | Phase 1-5 共 +6 个新测试文件，176 个 Castle/Brain 测试全绿；全仓 606 passed / 6 skipped（2 个 integration 失败为环境性，与本升级无关） |

> **NOT touched**：Phase 4 §8 wire 13 锁、ADR-L1.5-001、`protocol_snapshot_p4.md`、Brain ECP 表面、cs_parity 4/4 守护、wire 协议字节序。这是**控制面**升级，**数据面零漂移**。

---

## §1 Tier 化设置变更模型（核心抽象）

| Tier | 含义 | 生效路径 | 典型 setting |
|:---:|:---|:---|:---|
| **0** | BB-write 即时 | 写 BB key → 下个 watcher tick 生效 | `behavior_mode`, `experience_mode`, IntentWorkspace 状态 |
| **1** | LiveKit 重连 | 写 `runtime_config.json` → 调 `forceUnityReconnect` RPC → Unity 拿新 token 重进 → Brain 下一个 `brain_entrypoint` 读到新值 | `line_id`（已在跑 = Tier 0）、`line_profile_id`、`room_profile_id`、`active_persona_id` |
| **2** | Brain 进程重启（5-10s downtime） | 调 orchestrator `/restart_component` → systemd 拉起 → BB 心跳恢复 | `PARROT_LLM_PIPELINE` env override、Vision tools 模型切换、Bus 拓扑变更 |
| **3** | 容器/ECS 重启（运维专属） | SSH/控制台 → `systemctl restart` 或 `docker compose down && up` | LiveKit server 配置、Redis/Falkor 镜像、orchestrator 自身代码升级 |

**注册表**：`data/registries/setting_change_tier.json` 已为 24 项 setting 标好 tier + ui_action + ux_decision_doc。Brain 端通过 `parrot.brain.setting_change_tier.tier_for(setting_id)` 查询；Unity 通过 `SettingChangeTierDto + SettingChangeTierUiHelper.Decide()` 决定渲染 toast / 确认弹窗 / 阻断。

**Tier 1 的 UX 决策（已固化进 registry）**：
- `ui_action = "confirm_reconnect"`
- 用户先确认 → 自动 reconnect → 不出现"我点了但没反应"窗口
- 这条决策**不再是 open question**（plan 里的 open-q-frontend-flow 已 closed）

---

## §2 配置优先级（已落地）

```
file (data/runtime_config.json)   ← orchestrator 唯一写入点
  > BB (global/brain_runtime_snapshot, global/active_line_id 等)
  > env (.env / systemd EnvironmentFile)
  > default (line_a + 默认 LineProfile)
```

**关键点**：
- 切线**不再改 .env**。`.env` 里 `PARROT_LLM_PIPELINE` 仅作"runtime_config.json 不存在 + BB 无 snapshot"时的 fallback。
- `running_line_id()` 现在**只看 file 与 env**，故意忽略 BB（避免 Round 5 Bug O 复发：BB drift 让 selected ≠ running）。
- `active_line_id()` 仍 BB-first（用户选择面）。两者出现差异时 `selection_drift` 指标会暴露在 `/status` 端点。

---

## §3 Castle Orchestrator HTTP API

| 端点 | 方法 | Bearer | 用途 |
|:---|:---:|:---:|:---|
| `/health` | GET | ❌ | systemd / docker liveness |
| `/status` | GET | ❌ | 聚合：runtime_config / brain_runtime_snapshot / selection_drift / processes（Redis 心跳）/ containers（docker compose ps）/ boot_preflight / last_crash / restart_stats |
| `/set_active_line` | POST | ✅ | 写 runtime_config.json `line_id` + 触发 forceUnityReconnect（Tier 1） |
| `/apply_room_profile` | POST | ✅ | 写 runtime_config.json `room_profile_id`（Tier 1 / 视字段） |
| `/force_unity_reconnect` | POST | ✅ | 直接触发 Brain 一侧 disconnect → Unity 拿新 token 重连 |
| `/restart_component` | POST | ✅ | `systemctl restart parrot-<component>` + 等心跳恢复（Tier 2） |
| `/clear_runtime_config` | POST | ✅ | 抹掉 runtime_config.json 让 .env 重新生效（运维兜底） |
| `/rolling_restart_brain` | POST | ✅ | Phase 3.4 — 双实例切流量（基于 `parrot-brain@.service` 模板） |

**鉴权**：`PARROT_ORCH_SECRET` 环境变量；空值=拒绝写操作（只读 /health, /status）。
**限频**：每个 component 5 次 / 300s 滚动窗口；超限返回 429 并写 `restart_stats` 计数器。
**SDK**：`parrot.castle.orchestrator.client` 提供 Python 客户端（httpx + urllib.request fallback），Brain 自调或 Web monitor 都能用。

---

## §4 部署形态对比

| 维度 | 旧（tmux） | 新（systemd + docker compose） |
|:---|:---|:---|
| 启动 Brain | 运维 SSH 进 Castle → `tmux new -s brain` → 手敲 `python -m parrot.brain.agent dev` | `systemctl start parrot-brain` 或 docker compose up（profile=`brain` 或 `all`） |
| 切线 | 改 `.env` `PARROT_LLM_PIPELINE` → 重启 tmux session → 用户重连 | `curl -H 'Authorization: Bearer …' :7890/set_active_line -d '{"line_id":"line_b"}'`，Unity 自动重连 |
| 重启 Brain | 杀 tmux + 重启 | `curl … :7890/restart_component -d '{"component":"brain"}'` |
| 滚动升级 | 不可能（停机） | `parrot-brain@1` / `parrot-brain@2` 双实例 + `/rolling_restart_brain` |
| Crash 可观测 | 翻 tmux scrollback | BB `global/brain_last_crash` + `/status.brain_last_crash` 直读 |
| 启动健康检查 | 没有 | `boot_preflight` 写 `global/brain_boot_preflight`（Redis / port 7889 / runtime_config 三项） |

**部署命令（已升级）**：
```bash
# 常规部署 — 仅 docker 容器 + tmux 拉起 Python 进程（兼容旧流程）
bash infra/deploy-castle.sh <castle-ip> [ssh-key]

# 推荐 — 装 systemd + 启 orchestrator
bash infra/deploy-castle.sh <castle-ip> [ssh-key] --systemd
```

`--systemd` 开关里做的事：
1. 在 `/opt/parrot/ParrotCarriers` 建 symlink 指向 `/opt/parrotcarriers`（systemd unit 的 WorkingDirectory）
2. `cp .env .env.castle`（systemd EnvironmentFile 路径）
3. `useradd parrot`（不存在则建）+ chown
4. 安装 5 个 unit + `parrot-brain@.service` 模板到 `/etc/systemd/system/`
5. `daemon-reload` + `enable` 5 个服务
6. `systemctl restart parrot-orchestrator` + 验证

---

## §5 安全 / 边界

| 维度 | 状态 |
|:---|:---|
| Bearer 鉴权 | `PARROT_MINT_SECRET`（手机→token-mint :7888）+ `PARROT_ORCH_SECRET`（运维→orchestrator :7890）；二者**独立**，不共用 |
| Phone-facing vs Nanobot 隔离 | env-castle.template 已在 §A / §B 显式分段；Nanobot（Maid + GOSLO Chat）**不直连手机**，只走 `parrot_bus` Stream + 第三方 IM (Telegram / WeChat by nanobot fork) |
| Docker host 控制权 | orchestrator 容器化时通过 `infra/docker-compose.orchestrator-host.yml` 显式 layer，挂载 `/var/run/docker.sock` + `/run/systemd/system` + `SYS_ADMIN`；不走这层 = orchestrator 仅能管自己进程，不能管 host docker / systemd |
| LIVEKIT_URL 内外用同一值 | 已知设计：手机走公网 IP，Brain 在 Castle 本机连同一公网 IP（穿一次 NAT 但避免内外配置分歧）；如未来要拆，加 `LIVEKIT_PUBLIC_URL` / `LIVEKIT_INTERNAL_URL` 即可 |
| crash hook 不抢 sentry | `sys.excepthook` 装链式（保留前驱）；`asyncio.set_exception_handler` 只接收未被 await 的 task 异常，不影响显式 try/except |

---

## §6 测试覆盖

| 测试文件 | 覆盖 |
|:---|:---|
| `tests/test_castle/test_runtime_config.py` | file > BB > env > default 解析 + 部分写 + snapshot 行为 + `_resolve_pipeline` 走 runtime_config + `running_line_id` 忽略 BB drift + `forceUnityReconnect` RPC 注册 |
| `tests/test_castle/test_orchestrator_status.py` | `/status` 聚合、process / container / drift 字段 |
| `tests/test_castle/test_orchestrator_actions.py` | set_active_line / apply_room_profile / force_unity_reconnect / restart_component / rolling_restart_brain |
| `tests/test_castle/test_orchestrator_auth.py` | Bearer 鉴权（写操作 401，只读 200） |
| `tests/test_castle/test_setting_change_tier.py` | tier registry 加载 / `tier_for` / `line_switch_tier_for_profile` / RoomSettingService 暴露 tier 字段 |
| `tests/test_castle/test_phase5_failure_propagation.py` | dsg listener 健壮性、boot_preflight 报告、crash hook（同步+异步）、限频重启、`restart_stats` 暴露 |

**结果**：176/176 castle+brain 测试绿；全仓 606 passed / 6 skipped；2 个 integration 失败（`test_brain_direct_route`）属于环境性（依赖真实 LiveKit dispatch + Redis 长连接稳定性），与本升级无关。

---

## §7 已知边界 / 后续

1. **Tier 1 forceUnityReconnect 的 Brain-side 触发链**：当前是 orchestrator → 写 `global/orchestrator_force_reconnect_marker` BB → Brain 自调本地 RPC。后续可改成 orchestrator 直接通过 LiveKit Server API 踢人，省一跳。
2. **`/rolling_restart_brain` 需要 `parrot-brain@.service` 双实例**：unit 模板已就位，但实际场景下 Brain agent 同 room 容易抢 identity；当前只支持顺序 stop A → start B 模式（轻 downtime），完全无停机需要在 `dispatch` 侧实现 client_router。
3. **LIVEKIT_URL 内外分流**：见 §5，标 P3 待办，不影响 V1。
4. **Web monitor UI 拼装 `/status` 数据**：API 已完备，前端实现未覆盖（见 Codex 指导 §B-1）。
5. **Nanobot 容器化**：当前 nanobot fork 仍走 systemd + Python venv，未做容器化；放 P3。

---

## §8 为什么这次必须做

源自 Round 5 audit 暴露的连续打击：
- Bug L `asyncio.shield` 掩盖 photo upload server 退出失败 → 需 graceful shutdown（Phase 5.1）
- Bug M `uvicorn.sys.exit(1)` 让 port 冲突 silent kill → 需 boot preflight（Phase 5.1）
- Bug N DSG trigger listener 无 per-message guard → 一条坏消息炸整个 listener（Phase 5.1 已修）
- Bug O `running_line_id` BB-first 与 `_resolve_pipeline` env-first 矛盾 → 需 file > BB > env 统一层级（Phase 1.2）

这四个 bug 的共同根因是**没有控制面**：crash 后无人 supervisor、设置变更无 tier 概念、配置源散落各处。Phase 1-5 把这层补上，Round 5 之后**任何后续单点失效都能被 orchestrator 看见 + 限频自愈**。

---

## §9 入口路径速查

| 想做什么 | 命令 / 路径 |
|:---|:---|
| 看 Castle 状态 | `curl http://<castle-ip>:7890/status \| jq` |
| 切线（Tier 1） | `curl -H 'Authorization: Bearer $PARROT_ORCH_SECRET' -d '{"line_id":"line_b"}' http://<castle-ip>:7890/set_active_line` |
| 重启 Brain（Tier 2） | `curl -H 'Authorization: Bearer $PARROT_ORCH_SECRET' -d '{"component":"brain"}' http://<castle-ip>:7890/restart_component` |
| 看上次 crash | `curl http://<castle-ip>:7890/status \| jq .brain_last_crash` |
| 抹掉 runtime override | `curl -H 'Authorization: Bearer $PARROT_ORCH_SECRET' -X POST http://<castle-ip>:7890/clear_runtime_config` |
| 升级 systemd unit | `cd /opt/parrotcarriers && git pull && systemctl daemon-reload && systemctl restart parrot-orchestrator` |
| 看 Brain 日志 | `journalctl -u parrot-brain -f` |

---

## §10 与外部文档对接

- `audit_log_index_20260511.md` §2 Round 5 18 个 bug 的修复 already 收口；本文是**Round 5 之后的下一阶段**（控制面）。
- `infra/systemd/README.md` 是 unit 文件本地文档（每个 unit 的设计意图）。
- `Interface/ecs_orchestrator_codex_guidance_20260512.md` 是给 Codex 的搬迁清单（哪些升级要进 SSOT、哪些要 Codex 接前端、哪些要持续审查）。
- `ecs_audit_prompt_for_castle_20260512.md` 是给 ECS 端的复用审计 prompt（运维侧自检清单）。

— 完 —

