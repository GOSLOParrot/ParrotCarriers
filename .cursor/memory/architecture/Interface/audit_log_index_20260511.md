# App V1 Audit Log — Index (Rounds 1-5, 2026-05-11)

> **SSOT** for Cursor 端 + Codex 端共享的接口审计与修复记录。
> 五轮审计加起来 18 个 bug + 1 design gap，全部已修，全部有回归测试。
> 本文是**单页索引**，明细见各 Round 报告。

| 字段 | 值 |
|:---|:---|
| 项目版本 | `parrotcarriers 0.1.0` |
| Sprint 阶段 | P2.5 — App V1 build phase |
| livekit-agents | 1.5.5 |
| 审计日期 | 2026-05-11 |
| 总测试 | 568 passed, 2 failed (pre-existing, 与 Round 5 无关), 4 skipped (全仓) |
| 触发上下文 | Codex 升级 `app_v1_session_context_pack_upgrade_20260511.md` 后，Cursor 跨五轮深审 RoomSetting / LineB / ECP-state / disconnect / 菜单画布 + 启动页 / Brain cold-start lifecycle 路径 |

---

## 1. 五轮审计入口（明细文档）

读这五份就能看完所有改动 + 推理 + 验证：

| Round | 焦点 | 文档 |
|:---|:---|:---|
| 1 | LLM 注入通道 + RoomProfile env/BB | [`app_v1_session_context_pack_audit_20260511.md`](app_v1_session_context_pack_audit_20260511.md) |
| 2 | RoomProfile draft + LineB session reset + voiceprint dim | [`app_v1_core_interface_audit_round2_20260511.md`](app_v1_core_interface_audit_round2_20260511.md) |
| 3 | ECP state ingest + disconnect 死代码 | [`app_v1_ecp_disconnect_audit_round3_20260511.md`](app_v1_ecp_disconnect_audit_round3_20260511.md) |
| 4 | 菜单画布 + 启动页 RPC（reserved id / silent fallback / payload warning / RPC mirror） | [`app_v1_menu_canvas_audit_round4_20260511.md`](app_v1_menu_canvas_audit_round4_20260511.md) |
| **5** | **Brain cold-start 生命周期（photo bind / shutdown / scheduler listener / running-vs-selected line）** | [**`app_v1_brain_cold_start_line_lifecycle_audit_20260511.md`**](app_v1_brain_cold_start_line_lifecycle_audit_20260511.md) §Round 5 |

升级文档（被审对象）见 [`app_v1_session_context_pack_upgrade_20260511.md`](app_v1_session_context_pack_upgrade_20260511.md)。

---

## 2. 全部 18 个 Bug + 1 Gap 一览

### Round 1 — Session Context Pack 升级审计

| ID | 严重度 | 模块 | 说明 |
|:---|:---|:---|:---|
| A | HIGH | `agent.py` / `mode_watcher.py` / `context_injector.py` | `update_instructions` 调用错位（livekit-agents 1.5+ 在 Agent 上不在 AgentSession 上），三处全部静默 no-op |
| B | MEDIUM | `session_context_pack.py` | `_active_room_profile_id` 优先 BB 后 env，与已修的 `line_profile.py` 不一致；RemoteSSH 显式 env 应该胜过陈旧 BB |
| C | LOW | `session_context_pack.py` | 未知 `prompt_target` frontmatter typo 静默吃掉 source |
| D | LOW | `session_context_pack.py` | L1.5 bootstrap 在 TriggerRunner 0 trigger 时丢事件 |

### Round 2 — Core / Business Interface 审计

| ID | 严重度 | 模块 | 说明 |
|:---|:---|:---|:---|
| A | HIGH | `preset_loader.py` / `session_context_pack.py` / `bb_schema.py` | 未保存的 RoomProfile draft `apply` 后 `setting_file_refs` 丢失（只写 id、不写全量 JSON） |
| B | MEDIUM | `lineb_audio_guard.py` / `agent.py` | `_recent_segments` 跨 session 残留 → 重连后第一秒 user_turn 被误判 `agent_echo` |
| C | MEDIUM | `lineb_voiceprint.py` | `_cosine_similarity` 默默截断不同维向量（ECAPA 192 vs Resemblyzer 256） |
| D | LOW | `agent.py` | `applyRoomProfile` RPC payload 拼写错时静默回退 default |

### Round 3 — ECP State + Disconnect 审计（实证验证）

| ID | 严重度 | 模块 | 说明 | 验证方式 |
|:---|:---|:---|:---|:---|
| E | HIGH | `ecp_state_ingest.py` / `agent.py` | `clear_bb_ecp_state()` docstring 声明被 disconnect 调用，实际**零调用点** | AST 扫描 |
| F | MEDIUM | `ecp_state_ingest.py` | `_last_seq` per-identity 序列号跨 session 残留 → 新 session seq=1..5 全被误判 duplicate | 直接 import 跑 5+5 packet 看 `duplicate_skipped` 计数器 |

### Round 4 — 菜单画布 + 启动页接口审计（实证验证）

| ID | 严重度 | 模块 | 说明 | 验证方式 |
|:---|:---|:---|:---|:---|
| G | HIGH | `preset_loader.py` / `room_setting.py` / `agent.py` | `saveRoomProfile` 可覆盖 builtin `default` preset（以及 `ephemeral` / `workspace_only` sentinel） | 直接 save 一个 `room_profile_id="default"` 的 RoomProfile 看 disk 是否被改写 |
| H | LOW | `agent.py` | `previewRoomProfile` / `saveRoomProfile` 缺 Round 2 Bug D 同款 payload typo 警告 | 代码对照（Round 2 已修 applyRoomProfile，这两个漏掉）|
| I | MEDIUM | `menu_registry.py` / `preset_loader.py` | `applyMenuSelection` 静默替换 invalid workspace_id；调用方拿到 `success=True` 但 BB 实际写的是 fallback workspace | 直接调 `apply_selection(workspace_id="nonexistent_xyz")` 看返回 + BB |
| J | LOW | `session_policy.py` | `setAppCapabilityMode` 未知 mode 静默回退 FullARCompanion，操作员看不到拼写错 | 直接调 `apply_capability_mode("totally_bogus_mode")` |
| **K (gap)** | LOW | `agent.py` / `app_first_version.py` | Photo Awareness / Camera mode / XRHand mode 只暴露 HTTP，没 LiveKit RPC；菜单画布 GOSLO Module 抽屉走 in-band 通道时缺失 | 设计文档 vs 实际 RPC handler 名单对照 |

### Round 5 — Brain cold-start 生命周期审计（实证验证）

| ID | 严重度 | 模块 | 说明 | 验证方式 |
|:---|:---|:---|:---|:---|
| **L** | HIGH | `photo_upload_server.py` | `stop_photo_upload_server` 用 `asyncio.shield(task)` → 卡死的 uvicorn shutdown 在 timeout 后**继续运行**，端口 7889 被泄到下个 session（直接撞 Bug M）| 跑 0.5s timeout + sleep(60) hung serve，看 task `done == False` / `cancelled == False` |
| **M** | CRITICAL | `photo_upload_server.py` | `start_photo_upload_server` 不预检端口；端口被占时 uvicorn `Server.startup` 调 `sys.exit(1)`，未 await 的 task `SystemExit` 沿 loop 上抛**杀掉 Brain agent 进程** | 占住 port 27889 后 `await start_photo_upload_server(port=27889)` → 看到 `Task exception was never retrieved: SystemExit(1)` 然后脚本死 |
| **N** | MEDIUM | `agent.py` | `_listen_scheduler_results` 外层 `except Exception` 吃掉 `async for` 里的失败 → 一次坏 payload / generate_reply 失败之后整个 session 的 nanobot 完成消息全部静默丢失 | 静态阅读 + AST 模式：`async for` 内无 per-message try/except |
| **O** | MEDIUM | `line_status.py` / `app_first_version.py` | `active_line_id()` BB-first；GOSLO Module canvas voice tile 把"用户选择的"线路当成"正在运行的"线路上报，cold-start drift 不可见 | env=line_a + BB=line_b → `active_line_id() == "line_b"`，canvas tile 没有 drift 字段 |

---

## 3. 共性模式（**三类 bug，不是 18 个独立事故**）

### 3.1 共性 A — module-level mutable state 必须有 session-end reset

四轮审计的 **B / E / F + 历史 RefBinding** 都是同一个 shape：

> **任何在 `parrot/brain/**` 里声明的 module-level mutable state（`_dict` / `_list` / `_set` / `OrderedDict`）必须有显式的 `reset_*_on_session_end()` 函数，并且该函数必须在 `brain.agent._on_room_disconnected` 完成 wire-up。**
>
> 否则就是潜伏 dead code，下次 disconnect 时旧 session 的尾巴污染下一个 session 的开头。

`agent.py::_on_room_disconnected` 顶端已加 TODO 注释指向本文。建议下次给 Codex 加一条 cursor rule。

当前已 wire-up 的 reset 函数（disconnect 时调用）：

| 模块 | 函数 | 用途 |
|:---|:---|:---|
| `refs.py` | `reset_refs_for_session()` | 清 RefBinding 注册表（Phase 4 W6-7 F-06）|
| `lineb_audio_guard.py` | `reset_lineb_audio_guard_on_session_end()` | 清 `_recent_segments` + `_last_decision`（Round 2 Bug B）|
| `ecp_state_ingest.py` | `reset_ecp_state_ingest_on_session_end()` | 清 `session/ecp_state` BB + `_last_seq` 序列去重（Round 3 Bug E + F）|

### 3.2 共性 B — 任何 I/O 资源必须 cooperative-then-cancel 关闭（Round 5 新增）

Round 5 的 **L + M** 是另一个 shape：

> **Brain agent 在每个 LiveKit room 任务里申请的任何 I/O 资源（端口 / 套接字 / 文件 / 子进程 / Redis pubsub）必须有 cooperative-then-cancel 关闭路径。`asyncio.shield` 只能用在"礼貌等待"阶段；礼貌等待超时之后必须显式 `task.cancel()`，否则资源会跟着 room 一起泄到下个 session 并撞车。**

启动侧的对偶约束（同样 Round 5）：

> **任何"会因为外部资源被占"而启动失败的 server，必须在 `start_*` 入口做预检（探针 + 早返 None / raise），并且任何被 fire-and-forget 包成 asyncio.Task 的 `serve()` 类协程必须挂 `task.add_done_callback` 显式记录 `SystemExit` / 异常，否则 uvicorn 这种"`sys.exit(1)`-on-bind-fail"框架可以**杀掉整个 Brain agent 进程**。**

当前已遵循该模式的 cleanup 路径：

| 资源 | start | stop | Round |
|:---|:---|:---|:---|
| Redis pubsub (DSG triggers) | `start_trigger_listener` | `_listen` finally + cancel from `_stop_room_scoped_background` | Round 1 |
| Redis pubsub (scheduler) | `_listen_scheduler_results` | finally + cancel；per-message try/except resilience | Round 1 + **Round 5 N** |
| Photo upload uvicorn task | `start_photo_upload_server` | cooperative `should_exit` + **cancel-on-timeout**（**Round 5 L**） | **Round 5 L** |
| Photo upload bind | `start_photo_upload_server` | 预检 `_is_port_bindable` + done callback（**Round 5 M**） | **Round 5 M** |

### 3.3 共性 C — running 与 selected 必须有独立访问器（Round 5 新增）

Round 5 Bug O 暴露的更深问题：

> **任何"用户选了什么 (selected/saved)"和"进程实际在跑什么 (running/live)"可能漂移的状态，必须提供两个独立访问器，并要求消费方显式选择。冷启动门控生效的前提是这两者可被分别看到；任何把它们混成一个单 getter 的设计都会在某次部分重启 / Web monitor 写入 / 静默回退中再次撞坑。**

当前已分离的对子：

| domain | selected 访问器 | running 访问器 | Round |
|:---|:---|:---|:---|
| Brain pipeline | `line_status.active_line_id()` (BB-first) | `line_status.running_line_id()` (env-first) | **Round 5 O** |

---

## 4. 已发现但本轮不动的事项（每条都已在源码加 TODO 注释）

每个 TODO 都直接锚定到代码行，grep `audit Round` 即可定位：

| 来源 | 文件 | TODO 锚点 | 行动条件 |
|:---|:---|:---|:---|
| Round 2 §A | `lineb_audio_guard.py::_score` | `# TODO (audit Round 2 §A` | 用户反馈 "TTS 后 1s 听不到我说话" → 在 `session/lineb_voice_activity` 加 `cooldown_until_ts` 字段供 UI grey-out mic |
| Round 2 §B | `lineb_audio_guard.py::_matching_segment` | `# TODO (audit Round 2 §B` | profiling 显示 deque 在热路径上 → 入口主动 prune 已过期 segment |
| Round 2 §C | `app_first_version.py::apply_room_profile` | `# TODO (audit Round 2 §C` | 下一次 RoomSetting UI chat → 返回 dict 加 `room_profile_id` 顶层字段 |
| Round 2 §E | `room_setting.py::snapshot` | `# TODO (audit Round 2 §E` | 前端要 N-Room compatibility 列表 → snapshot 加 `compatibility_states` map |
| Round 2 §G | `lineb_voiceprint.py::enroll_from_audio_files` | `# TODO (audit Round 2 §G` | 下次 enrollment chat → 持久化 `embedding_dim` 到 manifest，让 verify 早层 fail-fast |
| Round 3 §A | `event_ingest.py::_is_duplicate` | `# TODO (audit Round 3 §A` | 任何时候，`time.time()` → `time.monotonic()` |
| Round 3 §B | `event_publisher.py::reset_ecp_event_publisher_for_tests` | `# TODO (audit Round 3 §B` | 真机 smoke 看到 publisher fail 日志噪音 → 加 `reset_ecp_event_publisher_on_session_end` |
| Round 3 §D | `photo_upload_server.py::upload_photo` | `# TODO (audit Round 3 §D` | Phase 5+ → 加 10MB 硬上限 + 413 响应 |
| Round 3 §E | `event_publisher.py::publish_nowait` | `# TODO (audit Round 3 §E` | `loop.create_task(..., name=...)` 让 debug 可追溯 |

涉及协议 / Unity / DTO 的事项（不在 Brain 单仓内）：

| 来源 | 描述 | 谁来做 |
|:---|:---|:---|
| Round 3 §C | `_state_context.get_state_snapshot()` 没有 staleness 检查（消费侧防线） | 下一轮 audit 或 Brain consumer chat |
| BUG-U2（既有 TODO） | EcpStateDto 加 `boot_id` 字段，让 Brain 可按 `(identity, boot_id)` 复合键去重，比现在的 `_DEDUP_WINDOW=10` 启发式更稳 | cs_parity 协议 chat |
| 上一轮 §E | `setting_file_refs` 路径白名单（受信本地 trust boundary，仅在云端同步上线时改） | App 安全审计 chat |

---

## 5. 改动清单（五轮合计）

| 文件 | 改动来源 |
|:---|:---|
| `src/parrot/brain/agent.py` | Rounds 1, 2, 3（disconnect cleanup + RPC fallback warning + 共性 TODO）+ **Round 5 N**（`_handle_scheduler_message` + per-message try/except）|
| `src/parrot/brain/mode_watcher.py` | Round 1（`current_agent.update_instructions`）|
| `src/parrot/brain/context_injector.py` | Round 1（同上）|
| `src/parrot/brain/session_context_pack.py` | Rounds 1, 2（env-vs-BB + prompt_target warning + L1.5 race + draft BB JSON 优先）|
| `src/parrot/brain/preset_loader.py` | Round 2（`apply_room_profile` 写全量 JSON）+ Round 4（reserved id guard + warnings）|
| `src/parrot/shared/bb_schema.py` | Round 2（新 `global/active_room_profile`）|
| `src/parrot/brain/lineb_audio_guard.py` | Round 2（`reset_lineb_audio_guard_on_session_end`）+ Round 2 TODO |
| `src/parrot/brain/lineb_voiceprint.py` | Round 2（cosine dim guard）+ Round 2 TODO |
| `src/parrot/brain/ecp_state_ingest.py` | Round 3（`reset_ecp_state_ingest_on_session_end`）|
| `src/parrot/brain/event_publisher.py` | Round 3 TODO |
| `src/parrot/brain/event_ingest.py` | Round 3 TODO |
| `src/parrot/brain/photo_upload_server.py` | Round 3 TODO + **Round 5 L**（cooperative-then-cancel）+ **Round 5 M**（pre-bind probe + done callback）|
| `src/parrot/brain/app_first_version.py` | Round 2 TODO + **Round 5 O**（voice tile drift metrics + summary/health）|
| `src/parrot/brain/room_setting.py` | Round 2 TODO + **Round 5 O**（`_process_line_id` 委托给 `running_line_id`）|
| `src/parrot/brain/line_status.py` | **Round 5 O**（`running_line_id` / `running_line_status` + 双访问器文档）|
| `src/parrot/brain/menu_registry.py` | Round 4 Bug I（apply_selection 报告 workspace fallback）|
| `src/parrot/brain/session_policy.py` | Round 4 Bug J（unknown mode warning）|
| `tests/test_brain/test_session_context_pack.py` | Round 2（draft apply 回归）|
| `tests/test_ecp_event/test_ecp_state_ingest.py` | Round 3（session-end reset 回归）|
| `tests/test_brain/test_menu_workspace.py` | Round 4（6 个回归覆盖 G/I/J）|
| `tests/test_brain/test_app_first_version_facade.py` | **Round 5 O**（一处 summary 等值断言放宽为 startswith）|
| `tests/test_brain/test_brain_lifecycle_static.py` | **Round 5 L**（锁定 cancel 路径）|
| `tests/test_brain/test_app_v1_round5_lifecycle.py` | **Round 5**（NEW — 12 回归覆盖 L/M/N/O + 静态守护）|
| 本目录 6 份 audit doc | NEW（含 Round 5）|

无 Unity 端改动（Cursor 仓侧）。无新增 Python 依赖。无 cs_parity 协议变更。`_voice_pipeline_status` 新增的 metrics 字段是 additive，向后兼容。

---

## 6. 测试矩阵

| 范围 | 命令 | 结果 |
|:---|:---|:---|
| Round 1 焦点 | `pytest tests/test_brain/test_session_context_pack.py` | 4 passed |
| Round 2 焦点 | `pytest tests/test_brain` | 113 passed |
| Round 3 焦点 | `pytest tests/test_ecp_event/test_ecp_state_ingest.py` | 12 passed |
| Round 4 焦点 | `pytest tests/test_brain/test_menu_workspace.py -k AuditRound4` | 6 passed |
| **Round 5 焦点** | `pytest tests/test_brain/test_app_v1_round5_lifecycle.py tests/test_brain/test_brain_lifecycle_static.py` | **15 passed** |
| 累计回归（brain + ecp_event + unity + shared） | `pytest tests/test_brain tests/test_ecp_event tests/test_unity tests/test_shared` | **370 passed** |
| **全仓** | `pytest tests` | **568 passed, 2 failed (pre-existing), 4 skipped** |

**Round 5 之外的 2 个 pre-existing failure**（与本审计无关，已验证不是 Round 5 引入）：

1. `tests/integration/test_nanobot_channel.py::test_parrot_bus_channel_consumes_and_replies`
   — Gemini API 拒绝 `function_declarations[49].name`（含非法字符）。Codex 端 nanobot tool 注册问题。
2. `tests/test_bus/test_registry.py::test_mount_preflight_l1_without_identity`
   — Python 3.11 下 `asyncio.get_event_loop()` 在没有 running loop 时 raise `RuntimeError`。test 自身的 deprecation 问题。

Round 4 文档里提到的"Cartesia 迁移"那个 pre-existing failure 这次没出现，
说明 Codex 端已经把 voice_profile JSON 跟 test 同步好了。

| Lint | `cursor ReadLints` | 0 errors（Round 5 改动文件全部干净）|

4 skipped 是 optional integration deps（如 nanobot worker、graphiti 真连接），与本次审计无关。

---

## 7. 给 Codex 的核心同步要点

1. **`update_instructions` 必须走 `session.current_agent`**（livekit-agents 1.5+）
   - `AgentSession` 没这个方法，`Agent` 才有，且是 `async`
   - 任何新代码涉及 system instructions 动态刷新都用 `await session.current_agent.update_instructions(...)`，不要 `session.update_instructions(...)`

2. **Module-level mutable state = 必须有 session-end reset**（共性 A）
   - 见 §3.1
   - `agent.py::_on_room_disconnected` 顶端有 TODO 注释提醒

3. **任何 I/O 资源 = 必须 cooperative-then-cancel**（共性 B，Round 5 新增）
   - 见 §3.2
   - `asyncio.shield(task)` 只能用在 cooperative 阶段；timeout 后必须 `task.cancel()`
   - fire-and-forget 包成 Task 的 server 必须挂 `add_done_callback` 显式 log

4. **running vs selected = 必须双访问器**（共性 C，Round 5 新增）
   - 见 §3.3
   - Brain pipeline 当前的双访问器：`running_line_id()` (env) / `active_line_id()` (BB)
   - 任何 canvas / status RPC 报告"运行时"状态时调 `running_line_id()`；任何 RoomSetting / 选择持久化时调 `active_line_id()`

5. **RoomProfile draft 流程**
   - 现在 `apply_room_profile(draft)` 即使 draft 没 save 到 disk 也能生效（BB 写全量 JSON）
   - 前端如果想保留"未保存提示"必须自己单独追踪 draft state

6. **LineB voiceprint 新 decision: `embedding_dim_mismatch`**
   - 当 user 切换 provider 但没重新 enroll 会触发
   - 前端 voiceprint UI 需识别这个 decision 并提示"声纹模型已变更，请重新注册"

7. **`applyRoomProfile` / `previewRoomProfile` / `saveRoomProfile` payload 拼写诊断**
   - 任何 `roomProfileId` camelCase / 大写拼写错都会触发 logger.warning 列出实际 keys
   - 在 ECS 日志里 grep `applyRoomProfile: payload missing` / `previewRoomProfile: payload missing` / `saveRoomProfile: payload missing` 反向修 Unity 拼写

8. **`saveRoomProfile` 拒绝 reserved id**（Round 4）
   - 任何 RoomProfile draft 用 `room_profile_id ∈ {"default", "ephemeral", "workspace_only"}` 都会返回 `status="error" / reason="reserved_room_profile_id"` 而不是覆盖系统 default
   - RoomSetting UI 必须识别这个 error 并提示用户改名
   - 常量 `RESERVED_ROOM_PROFILE_IDS` 已 export

9. **`PresetApplyResult.warnings` 字段**（Round 4）
   - `applyMenuSelection` 在 workspace fallback 时把
     `"workspace_id='X' not registered; substituted to fallback 'mansion_hub'"` 写进 warnings
   - 菜单画布 UI 读 `result.warnings`，非空就显示 toast 或重新同步 active_workspace_id
   - 字段是 additive，不破坏向后兼容

10. **`setAppCapabilityMode` 未知 mode 仍然 fallback 到 FullARCompanion**（Round 4）
    - 但现在打 warning。Unity 应当只发送 enum 已知值
    - 操作员 grep `unknown capability mode` 可反查 Unity 拼写错误

11. **3 个 menu canvas LiveKit RPC**（Round 4 Gap K）
    - `setPhotoAwareness` / `setCameraMode` / `setXrHandMode`
    - 菜单画布 GOSLO Module 抽屉应当用这些，不要再调 HTTP `/api/app/awareness` 等
    - Web monitor 仍然用 HTTP（不改）

12. **GOSLO Module canvas voice tile 新 metrics: `running_line_id` / `selected_line_id` / `selection_drift`**（NEW Round 5 Bug O）
    - `selection_drift == True` 表示用户在 RoomSetting 里选了 Line X 但 Brain 进程跑的是 Line Y
    - canvas tile 现在会在 summary 末尾追加 "(selection drift: selected=X but running=Y — Brain cold restart required to apply the selection)"
    - 健康度从 `ok` 升级为 `warning`，让操作员看到 cold-restart 缺口
    - Legacy `metrics["active_line_id"]` 保留旧含义（selection-driven）；新代码请直接读 `running_line_id` / `selected_line_id`

13. **photo upload server 现在可以 cleanly 返回 `None`**（NEW Round 5 Bug M）
    - 端口被占时 `start_photo_upload_server()` 返回 `None` 并记录 ERROR 日志，**不再** SystemExit-杀掉 Brain agent 进程
    - 现有调用方（`brain.agent.brain_entrypoint`）已经 `is not None` 守护，安全
    - 操作员看到 `cannot start: 127.0.0.1:7889 already in use` 时去找 stale Brain / uvicorn 并 kill 它

14. **scheduler result listener 现在抗一次性失败**（NEW Round 5 Bug N）
    - 任何单次 message 处理失败（坏 JSON / generate_reply 拒绝）都打 `scheduler_result_listener: per-message handler failed; staying subscribed for the next event`
    - 但 listener 继续订阅；**不再**整个 session 静默死掉
    - 任何想加新 per-message 副作用的代码都驱动 `_handle_scheduler_message(session, message)`，不要重建 listener

15. **真机回归 sanity 列表**
    - 切 Room 后日志出现 `session_context: refreshed instructions`
    - 断开重连后日志出现 `[ecp_state_ingest] cleared N per-identity sequence dedup entries`
    - 连续切换 Room 不会泄 BB（`global/active_room_profile` JSON 跟 id 一起更新）
    - 菜单切换 invalid workspace 时日志/响应里能看到 fallback warnings
    - **冷启动重启时端口 7889 被占**：日志应当出现 `[photo_upload] cannot start: 127.0.0.1:7889 already in use`，agent **进程不死**，photo upload 静默禁用本 session（NEW Round 5）
    - **Line cold-start drift**：env=line_a + BB=line_b 时，canvas voice tile summary 里能看到 `selection drift: selected=line_b but running=line_a` 字样（NEW Round 5）

---

## 8. 这份报告放哪里？谁能看到？

| 工作区 | 入口 | 是否能看到 |
|:---|:---|:---|
| Cursor（当前工作区）| `.cursor/memory/architecture/Interface/INDEX.md` | ✅ 已登记 5 份审计 doc + 1 份 Round 5 |
| Codex（外挂工作区）| `codex_workspace/INDEX.md` § Source Anchors | ✅ Codex 一进入就读到 `Interface/INDEX.md` 链接 |
| Codex `backend_interface_map`（业务接口设计入口）| `codex_workspace/design_workspace/backend_interface_map/README.md` | ✅ 显式 audit log 指针 |
| Web console / 其他外部| 通过 git 仓库直接访问路径 | ✅ 仓库公开路径 |

> Cursor 端 SSOT = `.cursor/memory/architecture/Interface/`
> Codex 端入口 = `codex_workspace/design_workspace/backend_interface_map/README.md` 指过去
> 两边任何一个 chat 都能在两步内拿到所有 6 份 doc（含 Round 5 superset 文档）

---

## 9. 下次审计建议入口

按价值排序：

1. **DSG triggers / L1.5 admit path** — Phase 4 之后 L2-B 写入闭环还没全审
2. **menu RPC 端到端 fuzzing** — 用 hypothesis 喂奇怪 payload 看 `_payload_*` helper
3. **`_state_context.get_state_snapshot` staleness 检测** — Round 3 §C 提到的消费侧防线
4. **`workspace_registry` fallback 链 + IntentWorkspace eviction** — 长跑 / 重启场景
5. **EcpStateDto BUG-U2** — `boot_id` 字段加上后能彻底取代 `_DEDUP_WINDOW=10` 启发式（涉及 cs_parity，需要协议 chat）
6. **Round 5 follow-ups**（按价值排序）：
   - **External Brain supervisor / RemoteSSH cold-restart 接口** — Bug O 现在能告诉用户"需要 cold restart"，但没人**做**这个 restart
   - **Photo upload server 端口冲突自愈** — Bug M 已经避免 SystemExit，但 stale 进程仍需手动 kill；可以做"端口被占就自动找下一个空闲端口"（需要 RPC 把端口下发给 Unity）
   - **Scheduler listener health probe** — Bug N 现在抗 per-message 失败，但没有"listener 还活着吗" 的健康指标；可以加个 BB key 让 Web monitor 看到
   - **Running-vs-selected 再泛化** — Round 5 Bug O 只覆盖了 Line。Persona / Model / Scene 可能也有"用户选择 vs 进程已加载"的漂移（虽然这些不是 cold-start，是 hot-swap），值得审一次

---

## 10. 致 Codex（总结）

五轮 18 个 bug + 1 gap，**全部 codex_workspace 一进入就能拿到完整推理 + 验证 + 修复 + 测试**。任何下次 RoomSetting / LineB / ECP / disconnect / cold-start 路径上的设计或修复，**强烈推荐先扫一眼这份索引**，避免重复踩同型坑。

三类共性模式（§3.1-3.3）已固化为规则：

- **A**：module-level mutable state ⇒ session-end reset
- **B**：I/O 资源 ⇒ cooperative-then-cancel + 启动预检 + done callback
- **C**：running vs selected ⇒ 双访问器 + drift 信号

下次 Cursor 这边继续审计时会增 Round 6+，本索引会同步追加。
