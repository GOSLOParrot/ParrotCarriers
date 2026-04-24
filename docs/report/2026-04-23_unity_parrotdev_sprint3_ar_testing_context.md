# Unity ParrotDev — Sprint 3 AR / 联调 / 测试基建 — 会话留档（2026-04-23）

本文档固化 **本轮 chat 的工程背景、目的、已做改动与已知边界**，供 **context 压缩后** 下一轮联调、真机测试、文档对照使用。后端已有独立日志与时间轴；本文侧重 **Unity 前端（ParrotDev）**。

---

## 1. 背景与目标

| 项 | 说明 |
|----|------|
| **项目** | ParrotCarriers — Unity AR 客户端（ParrotDev）+ LiveKit + Brain/Gemini 链路。 |
| **阶段诉求** | Sprint 3 真机验收（AC 类）：**AR 相机画面**、**平面点击放置**、**视频轨进 LiveKit**、**VideoTier / 补充通道**等可测；此前 APK 仅有默认 3D + 方块，**场景未接 AR 与接收器**，等于未测到交付面。 |
| **本轮目标** | ① 用 **Editor 工具** 把 `Dev` 等场景 **增量** 接到 AR Foundation + LiveKit 测试骨架；② **按 AR 5.1 技能审计** 修正锚点 API；③ 建立 **可看见、可落盘、可对时间轴** 的前端诊断与 **Editor 侧断连模拟**；④ 目录上 **区分 Runtime（真机+Editor Play）与 Editor-only**。 |

**约束（技能/工程）**：Unity **2022.3 LTS** + AR Foundation **5.1.x**；编辑器迭代优先 **XR Simulation**（与 `ar-foundation-samples` 一致）；不写 Unity 6 / AF 6。

**与仓库事实源的关系**：全局仍以 **`.cursor/memory/INDEX.md`** 为准；进度条与 AC 栏以 **`.cursor/memory/active_context.md`** 与 **`architecture/sprint3_completion_report_20260423.md`**（若存在）为准。本文是 **`docs/report`** 侧对 **Unity 前端这一轮** 的补片，不替代 INDEX。

**手测操作顺序（实习生）**：以 **`docs/test/p2_5/pipeline_test_matrix_sprint3.md` §0（P0→P1→P2）→ §A～§F** 为 **唯一推荐步骤**；`sprint3_completion_report` **§7** 只填 **AC1–AC8** 状态；本文 §3 仅说明脚本从哪来 — **若与操作表冲突，以 `docs/test/p2_5/…` 为准**。真 `active_context.md` 不进 Git 时交接见 **`docs/test/p2_5/HANDOFF_ACTIVE_CONTEXT_FOR_ECS.md`**；远端独立报告见 **`docs/test/p2_5/ECS_RUN_REPORTS/`**。

---

## 1.5 在总线架构中的位置（给压缩后上下文）

ParrotDev 处于 **「端侧采集 + LiveKit 传输」** 一层：经 **`RoomManager`** 进房，身份与 Brain 侧约定（如 **`unity-*` / `agent-*`** 前缀）；**`ARVideoPublisher`** 把相机纹理变成 **LiveKit 视频轨**；**`VideoTierReceiver`** 接 Brain 经 RPC 下发的 **`setVideoTier`**，与 **`PerceptionSupervisor` / track_rebuilding** 等后端叙事衔接（详见 Sprint 2/3 报告与 `module_map_p2` 数据流）。

**Dev.unity 的定位**（与 `active_context` 一致）：**集成测试舞台**，用于 AC1–AC8 与接缝验证；**不是**最终上架的 Launcher+主 AR 产品场景。后续 AR App 独立工程会复用已验证接口。

**测试 vs 产品设计**：`RoomManager` 与 Editor 断连菜单验证 **连通性与可观测性**，**不等于**「App 冷启动→进房」的产品流程设计；见 **§10.5**。

---

## 2. 问题摘要与结论

1. **场景缺组件**：`Dev.unity` 未挂 `AR Session` / `XR Origin` / `ARCameraManager`+`ARCameraBackground` / Plane+Raycast / `TapToPlace` / `VideoTierReceiver` 等 → **无 AR 画面、无平面点击、Brain 下 tier 可能无人接**。  
2. **`UNITY_AR_FOUNDATION` 在 Standalone 目标下常未定义** → Editor 菜单若仅用 `#if` 会误报「切 Android」。**对策**：`Sprint3SceneAugment` 用 **反射** `Type.GetType(..., Unity.XR.ARFoundation)` 挂组件，**不必**为点菜单先切 Build Target。  
3. **Safe Mode CS0104**：`using System` + `Object.FindObjectOfType` → **`Object` 歧义**。**对策**：改为 **`UnityEngine.Object.FindObjectOfType`**。  
4. **锚点 API**：`TapToPlace` 曾用 `AttachAnchor(null, pose)`，与 **AR Foundation 5.1 官方** `AttachAnchor(ARPlane, Pose)` 不一致。**对策**：用射线命中的 **`ARPlane`** 调用 `AttachAnchor(plane, anchorPose)`（通过 `_pendingAttachPlane` + `try/finally` 传递）。  
5. **新 Input System 弹窗**：工程装了 Input System 包但 Player 未开原生后端 → 建议 **Yes** 启用并重启；**再核对** `Player → Active Input Handling` 是否与此前 **Android 打包** 策略一致（工程曾用 **仅 Input Manager (Old)**）。  
6. **XR Plug-in**：**Android 页**需勾选 **Google ARCore** 才有真机相机背景；**Editor 页**勾选 **XR Simulation** 才便于编辑器内跑平面（与真机摄像头不是同一路语义）。  

---

## 2.5 关键决策原因（Why，压缩后可读）

| 决策 | 原因 |
|------|------|
| **Augment 用反射挂 AR 组件** | `UNITY_AR_FOUNDATION` 随 **Active Build Target** 变化；团队在 **Standalone** 下也要能 **摆场景、保存、再切 Android 打包**。反射让 **Editor 工具不依赖该宏** 即可 `AddComponent(ARSession)` 等。 |
| **不合并 `DevSceneSetup` 的「整场景重建」** | 旧菜单会破坏已有 Dev；**Sprint3SceneAugment** 选择 **增量**，降低 YAML 手改与误删风险。 |
| **`ARVideoPublisher.useWebcamFallback=false`（Augment 写入）** | 真机 Sprint 3 验收优先走 **ARCameraBackground** 路径；编辑器若需 WebCam 可在 Inspector **手动勾回**。 |
| **诊断三件套 `DontDestroyOnLoad`** | 与 **`RoomManager`** 一致跨场景存活，避免切场景丢 HUD/环形日志；单例重复时 **销毁后者**（见 `ParrotDiagnosticsLog`）。 |
| **日志写 `persistentDataPath`** | 真机 **adb** / 文件管理器可拉取，便于与 **Castle 日志**按时间对齐；**默认每局清空**（`truncateLogOnPlay`）避免文件无限增长。 |
| **Editor 菜单不自动改 XR Plug-in** | 自动写 **ProjectSettings** 易产生 **不可见 diff、合并冲突、误关 ARCore**；清单 + 人工勾选更符合 **可审计** 流程（`ar-foundation-samples` 强调的 Simulation 工作流同理）。 |
| **`RoomManager.ConnectToRoom` 前先断旧 `Room`** | 重复 `Connect()` / 重连测试时避免 **泄漏或未订阅的旧 Room**；并能量化 **`LastConnectDurationSeconds`**。 |
| **`TapToPlace` 用 `_pendingAttachPlane` 而非改 `PlaceGoslo` 全签名** | 减少 `#if` 分叉与调用方爆炸；`try/finally` 保证 **异常路径也清掉 pending**，避免脏状态。 |

---

## 3. 脚本与目录（当前真相）

### 3.1 AR 场景增量（Editor）

| 文件 | 路径 | 说明 |
|------|------|------|
| **Sprint3SceneAugment** | `unity/ParrotDev/Assets/Scripts/Testing/Editor/Sprint3SceneAugment.cs` | 菜单 **`Parrot/Sprint3 — Augment Open Scene (AR + receivers)`**：反射挂 AR Session、XR Origin、相机 AR 组件、Plane/Raycast/Anchor、`ARFoundationSetup`、`TapToPlace`（绑 `ParrotCube`）、`VideoTierReceiver`（在 `LiveKitManager`）、`TokenService`、`SceneProfileManager`、`EventSystem`；必要时关旧 `Main Camera`；写 `ARVideoPublisher.arCamera` + `useWebcamFallback=false`；**若无则创建 `ParrotDiagnostics` 三件套**。 |

**说明**：原路径 `Assets/Editor/Sprint3SceneAugment.cs` **已删除**，统一归入 **`Scripts/Testing/Editor`**。

### 3.2 前端诊断与自检（Runtime — 真机 + Editor Play）

| 文件 | 路径 | 说明 |
|------|------|------|
| **ParrotDiagnosticsLog** | `unity/ParrotDev/Assets/Scripts/Testing/Runtime/ParrotDiagnosticsLog.cs` | 订阅 `logMessageReceivedThreaded`，环形缓冲 + 可选 **`persistentDataPath/parrot_diagnostics.log`**；`CopyRecentToClipboard`。 |
| **ParrotRuntimeHud** | `…/Testing/Runtime/ParrotRuntimeHud.cs` | 左上角状态条；**F3** 展开日志尾 + Run self-test + Copy；订阅 `RoomManager` 连断。 |
| **ParrotSelfTestCoordinator** | `…/Testing/Runtime/ParrotSelfTestCoordinator.cs` | 周期 **Snapshot**（LiveKit、Brain agent、`unity_join_token.txt`、`ARVideoPublisher`、`VideoTierReceiver`、AR Session、`LastConnectDurationSeconds`、Editor 下 **`LoaderUtility`+`XRCameraSubsystem`** 提示）；进 Play 可自动跑 **OneShotSelfTest**；首尾写 **`[SEQ]`** 锚点。 |
| **ParrotRpcRttProbe** | `…/Testing/Runtime/ParrotRpcRttProbe.cs` | **`onGosloPlaced`** 轻载 RTT ×N；日志前缀 **`[RpcRtt]`**（步骤见 `docs/test/p2_5/…` §C 步 6）。 |

**已删除旧路径**：`Assets/Scripts/Diagnostics/*.cs`（三文件）— 勿再引用。

### 3.3 Editor-only 测试菜单

| 文件 | 路径 | 说明 |
|------|------|------|
| **ParrotDiagnosticsMenu** | `…/Testing/Editor/ParrotDiagnosticsMenu.cs` | **`Parrot/Test/Editor/Add Runtime Diagnostics (HUD + Log + SelfTest)`** |
| **ParrotEditorNetworkTests** | `…/Testing/Editor/ParrotEditorNetworkTests.cs` | Play 下：**断开**、**1s 重连**、**断→等→连**（打 `[EditorTest]` 到诊断日志） |
| **ParrotEditorRpcTests** | `…/Testing/Editor/ParrotEditorRpcTests.cs` | Play 下：**`Parrot/Test/Editor/RPC — Brain RTT…`**（与 F3 面板 **Brain RPC RTT x3** 一致） |
| **ParrotEditorSequenceMarkers** | `…/Testing/Editor/ParrotEditorSequenceMarkers.cs` | **不 Play**：**`Parrot/Test/Editor/Sequence — Log P0 static checklist done`** → 打 `[SEQ] P0-done…`（见 `docs/test/p2_5/…` §0） |
| **ParrotArEditorChecklist** | `…/Testing/Editor/ParrotArEditorChecklist.cs` | **XR Simulation 清单**打到 Console/诊断日志（不自动改 Project Settings） |

### 3.4 LiveKit 运行时增强

| 文件 | 说明 |
|------|------|
| **`unity/ParrotDev/Assets/Scripts/LiveKit/RoomManager.cs`** | `LastConnectDurationSeconds`；`ConnectToRoom` 前 **断开旧 Room** 避免重复连接泄漏；**`DisconnectForTesting`** / **`ReconnectUsingCachedCredentials`**；**`#if UNITY_EDITOR`** 下 **`StartEditorReconnectTest(delay)`** 供 Editor 菜单做断连重连。 |
| **`unity/ParrotDev/Assets/Scripts/LiveKit/BrainParticipantResolver.cs`** | 统一解析 Brain 参与者（`agent-*` 或 `brain`）；`RoomManager` / `TapToPlace` / `ARVideoPublisher` / `SceneProfileManager` / `VideoStateReporter` / SelfTest 共用。 |

### 3.5 AR 行为修正（Runtime）

| 文件 | 说明 |
|------|------|
| **`unity/ParrotDev/Assets/Scripts/AR/TapToPlace.cs`** | **`AttachAnchor(plane, anchorPose)`**；`_pendingAttachPlane` + `try/finally`。 |

### 3.6 索引说明（文本）

| 文件 | 说明 |
|------|------|
| **`unity/ParrotDev/Assets/Scripts/Testing/README.txt`** | **Runtime vs Editor** 分工、与后端日志对时间轴的提示。 |

---

## 4. 与 AR 技能（ar-foundation-api / ar-foundation-samples）的对齐

| 项 | 状态 |
|----|------|
| **版本** | 工程 `manifest`：**arfoundation / arcore / arkit 5.1.5** — 与技能 **2022.3 + AF 5.1** 一致。 |
| **XR Simulation** | Augment 弹窗 + **`ParrotArEditorChecklist`** 写明步骤；**不**在 Editor 脚本里自动改 XR 勾选（避免误操作）。 |
| **LoaderUtility / XRCameraSubsystem** | 仅在 **`UNITY_AR_FOUNDATION && UNITY_EDITOR`** 下写入 Snapshot（**ar-foundation-api** Quick Reference 模式）。 |
| **AttachAnchor** | 已按 **Unity 5.1 Anchors 手册** 使用 **平面附着**。 |

**未在 Unity 内实现的深度项**（留给后续）：专用 **RPC echo RTT**、DataChannel 计数进 HUD（需与现有 RPC/Data 脚本对接后再加字段）。

---

## 5. 测试怎么分工（给下一轮 chat）

| 场景 | 做法 |
|------|------|
| **Editor Play** | 开 **XR Simulation**（Editor 插件页）+ **`Window → XR → XR Simulation`**；用 **F3** + **`Parrot/Test/Editor/Network — …`** 做断连重连；菜单 **AR — Log XR Simulation checklist** 打锚点。 |
| **真机 APK** | XR **Android** 勾选 **ARCore**；看 **HUD** + 拉 **`parrot_diagnostics.log`**；与 **Castle/Brain 日志**对同一时间轴。 |
| **对表** | 同一动作先后看：**Console**、**parrot_diagnostics.log**、**后端日志**；`[EditorTest]` / `[SelfTest]` 前缀便于 grep。 |

---

## 6. 已知边界与风险

- **Simulation ≠ 真机摄像头**：XR Simulation 测 **追踪/平面/交互**；真机 **ARCore** 才测 **物理相机 + 推流语义**。  
- **`VideoTierReceiver`** 的 `videoPublisher` 若未在 Inspector 绑定，**VIDEO_OFF 等**可能只落日志不控轨 —— 验收时核对 **LiveKitManager** 引用。  
- **`LoaderUtility`** 若编译缺包，以 **Console 报错** 为准补 **XR Management** 引用链（一般随 AR Foundation）。  

---

## 7. 下一轮可接续任务（用户已删任务列表，此处仅建议）

1. 真机跑通 **AC** 列表，把 **HUD 截图 + diagnostics.log 片段 + 后端同时间段** 归档到 `docs/report/` 或 issue。  
2. 可选：Brain 增加 **`ping`/`echo` RPC**，Unity **`ParrotSelfTestCoordinator`** 展示 **RTT 毫秒**。  
3. 可选：将 **DataChannel** 收发包计数接入 **Snapshot**（需读 `RoomManager` / RPC 桥接脚本）。  

---

## 8. 相关路径速查

```
unity/ParrotDev/Assets/Scripts/Testing/Runtime/   ← 真机 + Editor Play 诊断三件套
unity/ParrotDev/Assets/Scripts/Testing/Editor/    ← Sprint3 Augment、Editor 测试菜单、AR 清单
unity/ParrotDev/Assets/Scripts/LiveKit/RoomManager.cs
unity/ParrotDev/Assets/Scripts/AR/TapToPlace.cs
unity/ParrotDev/Assets/Scripts/Core/LauncherUI.cs   ← 权限与进主场景（若从 Launcher 走）
unity/ParrotDev/Assets/Resources/parrot_config.json.example  ← Mint/LiveKit 示例（真配置 gitignore）
.cursor/memory/active_context.md                  ← AC1–AC8 与阶段路径
.cursor/memory/INDEX.md                           ← 全局索引
docs/report/2026-04-23_unity_parrotdev_sprint3_ar_testing_context.md  ← 本文
```

---

## 9. AC1–AC8 与 Unity 侧对象的粗略映射（摘自 active_context，便于对测）

> 具体步骤以 `active_context` 与 `sprint3_completion_report` 为准；下表帮助 **下一轮 chat** 快速把 **AC 编号** 指到 **场景/脚本**。

| AC | 用户可见目标 | Unity 侧主要依赖（非穷尽） |
|:--|:--|:--|
| AC1 | Launcher 权限 | `LauncherUI` + Android `Permission`（仅真机构建路径） |
| AC2 | 连接 / Token | `TokenService`、`RoomManager`、`parrot_config` / `unity_join_token.txt` |
| AC3 | 进 AR + 问候 | 场景加载 + `RoomManager` → `onSceneReady` RPC；需 Brain 已在房 |
| AC4 | 平面放置 + 上报 | `TapToPlace` → `onGosloPlaced`；需 AR 平面与射线管理器 |
| AC5 | 视频全开 / tier | `VideoTierReceiver` + `ARVideoPublisher` 重建轨；Brain `setVideoTier` |
| AC6 | 视频关 / mute | 同上 + DSG 模式在后端；Unity 侧 mute 轨 |
| AC7 | 断网降级 | 网络层 + Supervisor（以后端日志为主）；Unity 可用 **Editor 断连菜单** 做 **弱网模拟子集** |
| AC8 | 场景 profile | `SceneProfileManager` + `setScene` RPC |

**本轮 Unity 工作直接撑住的 AC**：**AC3 前置（场景里有 AR + LiveKit 接收）**、**AC4 平面链**、**AC5/6 的接收与推流前提（组件在位）**；**AC1/2** 仍依赖 Launcher 流程与 Mint；**AC7** 以后端与网络为主，Editor 菜单仅 **模拟 LiveKit 断连**。

---

## 10. 日志对表模板（复制即用）

| 字段 | 填写示例 |
|:-----|:---------|
| UTC / 本地时间 | |
| 动作 | 例：`EditorTest Disconnect→1s→Reconnect` / `真机 AC4 点击` |
| Unity Console 锚点行 | 贴 `[RoomManager]` / `[SelfTest]` / `[EditorTest]` 一行 |
| `parrot_diagnostics.log` 片段 | `adb pull` 或文件分享路径 |
| 后端/Castle 日志锚点 | 同秒级 `grep` 关键字 |
| 结果 | pass / fail / flaky |
| 备注 | 设备型号、Build、Git SHA |

**注意**：`ParrotDiagnosticsLog` 会镜像 **全部** `Debug.Log`；**勿**在客户端打印 **JWT 全文、Mint secret**（`parrot_config.json` 已 gitignore；对表时仍建议打码 token 长度即可）。

---

## 10.5 测试目的标识与架构边界（必读，防误解）

### 10.5.1 三类东西必须分开命名心智

| 类别 | 含义 | 本轮实际落在哪 |
|:-----|:-----|:----------------|
| **A. 产品：AR App 启动与连接流程** | 冷启动 → 权限 → Mint/Token → 用户确认 → 进房 → 进 AR 场景 → 断线重试与文案。**尚未作为独立设计文档/状态机收口**；`LauncherUI` + `Dev` 直连等是 **现状拼接**，不是终稿。 | **未在本轮实现「正式 App 流程设计」** |
| **B. 运行时：`RoomManager` 等** | 真实业务用的 **LiveKit 房间生命周期**（连房、收轨、RPC）。`LastConnectDurationSeconds`、**测试用断开/重连** 是 **可观测性 + 联调辅助**，**不是**对最终用户「首连 SLA」的承诺口径。 | `RoomManager.cs` |
| **C. 测试 harness** | **Editor 菜单断连**、`ParrotDiagnostics*`、`SelfTest`：**目的**是 **暴露后端路径、对日志时间轴、找缺陷**；**允许且鼓励**继续改强，但 **不得被误读为「App 连接架构的权威定义」**。 | `Testing/Editor/*`、`Testing/Runtime/*` |

**结论（用户原话固化）**：**可以把 ParrotDev 与测试脚本改好、改到更能覆盖后端**；但 **不能把「连接性能/断连 smoke」当成 AR App 启动与连接流程的设计基础与依赖**。新任务里写测试计划时，请 **显式标注测试目的**（例：`[目的: LiveKit 连通性+重连 smoke，非 App 启动 UX]`）。

### 10.5.2 已观察到的架构缺口与不足（仅记录，本轮不擅自当产品改）

以下 **不自动改代码/不写死产品方案**，供下一轮讨论或专门「App 流程」任务收口：

1. **缺少统一的「App 会话」层**：启动、Token、进房、切场景、AR Session 就绪、失败重试 **分散在** `LauncherUI`、`RoomManager`、`Dev` 场景入口；**无**单一 FSM/编排文档，**测试 harness 无法替代**这一层设计。  
2. **`RoomManager` 双入口语义**：`autoConnectOnStart` 在 Dev 与 Launcher 行为不同 — **对测友好**，对 **最终用户心智** 仍要再设计「唯一真相」入口。  
3. **重连策略**：当前 **测试** 为「立即/固定 1s 重连」；**产品级** 退避、最大次数、UI 提示、与 Brain 侧状态对齐 **未定义**。  
4. **`VideoTierReceiver` ↔ `ARVideoPublisher`**：Inspector 绑定若漏，**tier 到了但轨行为不对** — 属于 **配置与验收清单** 缺口，非单测脚本能兜底。  
5. **XR / 权限 / 网络失败组合**：真机 **AC7** 与 Editor **LiveKit 断连** 覆盖面 **不等价**；需在测试计划里 **分别标注目的**。

### 10.5.3 对后续改测试/ParrotDev 的鼓励边界

- **可随便改、且应改好**：`Testing/**`、`Augment`、诊断 HUD、SelfTest 断言与日志锚点，**目标是多触发后端分支、好对表、好复现**。  
- **改 `RoomManager` 等产品脚本时**：保留 **与测试 API 的清晰分界**（已有 `DisconnectForTesting` 等命名）；大改 **启动/连接产品流程** 前应 **单开设计任务**，避免测试代码反向绑架产品。

---

## 11. 本轮明确未改动的范围（防协议/后端漂移）

- **未改** Python Bus / Brain / DSG 业务逻辑；**未改** LiveKit 服务端拓扑。  
- **未新增** 正式协议 schema 文档；仅 **Unity 场景与测试 harness**。  
- **RPC RTT（前端）**：使用 **既有** `onGosloPlaced` 作为 **轻载往返** 探针（`ParrotRpcRttProbe` + HUD / Editor 菜单），**不新增** Brain RPC 方法名；与「专用 echo 合同」无关。详见 `docs/test/p2_5/pipeline_test_matrix_sprint3.md` §3 `T-RPC-01`。  
- **未自动** 修改 `ProjectSettings` 里 XR / Input 的勾选（除用户本机已在 Editor 里点的 Unity 自带弹窗外）。

---

## 12. 压缩后下一轮建议打开顺序

1. **`docs/test/p2_5/pipeline_test_matrix_sprint3.md`**（**§A～F** 操作顺序 + **§3** 矩阵 — 实习生主入口）  
2. **`architecture/sprint3_completion_report_20260423.md` §7**（AC1–AC8 状态栏）  
3. **本文**（`docs/report/2026-04-23_…` — 工具说明与边界）  
4. **`active_context.md`** 头部 + AC 栏  
5. **`module_map_p2.md`** 若需查 Unity↔Brain 数据流一句  
6. 真机问题时：**`parrot_diagnostics.log` + logcat** 与后端同时间段  

---

*文档由会话整理并二次扩充，用于 context 压缩后的工程背景恢复。*
