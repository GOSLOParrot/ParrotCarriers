---
status: partial
category: completion-report
status_note: "GAP-1 全部落地（含审计修复 ca913ac）。230/230 全绿。联机 smoke 5 验收口径 ⏳ 待环境就绪。"
last_reviewed: 2026-04-30
commits: "1ad3d37 (GAP-1 初版) + ca913ac (审计修复)"
---

# Sprint4 Phase 4 联机 smoke + GAP-1 完成报告（2026-04-30）

---

## §0 完成状态总览

| 任务段 | 状态 | 说明 |
|:--|:--|:--|
| **A — GAP-1 EcpState ingest** | ✅ 完成 | 含审计修复，230/230 |
| **B — 联机 smoke 5 验收口径** | ⏳ 待环境 | 需 docker compose + Brain dev + Unity Play |

---

## §1 GAP-1 功能完成明细

| 功能点 | 状态 | 说明 |
|:--|:--|:--|
| `ecp_state_ingest.py` 文件新建 | ✅ | `src/parrot/brain/ecp_state_ingest.py` |
| `attach_ecp_state_ingest(room)` 函数 | ✅ | 注册 `room.on("data_received")` 回调 |
| Topic 过滤 `parrot.ecp.state` | ✅ | 其他 topic → silent ignore，计入 `foreign_topic_ignored` |
| JSON 解析 + dict 类型检查 | ✅ | 失败 → `parse_failures` counter + return |
| schema_version 不匹配 → **skip（不写 BB）** | ✅（审计修复后） | `ecp.v2.alpha` 之外全部跳过 |
| BB `session/ecp_state` 写入 | ✅ | writer = `"brain._rpc_bridge"`（与 bb_schema:178 一致） |
| **不写 `tick/body_state` / `tick/head_state`** | ✅ | single-producer 约束；writer = `brain.telemetry_receiver` |
| 6 项 metrics（received/dispatched/parse_failures/schema_mismatch/bb_write_failures/foreign_ignored）| ✅ | |
| `agent.py` boot wire-up | ✅ | `attach_ecp_state_ingest(ctx.room)`，位于 publisher 之后 |
| `bb_schema.py` 移除 `# CANDIDATE` | ✅ | 注释更新为实际 producer |
| 10 项测试全绿 | ✅ | `tests/test_ecp_event/test_ecp_state_ingest.py` |
| `test_state_context.py` 注释更新 | ✅ | `test_get_snapshot_handles_missing_keys` 说明更新 |
| audit doc §1.1/§3.3/§5.3/§5.4/§5.5/§5.6 更新 | ✅ | Finding B → ✅ resolved |
| **sequence_id 去重** | ⚠ 未做 | 1Hz 心跳重连场景可能重复写；Phase 5+ 加 (identity, seq_id) 去重 |
| **OnDisconnect 清 BB** | ⚠ 未做 | `session/ecp_state` 不随断连自动清空；旧值在下次 connect 前持续存在 |

### 1.1 schema_version 策略（审计后最终决策）

| 场景 | 行为 |
|:--|:--|
| `schema_version == "ecp.v2.alpha"` | 正常写入 BB `session/ecp_state` |
| `schema_version` 缺失或不匹配 | skip（`schema_version_mismatch` +1）；不写 BB；不 crash |

**理由**：防止 Unity 端升级 schema 后，Brain 端写入不兼容格式污染 `session/ecp_state`，导致 `_state_context.get_state_snapshot()` 读到格式错误的 dict 影响 LLM 注入。Unity 升级 schema_version 时需同步更新 `_EXPECTED_SCHEMA_VERSION`。

### 1.2 GAP-1 修复效果

修复前：`session/ecp_state` 永远 None → `format_state_header()` 里 `active_locks` / `active_command_id` 永远空白。

修复后（联机时）：Brain 每秒收到 Unity `EcpStateDto`，写入 BB → `_state_context` 读到真实值 → LLM 看到 `[GOSLO state] locks=fly_to active_cmd=cmd_abc12345`。

---

## §2 测试基线

```
pytest tests/ --ignore=tests/integration -q
→ 230 passed in 3.54s
```

| 测试套 | 项数 |
|:--|:--|
| W8 新增 (test_ecp_state_ingest.py) | 10 |
| 原有 baseline | 220 |
| **总计** | **230** |

10 项覆盖：room 注册 / BB 写入 / 序列覆盖 / 外 topic 忽略 / JSON 错误 / 非 dict / schema_version skip / metrics 全 keys / metrics 初始值全零。

---

## §3 联机 smoke — 环境启动顺序

> **状态**：⏳ 等待用户启动环境后执行

```bash
# 1. LiveKit + Redis
docker compose -f infra/docker-compose.dev.yml up -d

# 2. Brain dev mode（新终端）
python -m parrot.brain.agent dev

# 3. 生成 token
python src/scripts/generate_token.py
# 填入 unity/ArSpike/unity_join_token.txt 或 Inspector

# 4. Unity Editor → 打开 ParrotSmokeScene → Play
```

**依赖 `.env` 变量**：`LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` / `GOOGLE_API_KEY`

---

## §4 联机 smoke — 5 验收口径（⏳ 待填）

| # | 验收口径 | 触发操作 | 期望证据 | 状态 |
|:--|:--|:--|:--|:--|
| 1 | 工具 ①：perch_to_finger 体感闭环 | Editor: HandSource ContextMenu → `Debug: Fire "index_finger_branch" gesture` | AnimationDriver state=PERCHED_ON_HAND + HEAD_TILT；BB tick/body_state 更新 | ⏳ |
| 2 | 工具 ②：identify_object 同步链（1.9s 内）| Brain 终端：sim_unity_client + PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1，让 GOSLO 说"那是什么" | Console: [capture]/[L0 no match]/[L1 no match] 三段；observer.sighting metrics +1；< 1.9s | ⏳ |
| 3 | ECP frontend_state 三态 + GAP-1 | 验收 #1 同时 | Brain log: `[GOSLO state] body=perched_on_hand ...`；`session/ecp_state` BB 有值；`active_locks/active_command_id` 非空（如有命令在途）| ⏳ |
| 4 | RefBinding + Event 不污染实时帧 | Editor: BBoxController × 1 + FocusController × 5 | Brain log: `attention.threshold.crossed` publish；Unity EcpEventDispatcher wildcard log；hint_writer metrics bumps_skipped_unresolved +1（UNRESOLVED 是常态）| ⏳ |
| 5 | 全链路 Editor 跑通（含工具 ④ Photo）| Editor: PhotoController ContextMenu → `Debug: Capture Test Photo` | EcpEvent photo.taken_preview 到 Brain；HTTP POST 200；`data/photos/.../ph_xxx.jpg` 落盘；photo.asset_uploaded 回程；observer.photo metrics photo_nodes_upserted +1 + photo_nodes_updated_with_asset +1 | ⏳ |

---

## §5 已知遗留问题与 Phase 5+ defer

| 项 | 严重性 | 触发条件 / 计划 |
|:--|:--|:--|
| GAP-1 sequence_id 去重 | 低 | 真机重连场景 1Hz 心跳可能短暂重复写 BB；Phase 5+ 加 `(unity_identity, sequence_id)` 去重 |
| GAP-1 OnDisconnect 清 BB | 低 | `session/ecp_state` 跨 session 保持旧值，下次 connect 覆盖前可能被读到（无 stale 危害，只是不精确）；Phase 5+ 加 `OnDisconnected` handler |
| W8 reconnect bytes 跨重启 | 低 | 内存缓存，App restart 后 `FullResJpeg=null` → Failed 照片不可恢复；Phase 5+ 加 PlayerPrefs / 磁盘缓存 |
| W8 AR 正式帧抓取 | 中 | Editor smoke 用 Camera.main；真 AR 帧需 ARCameraManager.frameReceived 路径；Phase 5+ 接 W3.A.2/A.3 baseline |
| W8 previewSent=false 时 PhotoNode 无法建立 | 中（设计限制）| room 断开时拍照，preview 不到 Brain，HTTP POST 收到 asset 后 observer.photo log `asset_for_unknown_photo_id`；Phase 5+ 考虑本地存 preview payload 等重连后补发 |

---

## §6 Commits

| Commit | 内容 |
|:--|:--|
| `1ad3d37` | GAP-1 初版：ecp_state_ingest.py + 10 测试 + agent wire-up + doc 收口 |
| `ca913ac` | 审计修复：schema_version 策略改为 skip；测试名/断言更新 |
