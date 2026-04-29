# Sprint 4 前置入口：测试束隔离、能力提炼与 AR App 启动设计

> 更新时间：2026-04-29  
> 状态：Sprint 4 前置固化稿  
> 用途：新开 Chat / 新任务时，用于先统一架构理解、任务顺序和提示词，避免把 P2.5 测试束误当正式 AR App 设计。

## 1. 当前判断

P2.5 / Sprint 3 的真机工作，本质是验证 **数据流生命周期**：

- LiveKit 房间连接与 Token Mint
- 麦克风音频轨
- AR / 相机视频轨与首帧
- Brain 是否在房
- Brain→Unity RPC
- Unity→Brain RPC
- Lossy DataChannel / telemetry
- 前后台、断线、重连、mute、track rebuild

这些数据流和能力划分已经足够清晰。真正还没完成的是：**它们在正式 AR App 中应该成为哪些功能入口，以及在哪个 App 生命周期阶段启用**。

因此，Sprint 3 测试脚本、`Dev.unity`、Runtime HUD、自检按钮、`Launcher -> Dev` 临时流程、WebCam fallback、`FindObjectOfType` 自动补绑定、3 秒等待等，只能作为 **测试束 / 事故记录 / 设计输入**。它们不能反向定义 Sprint 4 的 App 启动、连接、权限或 AR 会话流程。

### 1.0 2026-04-29 状态更新

Sprint3 真机 smoke 已完成，测试结果已提炼到 `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md`。当前不再建议继续扩测试束；下一步进入 **Sprint4 协议 / 数据流 / AR 工作区升级收口**。

新增背景锚点：`.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`。

正式协议稿：`.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`。

该背景锚点记录以下新共识：

- Sprint4 应先统一协议 V2 / ECP、数据流连接健壮性、DSG L2-B / Graphiti / Obsidian / Ref 边界，再进入四个验证工具实现。
- 四个验证工具顺序：核心对话 / 简单指令库 / 飞到手指 → 按需发现物体升级 → Focus 放大镜 / Bounding Box 后端接口 → 照相机功能。
- ECP 不是替代 Scheduler / BT / Reflex-Intent-Task；ECP 是从后端决策到 Unity 前端状态机的目标命令与回执协议。
- 未来 BT 森林可以按 `Scene` / `BehaviorMode` / `VisualState` / `BodyState` 扩展，但所有树应输出统一 `EcpCommand`，由 Arbiter 与 Unity 前端状态机处理。
- DSG L2-B / L3 是工作记忆和潜意识索引；Graphiti 是长期时间图和可检索信息源；Obsidian 是人类维护的 Ref / SSOT。
- Ref 不一定使用 UUID，但绑定关系必须稳定可追踪；Graphiti node UUID 是与 L2-B Node 高效适配的重要锚点之一。

## 1.1 Sprint 4 计划补充：数据流设计、协议 V2 与后端接口提炼

Sprint 4 的重点不只是“把几个功能做出来”，而是完成 **数据流设计升级 + 协议 V2 升级 + P2.5 后端接口提炼**。

用户已补充 UI 布局、App Flow、ECP、LiveKit/WebRTC、DSG/Graphiti、潜意识工作区等调研，结果集中在：

- `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md`
- `docs/sprint4_research/result/02_LLM_Control_Protocol_and_State_Machine.md`
- `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md`

这些调研的作用不是替项目重写架构，而是帮助筛选 Sprint3/Sprint4 中哪些能力应该沉淀为正式协议和后端接口。

### 双管线适配边界

当前已跑通的是 **Line A：Gemini Live 原生管线**：

- Unity 麦克风轨 → LiveKit → Gemini Live
- Unity 视频轨 → LiveKit → Gemini Live `video_input`
- Gemini Live 内部处理 ASR / TTS / turn detection / 语音回复
- Brain tools / RPC / DataChannel 作为控制与补充通道

Sprint 4 必须为未来 **Line B：自建 ASR/TTS/VLM 可替换管线** 预留协议边界：

- Unity 音频轨 → 自建 ASR → Brain / Scheduler / DSG
- LLM 文本输出 → 自建 TTS → Unity / LiveKit 播放
- TTS / ASR / LLM 事件显式写入时间轴
- 视频帧 / snapshot / sighting 与语音 turn 对齐
- A10 / DSG / identify_object 可按需消费高清截图或短时升档视频

Sprint 4 不要求完整实现 Line B，但必须让协议 V2、事件时间轴、DSG L2-B、snapshot、speech state 能兼容 Line B。不要让 Gemini Live 黑盒成为唯一真相源。

### 协议 V2 / ECP 升级方向

协议 V2 应从“纯 RPC 指令”升级为 **目标驱动 + 状态同步 + 可过期命令 + 前端状态机回执**。

需要在 Sprint 4 前置设计中明确：

- `TurnEvent`：语音/文本 turn 的统一事件，未来可来自 Gemini Live 或自建 ASR。
- `SpeechStateEvent`：LISTENING / THINKING / SPEAKING / INTERRUPTED / SILENT 等状态。
- `SightingEvent`：前端/感知侧看到的对象、区域、关键帧、置信度、来源。
- `SnapshotEvent`：按需截图的路径、时间戳、来源相机、关联对象或用户意图。
- `EcpCommand`：Brain / Scheduler 下发给 Unity 的目标驱动命令。
- `EcpAck` / `EcpState`：Unity 前端状态机的执行回执、拒绝原因、过期丢弃、micro-lock 状态。

ECP 命令至少应考虑字段：`command_id`、`issued_at`、`valid_after`、`expires_at`、`priority`、`interruptibility`、`source_turn_id`、`source_sighting_id`、`target_state`、`expected_duration`、`fallback_behavior`。

### DSG L2-B 与 Graphiti 协议升级

Sprint 4 的数据流设计必须把 DSG L2-B 放入协议 V2：

- L2-B 是场景工作记忆 / 注意力 / 潜意识工作区，不是长期数据库。
- Graphiti 是长期时间图，不应接收每帧视频或每个检测框。
- Graphiti 写入应通过后台投影器 / EpisodeArchiver / MemoryWriter，而不是实时视频循环或实时对话直接写。
- L0 Event Stream 应作为状态变化的可回放源，贯穿原始事件 → sighting → L2-B node → Graphiti episode → Obsidian SSOT。

Sprint 4 应先设计最小接口，而不是直接扩大实现：

- `SceneObservationEvent`
- `EpisodeArchivePayload`
- `GraphitiPreloadResult`
- `ContextInjectionCandidate`
- `SubconsciousTrigger`

### P2.5 后端接口提炼目标

Sprint 4 需要从 P2.5 测试和现有代码中提炼出后端接口，而不是继续把测试脚本当接口：

- LiveKit 连接状态接口
- Audio publish / subscribe 状态接口
- Video source / first-frame / tier / mute / rebuild 状态接口
- Snapshot capture 接口
- identify_object 输入输出接口
- Brain presence / tool availability 接口
- ECP command / ack 接口
- DSG observation / preload / archive 接口
- Context injection 候选接口

这些接口应服务正式 App 和后端模块，不服务 Runtime HUD 本身。

## 2. 最高效执行顺序

1. **已完成最小真机测试与有效经验提炼**  
   结论见 `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md`。后续只把测试结果作为设计输入，不继续为了测试体验堆 Runtime HUD / SelfTest。

2. **阅读 Sprint4 协议 / ECP 背景锚点**  
   先读 `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`，确认 ECP、Reflex/Intent/Task、BT Router、未来 BT 森林、DSG/Graphiti/Obsidian/Ref 的统一口径。

3. **阅读 Protocol V2 / ECP 正式设计稿**  
   以 `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md` 为后续实现入口，字段仍处于 tentative，待最小 ECP envelope 和四个验证工具跑通后冻结。

4. **进入最小 ECP envelope 实现**  
   先新增 Python / Unity DTO，并包住 `flyTo`、`animate`、`setVideoTier`。旧 RPC 保持兼容，不一次性替换。

5. **进入 Sprint4 四个验证工具实现**  
   顺序为：核心对话 / 简单指令库 / 飞到手指 → 按需发现物体升级 → Focus 放大镜 / Bounding Box → 照相机功能。每个工具必须能解释其 App 生命周期位置、ECP 目标命令、状态回执和 DSG / Ref 边界。

6. **同步技能文档**  
   `.cursor/skills/livekit-unity-video-publish/SKILL.md` 和 `bus-deploy-livekit-ecs/SKILL.md` 必须反映 Sprint 4 前置判断：主视频是策略门控共享源，Castle 从最小连通进入稳定性验证。

## 3. 能力与 App 功能入口的理解方式

后续设计应按“入口”而不是“脚本”组织：

| App 功能入口 | 可能使用的能力 | 设计关注点 |
|:--|:--|:--|
| 启动 / 权限入口 | Camera、Microphone、网络状态、配置读取 | 不等于 `LauncherUI` 当前临时实现；需明确拒权、重试、降级 |
| 连接入口 | Token Mint、LiveKit Room、Brain presence | 连接成功不等于 Brain 可用；要区分 LiveKit ON 与 Brain agent yes |
| AR 会话入口 | ARSession、ARCameraManager、平面检测、tracking state | 何时启动/暂停/恢复 AR；跟踪丢失如何提示 |
| 对话入口 | 麦克风轨、Brain/Gemini 订阅、远端音频播放 | 无视频可对话，但必须有麦轨和消费端 |
| 视频 / 感知入口 | ARVideoPublisher、video tier、首帧、mute、rebuild | PublishTrack 成功不等于有真实帧 |
| 识别入口 | `captureSnapshot`、`identify_object`、Graphiti / L2-B | 按需截帧，不把 Gemini 黑盒“看到”当可存档图片 |
| 操控 / 动画入口 | `flyTo`、`animate`、ParrotController | Brain→Unity RPC 与 App UI/触控入口要分清 |
| 手势 / perching 入口 | XR Hands、DataChannel、perching 规则 | 手势 telemetry 是补充通道，不是主视频 |
| 便签 / 轻 UI 入口 | Unity UI、RPC / DataChannel / Brain tool | Sprint 4 可做 MVP，但要避免与测试 HUD 混淆 |
| 调试 / 测试入口 | Runtime HUD、自检、DiagnosticsLog、adb 对表 | 只能留在 Testing/Runtime、Testing/Editor、docs/test |

## 4. Sprint 3 有效内容提炼清单

可保留为 Sprint 4 设计输入：

- LiveKit 房间连接和 Token Mint 链路。
- 麦克风轨发布与权限问题。
- 视频轨发布必须检查首帧。
- Brain 未在房时，Unity 侧成功连接不代表对话/识别成立。
- 无视频仍可语音对话，但需要麦克风轨和 Brain/Gemini 消费端。
- `setVideoTier`、mute、track rebuild 是视频生命周期能力，不是 App UI 流程。
- RPC 与 DataChannel 是控制/补充通道，不是主视频/主音频。
- 断线、前后台、重连必须清理本地发布状态，不能让 HUD 显示假成功。
- 日志必须清楚区分：连接失败、权限失败、无设备、无首帧、发布失败、Brain 缺席、无人消费。

必须降级为测试束 / 留档：

- Runtime HUD 和真机测试按钮。
- `ParrotSelfTestCoordinator` 的 3 秒等待与自检文本。
- `ParrotDiagnosticsLog` 的 logcat / 文件对表。
- Editor 菜单静态审计。
- `Dev.unity` 作为集成测试场景。
- `Launcher -> Dev` 的当前临时跳转。
- WebCam fallback 和自动查找绑定。

## 5. 新 Chat 启动提示词

```markdown
你是 ParrotCarriers 的架构/产品化审计助手。请始终用中文回答。

当前目标不是继续堆测试脚本，而是：
1. 理解现有数据流能力；
2. 审计 Sprint3 真机测试暴露的问题；
3. 吸收 `docs/sprint4_research/result/` 中关于 LiveKit/WebRTC、ECP、App Flow/UI 的调研；
4. 提炼哪些能力和坑能指导 Sprint4；
5. 设计 AR App 的功能入口和生命周期边界；
6. 设计数据流升级、协议 V2 / ECP、DSG L2-B、后端接口提炼；
7. 再决定 Sprint4 实现顺序。

请先阅读：
- `.cursor/memory/active_context.md`
- `.cursor/memory/architecture/sprint4_pre_entry_prompt_and_plan.md`
- `.cursor/memory/architecture/sprint4_protocol_ecp_background_20260429.md`
- `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`
- `.cursor/memory/architecture/ar_app_flow_ui_design.md`
- `.cursor/memory/architecture/ar_app_plan.md`
- `.cursor/memory/architecture/ar_feature_implementation_plan.md`
- `.cursor/memory/architecture/ar_feature_vision.md`
- `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`
- `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`
- `docs/sprint4_research/result/01_WebRTC_Lifecycle_and_Video_Strategy.md`
- `docs/sprint4_research/result/02_LLM_Control_Protocol_and_State_Machine.md`
- `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md`
- `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md`
- `docs/test/p2_5/unity_channels_audit_mobile_zh.md`
- `docs/test/p2_5/mobile_runtime_harness_zh.md`
- `.cursor/skills/client-sdk-unity/SKILL.md`
- `.cursor/skills/livekit-unity-video-publish/SKILL.md`

请特别注意：
- `Dev.unity`、Runtime HUD、自检按钮、Launcher→Dev 临时流程、WebCam fallback、`FindObjectOfType` 自动补绑定等都是测试束，不是正式 AR App 设计。
- 不要从测试脚本反推产品启动流程。
- Sprint4 仍以数据流为主，但必须考虑这些数据流在 App 生命周期里的位置。
- 主视频不再默认固定高质量；它是 Unity 端和 Bus 云端共同门控的共享源。
- Gemini Live 默认优先低延迟与稳定，A10/SAM2/DINOv2 才触发更高质量或更密采样。
- 当前 Gemini Live 原生管线是 Line A；Sprint4 必须为未来自建 ASR/TTS/VLM 的 Line B 预留协议边界。
- 协议 V2 / ECP 应从纯 RPC 升级到目标驱动、状态同步、可过期命令、前端状态机回执。
- ECP 不是替代 Scheduler / BT / Reflex-Intent-Task；它是后端决策到 Unity 前端状态机的目标命令与回执协议。
- DSG L2-B 应作为场景工作记忆 / 注意力 / 潜意识工作区接入协议 V2；Graphiti 是长期时间图，不应被实时帧循环直接写入。
- Obsidian 是人类维护的 Ref / SSOT；Ref 不一定使用 UUID，但绑定关系必须稳定可追踪。
- Sprint4 应从 P2.5 提炼可复用后端接口，而不是把 Runtime HUD / SelfTest 当接口。
- AR App Flow / UI 以 `ar_app_flow_ui_design.md` 为当前基线；`ar_app_plan.md` 只作为早期问卷与历史追溯。

请输出：
1. 总体判断；
2. 最高效执行顺序；
3. 能力 → App 功能入口映射；
4. Sprint3 有效内容提炼清单；
5. 测试束隔离清单；
6. Sprint4 数据流升级与协议 V2 目标；
7. Gemini Live 原生管线与未来自建 ASR/TTS/VLM 管线的适配边界；
8. DSG L2-B / Graphiti / Obsidian 的最小协议接口建议；
9. P2.5 后端接口提炼清单；
10. Sprint4 前置准入清单；
11. 推荐现在应先完成测试、调研，还是开始实现，并说明理由。
```

## 6. LiveKit 稳定性与视频策略补充

详见 `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`。当前固定判断：

- 真机按钮、HUD、零散 logcat 只适合证明连通性，不适合直接推导视频质量策略。
- Sprint 4 前置应优先调研 LiveKit 官方 self-hosting、TURN/TLS、host networking、simulcast/dynacast/adaptive stream、Android 后台/重连行为。
- 主视频流应由消费者需求反推上限：Gemini Live 默认低延迟低码率，`identify_object` 走按需截图，A10 感知任务再短时升档。
- 直连不必然最稳；必须对照 direct UDP、TCP fallback、TURN/UDP、TURN/TLS 443。

## 7. 当前建议

当前已完成 **最小真机测试** 与有效经验提炼。现在应进入：

1. 阅读协议 V2 / ECP 背景锚点与正式协议稿。
2. 最小 ECP envelope 实现：Python / Unity DTO，先包住 `flyTo`、`animate`、`setVideoTier`。
3. 数据流连接健壮性实现：前后台、重连、音频设备切换、外放回声、视频首帧/新鲜帧/tier。
4. DSG L2-B / Graphiti / Obsidian / Ref 最小接口实现。
5. Sprint4 四个验证工具的分阶段实现。
