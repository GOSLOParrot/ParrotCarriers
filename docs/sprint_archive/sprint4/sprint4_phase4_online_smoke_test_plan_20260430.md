---
status: ratified
category: test-plan
status_note: "Phase 4 联机 smoke + ECS 推送测试建议。承接 W8 Unity 完成报告 + GAP-1 完成报告 + Phase 4 完成审计 §2/§5。新 chat 拿此 doc 即可执行；包含本地 smoke + ECS 部署 sanity，真机 spike 留独立 chat。"
last_reviewed: 2026-04-30
acceptance_target: "Phase 4 §0.2 验收口径 #5（联机部分）从 ⏳ → ✅"
---

# Phase 4 联机 smoke 测试计划（2026-04-30）

> **本文用途**：把 Phase 4 协议升级 + W3-W8 全部 chat 落地后剩下的"真跑一遍 Editor↔Brain↔Editor 全链路"工作整理成可执行测试清单 + ECS 推送 sanity。新 chat 复制此 doc 即可作为执行 SOP。
>
> **关联**：
> - `sprint4_phase4_completion_and_final_audit_20260430.md` §2（5 验收口径）+ §8.2（联机 smoke chat 派发）
> - `sprint4_phase4_w8_unity_completion_20260430.md` §5（离线 Editor smoke 已跑过的部分）
> - `sprint4_phase4_smoke_and_gap1_completion_20260430.md` §3 §4（环境启动顺序 + 5 验收 ⏳ 待填）
> - `sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md`（启动 prompt — 本 doc 是它的 B 段补充材料）

---

## §0 W8 + GAP-1 完成报告审计结论（终审）

读 `sprint4_phase4_w8_unity_completion_20260430.md` + `sprint4_phase4_smoke_and_gap1_completion_20260430.md` 的审计结论：

| 维度 | W8 Unity 报告 | GAP-1 报告 |
|:--|:--|:--|
| Prompt B.1-B.6 / A 段 全覆盖 | ✅ | ✅ |
| 12 字段 payload 对齐 / 6 metrics keys | ✅（与 bb_schema 注释逐字段核对）| ✅（含 schema_version skip 策略）|
| 硬约束 10 条遵守 | ✅ | ✅ |
| 内部审计修复（`ca913ac`）抓到的真实 bug | reconnect bytes 缓存 / HTTP 4 次重试 / scene .meta 入库 | schema_version skip vs match 策略 |
| 跨 doc 同步 | entry §8.7 W8 row 已升级；Phase 4 final audit §3.1/§3.3/§5.3/§5.5 同步 | bb_schema # CANDIDATE 移除；entry §8.2 通道矩阵更新；Finding B 标 ✅ resolved |
| 测试基线 | 220 → 230（+10 GAP-1）全绿 | 同（10 ecp_state_ingest tests）|
| 诚实标注遗留项 | reconnect bytes 跨重启 / AR 正式帧 / 工具柜 UI 等 8 项 Phase 5+ defer | sequence_id 去重 / OnDisconnect 清 BB 等 5 项 Phase 5+ defer |

**审计结论：两报告全部 PASS，0 残留 finding 需要回头修**。本 chat 不再补 Brain 端代码 / 不动协议契约；ECS 推送 + 联机 smoke 是接下来唯一 v1 阻塞项。

**给新 chat 的小提示**（不算 finding，仅协调说明）：
- W8 Unity 报告 §6 Commits 列表是 `f6f3da9 + ca913ac` 两项；实际还有 `f3cba34`（doc-only 同步）和 GAP-1 的 `1ad3d37` 在同一时间合入。新 chat 看 git log 时不要被 commit 数对应不上吓到，是合并 chat 的自然现象。

---

## §1 测试范围与不范围

### 1.1 本 chat 范围（联机 smoke chat）

| 测试 | 目的 |
|:--|:--|
| **测试 1**：本地联机 smoke（Editor + 本机 docker compose） | 验 5 验收口径 + GAP-1 + W8 photo 全链路；本地能跑通 = Phase 4 §0.2 #5 离线/伪联机 ✅ |
| **测试 2**：ECS 部署 sanity（Castle 跑 Brain + LiveKit + photo_upload_server） | 验部署脚本 + 服务 reachability + .env 同步；不验业务功能（功能由测试 1 保证） |

### 1.2 不在本 chat 范围（明确 defer）

| 项 | 后续 chat |
|:--|:--|
| **真机 spike**（手机 ADB / TestFlight + Castle URL）| 真机 spike chat（独立）— 测试 1+2 都过后再起 |
| 真机特定项：蓝牙音频 / AR Camera 实拍 / 5G 网络延迟 / Android 16KB 对齐 | 真机 spike chat |
| 性能 profile（identify_object 真 1.9s 预算 / EcpState 1Hz 心跳 jitter）| 真机 spike chat（性能在真机才有意义）|
| 隐私 / 治理 / 对象存储替换 / HTTP 鉴权 | Phase 5+ |

---

## §2 测试 1：本地联机 smoke（5 验收口径）

### 2.1 前置环境

```bash
# 1. LiveKit + Redis dev stack
docker compose -f infra/docker-compose.dev.yml up -d
# 验证：docker ps | grep -E "livekit|redis"

# 2. .env 至少需要这些键：
#    LIVEKIT_URL=ws://localhost:7880
#    LIVEKIT_API_KEY=devkey
#    LIVEKIT_API_SECRET=...（看 docker-compose.dev.yml）
#    GOOGLE_API_KEY=...（Gemini Live；本 chat 你的 dev key）
#    PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1（验收 #2 需要）

# 3. Brain agent dev mode（独立终端）
.venv\Scripts\python.exe -m parrot.brain.agent dev
# 期望日志：
#   "Brain L1: starting AgentSession in room '...'"
#   "Sprint4 Phase 4 wired: EcpEventIngest + Observers + ..."
#   "EcpEventPublisher attached — topic parrot.ecp.event ..."
#   "EcpStateIngest attached ..." （GAP-1 wire-up 证据）
#   "[photo_upload] server started host=127.0.0.1 port=7889 ..." （W8 wire-up 证据）

# 4. 生成 token + 写入 Unity
.venv\Scripts\python.exe src/scripts/generate_token.py
# 输出 token + 写入 ../unity_join_token.txt
# Unity Editor: ParrotSmokeScene → RoomManager Inspector 确认 token 已加载

# 5. Unity Editor → ParrotSmokeScene → Play
# 期望 Console:
#   "[RoomManager] Connected — room='parrot-main' identity='unity-...'"
#   "[Heartbeat:DC] state sent ts=..." （W3.A.3 EcpState 心跳）
#   "[AttentionConfigEchoPublisher] EchoNow sent=True ..." （F-05 Echo）

# ⚠️  连 Castle Brain 时的额外检查（2026-04-30 新增）：
#
# A. PhotoController.brainHost 必须改成 Castle IP
#    Scene Hierarchy → Photo → PhotoController Inspector
#    → Brain Host 字段：127.0.0.1 改为 8.216.45.45（或 Castle 内网 IP）
#    否则验收 #5 HTTP POST 全部失败（连本机 7889 打不到 Castle）
#
# B. ParrotSmokeScene.unity 为手工 YAML 编辑，打开后先看 Console 有无
#    "Failed to load scene" / "unexpected token" 等 YAML 解析错误
#    如有报错，重跑 Tools/Parrot/Build A2 Smoke Scene 重建场景即可
```

### 2.2 验收 #1 — 工具 ① perch_to_finger 体感闭环

**触发**：Editor Hierarchy → 选 HandSource GameObject → Inspector ⋮ → `Debug: Fire "index_finger_branch" gesture`

**期望证据**（Unity Console + Brain 终端）：

| 来源 | 期望 log |
|:--|:--|
| Unity Console | `[XRHandTracker] gesture=open_palm published`<br/>`[AnimationDriver] state Idle → FlyToHand`<br/>`[AnimationDriver] arrived index finger middle joint → state PerchedOnHand head HEAD_TILT`<br/>`[Heartbeat:DC] state event-driven body=PERCHED_ON_HAND head=HEAD_TILT` |
| Brain 终端 | `[ecp_state_ingest] received parrot.ecp.state body=PERCHED_ON_HAND head=HEAD_TILT`<br/>`BB tick/body_state: ... → PERCHED_ON_HAND` |
| 验 GAP-1 | Brain BB `session/ecp_state` 现在含完整 EcpStateDto；之前 GAP-1 修复前是空 |

**验收 PASS 条件**：
- [ ] Animation 播 fly_to_hand → 站手上 → 自动接续 head tilt
- [ ] EcpState 心跳事件驱动触发（不是等 1Hz 定时）
- [ ] Brain 收到并写 BB（GAP-1 接通）
- [ ] LLM 后续说话不会"GOSLO 跳舞时说出门散步"（GOSLO Live 主动说一句话验证 — 需要麦克风触发）

### 2.3 验收 #2 — 工具 ② identify_object 同步链 < 1.9s

**前置**：环境变量 `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1`（默认 off，audit §3.4 安全 gate）

**触发**：用麦克风对 GOSLO 说"那是什么？"或类似让 Gemini 调 identify_object

**期望证据**（Brain 终端）：

```
[brain.tools.identify_object] _match_staged description="..." category="..."
  [capture] ok 280ms
  [L0] no L2-B match (45ms)
  [L1] Graphiti search ... 600ms
  [L1] no Graphiti match (610ms timeout)
unknown: ... did not match anything in working memory or Graphiti.
snapshot_id: snap_xxx
[observer.sighting] sighting.unmatched received → archiver_attempts +1
```

**验收 PASS 条件**：
- [ ] 三段 stage info 都在 LLM-facing return 里
- [ ] 总时长 < 1.9s（看 stage info 的 ms 累加）
- [ ] capture 失败 / L0 timeout / L1 timeout 任一段单独 graceful degrade
- [ ] sighting.unmatched EcpEvent 真发出
- [ ] observer.sighting metrics `unmatched_received` +1

### 2.4 验收 #3 — ECP frontend_state 三态对齐 LLM（GAP-1 关键验证）

**触发**：让 GOSLO 调 `fly_to(1, 2, 3)`（语音"飞到那里"）—— 同时 #1 站手上时

**期望证据**（Brain 终端）：

```
fly_to result:
[GOSLO state] body=PERCHED_ON_HAND head=HEAD_TILT cognitive=THINKING locks=fly_to active_cmd=cmd_xxx
{actual RPC response JSON}
```

**关键 GAP-1 验证点**：
- [ ] **`active_cmd=cmd_xxx`** 显示真实命令 ID（GAP-1 修复前永远 missing）
- [ ] **`locks=fly_to`** 显示当前活跃 lock（同上）
- [ ] body / head 反映 Unity 当下真实状态（不是默认值）
- [ ] cognitive 跟随 Gemini agent_state_changed 事件变化

**验收 PASS 条件**：
- [ ] 至少 3 个 tool call（fly_to / animate / set_video_tier）的 return 都看到完整 selection-C header
- [ ] GOSLO 说话内容与 body 状态一致（"我在你手上呢，我先飞下去"等）

### 2.5 验收 #4 — RefBinding + Event 不污染实时帧

**触发 A — BBox**（Editor Hierarchy → BBoxController GameObject → Inspector ⋮ → `Debug: Place Test BBox`）

**触发 B — Focus**（FocusController → ⋮ → `Debug: Anchor Test Focus` × 5 次连点）

**期望证据**（Unity Console + Brain 终端）：

| 来源 | 期望 log |
|:--|:--|
| Unity Console | `[BBoxController] PlaceBBox bbox_id=bb_xxx → publish bbox.placed`<br/>`[EcpEvent:SENT] event_type=bbox.placed`（连接成功）|
| Brain 终端 | `[event_ingest] dispatched event_type=bbox.placed event_id=evt_...`<br/>`[observer.bbox] placed bbox_id=bb_xxx → bind ref_id=ref_...`<br/>`[attention.threshold] crossed subject=bbox:bb_xxx weight=1.00 source_event_id=...`<br/>`[event_publisher] publishing attention.threshold.crossed correlation_id=...` |
| Unity Console（回程）| `[EcpEventDispatcher] received attention.threshold.crossed payload={"ref_id":"ref_...","weight":1.0,...}` |

**5 次 Focus 后**：
- [ ] 第 5 次（5 × 0.2 = 1.0）触发 cross
- [ ] 前 4 次仅 `[event_ingest] dispatched`，无 cross

**验收 PASS 条件**：
- [ ] BBox 1 次直接 cross（Δ_bbox=1.0）
- [ ] Focus 5 次累加 cross（Δ_focus=0.2）
- [ ] BB `transient/current_attention_hint` 写入（外读：`from parrot.scheduler.blackboard import open_bb_client; open_bb_client(name='r', writer='test').get('transient/current_attention_hint')`）
- [ ] hint_writer metrics `bumps_skipped_unresolved` +1（设计意图 — Phase 4 W6-7 常态）
- [ ] 实时帧（30-60Hz pose / hand_gesture）依然在 lossy 通道，不被 reliable EcpEvent 卡

### 2.6 验收 #5 — 全链路（含工具 ④ Photo）

**触发**：Editor Hierarchy → Photo GameObject → PhotoController ⋮ → `Debug: Capture With Active Refs`（先做 #4 BBox + Focus 让 active refs 非空）

**期望证据**（5 段 log 串联）：

| 段 | 来源 | 期望 |
|:--|:--|:--|
| 1. Unity preview 生成 | Unity Console | `[PhotoController] photo_id=ph_xxx ... b64_bytes=N previewSent=True` |
| 2. Brain 收 preview | Brain 终端 | `[event_ingest] dispatched photo.taken_preview event_id=evt_xxx`<br/>`[observer.photo] PhotoNode upserted photo_id=ph_xxx`<br/>BB `transient/last_photo_event` stage="preview" 写入 |
| 3. Unity HTTP POST | Unity Console | `[PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=N` |
| 4. Brain 收 HTTP + publish 回程 | Brain 终端 | `[photo_upload] saved photo_id=ph_xxx bytes=N publish_ok=True`<br/>`[event_publisher] published photo.asset_uploaded` |
| 5. Brain observer 接回程 | Brain 终端 | `[observer.photo] PhotoNode photo_id=ph_xxx asset_ref=/upload/photo/2026-04-30/ph_xxx.jpg`<br/>BB `transient/last_photo_event` 升级 stage="asset_uploaded" |

**Disk 落盘验证**：
- [ ] 文件存在：`data/photos/2026-04-30/ph_xxx.jpg`
- [ ] 大小 = HTTP POST 报告的 bytes
- [ ] 可打开看（真 JPEG）

**Unity → Brain 回程触发**（如 Unity 端有 wildcard handler）：
- [ ] Unity Console 出现 `[EcpEventDispatcher] inbound event_type=photo.asset_uploaded`

**验收 PASS 条件**：5 段 log 全部出现 + disk 文件可打开 + observer.photo 两次 metrics 各 +1（`photo_nodes_upserted` + `photo_nodes_updated_with_asset`）

---

## §3 测试 2：ECS 部署 sanity

### 3.1 前置

| 项 | 命令 / 检查 |
|:--|:--|
| Castle ECS IP / SSH | 确认能 SSH 到 Castle（参考 `infra/sync-castle.ps1`）|
| docker compose 在 Castle | `ssh castle "cd ~/parrot && docker compose ps"` 看现状 |
| Castle .env | 与本地 .env 比对：`LIVEKIT_URL` 改 `wss://<castle-domain>:7880`；`LIVEKIT_API_SECRET` 必须一致；`GOOGLE_API_KEY` 必须有 |

### 3.2 推送代码

```bash
# 本地 → Castle 同步
.\infra\sync-castle.ps1                # 仅代码
# 或
.\infra\sync-castle.ps1 -All           # 代码 + .env + nanobot persona
```

**验证推送成功**：
- [ ] `ssh castle "cd ~/parrot && git log --oneline -3"` 看到本地最新 3 个 commit
- [ ] `ssh castle "cd ~/parrot && cat src/parrot/brain/photo_upload_server.py | head -20"` 看到 W8 W8 文件存在
- [ ] `ssh castle "cd ~/parrot && cat src/parrot/brain/ecp_state_ingest.py | head -20"` 看到 GAP-1 文件存在

### 3.3 安装新依赖（W8 引入 fastapi）

```bash
# Castle 上跑
ssh castle "cd ~/parrot && .venv/bin/pip install '.[http,memory,dev]'"
# 或 Docker 化部署：rebuild infra/Dockerfile.brain
```

**验证依赖安装**：
- [ ] `ssh castle ".venv/bin/python -c 'import fastapi; print(fastapi.__version__)'"`
- [ ] 同上 `import uvicorn; import httpx; import rustworkx`

### 3.4 服务启停 + health check

| 服务 | 端口 | health 命令 |
|:--|:--|:--|
| LiveKit Server | 7880 (TCP) + 7881 (TCP) + 3478 (UDP/TURN) | `curl https://<castle>:7880/` 应该返回 LiveKit JSON banner |
| token_mint | 7888 | `curl http://localhost:7888/health` → `{"status":"ok","service":"token-mint"}` |
| **photo_upload_server**（W8 新增） | 7889 | `curl http://localhost:7889/health` → `{"status":"ok","service":"photo-upload"}` |
| Brain agent worker | (LiveKit Worker, 不监听 port) | `tmux attach -t brain` 看日志确认 "Sprint4 Phase 4 wired ..." |
| FalkorDB / Graphiti | 6380 | `redis-cli -p 6380 ping` |
| Redis | 127.0.0.1:6379 | `redis-cli ping` |

**关键确认**：
- [ ] photo_upload_server 真起来了（W8 新东西，agent boot 时启动 — 看 brain tmux log "[photo_upload] server started"）
- [ ] photo_upload_server 监听的 host 是 `127.0.0.1`（默认）— 如要接受 Unity 真机的 HTTP POST，需改 `PARROT_PHOTO_UPLOAD_HOST=0.0.0.0` 并开放 7889 端口
- [ ] Castle 安全组放通：7880 + 7881 + 7888 + (7889 if Unity 真机要 POST)

### 3.5 .env 同步检查

```bash
# 本地 vs Castle .env 关键键比对
diff <(ssh castle "cat ~/parrot/.env | grep -v '^#' | sort") <(cat .env | grep -v '^#' | sort)
```

**必须一致的键**（cross-machine secret coupling）：
- [ ] `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`（token_mint 与 LiveKit Server 必须同）
- [ ] `PARROT_MINT_SECRET`（Unity 调 mint 用）
- [ ] `GOOGLE_API_KEY`（Brain Gemini Live 用）

**必须不同**的键：
- [ ] `LIVEKIT_URL` 本地 `ws://localhost:7880` / Castle `wss://<castle-domain>:7880`
- [ ] `PARROT_PHOTO_UPLOAD_HOST` 本地 `127.0.0.1` / Castle `0.0.0.0`（如真机要 POST）

### 3.6 Castle 端 sanity smoke

```bash
# 在 Castle 上跑（不开 Unity，仅 Brain 自检）
ssh castle "cd ~/parrot && .venv/bin/python -m parrot.brain.agent console"
# 期望 console 模式启动 — 不连 LiveKit Server，仅验 Brain 模块加载 OK
```

**期望 log 包含**：
- [ ] `Sprint4 Phase 4 wired: EcpEventIngest + Observers + AttentionConfigHandler + FocusBboxThreshold + Publisher`
- [ ] `[photo_upload] server started host=0.0.0.0 port=7889 cache_root=data/photos`
- [ ] `[ecp_state_ingest] attached ...`（GAP-1 wire-up）
- [ ] No traceback / fatal error

---

## §4 测试 3 — 真机 spike（**不在本 chat 范围**，仅 spec 派发）

后续真机 spike chat 应在测试 1 + 2 都 ✅ 后启动。验收同 §2.2-2.6 但增加：
- 蓝牙音频路由（Sprint3 已踩坑，参考 `livekit-unity-sdk.mdc`）
- AR Camera 真实平面 + 帧抓取（W3.A.2/A.3 baseline）
- Android 16KB ELF 对齐（`tools/verify_so_alignment.ps1`）
- 5G / WiFi 网络抖动下 EcpEvent dedup 真实触发（dedup_dropped_count > 0）
- 1.9s identify_object 预算真机超 / 不超

派 prompt 时引本 doc §4 + W6-7 Unity completion §10 前向兼容审计 + sprint4_livekit_stability_and_video_strategy。

---

## §5 失败模式 + bug 上报模板

### 5.1 失败分类决策树

```
某 验收 FAIL ?
├── 是 wire schema / 协议级问题（payload 字段缺 / topic 错 / event_type 漂移）
│   └── 写 finding 入新审计 doc，不改协议（按 audit §6.3 硬约束）
│   └── 报告用户后用户决定是否回 W4-5/W6-7/W8 Brain chat 修
├── 是 实现级 bug（代码里 typo / 逻辑错 / metric 失准）
│   └── 直接修 Brain（不动 wire schema），加测试，commit
│   └── 测试基线必须保持全绿（230+/230+）
├── 是 Unity 端 bug（手势触发不灵 / payload 字段没填）
│   └── 不改！记 finding 派回 W3.A.2 / W6-7 / W8 Unity chat
└── 是 环境 / 配置问题（.env / docker / port / 服务挂）
    └── 修配置 + 写 README 段；不算 finding
```

### 5.2 finding 上报模板（与 Brain 自审 audit 同款）

```text
[finding-N] severity:high|med|low  confidence:high|med|low  category:protocol|impl|unity|env
file:        path:line
problem:     一句话 — 哪里出问题
proposal:    一句话 — 想怎么改
why:         一段 — 理由（特别 protocol-violating 必须说）
considered_intent: yes|no — 是否考虑过这是 Phase 4 故意 defer
status:      applied | proposed | rejected | wait-for-user
```

---

## §6 完成后必交付

新 chat 跑完 §2 + §3 后：

1. **联机 smoke 完成报告 doc**（建议路径 `architecture/sprint4_phase4_online_smoke_completion_20260430.md`）：
   - §2.2-2.6 5 验收口径逐条状态（PASS / FAIL / 部分 + 证据 log 截取）
   - §3 ECS 部署 sanity 状态（含 photo_upload_server reachability 关键确认）
   - 5 失败 / 不预期 log 上报清单（按 §5.2 模板）
   - 已知遗留待真机 spike chat 处理项

2. **Phase 4 完成审计 doc 升级**（`sprint4_phase4_completion_and_final_audit_20260430.md`）：
   - §2 验收 5 条 #5 状态 `离线 ✅ / 联机 ⏳` → 真实结果
   - §0 TL;DR 验收 4.5/5 → 5/5（如全绿）

3. **active_context.md 升级**：
   - "下一步" 段从 "联机 smoke 待执行" → "真机 spike 待执行 + P2.5 完成汇报准备"

4. **commits**：建议 ≥ 2 个：
   - `docs: Phase 4 联机 smoke 完成报告（5 验收 + ECS sanity）`
   - `docs(sprint4/phase4): 完成审计 verdict 升级 5/5 + active_context 同步` (如全绿)

---

## §7 推荐执行顺序

| 步 | 内容 | 时长 |
|:--|:--|:--|
| 1 | 本地 §2 5 验收口径全跑（先简单后复杂：先 #3 GAP-1 验证 → #1 → #4 → #5 → #2）| 1-2 小时 |
| 2 | 推送 ECS（`sync-castle.ps1`）| 5 分钟 |
| 3 | Castle 装新依赖（fastapi / uvicorn / httpx）| 10 分钟 |
| 4 | §3 ECS 部署 sanity（health checks + .env diff）| 30 分钟 |
| 5 | （可选）Castle 跑 brain console 自检 | 10 分钟 |
| 6 | 写完成报告 + commit | 30 分钟 |

**总预算**：3-4 小时（顺利）；如果 §2 暴露任何 bug 走 §5.1 决策树，时长翻倍。

---

## §8 不推荐做的事（防 scope creep）

新 chat 严守：

1. **不改协议契约** — entry §8 / audit §9 / EcpEvent enum / topic / 8KB / schema_version 全锁
2. **不补 Phase 5+ defer 项**（隐私 / 对象存储 / sequence_id 去重 / OnDisconnect 清 BB / Unity AR 正式帧抓取 / 工具柜 prefab 等）
3. **不动 Unity 端代码**（Unity 出 bug 记 finding 派回去）
4. **不跑真机**（独立 chat）
5. **不做性能 profile**（真机才有意义）
6. **不写新 chat launch prompt**（已有 `sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md`，本 doc 是它的 B 段补充材料）

---

## §9 引用

- `architecture/sprint4_phase4_completion_and_final_audit_20260430.md` — Phase 4 主收口
- `architecture/sprint4_phase4_smoke_and_gap1_completion_20260430.md` — GAP-1 完成 + 联机 smoke ⏳
- `architecture/sprint4_phase4_w8_unity_completion_20260430.md` — W8 Unity 半边完成
- `architecture/sprint4_phase4_smoke_and_gap1_chat_launch_prompt.md` — 启动 prompt（A 段已完成；B 段是本 doc 补充）
- `architecture/sprint4_phase4_entry_20260430.md` §8 — 决策锁
- `infra/sync-castle.ps1` / `infra/deploy-castle.sh` — ECS 同步脚本
- `.env.template` / `.env` — 配置基线
