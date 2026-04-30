---
status: ratified
category: chat-launch-prompt
status_note: "用于启动 Phase 4 联机 smoke + GAP-1 (EcpState ingest handler) chat。Brain 端 30min 小修 + Editor↔Brain 全链路验 5 验收口径。建议模型：Sonnet 4.6 medium thinking。"
last_reviewed: 2026-04-30
---

# Launch Prompt — Phase 4 联机 smoke + GAP-1 EcpState ingest

> **复制下面 ```text``` 块的内容**到新 chat 即可。预设模型：**Sonnet 4.6 medium thinking**（备选 GPT-5.3 Codex high-fast；不要用 Opus 4.7 / Composer-2 / Gemini）。
>
> **前置条件**：W8 Unity 半边（`sprint4_phase4_w8_unity_chat_launch_prompt.md`）已完成 + push。否则联机 smoke 无法验证工具 ④ photo 闭环。

```text
你是 ParrotCarriers Sprint4 Phase 4 联机 smoke + GAP-1 (EcpState ingest)
助手。think in English，用中文回答。

## 第一步（不可跳过）

按顺序读以下 6 份文件 / 区段：

1. .cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md
   §0 (TL;DR) + §2 (验收 5 条) + §5.5 Finding B (GAP-1 spec) + §8.2
   (本 chat 范围)
2. .cursor/memory/architecture/sprint4_phase4_entry_20260430.md §0.2
   (验收 5 条 verbatim) + §8.1 L1 (EcpState 频率锁) + §8.2 通道默认值
3. .cursor/memory/architecture/sprint4_phase4_w6_w7_unity_completion_20260430.md
   §5 (离线 Editor smoke 已验过的部分 + 联机 smoke 不能验证的 list)
4. src/parrot/brain/event_ingest.py（**只读**；学 attach_ecp_event_ingest
   pattern — 你的 ecp_state_ingest 要 mirror 这个模式）
5. src/parrot/brain/telemetry_receiver.py（**只读**；这是另一个
   topic-routing 范本 — attach_telemetry_receiver 听 parrot.telemetry +
   parrot.event topic，你听 parrot.ecp.state）
6. unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpStateDto.cs
   （**只读**；EcpStateDto 字段集 = 你解析后写 BB session/ecp_state 的
   payload schema）

## 任务范围（两段 — 顺序不可换）

### A. GAP-1 修复 — Brain 端 EcpState ingest handler（必先做完才进 B）

**问题**（来自 audit §5.5 Finding B）：
- Unity W3.A.3 `LifecycleHeartbeatPublisher` 在 `parrot.ecp.state` topic
  publish `EcpStateDto`（1Hz 心跳 + 三态变化事件驱动）
- Brain 端 `event_ingest` 只路由 `parrot.ecp.event` topic；`parrot.ecp.state`
  入站后落到 `attach_telemetry_receiver` 的 silent-ignore 分支
- BB `session/ecp_state` 永远空 → selection-C tool wrappers 看不到
  `active_locks` / `active_command_id` / 真实 body/head/cognitive
  （目前用 BB tick/cognitive_state + tick/body_state 拼凑，缺 ECP 全貌）

**实施**（30 分钟工作量）：

1. 新文件 `src/parrot/brain/ecp_state_ingest.py`：
   - 模式参考 `parrot.brain.telemetry_receiver`：attach_*(room) 函数 +
     room.on("data_received") 回调 + 按 topic 过滤（只处理
     parrot.ecp.state，其他 silent-ignore）
   - 解析 `EcpStateDto` JSON（不 import EcpStateDto.cs；直接 json.loads
     拿 dict）
   - 写 BB `session/ecp_state` 完整 dict（writer = `brain._rpc_bridge`，
     与 bb_schema.py:178 声明一致）
   - 写 BB `tick/body_state` / `tick/head_state` 镜像（如果 EcpState 三态
     字段存在）— 注意 writer = `brain.telemetry_receiver`，与现有
     telemetry_receiver 双写者冲突？查 bb_schema.py 确认；如冲突则
     **不**镜像 tick 字段，只写 session/ecp_state
   - 防御：JSON parse 失败 / dict 缺字段 / schema_version 不匹配 → log
     debug + skip，不 crash（参考 telemetry_receiver 的 try/except）
   - 加 5-7 项 metrics（received_count / dispatched_count / parse_failures /
     等）+ get_metrics_snapshot

2. `src/parrot/brain/agent.py` boot wire-up：
   - 在 `attach_ecp_event_ingest(ctx.room)` 之后立即加
     `from parrot.brain.ecp_state_ingest import attach_ecp_state_ingest;
      attach_ecp_state_ingest(ctx.room)`
   - 注释引 GAP-1 finding（防 refactor 静默删 wire）

3. 测试 `tests/test_ecp_event/test_ecp_state_ingest.py`：
   - test_attach_subscribes_to_data_received（mock room）
   - test_parrot_ecp_state_packet_writes_bb（fake DataPacket → 验证
     BB session/ecp_state 内容）
   - test_foreign_topic_silently_ignored（parrot.telemetry packet → 不动
     session/ecp_state）
   - test_malformed_json_skipped_no_crash
   - test_metrics_snapshot_keys

4. 跑 pytest 全量：`.venv\Scripts\python.exe -m pytest tests/
   --ignore=tests/integration -q` → 期望 220 + 5 = 225 全绿

5. doc 同步：
   - audit §5.5 Finding B status 从 "proposed" → "✅ resolved"
   - bb_schema.py session/ecp_state 移除 # CANDIDATE marker
   - entry §8.7 + completion 报告：标 GAP-1 ✅
   - 不动 entry §8 锁定值；不动 audit §9

GAP-1 commit 拆 2 个：feat(brain) ecp_state_ingest + 测试 / docs GAP-1 收口。

### B. Editor → Brain → Editor 全链路联机 smoke（Brain + 5 工具全跑）

**前置环境**（你的 chat 内手动起）：

1. LiveKit dev server: `docker compose -f infra/docker-compose.dev.yml up -d`
   （Redis + LiveKit Server）
2. Brain agent dev mode: `python -m parrot.brain.agent dev`
   （新终端）
3. Token: `python src/scripts/generate_token.py`
   → 拷贝 token 到 unity/ArSpike/unity_join_token.txt（或 Inspector）
4. Unity Editor: 打开 ParrotSmokeScene → Play

**5 验收口径逐条跑**（entry §0.2 verbatim）：

| # | 验收口径 | 你 chat 内动作 | 期望 |
|:--|:--|:--|:--|
| 1 | 工具 ① perch_to_finger 体感闭环 | Editor: 触发 XRHandTracker open_palm 手势模拟（参考 W3.A.2 完成报告 §5）| Console: AnimationDriver state=PERCHED_ON_HAND + head=HEAD_TILT；EcpState 心跳 body_state=PERCHED_ON_HAND head_state=HEAD_TILT；Brain BB tick/body_state + tick/head_state（GAP-1 修后）正确接到 |
| 2 | 工具 ② identify_object 同步链 | 在 Brain 终端跑 sim_unity_client 让 GOSLO 调 identify_object("blue mug")（用 PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1）| Console: stage info 含 [capture] / [L0 no L2-B match]（空 Graphiti 是预期）/ [L1 no Graphiti match]；返回 unknown reply + snapshot_id；observer.sighting metrics unmatched_received +1；总时长 < 1.9s |
| 3 | ECP frontend_state 三态对齐 LLM | 同 #1 跑过即验 | tool_state_context 在 fly_to / animate / set_video_tier 返回里附 [GOSLO state] body=... head=... cognitive=... locks=... active_cmd=...（GAP-1 修后 active_cmd / locks 不再空） |
| 4 | RefBinding + Event 落地不污染实时帧 | Editor: BBoxController.PlaceBBox + FocusController.AnchorFocus(5 次) → Console attention.threshold.crossed | Brain BB transient/current_attention_hint 写入；Unity 端 EcpEventDispatcher wildcard log 看到 attention.threshold.crossed brain-source；hint_writer metrics bumps_skipped_unresolved +1（UNRESOLVED 是常态，per W6-7 设计） |
| 5 | 全链路 Editor 跑通（含工具 ④） | Editor: PhotoController.CapturePhoto（W8 Unity 半完成后）| photo.taken_preview EcpEvent 发出；HTTP POST /upload/photo/{photo_id} 200；Brain disk data/photos/{yyyy-mm-dd}/{photo_id}.jpg 落盘；photo.asset_uploaded 回程 EcpEvent；observer.photo metrics photo_nodes_upserted + photo_nodes_updated_with_asset 各 +1；BB transient/last_photo_event stage 序列 preview → asset_uploaded |

**Editor 离线 smoke vs 联机 smoke 区别**：W6-7 Unity 完成报告 §5 已经
跑过离线 EcpEvent DROPPED log；本 chat 是**真 LiveKit + Brain + Unity**
联机，期望看到事件真到对端、handler 真触发、BB 真写入。

**发现 bug 的处理**：
- 协议级 bug（违反 entry §8 锁定值 / 跨 doc 漂移）→ 写 finding 入新
  audit doc，**不直接改协议**；按 audit §6.3 硬约束 10 条流程
- 实现级 bug（小修 + 不动 wire schema）→ 直接修 + 测试 + commit
- 边界 / 设计问题 → 记 finding 报用户

## 不允许（硬约束 — Phase 4 已锁）

1. 不改 entry doc §8 任意条款（修改即漂移，必须 sign off）
2. 不改 audit doc §9 任意条款（同上）
3. 不改 ecp_event.py 的 EcpEventType / EcpEventSource 枚举值（C# parity）
4. 不改 ecp_event.py 的 8KB / topic / schema_version 常量
5. 不改 bb_schema.py 任意 key 的 producer 字段（GAP-1 ecp_state_ingest 的
   writer 必须是 brain._rpc_bridge — 与 bb_schema:178 声明一致）
6. 不动 W3 / W4-5 / W6-7 / W8 Brain 端已落地代码（除非联机 smoke 发现
   critical bug；critical 定义 = 阻塞 5 验收口径任一）
7. 不动 Unity 端任何代码（如发现 Unity 侧 bug，记 finding 派回 W8 Unity
   chat / W6-7 Unity chat / W3 Unity chat）
8. 联机 smoke 跑完无论结果如何都不删 / 改测试基线（GAP-1 加 5 测试 →
   225 全绿）
9. 真机部分**不在本 chat 范围**（在另一个独立 chat 跑 Castle + 手机）
10. defer 列表里的项（audit §9.5 / entry §8.6 / completion §6）默认不补；
    联机 smoke 暴露 defer 项需要补的话先 propose 再做

## 完成后必交付

1. GAP-1 落地 commits（feat + test + doc 收口 共 ~3 commits）
2. 联机 smoke 完成报告
   `sprint4_phase4_smoke_and_gap1_completion_20260430.md`：
   - GAP-1 实施细节
   - 5 验收口径逐条联机验证状态（PASS / FAIL / 部分通过 + 证据）
   - 发现的 bugs 列表（finding 表）
   - Editor 联机环境配置 README（dev compose / token / Brain 启动顺序）
   - Phase 5+ 派生待办（如发现 GAP-2 等）
3. 测试基线最终：225/225 全绿（220 baseline + GAP-1 新增 5）
4. 不更新 entry §8 / audit §9 任何锁定项；只升级 §0.2 验收 #5 状态：
   "联机 ⏳" → "联机 ✅" 或 "联机 ⚠ 部分通过"（按真实结果）

## 不在本 chat 范围（明确不做）

- 真机部署 / 手机 spike（独立 chat — 联机 smoke 通过后再起；环境是
  Castle docker + 手机 ADB / TestFlight）
- DSG L2-B 完善 / L1.5 预加载池（独立 chat — Phase 5+）
- Brain SDK / 接口提炼（独立 chat — 真机 spike + DSG L2-B 后再决定）
- AR 正式工作区 / Launcher 正式版（独立工程 — P2.5 验收后启动）
- Phase 5+ 任何项（隐私 / 对象存储 / Multi-Brain 协作 / web_search tool /
  identify_object L2 完整化 / Episode lifecycle 完整化）

## Sprint 4 终极目标 (不要忘)

完成本 chat 后：
- Phase 4 + 5 验收口径全部 ✅（如真机 spike 也过则 P2.5 准入）
- GAP-1 修复 → selection-C tool wrappers 真正看到 active_locks /
  active_command_id（felt experience 完整）
- Phase 5+ 真正可起（基础协议 + 工具 + 4 验收口径全闭环）
```

---

## 配套备注（不进 prompt）

| 项 | 说明 |
|:--|:--|
| 模型选择理由 | Sonnet 4.6 medium thinking — GAP-1 是 Brain 小修（mirror 既有 telemetry_receiver 模式）+ 联机 smoke 大量 cross-doc / cross-process 调试需要长 context；Sonnet 4.6 在 audit / 联调场景比 Opus 4.7 性价比高 |
| 预计工作量 | GAP-1：30-60 分钟（含测试 + doc）；联机 smoke：1-3 小时（环境起 + 5 验收逐条跑 + finding 整理 + 完成报告） |
| 前置依赖 | **W8 Unity 半边必须先完成 + push**（否则验收 #5 工具 ④ 无法验联机）；建议两个 chat 并行启 — W8 Unity 实施时本 chat 先做 GAP-1 + 完成报告骨架，W8 一并完成后立刻跑全 5 验收 |
| 风险点 | (a) Brain agent dev 模式 + LiveKit Server 真起来需要 .env 配置全 + Castle 公网 vs 本地切换；(b) sim_unity_client 老脚本可能与最新 LiveKit Unity SDK 接口漂移；(c) GAP-1 修后 BB 双写 (telemetry_receiver + ecp_state_ingest 都想写 tick/body_state) 可能冲突 — prompt 内已提示选其一 |
| 收口验收 | 225/225 全绿 + 联机 smoke 完成报告 + Phase 4 §0.2 验收 #5 升级 + 残留 bug 全 finding 化（不带 bug 进 P2.5） |
| 后续 chat 衔接 | 完成后下一个 chat = 真机 spike chat（Castle docker + 手机 ADB / TestFlight 跑全 5 验收）；之后 = P2.5 完成汇报 chat |
