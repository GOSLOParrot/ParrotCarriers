---
status: ratified
created: 2026-04-23
---

# Sprint 3 模拟推演 + Bug 修复台账

> 类比 Sprint 2 附录 B。Sprint 3 代码落地后对全链路做路径推演，发现 5 个问题并当场修复。

---

## 推演路径一览

### Path A: SceneProfileManager → setScene → Brain BB

```
Unity 启动
  → SceneProfileManager.DetermineProfile()
  → Android 设备 + ARCore → AR_HANDHELD
  → OnRoomConnected() → SendSetSceneRpcCoroutine()
  → PerformRpc("setScene", {"scene":"ar_handheld"})
  → Brain onSetScene handler (B5 修复后新增)
  → _rpc_bridge.set_scene(Scene.AR_HANDHELD)
  → BB session/scene = AR_HANDHELD
  → ContextInjector C3 播报场景变化
```

### Path B: RoomManager → onSceneReady → Gemini 打招呼

```
Unity Room 连接成功 → TriggerGreetingAfterDelay(0.5s)
  → 等 500ms → 找 Brain (p.Identity.StartsWith("agent-"))
  → PerformRpc("onSceneReady", {"time_of_day": "morning"})
  → Brain _on_scene_ready handler
  → session.generate_reply(instructions=打招呼)
  → Gemini 输出: "早上好！..."
```

### Path C: TapToPlace → ARAnchor → AnimationDriver.FlyTo → onGosloPlaced

```
用户点击桌面
  → ARRaycast hit → plane.extents 面积校验 ≥ 0.09m²
  → PlaceGoslo(targetPos)
  → Instantiate(gosloPrefab) or Find("GOSLO")
  → AnimationDriver.FlyTo(targetPos)
  → 每帧 UpdateFly(): MoveTowards + Slerp → 到达 → SetState(Idle)
  → ARAnchor 创建 (AR 设备路径)
  → NotifyBrainPlacementCoroutine()
  → PerformRpc("onGosloPlaced", {"x":..,"y":..,"z":..})
  → Brain _on_goslo_placed: log only
```

### Path D: set_video_tier tool → Supervisor → RebuildTrack

```
用户: "视频全开"
  → Gemini 调用 set_video_tier(tier="VIDEO_FULL")
  → PerceptionSupervisor.set_manual_override(combo, hold_s=300)
  → BB session/video_tier = VIDEO_FULL
  → Supervisor _on_decision_committed()
  → push_video_tier("VIDEO_FULL") → Unity PerformRpc "setVideoTier"
  → VideoTierReceiver.ApplyTier(Full)
  → ARVideoPublisher.ApplyVideoTier(Full)
  → RebuildTrack(Full) coroutine:
    → SendTrackRebuildingRpc(rebuilding=true)
      → PerformRpc("onVideoDegraded", {"reason":"track_rebuilding"})
      → Brain vision/state: TRACK_REBUILDING → PAUSED
      → Supervisor: visual_state=PAUSED → 不计入 degraded_since
    → UnpublishTrack → PublishTrack(1Mbps/30fps)
    → SendTrackRebuildingRpc(rebuilding=false)
      → PerformRpc("onVideoDegraded", {"reason":"ok"})
      → Brain: visual_state → ACTIVE
```

### Path E: identify_object L2-B Path 2 → 快速命中

```
Gemini 调用 identify_object("蓝色杯子", action="match")
  → _match_known("蓝色杯子", "")
  → _l2b_quick_match: L2BGraph.get_node_by_label("蓝色杯子")
    → 子串匹配 label.lower() in "蓝色杯子"
    → 找到 node.label="蓝色马克杯", evidence_score=0.75 ≥ 0.5 ✓
    → confirmation != GHOST ✓
    → 返回 node
  → _upsert_to_l2b: attention += 0.2 (不写 Graphiti)
  → 返回 "L2-B 快速命中: '蓝色马克杯'..."
```

### Path F: A10 heartbeat → Supervisor 升档

```
A10 启动: python -m parrot.a10.heartbeat
  → start_a10_heartbeat()
  → r.setex("parrot:a10_heartbeat", 60, "alive")
  → 每 30s 刷新

Castle Supervisor._control_loop (每 1s):
  → _check_a10_health()
  → r.ttl("parrot:a10_heartbeat") → 45s (正常)
  → a10_healthy = True
  → _update_timers: a10_up_since = now (首次见到)
  → 60s 后 decide(): a10_up_long_enough=True + visual_acceptable=True
  → new_combo = (VIDEO_FULL, DSG_FULL)
  → push_video_tier("VIDEO_FULL") → Unity track 升档
```

### Path G: Token Mint → Unity 连接

```
LauncherUI.OnConnectClicked()
  → TokenService.FetchToken(deviceId)
  → PlayerPrefs 检查 → 过期/不存在
  → POST http://<castle>:7888/mint
    Authorization: Bearer <PARROT_MINT_SECRET>
    {"room":"parrot-main","identity":"unity-<deviceId>"}
  → token_mint.mint_token(): _generate_token() → JWT
  → {"token":"<jwt>","url":"ws://...","expires_at":1234567890}
  → PlayerPrefs 缓存 24h
  → RoomManager.Connect(token, url)
  → Room 连接成功
```

---

## 发现的 5 个 Bug + 修复

| # | 级别 | 根因 | 修复位置 |
|:--|:-----|:-----|:---------|
| B1 | 高 | `PerformRpc` 用了命名参数语法，SDK 要求 `new PerformRpcParams{...}` | `SceneProfileManager`, `TapToPlace`, `ARVideoPublisher`, `RoomManager` |
| B2 | 高 | `RemoteParticipants.Keys`（string） → 应该是 `.Values`（RemoteParticipant 对象） | 同上 |
| B3 | 高 | Brain 过滤用 `!StartsWith("unity")` → 应该是 `StartsWith("agent-")`（VideoStateReporter 已验证） | 同上 |
| B4 | 高 | `SendTrackRebuildingRpc` 用 `WaitUntil(() => rpcTask.IsCompleted)` → 应该是 `yield return rpcCall` | `ARVideoPublisher.cs` |
| B5 | 中 | Brain 无 `setScene` RPC handler → `session/scene` BB 键不被 Unity 更新 | `agent.py _attach_scene_ready_rpc` |

Bugfix commit:
```
[S3.bugfix] 5-issue simulation audit: PerformRpcParams / RemoteParticipants.Values /
            agent-prefix / yield-return-rpcCall / setScene Brain handler
```

---

## 截图（captureSnapshot）生命周期说明

**Sprint 3 不实现截图功能**（刻意削减，见 sprint3_kickoff_prompt.md §3）。

Sprint 4 S4.A 计划路径:
```
用户/Gemini 触发 captureSnapshot
  → Unity SnapshotService.cs AsyncGPUReadback + EncodeToJPG + base64
  → RPC captureSnapshot(max_kb, resolution) → Python
  → brain/vision/snapshot.py capture_current_frame()
  → 落盘 data/snapshots/objects/{uuid}/reference.jpg
  → SemanticNode.reference_image_path 写入 L2-B (S4.A5)
  → Graphiti 写回 (TODO S4.B)

生命周期:
  TENTATIVE (刚拍) → 经 identify_object 确认 → CONFIRMED → 写 Graphiti
  断电不丢失: 文件在 ECS volume data/snapshots/
  git ignore: 不进仓库 (S0.5 已配置 .gitignore)
```

---

## 日志可检查点（ECS + Unity Console）

### Castle ECS 侧日志

| 日志源 | 查看方式 | 内容 |
|:-------|:---------|:-----|
| Brain Agent | `tmux attach -t brain` | Gemini 对话、RPC 收发、Supervisor 决策、BB 写入 |
| Redis obs_log | `redis-cli XREAD COUNT 20 STREAMS parrot:obs_log 0` | Intent 决策、Ingest 事件、Visual state 变化 |
| Redis events.log | `redis-cli XREAD COUNT 20 STREAMS parrot.events.log 0` | L0 跨进程事件（tier_change 等） |
| Redis A10 heartbeat | `redis-cli TTL parrot:a10_heartbeat` | 正数=alive，-2=A10 下线 |
| Token Mint | `docker compose logs token-mint -f` | /mint 请求记录 |
| Supervisor 状态 | Brain 终端日志 `Supervisor BB write:` | 档位变化时间戳 |

**关键日志片段示例**（Brain 终端）:
```
[vision.state] BB session/visual_reason: None → VisualStateReason.TRACK_REBUILDING
[vision.state] BB session/visual_state: active → paused
[ARVideoPublisher] Track rebuilt: 1000kbps/30fps (tier=Full)
[vision.state] BB session/visual_state: paused → active
Supervisor BB write: video_tier=video_full dsg_mode=dsg_full (cause=a10_up_60s)
```

### Unity Console 侧日志

| 前缀 | 触发时机 |
|:-----|:---------|
| `[ARVideoPublisher]` | Track 发布/重建/mute/unmute |
| `[VideoTierReceiver]` | setVideoTier RPC 收到 + 档位切换 |
| `[ARFoundationSetup]` | 平面检测状态变化 |
| `[TapToPlace]` | 点击事件、GOSLO 放置、ARAnchor |
| `[AnimationDriver]` | 状态切换 (Idle/Fly/HeadBob/Perch) |
| `[SceneProfileManager]` | 场景检测结果 + setScene RPC |
| `[TokenService]` | Token 获取成功/失败/缓存命中 |
| `[LauncherUI]` | 权限状态、连接流程 |
| `[RoomManager]` | 连接成功 + onSceneReady 发送 |

---

## Sprint 3 验收用例（含 log 预期）

```
用例 1: Launcher 权限 + 连接
  预期 Unity Console:
    [LauncherUI] 请求权限中...
    [LauncherUI] 就绪 — 点击连接
    [TokenService] Minted token and cached (expires_at=...)
    [RoomManager] Connected — room='parrot-main'
    [RoomManager] onSceneReady sent (time_of_day=morning)

用例 2: AR 平面检测
  预期 Unity Console:
    [ARFoundationSetup] AR tracking active — plane detection running
    [ARFoundationSetup] Plane visible: TrackableId(...) area=0.24m²

用例 3: 点击放置 GOSLO
  预期 Unity Console:
    [TapToPlace] GOSLO placed at (0.12, 0.00, 0.34) (anchor=True)
    [AnimationDriver] State → Fly
    [AnimationDriver] Arrived at (0.12, 0.00, 0.34)
    [AnimationDriver] State → Idle
  预期 Brain 终端:
    INFO onGosloPlaced: GOSLO placed on desk — no action needed in Brain

用例 7: 说"视频全开"
  预期 Brain 终端:
    INFO set_video_tier: manual override → VIDEO_FULL (hold=300s)
    INFO Supervisor BB write: video_tier=video_full dsg_mode=dsg_full (cause=manual_override)
  预期 Unity Console:
    [VideoTierReceiver] tier GeminiOnly → Full (reason=manual_override)
    [ARVideoPublisher] Track rebuilt: 1000kbps/30fps (tier=Full)
    [ARVideoPublisher] onVideoDegraded(reason=ok) sent → Brain

用例 8: A10 heartbeat → Supervisor 升档
  ECS 检查: redis-cli TTL parrot:a10_heartbeat → 45 (alive)
  Brain 终端 (60s 后):
    INFO Supervisor BB write: video_tier=video_full dsg_mode=dsg_full (cause=a10_up_60s)

用例 10: identify_object L2-B 快速命中
  Brain 终端:
    INFO identify_object: L2-B fast hit → '蓝色马克杯' (uuid=..., score=75%)
  (无 Graphiti search 日志 ← 验证 Path 2 生效)
```
