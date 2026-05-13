---
name: livekit-unity-lifecycle
description: Use when working with Unity AR app lifecycle / 防御性机制 — Room 重连、SignalReconnect/ICE restart、OnApplicationPause 切后台短/长背景策略、graceful shutdown / 30s ICE 残留 / identity 抢占防御、connection health 聚合、ARCore 后台 blank texture / pause-resume crash、audio route policy、shutdown chokepoint、setVideoTier 切换副作用。配套 livekit-unity-video-publish 数据流主题。
---

# LiveKit Unity Lifecycle / 防御性机制

> **配套 skill**：`.cursor/skills/livekit-unity-video-publish/IMPL_REF.md` —— 数据流 / 推流 / 截帧 / 多采样主题；本 skill 与之**互不重复**，遇到冲突以本 skill 为 lifecycle 真源、video-publish 为数据流真源。
>
> **调研稿（厚稿）**：`docs/sprint4_research/result/05_lifecycle_and_defensive_design.md` —— 含 Phase A/B 完整对比表、证据等级、spike 清单与弃用清单。本 skill 是"实现侧速查"，调研稿是"决策依据"。
>
> **Phase 3 启动入口**：`docs/sprint4_research/result/INDEX_for_phase3.md` —— 三段式输入摘要的索引版（导向决策）。

## 边界（不允许误读）

1. 本 skill 描述 Unity 客户端 FSM；**不暴露给后端 BT / Scheduler**。后端通过 `EcpState.app_lifecycle_state` + `connection.health.changed` 事件感知。
2. VideoTier 切换属于 Intent；**禁止**塞进 Reflex 做毫秒级反应。
3. DSG L2-B 工作记忆**不接受**实时帧；本 skill 不新增 L2-B 写入路径。
4. 2026-05-09 ChatA 修订：蓝牙音频进入正式 App 支持范围；有蓝牙输入路由时默认优先使用蓝牙，蓝牙 / 手机麦克风切换必须稳定重建 mic track 且不重连 room。候选 BB 键 `session/audio_route_policy` 仍保留 candidate 标记，无协议 producer。
5. 测试束隔离：本 skill 描述的 `AppLifecycleManager` 在 `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/`；不要把 `unity/ParrotDev/` 的 SelfTest / Runtime HUD 反向当生命周期源。

## 当 LLM 写代码时应当如何用

| 任务 | 主读 | 配套读 |
|:--|:--|:--|
| 实现 `AppLifecycleManager` FSM | 本 skill `IMPL_REF.md` §1-§3 | 设计稿 §9.2 + 调研稿 §4.1 |
| 实现 `RoomManager.OnApplicationQuit` graceful shutdown | 本 skill `IMPL_REF.md` §2 | livekit/client-sdk-unity-web #24 + commit `434009b` |
| 实现 connection_health 聚合 | 本 skill `IMPL_REF.md` §4 | 设计稿 §9.1 |
| 处理 ARCore 后台黑帧 / pause-resume | 本 skill `IMPL_REF.md` §5 | `ar-foundation.mdc` rule + arfoundation-samples #592 |
| 让 `ARVideoPublisher` / `MicrophonePublisher` 听 lifecycle 事件 | video-publish `IMPL_REF.md` §6 + 本 skill `IMPL_REF.md` §3 | — |
| setVideoTier 切换副作用（黑帧 / cool-down） | 本 skill `IMPL_REF.md` §6 | video-publish §2 publish 配置 |

## 与 ECP 的接合

```text
Unity AppLifecycleManager (本 skill)
  ├─ AppLifecycleState 枚举    →  EcpState.app_lifecycle_state（reliable DataChannel 周期上报）
  ├─ ConnectionHealthState    →  EcpState.connection_health (overall: healthy/degraded/...)
  ├─ AudioRoutePolicy.status_note → EcpState.meta.audio_route_status (Sprint4 仅 baseline)
  └─ 关键转换 → L0 events
       ├─ connection.health.changed
       ├─ media.audio_route.changed
       ├─ media.video_state.changed (含 lifecycle reason 词表扩展)
       └─ intent.disconnect (graceful vs 被动)
```

**不要**把 lifecycle FSM 状态塞进 `EcpAck.frontend_state`，那是 per-command ack；lifecycle 上报走 `EcpState`（参考设计稿 §5.3）。

## 触发本 skill 的关键词

切后台 / OnApplicationPause / Background / 重连 / Reconnecting / Room.Disconnect / Dispose / graceful shutdown / 30s ICE / identity 抢占 / 切前后摄 / ARSession pause / ARCore black texture / connection health / watchdog / heartbeat / 蓝牙路由 / 耳机插拔 / setVideoTier 副作用 / cool-down / lifecycle FSM / app lifecycle state

