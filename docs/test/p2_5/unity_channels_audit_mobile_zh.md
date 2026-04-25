# Unity 真机 — 数据面 / RPC / 补充通道审计（2026-04）

> **目的**：把「连上 LiveKit」与「Brain 能感知、能对话、能控鸟」拆成**不同通道**，避免把「无视频」误判为「不能语音」。  
> **验收**：真机用 `ParrotRuntimeHud` +「运行自检」+ `adb logcat` / `parrot_diagnostics.log`；编辑模式用菜单 **Parrot → Test → Editor → Audit LiveKit channels**。

---

## 1. 通道分层（不要混为一谈）

| 通道 | 载体 | Unity 侧典型组件 | Brain 未进房时 |
|:-----|:-----|:-----------------|:---------------|
| **房间 + 信令** | LiveKit WebSocket | `RoomManager` | 仍可 `Connected=true`，但无对端业务 |
| **像素轨（主/测试相机）** | LiveKit Video Track | `ARVideoPublisher` | 仍可发布；无人订阅则无「视觉」 |
| **语音轨** | LiveKit Audio Track | `MicrophonePublisher` | 仍可发布；**无人订阅则对端听不见你** |
| **Brain→Unity RPC** | LiveKit RPC | `VideoTierReceiver`、`ParrotRpcHandler` | 注册成功但调用方不在房则超时/无响应 |
| **Unity→Brain RPC** | LiveKit RPC | `RoomManager`（onSceneReady）、`VideoStateReporter`、`SceneProfileManager`、`ARVideoPublisher`（track_rebuilding）、`TapToPlace` 等 | 目标 identity 不存在则跳过或报错 |
| **补充 / Lossy DataChannel** | `PublishData` | `XRHandTracker`（`parrot.event` / `hand_gesture`）等 | 发出成功；无人消费则无效果 |

**结论（回答「没视频能对话吗」）**：

- **仅房间连通**：不保证任何「对话」——对话需要 **Brain Agent 在房** 且通常要 **音频轨被 Brain/Gemini 管道订阅**。  
- **无视频、有麦克风、Brain 在房**：在依赖 Gemini Live **音频** 的拓扑里，**可以**对话（视觉可选）。  
- **无视频、无麦克风**：没有用户音频输入，**不应期望**语音对话；最多剩文本类工具链（若未来单独做）。  
- **Brain 未打开**：Unity 仍可显示 `LiveKit: ON`；`Brain agent: no`；`onSceneReady` 会跳过；**对向 RPC / 订阅均无主语**。

---

## 2. 已发现并修复 / 补强的问题（代码与场景）

1. **`VideoTierReceiver.videoPublisher` 在 `Dev.unity` 中为空**  
   - 现象：`setVideoTier` RPC 到达后只打日志，**不改变** `ARVideoPublisher` 码率/静音。  
   - 修复：场景里绑定 `ARVideoPublisher`；`VideoTierReceiver.Start` 若未绑则 `FindObjectOfType<ARVideoPublisher>()`。

2. **`VideoTierReceiver` / `ParrotRpcHandler` 重复 `RegisterRpcMethod`**  
   - 风险：同一 `Room` 上多次 `OnConnected` 回调导致重复注册。  
   - 修复：按 **`Room` 实例** 去重，仅对新 `Room` 注册一次。

3. **`VideoStateReporter` 未进 Dev 场景**  
   - 风险：`onVideoDegraded`（前后台、TRACK_MUTED）**不**上报 Brain。  
   - 修复：在 `LiveKitManager` 上增加 `VideoStateReporter`，并绑定同一 `ARVideoPublisher`；脚本内未绑时也会自动查找。

4. **Launcher 根物体无音视频组件**  
   - **设计现状**：`LauncherRoot` 只有 `RoomManager` + `TokenService` + `LauncherUI`；**麦克风/视频在 `Dev` 的 `LiveKitManager`**。从 Launcher 进 Dev 后，`RoomManager` 单例留在 Launcher 物体上，**Dev 场景里的发布器仍挂到 `RoomManager.Instance`**，可正常工作。  
   - **勿**在 Launcher 上再挂一套 `MicrophonePublisher`，否则进 Dev 后会出现**双麦克风**双轨风险。

5. **真机 HUD**  
   - 须用触控按钮展开自检，勿依赖 F3；见 `mobile_runtime_harness_zh.md`。

6. **视频轨生命周期只看 `PublishTrack` 不够**  
   - 风险：AR 组件存在但没有相机帧、或 WebCam fallback 启动失败时，旧逻辑可能仍发布空 `RenderTexture`，HUD 显示 `Video pub: yes` 但 Brain 看到黑/空画面。  
   - 修复：`ARVideoPublisher` 现在记录 `source / frame count / last frame age / last error`；AR 路径和 WebCam 路径都必须先产出首帧，才继续发布 LiveKit 视频轨。

7. **断线 / 重连后发布状态可能污染结论**  
   - 风险：发布器只监听 `OnConnected`，断线后 `_isPublishing` 仍为 true，重连时不重新发布。  
   - 修复：`ARVideoPublisher` 与 `MicrophonePublisher` 都监听 `OnDisconnected`，清理本地发布状态；重连后重新走发布流程。

---

## 3. 真机推荐检查顺序（模拟路径）

1. **权限**：Launcher 已要相机+麦；`MicrophonePublisher` 仍会做 `RequestUserAuthorization` 兜底。拒绝麦 → `MicPublishing` 长期 `no`。  
2. **连接后 3s 自检日志**：看 `[SelfTest]` 段落 — `MicrophonePublisher`、`ParrotRpcHandler`、`VideoStateReporter`、`SceneProfileManager`。  
3. **HUD 第二/三行**：`Video pub(source/frameCount)`、`Audio pub`、`RPC in`、`Hand DC`、`VisRPC`。  
4. **Brain 在房后**：点 **Brain RPC RTT x3**；再观察 Brain 是否下发 `setVideoTier`（Tier 应从 `Unknown` 变化）。  
5. **DataChannel**：举手/手势若装了 XR Hands，看服务端是否收到 `hand_gesture`（需 Brain/Bus 消费端在线）。

---

## 4. Editor 静态审计（不入 Play）

菜单：**Parrot → Test → Editor → Audit LiveKit channels (open scene, edit mode)**  

打开 `Dev.unity` 后点一次，Console 输出 `[+]/[-]` 清单，与上表对表即可。

---

## 5. 相关源码入口

| 脚本 | 通道 |
|:-----|:-----|
| `RoomManager.cs` | 连接、远端音频播放、`onSceneReady` |
| `MicrophonePublisher.cs` | 本地麦轨 |
| `ARVideoPublisher.cs` | 本地视频轨、tier 重建、`track_rebuilding` RPC |
| `VideoTierReceiver.cs` | `setVideoTier` |
| `VideoStateReporter.cs` | `onVideoDegraded` |
| `ParrotRpcHandler.cs` | `flyTo` / `animate` |
| `XRHandTracker.cs` | `PublishData` lossy |
| `SceneProfileManager.cs` | `setScene` |
| `ParrotSelfTestCoordinator.cs` | 快照 + 自检文案 |
