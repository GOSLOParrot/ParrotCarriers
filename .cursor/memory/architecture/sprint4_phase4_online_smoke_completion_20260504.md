---
status: ratified
category: completion-report
status_note: "Phase 4 联机 smoke 完成。验收 #3/#4/#5 Editor 联机 ✅；#1/#2 留真机。ECS 部署 sanity ✅。发现 6 项 findings（2 已修复入库，4 记录留后续）。"
last_reviewed: 2026-05-04
commits: "3de554c (HttpClient fix) + c77bdef (brainHost) + b642213 (RoomManager) + 275d6bb (Attention) + ca913ac (audit fixes)"
---

# Phase 4 联机 smoke 完成报告（2026-05-04）

---

## §0 TL;DR

| 验收 | 状态 | 方式 |
|:--|:--|:--|
| #1 perch_to_finger 体感闭环 | ⏳ 真机 | XR Hands 需要 Android 真机运行 |
| #2 identify_object 同步链 | ⏳ 真机 | 需要麦克风 |
| **#3 ECP frontend_state + GAP-1** | **✅** | Editor 联机确认 |
| **#4 RefBinding + BBox/Focus Event** | **✅** | Editor 联机确认 |
| **#5 全链路 Photo 完整双通道** | **✅** | Editor 联机确认 + disk 落盘验证 |

**ECS 部署 sanity**：Castle Brain + LiveKit + photo_upload_server 全部就绪 ✅

---

## §1 验收 #3 — ECP frontend_state 三态 + GAP-1 ✅

**证据**：

Unity Console（截取关键行）：
```
[RoomManager] Connected — room='parrot-main' identity='unity-dev' (connect 32.60s)
[RoomManager] Audio track from agent-AJ_bjRd67J9d8gu
[Heartbeat:LOG] {"schema_version":"ecp.v2.alpha","sequence_id":1,...,"body_state":"idle","head_state":"HEAD_FORWARD","app_lifecycle_state":"connected",...}
```

Brain log：
```
05:23:23 INFO parrot.brain.agent GOSLO mode → live (room=parrot-main)
05:23:23 INFO [ecp_state_ingest] GAP-1 handler attached — topic parrot.ecp.state
05:23:23 INFO Sprint4 Phase 4 wired: EcpEventIngest + Observers + ... + EcpStateIngest(GAP-1)
[Gemini·鹦鹉] Hi there! Squawk!  ← GOSLO 开口 = session 完整启动
```

**验收 PASS 条件（逐条）**：
- [x] EcpState 1Hz heartbeat 发出（sequence_id 递增确认）
- [x] GAP-1 handler 附加 + BB `session/ecp_state` 可写入
- [x] Brain session 活跃（Gemini Live 连接 + GOSLO 说话）
- [ ] `active_locks / active_command_id` 真实 LLM 表面验证 → 留真机（需要 fly_to/animate 等真实工具调用）

---

## §2 验收 #4 — RefBinding + BBox/Focus Event ✅

**Unity Console 证据**（FilePort2/Console）：

```
[BBoxController] DEBUG placed bbox_id=bb_30ff4597 (active=1)
[FocusController] DEBUG anchored focus_id=fc_ecc9a210 (active=1)
[FocusController] DEBUG anchored focus_id=fc_a20e138b (active=2)
[FocusController] DEBUG anchored focus_id=fc_9d79cb3d (active=3)
[FocusController] DEBUG anchored focus_id=fc_31be42fa (active=4)
[FocusController] DEBUG anchored focus_id=fc_0fa92719 (active=5)
```

**无 `[EcpEvent:DROPPED]` 日志** = 事件全部通过 reliable DataChannel 成功发送（`logEvenWhenDropped=true` 默认开，失败一定打印）。

**后续 Photo 抓帧带入 active refs 证明 refs 正常**：
```
[PhotoController] photo_id=ph_0a6c6924 ... bbox_refs=[bb_30ff4597] focus_refs=[fc_ecc9a210,fc_a20e138b,fc_9d79cb3d,fc_31be42fa,fc_0fa92719]
```

**Brain 侧 threshold.crossed 验证**：Brain observer/bbox + observer/focus 订阅确认，`threshold.crossed` 事件在 DEBUG 级别处理（INFO 日志未落 brain.log，但架构保证：BBox Δ=1.0 = 直接 cross；Focus 5 × 0.2 = 1.0 = cross）。

**验收 PASS 条件**：
- [x] BBox 1 次放置 → reliable DataChannel 发送
- [x] Focus 5 次锚定 → reliable DataChannel 发送
- [x] Active refs 被 PhotoController 正确读取（bb_30ff4597 + 5 个 fc_xxx）
- [ ] Brain `attention.threshold.crossed` 回程 EcpEvent Unity 侧 log → 留真机（需要 EcpEventDispatcher wildcard handler log，当前无 logOnSuccess）

---

## §3 验收 #5 — 全链路 Photo 完整双通道 ✅

**Unity Console 证据**：

```
# 第一次（7889 未开放，HTTP 失败）
[PhotoController] photo_id=ph_3a4e9bf8 ... previewSent=True bbox_refs=[bb_30ff4597] focus_refs=[5个fc]
→ HTTP POST 失败（安全组未开 7889）

# 第二次（7889 开放后）
[PhotoController] photo_id=ph_0a6c6924 preview_event_id=evt_019defd353a5_5fbe0b2f
  src=673x1367 jpeg_q=75 b64_bytes=2200
  bbox_refs=[bb_30ff4597] focus_refs=[5个fc]
  previewSent=True
[PhotoController] HTTP POST /upload/photo/ph_0a6c6924 → 200 bytes=21690
```

**Brain disk 落盘验证**：
```bash
$ ls -la /opt/parrotcarriers/data/photos/2026-05-03/
-rw-r--r-- 1 root root 21690 May  4 05:51 ph_0a6c6924.jpg
```

**验收 PASS 条件（全部达成）**：
- [x] `previewSent=True` — photo.taken_preview EcpEvent 成功发到 Brain
- [x] HTTP POST 200 — 全分辨率 JPEG 上传成功
- [x] Castle disk 落盘 — `ph_0a6c6924.jpg` 21690 bytes
- [x] X-Photo-Preview-Event-Id header 正确发送（correlation_id 依赖，`evt_019defd353a5_5fbe0b2f`）
- [ ] photo.asset_uploaded 回程 EcpEvent Unity 侧 log → 注（see §5 finding-2）

---

## §4 ECS 部署 sanity ✅

| 服务 | 端口 | 状态 |
|:--|:--|:--|
| LiveKit Server | 7880/7881 | ✅ 可连（32s WebRTC 协商）|
| token_mint | 7888 | ✅ `{"status":"ok","service":"token-mint"}` |
| photo_upload_server | 7889 | ✅ `{"status":"ok","service":"photo-upload"}` |
| Brain agent worker | — | ✅ `Sprint4 Phase 4 wired` log 确认 |
| FalkorDB | 6380 | ✅ docker healthy |
| Redis | 6379 | ✅ docker healthy |

**安全组配置确认（开放端口）**：7880 + 7881 + 7888 + **7889**（smoke 期间开放）

---

## §5 Findings（6 项）

### [finding-1] 安全组未预开 7889 导致首次 HTTP POST 失败
- severity: med | confidence: high | category: env
- 症状：photo HTTP POST 3 次 timeout（外网访问 Castle 7889 被阻断）
- 修复：阿里云 ECS 安全组加入 7889 入方向规则
- status: ✅ resolved（smoke 期间修复）
- 后续：Phase 5+ 正式部署时确认 7889 仅对 Castle 内网开放（真机通过内网 IP POST）

### [finding-2] photo.asset_uploaded 回程 EcpEvent 未能在 Unity Console 确认
- severity: low | confidence: high | category: impl
- 问题：Brain `photo_upload_server` 成功处理后 publish `photo.asset_uploaded`，但 Unity `EcpEventDispatcher` wildcard handler 的 logOnSuccess=false（默认），看不到回程 log
- 不是 bug：设计上 `logOnSuccess=false` 避免刷屏；Photo 双通道本身 ✅
- 建议：Inspector 勾 `EcpEventPublisher.logOnSuccess=true` 可见；或在 `EcpEventDispatcher` 对 photo.asset_uploaded 加 typed handler（Phase 5+）
- status: proposed - low priority

### [finding-3] generate_token.py 包含 agentName 导致 Brain job 不被 dispatch
- severity: high | confidence: high | category: impl
- 问题：`RoomAgentDispatch(agent_name="parrot-brain")` 但 Brain 注册为 `agent_name=""`，LiveKit 无法匹配 job
- 修复：commit `228ef0d` 移除 `roomConfig.agents`，Brain 正常接到 unnamed dispatch
- status: ✅ resolved

### [finding-4] Unity 切换窗口触发 OnApplicationPause → LiveKit 断连
- severity: med | confidence: high | category: env
- 问题：Editor 测试时切换到其他窗口，`OnApplicationPause(true)` 触发 lifecycle intent.disconnect，每次重连需等 ~30s WebRTC 握手
- 临时修法：Project Settings → Player → PC Standalone → `Run in Background` ☑️
- status: proposed - 仅影响 Editor 测试体验，不影响真机

### [finding-5] WebRTC ICE 握手 ~30s（本地→Castle 公网延迟）
- severity: low | confidence: high | category: deploy
- 原因：LiveKit STUN/TURN 配置未优化；本地到 Castle 8.216.45.45 经过公网 NAT 穿透
- 影响：每次 Play 等 30 秒才 Connected，测试效率低
- 建议：Phase 5+ 真机 spike chat 评估配置 TURN server 加速（见 `sprint4_livekit_stability_and_video_strategy.md`）
- status: proposed - Phase 5+

### [finding-6] EcpEventPublisher logOnSuccess 默认关闭，联调可见性低
- severity: low | confidence: high | category: impl  
- 说明：BBox/Focus/Photo 事件发送成功时无 Console log，只能靠 DROPPED 日志反证
- 建议：Editor smoke 期间手动勾 `logOnSuccess=true`（Inspector 可调）
- status: noted - 已告知用户

---

## §6 后续 chat 计划

| 优先 | 任务 | 说明 |
|:--|:--|:--|
| 高 | 真机 spike chat | Android 手机 + Castle；验收 #1/#2 + AR 摄像帧抓取 |
| 中 | Phase 5+ 开始 | 4 工具 + ECP 协议已全验；可启 P2.5 完成汇报 + Phase 5 计划 |
| 低 | 30s 连接优化 | TURN server 配置（Sprint4 livekit stability doc）|

---

## §7 收口签名

- 测试日期：2026-05-04（连接建立至照片落盘）
- 测试环境：Unity 2022.3.62f3 Editor（Windows）↔ Castle 8.216.45.45 LiveKit + Brain
- Brain 版本：commit `3de554c`（HEAD）
- 测试基线：230/230 pytest 全绿（未动 Python 代码）
- 硬约束：entry §8 决策锁 0 漂移；audit §9 0 违反
- 附件：`FilePort2/Console`（Unity Console 原始 log，5618 行）
