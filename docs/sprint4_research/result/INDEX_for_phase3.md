# Sprint4 Phase 3 决策索引（lifecycle / 防御性 / 数据流）

> **本文用途**：给 Phase 3 实现 chat 的**起步页**。只列**做什么 / 不做什么**，不列原因。原因进 `05_lifecycle_and_defensive_design.md`。
>
> **状态**：2026-04-29 调研冻结。Phase 3 实现可直接按本表推进，不必重读 result/01–04。
>
> **本文与 result/05 的分工**：05 是厚稿（Phase A/B 对比表 + 证据等级 + 弃用理由）；本文是薄索引（决策清单 + 入口路径）。读 05 = 复盘原因；读本文 = 直接动手。

---

## 0. 入门顺序（5 分钟）

1. 读本文 §1 已确认采用 → 知道 Phase 3 主线代码要落到哪里
2. 读本文 §2 spike 清单 → 知道实现前必须先验证哪 8 件事
3. 读本文 §3 弃用清单 → 知道哪些路径**不要再尝试**
4. 实现时按主题进 skill：
   - 数据流 / 推流 / 截帧 / 黑帧门 → `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md`
   - lifecycle / 重连 / shutdown / connection_health / VideoTier 切换副作用 → `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md`
5. 卡住时回 `result/05_lifecycle_and_defensive_design.md` 找证据 / 替代方案
6. 协议字段进 ECP → `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`

---

## 1. 已确认采用（直接落地，不再讨论）

| # | 决策 | 实现入口 |
|:--|:--|:--|
| 1 | 混合背景状态机：`OnApplicationPause(true)` 后短背景 5s 防抖窗，5–30s 长背景上报 degraded（不强切），>30s 进 graceful shutdown | lifecycle skill §1 |
| 2 | Graceful shutdown chokepoint：`UnpublishTrack(video) → UnpublishTrack(audio) → Room.Disconnect → 等 Disconnected event（5s 兜底超时）→ Room.Dispose → cool-down 5s` | lifecycle skill §2 |
| 3 | 自维护 connectivity watchdog 搭车 ECP `EcpState` 上行通道（reliable DataChannel）；不依赖 SDK Disconnected event | lifecycle skill §3 |
| 4 | `ConnectionHealthState.overall` 4 态聚合（healthy / degraded / unhealthy / unknown），单字段单 producer | lifecycle skill §4 |
| 5 | Blit + `ARCameraManager.frameReceived` 主推流路径不变（Sprint3 已通） | video-publish skill §2 |
| 6 | `captureSnapshot` 主路径：AR 走 `XRCpuImage.ConvertAsync`，WebCam fallback 走 `AsyncGPUReadback.Request(_rt)`；按 `SceneProfile` 选；薄抽象 `IFrameCapturer` | video-publish skill §4 |
| 7 | First frame gate + stale frame 降级（已有 `HasFreshFrame` / `lastAge`，扩展 `_lifecycle_reason` 区分原因） | video-publish skill §6 + lifecycle skill §4.2 |
| 8 | > 15KB 图片走 `LocalParticipant.SendFile()` / ByteStream；阈值 `BYTESTREAM_RPC_THRESHOLD_BYTES=15360` | video-publish skill §4 + lifecycle skill §10 |
| 9 | VideoTier 切换：unpublish → cool-down `T_TIER_COOLDOWN=3s` → republish；FFI bridge 不暴露 SetParameters，无第二条路径 | video-publish skill §2 + lifecycle skill §6 |
| 10 | `Simulcast=false` 默认（单消费者拓扑） | video-publish skill §2（已合入） |
| 11 | `AppLifecycleState` 11 状态 FSM：cold_start / permission_gate / token_gate / ar_session_starting / connecting / connected / running / short_background / long_background / reconnecting / degraded / shutting_down / disconnected | lifecycle skill §1 |
| 12 | 音频 baseline 锁 `phone_mic_48k_headphones_recommended`（Sprint3 fix 不退回） | lifecycle skill §7 |
| 13 | `EcpAck.frontend_state` 扩展 `app_lifecycle_state` / `ar_tracking_state` / `connection_overall`；周期 `EcpState` 承载完整 ConnectionHealthState | result/05 §4.5 |
| 14 | ARCore 后台过渡期暂停 Blit（不 unpublish track）；`OnApplicationPause(false)` 后等 `ARSession.state == SessionTracking` + 一次新 frameReceived 再恢复推流 | lifecycle skill §5 + video-publish skill §7 |
| 15 | 用户切前后摄 / 重启 ARSession 限频 `T_AR_SESSION_TOGGLE_MIN=2s` | lifecycle skill §5 + §10 |
| 16 | 显式 `intent.disconnect` ECP event（区分 graceful vs 被动断），补 LiveKit Unity SDK `DisconnectReason` 缺失 | lifecycle skill §9 |
| 17 | 所有阈值 / 超时 / cool-down 集合到 ScriptableObject `ParrotLifecycleConfig.asset`，开发者菜单 `Tools/Parrot/Lifecycle Tuning` 可调，未来挂 app 设置 | lifecycle skill §10（17 个参数全表） |
| 18 | 候选 BB 键 `session/connection_health` / `session/audio_route_policy` 保留 candidate 标记直至 producer 全部就位（审计 B5 反模式护栏） | lifecycle skill §4.3 + §7 |

---

## 2. 必跑 Spike（实现前先验证；每条带验收标准）

| # | 范围 | 验收标准（不达则改方案） |
|:--|:--|:--|
| **S1** | LiveKit Unity SDK Disconnect race / Room "复活" 是否影响我们 | adb tc 弱网 5 分钟，Connect/Disconnect 切换中 Room 复活 0 次。如有 → 业务层加 `_disconnecting` flag |
| **S2** | iOS / Android 飞行模式开关下 `Room.Disconnected` event 触发延迟分布 | 100 次采样：P95 < 5s，未触发率 < 5%。超出 → watchdog 软超时改 5s |
| **S3** | ByteStream 50KB JPEG 端到端 RTT + 失败率（移动 4G/WiFi） | 100 次采样：P50 < 500ms，P95 < 2s，失败率 < 1%。超出 → captureSnapshot 必须降到 480x270 走 RPC |
| **S4** | `XRCpuImage.ConvertAsync` vs `AsyncGPUReadback` 真机性能对比（Pixel 6a / 三星中端） | 480x270 JPEG 端到端延迟 + 主线程占用对比；选胜者作为 captureSnapshot 主路径 |
| **S5** | `setVideoTier` unpublish→republish 期间黑帧时长 | GeminiOnly→FULL→GeminiOnly 三档跳变 P95 < 800ms。超出 → setVideoTier 改"仅用户主动升档" |
| **S6** | ARCore pause/resume 高频崩溃（Issue #1736）在我们设备的复现率 | adb 自动脚本 5 分钟运行：crash 率 < 5%。否则 L4 切前后摄需用户确认对话框 + 限频改 3s |
| **S7** | `ParticipantAttributes` 写入 Unity SDK 稳定性 | 100 次写入观察远端订阅：成功率 ≥ 95%。否则放弃 attributes，全走 Reliable DataChannel |
| **S8** | 蓝牙耳机插拔检测 API 存在性（不实现 producer） | `AudioSettings.OnAudioConfigurationChanged` 在 Android 蓝牙连接时是否触发；接口存在即闭项 |

---

## 3. 明确弃用（不要再尝试）

| 弃用项 | 短理由 |
|:--|:--|
| `RTCRtpSender.SetParameters` 运行时调码率 | FFI bridge 不暴露 |
| Sprint4 默认 `Simulcast=true` | 单消费者拓扑反效果 + 移动端发热 + 切换黑屏 |
| 纯依赖 SDK 自动重连，无业务层 watchdog | client-sdk-unity #90 / #53 证伪 |
| 把 lifecycle FSM 塞进后端 BT / Scheduler | 违反 ECP 边界 + 三层意识 |
| 把 VideoTier 切换塞进 Reflex | VideoTier 属于 Intent，Reflex 不做秒级 negotiate |
| Sprint4 实现蓝牙音频自动接管 | 标 OOS；候选 BB 键无 producer |
| `Texture2D.ReadPixels + EncodeToJPG` 截帧 | 阻塞主线程 50–200ms |
| `Camera.Render()` / `targetTexture` 抓 ARCameraBackground | ARCore GPU OES 不经标准相机管线 |
| 动态创建副相机 + RenderTexture 抓帧 | URP RTHandles 泄漏 UUM-40249 |
| `OnDestroy` 里直接 `Room.Disconnect` 然后 return | Unity 销毁顺序无法保证 SDK 协程跑完，必须走 `OnApplicationQuit` + 协程 |
| 把生命周期上报塞 `EcpAck.frontend_state` 周期上报 | EcpAck 是 per-command；周期上报走 `EcpState` |

---

## 4. Phase 3 落地代码主区域

> Sprint4 起新代码全部进 `unity/ArSpike/Assets/Scripts/ParrotApp/`；`unity/ParrotDev/` 只作真机回归对照（受 `MIGRATION.md` 治理）。

| 模块 | 建议落地路径 | 主读 skill |
|:--|:--|:--|
| `AppLifecycleManager`（11 状态 FSM） | `unity/ArSpike/Assets/Scripts/ParrotApp/Lifecycle/` | lifecycle |
| `RoomManager` graceful shutdown 增强 | 现有 `Scripts/LiveKit/RoomManager.cs` | lifecycle §2 |
| `ConnectionHealthAggregator` | `unity/ArSpike/Assets/Scripts/ParrotApp/Health/` | lifecycle §4 |
| `LifecycleHeartbeatPublisher`（搭车 EcpState） | `unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/` | lifecycle §3 |
| `ARVideoPublisher` 增强（首帧门 / 后台暂停 Blit / lifecycle 监听） | 现有 + 搬迁 | video-publish + lifecycle §5 |
| `IFrameCapturer` 抽象（XRCpuImage / AsyncGPUReadback 双实现） | `unity/ArSpike/Assets/Scripts/ParrotApp/Vision/` | video-publish §4 |
| `ParrotLifecycleConfig` ScriptableObject（17 个可调参数） | `unity/ArSpike/Assets/Scripts/ParrotApp/Config/` | lifecycle §10 |
| Brain 侧 `connection.health.changed` / `intent.disconnect` event 处理 | `src/parrot/brain/...` 待 ECP Phase 2 收口后再加 | result/05 §7 |

---

## 5. 关键文件索引

| 文件 | 作用 |
|:--|:--|
| `docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` | 本次调研厚稿（Phase A/B + 证据等级 + 弃用理由） |
| `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md` | 通用 WebRTC 策略 + 2026-04-29 补遗（与 05 对齐） |
| `docs/sprint4_research/result/02_LLM_Control_Protocol_and_State_Machine.md` | 已有 ECP 协议草案 |
| `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md` | UI / Flow（Phase 3 实现联动） |
| `docs/sprint4_research/result/04_DSG_Graphiti_Memory_and_Subconscious_Design.md` | DSG / 记忆侧（Phase 3 不主写） |
| `.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` | 数据流速查（推流 / 截帧 / 多采样 / 黑帧门 / VideoTier 切换路径） |
| `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` | lifecycle 速查（FSM / shutdown / watchdog / health / 后台 blank / 可调参数表） |
| `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` | ECP 协议设计稿（lifecycle 字段最终落点） |
| `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md` | ECP / 三层意识边界（不允许误读） |
| `.cursor/memory/architecture/sprint4_ecp_minimal_audit_20260429.md` | ECP-minimal 审计 + 漂移记录（候选 BB 键护栏） |
| `.cursor/memory/architecture/ar_workspace_index.md` | AR 工作区聚合入口（已登记本文） |

---

## 6. 给下一个 chat 的启动提示词

> 复制下面这段直接发给 fork 出来的 Phase 3 实现 chat。

```
进入 Sprint4 Phase 3 实现（lifecycle / 防御性 / Unity AR 数据流稳定化）。

调研已收口，决策索引在：
  docs/sprint4_research/result/INDEX_for_phase3.md

请按这个顺序起步：
1. 读 INDEX_for_phase3.md §1 已确认采用 + §3 已弃用，知道做/不做什么
2. 读 INDEX_for_phase3.md §2 spike 清单，先安排 S1/S2/S6 在真机跑（其他 spike 可与实现并行）
3. 实现时按主题进对应 skill：
   - 数据流 → .cursor/skills/livekit-unity-video-publish/IMPL_REF.md
   - lifecycle → .cursor/skills/livekit-unity-lifecycle/IMPL_REF.md
4. 协议字段最终落到 sprint4_protocol_v2_ecp.md，期间复用 EcpAck.frontend_state（Phase 2 dict 镜像下行通路），周期上报走 EcpState

约束（不要破坏）：
- ECP 不替代 BT / Scheduler；lifecycle FSM 在 Unity 侧，不暴露给后端 BT
- VideoTier 切换是 Intent；不允许塞 Reflex
- DSG L2-B 不接受实时帧
- 蓝牙音频 Sprint4 OOS（候选 BB 键保留，无 producer）
- 新代码进 unity/ArSpike/Assets/Scripts/ParrotApp/，不反向污染 unity/ParrotDev/ 测试束
- 所有阈值挂 ParrotLifecycleConfig ScriptableObject（17 个，见 lifecycle skill §10），不要硬编

ECP-minimal Phase 1 已落地（Pydantic schema + RPC bridge mirror + Unity DTO/handler），可直接在其上扩展 frontend_state / EcpState。
```

---

## 7. 变更日志

- 2026-04-29：创建。承载 Sprint4 Phase 3 前置调研最终决策索引；导向决策而非原因。
- 2026-04-29 (Phase 3 入场)：L1 纯数据/纯 FSM 骨架 + L2 Python EcpState 落地。新增 ArSpike `Scripts/ParrotApp/Config | Lifecycle | Health | Ecp` 八个文件 + `EcpFrontendStateDto.connection_overall` 扩展；Python `EcpState` / `EcpConnectionHealth` / `ConnectionOverall` 三个新模型。L3 (LiveKit transport / 旧脚本搬迁) 阻塞在 `Packages/manifest.json` 加 `io.livekit.unity`，作为 Phase 3 后段任务 (`phase3-livekit-bridging`)。验证 `uv run pytest tests/test_scheduler/test_ecp.py` 14 passed。
