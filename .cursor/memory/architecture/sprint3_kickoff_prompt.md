---
status: ready
status_note: "Sprint 3 开工前必读 + 6 个对齐问题。新 chat 无需重新理解全部架构，直接读这份 + 必读文档列表，对齐 6 个问题后开干。"
created: 2026-04-23
---

# Sprint 3 Kickoff Prompt — AR 桌面 MVP + identify_object L2-B + Token Mint

> 定位: 新 chat/新会话 的**上下文压缩包**。把它喂给 Agent，回答 6 个对齐问题后，Agent 可以直接执行 T 任务，不需要重新理解全部历史。
>
> 背景节奏: Sprint 1 ✅（自知底座）→ Sprint 2 ✅（两轴自主闭环）→ Sprint 2 模拟推演清理 ✅ → **现在进 Sprint 3**
> Sprint 3 是首次涉及真机 AR + Python/Unity 双侧同步推进的冲刺，规模约 5-7 天。

---

## 0. 你在哪里

**代码状态 (2026-04-23)**:

- `master` 最新 commit: `[S2.cleanup]` 4 个模拟推演后清理项
- Sprint 2 全部 T 任务 + 2 批 bugfix + 1 批 cleanup 已全部落地
- Python 侧: `src/parrot/` 新增 `perception_supervisor`, `dsg/ingest/`, `dsg/mode_controller` 等约 1,800 行
- Unity 侧: `VideoTierReceiver.cs`, `VideoStateReporter.cs`, `ARVideoPublisher.SetPublishMuted` 已对接
- 关键遗留 (Sprint 3 要处理的骨头，详见 sprint2_completion_report §6):
  - §6.1 `PublishTrack` 不可变 — `VIDEO_FULL` 和 `VIDEO_GEMINI_ONLY` 之间目前**不改实际 bitrate/fps**，Sprint 3 一并重建
  - §6.3 A10 健康 probe 是 stub — `PARROT_A10_HEALTH_URL` 没设就永远 True

---

## 1. 必读文档 (按序，每份只读对应段)

| 顺序 | 文档 | 读哪里 |
|:-----|:-----|:-------|
| 1 | `.cursor/memory/active_context.md` | 头部 30 行（版本锁定表 + 当前阶段） |
| 2 | `.cursor/memory/architecture/sprint2_completion_report_20260423.md` | §6 遗留 + §8 Sprint 3 交接 + 附录 B |
| 3 | `.cursor/memory/architecture/ar_feature_implementation_plan.md` | Sprint 3 段 (S3.A-D) + Sprint 4 段 (S4.A-B 仅预览边界) |
| 4 | `.cursor/memory/architecture/ar_feature_vision.md` | §3.4 补充通道（相机模式） + §3.7 Ingest 边界 |
| 5 | `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` | §5 Path 1-3 全文（Sprint 3 要走通 Path 1 + Path 2） |
| 6 (选读) | `.cursor/skills/ar-foundation-api/SKILL.md` | AR Foundation 5.1 API 约束 |
| 6 (选读) | `.cursor/skills/ar-foundation-samples/SKILL.md` | Plane detection / Anchor 具体模式 |

**不需要重读**（已在压缩摘要里）:
- `sprint2_plan_20260423.md` (执行细节已落地)
- `sprint1_completion_report_20260422.md` (只在 Sprint 1 时重要)
- `bus_v4.md` / `protocol_snapshot_p1.md` (协议层没动)

---

## 2. Sprint 3 范围

Sprint 3 的核心问题是: **让用户在手机上真正把 GOSLO 放到桌面，同时打通 identify_object 的 L2-B 优先搜路径（Path 2）**。

### Python 侧 (T-P1 ~ T-P4)

| T | 模块 | 核心任务 | 关键约束 |
|:--|:-----|:---------|:---------|
| T-P1 | `brain/tools/set_video_tier.py` 新 | 新 Gemini tool `set_video_tier` — 用户/Gemini 主动请求切换档位，**调 `PerceptionSupervisor.set_manual_override()` 而非直写 BB** | 双写 BB 是禁区（见 §3.1 决策点 D1） |
| T-P2 | `perception_supervisor.py` 改 | A10 健康 probe 真实化: Redis heartbeat key `parrot:a10_heartbeat` （A10 每 30s SETEX）, Castle 侧 supervisor 检查 TTL | 见 §3.1 决策点 D2 |
| T-P3 | `brain/tools/identify_object.py` 改 | Path 2 实现: `_match_known` 先走 L2-B 内存搜（`get_node_by_label`），命中就返回，未命中再走 Graphiti；Path 1 的 A10 CV track 是 Sprint 4 才来的货，这里只做 Path 2 | L2-B 搜到的结果不再重复写 Graphiti，只更新 attention |
| T-P4 | `src/parrot/castle/token_mint.py` 新 + `infra/docker-compose.yml` | FastAPI `/mint` 端点，Bearer 验证 `PARROT_MINT_SECRET`；Unity `TokenService.cs` POST → 存 PlayerPrefs 24h；失败 fallback 读 `StreamingAssets/parrotdev.json` | 见 §3.1 决策点 D3 |

### Unity 侧 (T-U1 ~ T-U5)

| T | 模块 | 核心任务 | 关键约束 |
|:--|:-----|:---------|:---------|
| T-U1 | `ARFoundationSetup.cs` / `TapToPlace.cs` | `ARPlaneManager(Horizontal)` + `ARRaycastManager` + 点击放置 + `ARAnchor` 绑定 GOSLO | AR Foundation 5.1 only（见 AR skill §1.1）；最小平面 0.3×0.3m |
| T-U2 | `SceneProfileManager.cs` | 读 config → 初始化 `DESKTOP_WEBCAM`（Editor/Webcam，虚拟 y=0）或 `AR_HANDHELD`（手机 AR）→ RPC `setScene` 告诉 Brain | 两条路径必须同时跑通，开发期 Editor webcam 是主测路径 |
| T-U3 | `Launcher.unity` + `LauncherUI.cs` | 连接按钮 + 状态指示 + 摄像头/麦权限申请（Android Runtime）；拒绝时退回 Launcher | 权限: `CAMERA`, `RECORD_AUDIO`, `INTERNET` 三项 |
| T-U4 | `AnimationDriver.cs` | 程序化 idle / head_bob / fly / perch 四个动画状态机（不用 Mixamo）；`body_state` 变化 → DataChannel → AnimationDriver 切换 | GOSLO 模型: 暂用方块占位（真模型 Sprint 4 换，AnimationDriver 接口提前设计好） |
| T-U5 | `ARVideoPublisher.cs` 改 | `UnpublishTrack → PublishTrack(TrackPublishOptions{Bitrate, Fps})` 动态重建；`VIDEO_GEMINI_ONLY` = 300kbps/15fps；`VIDEO_FULL` = 1Mbps/30fps | 见 §3.1 决策点 D4 |

---

## 3. Sprint 3 不做的事（显式削减）

- ❌ iOS 支持（P3+，等设备）
- ❌ 墙面 / 地面平面（只做桌面 Horizontal）
- ❌ Mixamo / 骨骼动画（AnimationDriver 只做程序化）
- ❌ A10 CV track 真机接入（A10 Path 1 是 Sprint 4 的 S4.B1，Sprint 3 只接 Redis heartbeat）
- ❌ Graphiti 写回（TODO(S4.B)，保持现状）
- ❌ captureSnapshot（S4.A，Sprint 4）
- ❌ Soul 按 DsgMode 分档（S4+，先用 trace 看需求）
- ❌ `TimelineNavigator`（ar_feature_vision §3.8，P3 长期项）

---

## 4. 六个对齐问题（先答后动手）

> 这 6 个问题是 Sprint 3 的核心决策点。对齐后再做 T 任务，避免半路架构折回。

### D1 — `set_video_tier` tool 和 PerceptionSupervisor 的写 BB 冲突

**背景**: `PerceptionSupervisor` 是 `session/video_tier` 和 `session/dsg_mode` 的唯一合法 writer（BB schema 声明）。如果新建 `set_video_tier` tool 也直写 BB，是双写，sprint2 中花了很多心思设计的 single-writer contract 就破了。

**候选方案**:
- (A) tool 调 `PerceptionSupervisor.set_manual_override(combo, hold_seconds=300)`，Supervisor 内部写 BB — **推荐，维持 single writer**
- (B) tool 直写 BB，同时 set Supervisor 的 bypass flag — 双写，隐患

**需要决策**: 用 A 还是 B？以及 `hold_seconds` 多久合适（用户说完 "切到全开" 希望持续多久才被 Supervisor 自动接管回去）？

### D2 — A10 健康 probe 的真实实现方式

**背景**: A10 和 Castle 在同 VPC，HTTP RTT < 1ms。但 A10 是**抢占式实例**，随时可能被回收，Brain 需要知道 A10 是否"活着"。

**候选方案**:
- (A) A10 启动后往 Redis 写 `SETEX parrot:a10_heartbeat 60 "alive"`，每 30s 刷新；Castle 侧 Supervisor 检查这个 key 的 TTL — **推荐，无额外端口**
- (B) Castle 侧 HTTP GET A10 的 `/health` 端点 — 多一个 HTTP 服务，A10 需要开 FastAPI；但直观

**需要决策**: A 还是 B？如果 A：A10 的 heartbeat 写入在哪里注册（Bus mount 时？还是单独 daemon）？

### D3 — Token Mint 安全模型

**背景**: Token Mint endpoint 如果没有 auth，任何知道 Castle IP 的人都能生成 room token。当前 fallback 是 `StreamingAssets/parrotdev.json` 里硬编码的 token（有效期固定）。

**候选方案**:
- (A) `Bearer PARROT_MINT_SECRET` header 验证（secret 在 Unity `Resources/parrot_config.json` 或 PlayerPrefs，不进 git）— **最简，适合个人项目**
- (B) 无 auth，只限制 IP 白名单（nginx allow 手机 IP）— 维护成本高
- (C) 保持 StreamingAssets fallback，Mint 是"锦上添花"，Token 在 Castle 侧按时间滚动生成后写进文件 — 最简，但每次要手动刷

**需要决策**: 现阶段 A 够不够？`PARROT_MINT_SECRET` 存在哪里？

### D4 — PublishTrack 动态重建期间的 PerceptionSupervisor 行为

**背景**: `UnpublishTrack()` 后到 `PublishTrack(new options)` 完成前，Unity 的视频 track 会短暂消失。LiveKit 会通知 Brain track 断开。此时 `onVideoDegraded` 会触发，`session/visual_state` 变成 `PAUSED` 或 `DEGRADED`，Supervisor 的 hysteresis 开始计时。如果重建耗时 > 15s，Supervisor 会触发降档——但降档请求本身又触发重建，可能死循环。

**候选方案**:
- (A) 在 `VideoTierReceiver.cs` 开始重建时，发一个 `"track_rebuilding"` RPC 到 Brain，`vision/state.py` 把它当作合法 `PAUSED` 状态（不触发 Supervisor 降档计时器）— **推荐**
- (B) Supervisor 的 `degraded_grace_s` 从 15s 临时拉长到 60s，依靠时间窗口避开重建期 — 魔法数字，不干净
- (C) 重建前调 `set_manual_override(VIDEO_GEMINI_ONLY, hold_seconds=60)`，让 Supervisor 停手 — 简单，但档位会先降再升

**需要决策**: 用 A？需要在 `vision/state.py` 加 `TRACK_REBUILDING` reason 吗？还是复用 `TRACK_MUTED`？

### D5 — AR 平面检测 + GOSLO 在 Gemini 视频帧里的地位

**背景**: GOSLO 是 Unity 渲染的 AR 对象，它**叠加在摄像头画面上**但**不是摄像头的真实内容**。当前推给 Gemini 的 LiveKit track 来自 `ARCameraBackground._rt`（纯摄像头画面），GOSLO 本体不在里面。

这意味着:
- Gemini 分析视频时看不到 GOSLO（看的是现实世界桌面）
- identify_object 说"我看到杯子"是真实识别，不是"识别到 GOSLO 旁边的杯子"
- GOSLO 放上桌面后，如果用户问"你在哪里"，Gemini 无法从视频帧里找到她

**候选方案**:
- (A) Sprint 3 保持现状（Gemini 看纯摄像头画面），GOSLO 通过 `session/scene` + `tick/ar_tracking_state` 知道自己的锚点坐标，但 Gemini 不能"看到"自己 — **推荐，sprint 3 不需要改这里**
- (B) 改用 Unity 合成后的渲染帧（Camera + AR overlay），给 Gemini 看到 GOSLO — 这是 S4.C 补充通道的事，Sprint 3 不做

**需要决策**: Sprint 3 确认 A，Sprint 4 再讨论 B。还是 Sprint 3 就要接通合成帧？

### D6 — GOSLO 模型素材

**背景**: `ar_feature_implementation_plan §S3.D1` 说"把 GOSLO.glb 换下当前方块占位"，但目前不清楚 `GOSLO.glb` 是否已经存在于 repo 或本地。

**需要决策**: 
- 模型文件在哪里？（repo 路径？还是需要从外部导入？）
- Sprint 3 是用真模型还是保持方块占位，等 Sprint 4 再换？（AnimationDriver 的骨骼/挂点设计取决于此）

---

## 5. 已知新问题 (Sprint 3 Agent 需要记录的决策)

以下问题在 Sprint 2 没有出现，是 Sprint 3 新暴露的架构边界：

### N1 — `set_video_tier` tool 是"用户主动意图"，要走 Intent 路由还是 tool 直达？

`ar_feature_implementation_plan §S1.F` 设计了 Intent 路由，`HandleIntent` 节点 acknowledge `layer=intent` 事件。`set_video_tier` 本质是 `intent` 层事件——它是用户表达意图（"全力开"），不是实时 reflex，不是 Task。

**问题**: 新 tool 应该:
- 直接调 `PerceptionSupervisor.set_manual_override()` → 不经过 Router（最快，但 Router 不知道）
- 发一个 `layer=intent` 事件到 Redis → Router `HandleIntent` ack → Supervisor 监听这个事件 → 写 BB（符合三层架构，但多一圈）

Sprint 2 的 `HandleIntent` 只做 ack，不做 BB 写（intentional design）。所以最简路径是 option 1（直调 `set_manual_override`）。记录到 obs_log 作为 Intent 层事件。**Sprint 3 建议选 option 1，不增加 Router 复杂度。**

### N2 — L2-B `get_node_by_label` 用子串匹配，Path 2 可能误召回

`L2BGraph.get_node_by_label("cat")` 会命中 `"black cat"` 节点（子串匹配）。`identify_object` Path 2 的短描述（`"blue mug"`) 可能匹配到 `"a large blue mug with logo"` 节点。

**暂定方案**: Sprint 3 在 `_match_known` 里对 L2-B 命中做 `confidence >= 0.5` 过滤，并在 Gemini 返回里标注"L2-B 快速命中（可能不完全匹配）"。精确匹配留 Sprint 4。

### N3 — Token Mint 和 Castle 的部署顺序

Token Mint 是 Castle 上的新服务。如果 Unity 先于 Token Mint 部署，Unity 会 fallback 到 `StreamingAssets` 硬编码 token。这在测试期是可接受的。**Sprint 3 的开发顺序应该是: Python Token Mint 先跑通，再改 Unity `TokenService.cs`，最后确认 fallback。**

---

## 6. T 任务执行顺序建议

```
Phase 1 (并行): T-P2 (A10 heartbeat) + T-U2 (SceneProfileManager)
  ↓
Phase 2 (并行): T-P4 (Token Mint) + T-U1 (AR plane + TapToPlace) + T-U3 (Launcher)
  ↓
Phase 3 (串行): T-U5 (PublishTrack 重建) → T-P1 (set_video_tier tool) → T-U4 (AnimationDriver)
  ↓
Phase 4: T-P3 (identify_object Path 2 L2-B 搜)
  ↓
验收: S3 验收用例全跑
```

**关键路径**: T-U1 是基底，T-U5 依赖 Sprint 2 的 Supervisor 降档信号（必须在 T-P1 前），T-P3 依赖 T-U1 完成后真机有 AR 场景数据。

---

## 7. Sprint 3 验收用例 (来自 ar_feature_implementation_plan §S3)

```
1. IQOO NEO9 上运行 → 启动界面 → 授权摄像头/麦 → 点连接 → 进 AR 场景
2. 摄像头对桌面 2 秒 → 看到半透明平面网格 (ARPlaneManager)
3. 点击平面 → GOSLO 从上方飞入, 落在手指处 (TapToPlace + ARAnchor)
4. GOSLO 说 "早上好 (根据当前时间)" (D15 打招呼)
5. 语音"过来一点" → GOSLO flyTo 手指附近
6. 切后台 10s 再回来 → GOSLO 仍在原位, Gemini 继续对话

新增 (Sprint 3 扩展验收):
7. 说"视频全开" → set_video_tier 触发 → Brain RPC → Unity track 重建 → BB video_tier=VIDEO_FULL
8. A10 heartbeat key 在 Redis 出现 → 60s 后 Supervisor 自动升档
9. Token Mint POST /mint → 收到 LiveKit token → Unity 用新 token 连接成功
10. identify_object("蓝色杯子") → L2-B 先搜 → 命中返回 "快速命中" → 不触发 Graphiti 搜
```

---

## 8. Sprint 4 边界预告（Sprint 3 Agent 不做，但设计时不要堵死）

Sprint 4 要做的事里，以下几项和 Sprint 3 的代码直接相关：

| Sprint 4 项 | 对 Sprint 3 的约束 |
|:------------|:------------------|
| `captureSnapshot` RPC (`S4.A1-A3`) | Unity 侧要预留 RPC handler 注册位置；`ARVideoPublisher` 不要把 camera ref 封死 |
| `SemanticNode` 扩 `reference_image_path` (`S4.A5`) | `l2b_types.py` 的 `SemanticNode` 不要加和图片相关的临时 field，等 S4.A5 一次加 |
| identify_object Path 1 (A10 CV track, `S4.B1`) | `CvTrackFilter` 骨架已在 Sprint 2 建好；Sprint 3 不要动它 |
| GOSLO.glb 换模型 (`S4.D1`) | `AnimationDriver.cs` 的挂点设计要提前和 GOSLO 模型对齐；如果模型没确定，Sprint 4 再换 |
| 相机模式 / 补充通道 (`S4.C`) | Sprint 3 的 `ARCameraBackground._rt` 推流路径不要改；补充通道是新增路径 |

---

## 9. 存档说明

本文档创建于 Sprint 2 完成后（2026-04-23），是 Sprint 3 的开工前文档。

执行时更新:
- `active_context.md` 头部 → 把 "Sprint 2 完成" 改为 "Sprint 3 进行中"
- Sprint 3 完成后写 `sprint3_completion_report_20260428.md`（日期按实际）
- `ar_feature_implementation_plan.md` 的 Sprint 3 段加 ✅ + 完成日期

**关联文档**:
- `.cursor/memory/architecture/sprint2_completion_report_20260423.md` — Sprint 2 事实记录（含模拟推演 bugfix 台账）
- `.cursor/memory/architecture/ar_feature_implementation_plan.md` — Sprint 3-4 任务清单
- `.cursor/memory/architecture/ar_feature_vision.md` — 愿景收口
