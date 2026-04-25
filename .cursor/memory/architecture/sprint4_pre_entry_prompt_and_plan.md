# Sprint 4 前置入口：测试束隔离、能力提炼与 AR App 启动设计

> 更新时间：2026-04-25  
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

## 2. 最高效执行顺序

1. **先完成最小真机测试**  
   只验证数据流事实：连接、麦克风、视频首帧、Brain 在房、RPC、DataChannel、断线/重连。不要继续为了测试体验去堆测试脚本。

2. **提炼 Sprint 3 有效经验**  
   把测试结果分成四类：
   - 可保留能力
   - 有效踩坑
   - 错误临时设计
   - 应迁入测试留档的内容

3. **联网调研 LiveKit / WebRTC / AR App 稳定性策略**  
   重点看权限门、连接门、AR 会话门、功能入口、降级态、前后台恢复。调研用于筛选 Sprint 3 经验是否对正式 App 有用，不照搬 UI。

4. **独立设计 AR App 功能入口、生命周期与视频门控**  
   先决定每个 App 功能入口使用哪些能力，再决定代码结构。不得从测试脚本反推产品流程。

5. **进入 Sprint 4 数据流实现**  
   Sprint 4 仍做数据流：`captureSnapshot`、相机模式补充通道、`identify_object Path1`、便签 UI、食指 perching 等。但必须能解释它们在未来 App 生命周期中的位置。

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
3. 联网调研 AR / 移动游戏 / 机器人控制 / WebRTC App 的启动与功能入口；
4. 提炼哪些能力和坑能指导 Sprint4；
5. 设计 AR App 的功能入口和生命周期边界；
6. 再决定 Sprint4 数据流实现顺序。

请先阅读：
- `.cursor/memory/active_context.md`
- `.cursor/memory/architecture/sprint4_pre_entry_prompt_and_plan.md`
- `.cursor/memory/architecture/ar_app_plan.md`
- `.cursor/memory/architecture/ar_feature_implementation_plan.md`
- `.cursor/memory/architecture/ar_feature_vision.md`
- `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`
- `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`
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

请输出：
1. 总体判断；
2. 最高效执行顺序；
3. 能力 → App 功能入口映射；
4. Sprint3 有效内容提炼清单；
5. 测试束隔离清单；
6. Sprint4 前置准入清单；
7. 推荐现在应先完成测试、调研，还是开始实现，并说明理由。
```

## 6. LiveKit 稳定性与视频策略补充

详见 `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`。当前固定判断：

- 真机按钮、HUD、零散 logcat 只适合证明连通性，不适合直接推导视频质量策略。
- Sprint 4 前置应优先调研 LiveKit 官方 self-hosting、TURN/TLS、host networking、simulcast/dynacast/adaptive stream、Android 后台/重连行为。
- 主视频流应由消费者需求反推上限：Gemini Live 默认低延迟低码率，`identify_object` 走按需截图，A10 感知任务再短时升档。
- 直连不必然最稳；必须对照 direct UDP、TCP fallback、TURN/UDP、TURN/TLS 443。

## 7. 当前建议

现在先去完成 **最小真机测试**。测试目标不是把 UI 跑顺，而是拿到足够事实：

- LiveKit 是否连上
- Brain 是否在房
- 麦克风轨是否发布
- 视频轨是否有首帧
- RPC 是否能双向对表
- DataChannel 是否能发出并被消费
- 前后台 / 断线 / 重连是否有假成功

拿到这批事实后，立刻停止继续堆测试束，进入“提炼 + 调研 + App 功能入口设计”。
