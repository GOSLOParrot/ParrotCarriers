---
status: partial
category: completion-report
status_note: "GAP-1 (EcpState ingest handler) ✅ 落地 + 230/230 全绿。联机 smoke（Editor↔Brain 5 验收口径）⏳ 等待环境就绪后补充。"
last_reviewed: 2026-04-30
---

# Sprint4 Phase 4 联机 smoke + GAP-1 完成报告（2026-04-30）

> **本文用途**：GAP-1 修复落地 + 联机 smoke 验证结果记录。
> GAP-1 段（A）已完成；联机 smoke 段（B）在 Brain dev + LiveKit 环境就绪后补充。

---

## §0 TL;DR

| 段 | 内容 | 状态 |
|:--|:--|:--|
| A — GAP-1 | `ecp_state_ingest.py` + 10 测试 + doc 收口 | ✅ |
| B — 联机 smoke | Editor↔Brain 全链路 5 验收口径 | ⏳ 待环境 |

**测试基线**：230/230 全绿（220 baseline + 10 GAP-1 新增）。

---

## §1 GAP-1 修复详情

### 1.1 问题（audit §5.5 Finding B）

Unity W3.A.3 `LifecycleHeartbeatPublisher` 在 `parrot.ecp.state` topic 以 1Hz + 事件驱动 publish `EcpStateDto`，但 Brain 端：
- `event_ingest` 只路由 `parrot.ecp.event`
- `telemetry_receiver` 路由 `parrot.telemetry` + `parrot.event`
- `parrot.ecp.state` → 落到 **silent-ignore** 分支

结果：BB `session/ecp_state` 永远 None → selection-C tool wrappers 看到 `active_locks=[]` / `active_command_id=""` 从 ECP 侧读不到实际状态。

### 1.2 实施内容

**新文件**：`src/parrot/brain/ecp_state_ingest.py`

| 要素 | 实现 |
|:--|:--|
| 模式 | mirror `attach_telemetry_receiver` — `room.on("data_received")` + topic 过滤 |
| Topic 过滤 | `TOPIC_ECP_STATE = "parrot.ecp.state"` (from `ecp_event.py` — 唯一真相源) |
| 解析 | `json.loads` → dict（不 import EcpStateDto.cs；直接 dict 解析）|
| BB 写入 | `session/ecp_state`，writer = `"brain._rpc_bridge"`（bb_schema.py:178 声明一致）|
| tick 字段镜像 | **不写** `tick/body_state` / `tick/head_state`（writer = `brain.telemetry_receiver`，单 producer 约束）|
| 防御策略 | JSON parse 失败 / 非 dict / schema_version 不匹配 → log debug + skip，不 crash |
| schema_version 策略 | 不匹配 → 警告 + **仍处理**（forward-compatible；旧 Unity 客户端不中断）|
| Metrics | 6 项：`received_count / dispatched_count / parse_failures / schema_version_mismatch / bb_write_failures / foreign_topic_ignored` |

**改动文件**：

| 文件 | 改动 |
|:--|:--|
| `src/parrot/brain/agent.py` | 在 `attach_ecp_event_publisher` 之后加 `attach_ecp_state_ingest(ctx.room)` + GAP-1 注释引用 |
| `src/parrot/shared/bb_schema.py` | `session/ecp_state` 移除 `# CANDIDATE` marker，更新注释为实际 producer |
| `.cursor/memory/architecture/sprint4_phase4_completion_and_final_audit_20260430.md` | §1.1 / §3.3 / §5.3 / §5.4 / §5.5 Finding B / §5.6 全部更新为 ✅ |

**新增测试**（10 项）：`tests/test_ecp_event/test_ecp_state_ingest.py`

| 测试类 | 测试项 | 覆盖 |
|:--|:--|:--|
| `TestAttachSubscribesToDataReceived` | test_registers_data_received_handler | room.on 注册验证 |
| `TestValidPacketWritesBB` | test_writes_session_ecp_state | BB 值验证（body/head/active_cmd/locks）|
| | test_dispatched_count_increments | metrics 验证 |
| | test_sequence_overwrite | 后到包覆盖前包（last-write-wins）|
| `TestForeignTopicSilentlyIgnored` | test_foreign_topic_does_not_write_bb | foreign topic counter |
| `TestMalformedJsonSkippedNoCrash` | test_invalid_json | JSON 错误不 crash |
| | test_non_dict_json_skipped | 非 dict payload 跳过 |
| | test_schema_version_mismatch_still_processes | forward-compat（处理不拒收）|
| `TestMetricsSnapshotKeys` | test_all_expected_keys_present | 6 个 key 全有 |
| | test_initial_all_zeros | 初始值全 0 |

### 1.3 GAP-1 修复后的效果

Selection-C tool wrappers (`tools/_state_context.get_state_snapshot`) 现在可以从 `session/ecp_state` 读取：
- `active_locks` — Unity 端 `active_locks[]` 字段
- `active_command_id` — 当前执行中命令的 ID
- `body_state` / `head_state` — ECP 侧（比 telemetry 侧更新）

`format_state_header()` 在有 active_locks / active_command_id 时将展示 `locks=...` / `active_cmd=...` 字段，让 LLM 真正看到完整 ECP 状态。

### 1.4 测试基线

```
pytest tests/ --ignore=tests/integration -q
→ 230 passed in 3.51s
```

### 1.5 已知设计选择

| 选择 | 理由 |
|:--|:--|
| 不写 tick/body_state | bb_schema single-producer 约束：writer = `brain.telemetry_receiver`；ecp_state_ingest 若强写 = 双写者竞争，可能覆盖更新鲜的 telemetry 包 |
| schema_version 不匹配仍处理 | forward-compatible：Unity 升级 schema_version 后 Brain 端不应直接 break；只 log 警告 |
| session/ecp_state 写完整 dict | 消费方（_state_context）自己 `.get()` 需要的字段，不需要 ecp_state_ingest 做裁剪 |

---

## §2 联机 smoke — 环境配置说明

> **状态**：⏳ 等待环境就绪后补充验证结果

### 2.1 前置环境启动顺序

```bash
# 1. LiveKit dev server (Redis + LiveKit Server)
docker compose -f infra/docker-compose.dev.yml up -d

# 2. Brain agent dev mode (新终端)
python -m parrot.brain.agent dev

# 3. Token 生成
python src/scripts/generate_token.py
# 拷贝 token 到 unity/ArSpike/unity_join_token.txt (或 Inspector)

# 4. Unity Editor: 打开 ParrotSmokeScene → Play
```

### 2.2 环境需求

| 依赖 | 说明 |
|:--|:--|
| Docker + compose | LiveKit + Redis |
| Python .venv | Brain agent + 所有依赖 |
| Unity 2022.3.62f3 | ParrotSmokeScene 已有 W3/W6-7/W8 全套 components |
| `.env` | `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` / `GOOGLE_API_KEY` |

---

## §3 联机 smoke — 5 验收口径（⏳ 待填）

以下表格在联机 smoke 执行后填写：

| # | 验收口径 | 状态 | 证据 |
|:--|:--|:--|:--|
| 1 | 工具 ①：perch_to_finger 体感闭环 | ⏳ | — |
| 2 | 工具 ②：identify_object 同步链（1.9s 内）| ⏳ | — |
| 3 | ECP frontend_state 三态对齐 LLM | ⏳ | — |
| 4 | RefBinding + Event 落地不污染实时帧 | ⏳ | — |
| 5 | 全链路 Editor 跑通（含工具 ④ Photo）| ⏳ | — |

---

## §4 已知 Bug / Finding（联机 smoke 后补充）

待联机 smoke 执行后填写。

---

## §5 Phase 5+ 派生待办（已知）

| 项 | 触发条件 |
|:--|:--|
| EcpState ingest sequence_id 去重 | 真机 spike 发现重复包时加 (unity_identity, sequence_id) 去重 |
| EcpState ingest disconnect 清 BB | OnDisconnect 时把 session/ecp_state 设 None（防旧值残留影响下次 session）|
| 联机 smoke 跑完后继续 P2.5 完成汇报 chat | 全 5 验收 ✅ 后起 |

---

## §6 收口签名（GAP-1 段）

- 新文件：`src/parrot/brain/ecp_state_ingest.py`
- 改动：`agent.py` + `bb_schema.py` + audit doc + test_state_context.py 注释更新
- 测试：230/230 全绿
- entry §8 决策锁：0 漂移
- 下一步：联机 smoke（环境就绪后）→ P2.5 完成汇报 chat
