# Sprint 3 一致性审计与 Sprint 4 统一大背景

## 1. Sprint 3 一致性审计结论
经过对 `sprint3_completion_report_20260423.md`、`brain_connected_black_video_20260425.md`、规则文件（AR Foundation、LiveKit SDK）以及技能文件的交叉比对，项目当前状态**高度一致且真实**：
- **交付内容与文档一致**：Unity 真机已能进房，AR 相机视频推流成功（带 `UNITY_AR_FOUNDATION` 宏修复），RPC 连通（RTT 129ms）。
- **规则与技能一致**：严格锁定了 Unity 2022.3 LTS + AR Foundation 5.1.x；视频流确立了“一流多采样”的单主轨策略。
- **行为与测试一致**：`set_video_tier` 升级为同步 Intent 闭环；`identify_object` 因缺乏截图和破坏同步体感，已被如实记录并默认禁用（`ALL_TOOLS` 移出），没有掩盖问题。
- **技术栈与前沿匹配度**：
  - **Unity 端**：AR Foundation 5.1 是目前最稳妥的跨平台基线，不追新 Unity 6 是明智的防踩坑策略。
  - **通信层**：LiveKit WebRTC 提供了毫秒级音视频与 DataChannel/RPC，是当前 AI Agent 实时交互的行业标配。
  - **AI 端**：Gemini Live (Multimodal) 结合 LiveKit Agents 框架，代表了当前端到端语音大模型的最前沿实践。
  - **记忆与知识**：Graphiti 知识图谱 + Nanobot 异步任务，是解决 LLM 长期记忆和长耗时工具调用的标准解法。

## 2. 能力提炼与边界
- **已验证能力**：
  - Unity ↔ LiveKit ↔ Python Brain 的全链路连通性。
  - AR SessionTracking 与视频帧的获取与推流（H264/VP8 fallback）。
  - 基础 RPC 往返（`onSceneReady`, `onGosloPlaced`, `setVideoTier`）。
  - Gemini Live 的原生音视频对话接入。
- **未完成能力（Sprint 4 核心目标）**：
  - **音频防回声与路由**：外放回声导致 Gemini VAD 误判、复读和打断。
  - **按需视觉证据**：`captureSnapshot` RPC 尚未实现，`identify_object` 缺乏图片输入。
  - **正式 App UX**：目前只有 `Dev.unity` 测试舞台，缺乏正式的 Launcher、权限请求流、音视频设备选择入口。
- **强依赖与风险边界**：
  - **强依赖**：LiveKit Unity SDK 的稳定性（Play/Stop 抢占、AudioStream 强引用回收问题）。
  - **风险边界**：Graphiti `add_episode` 写入耗时（20-46s），绝对不能阻塞实时语音流；LiveKit RPC Payload 限制（15KB），传图需降频或改走 ByteStream。

## 3. 统一大背景（供所有 DeepResearch 子任务共享）
ParrotCarriers / GOSLO 是一个 AR + LiveKit + Gemini Live + Bus/DSG/Graphiti/Nanobot 的多模态桌面鹦鹉 Agent。

当前阶段：Sprint3 已完成并通过 smoke。Unity Android 真机可以进入 LiveKit 房间，Brain Agent 能接入 Gemini Live，GOSLO 能语音对话、接收视频、看到 AR 相机画面，AR Foundation 显示 SessionTracking，Unity→Brain RPC RTT 约 129ms。Sprint3 验证的是“连接、媒体、AR、RPC、基础行为工具”的主链路，不是最终 App UX。

技术基线：
- Unity：Unity 2022.3 LTS。
- AR：AR Foundation / ARCore / ARKit 5.1.x，当前不升级 Unity 6 或 AR Foundation 6.x。
- LiveKit：Unity SDK 通过 UPM git URL，仍属 developer preview；用于音频、视频、RPC、DataChannel。
- Brain：Python LiveKit Agents + Gemini Live native audio/video。
- 视频：Unity 发布一条 `ar-camera` 主视频流，Gemini Live 默认消费；后续 A10/DSG/identify_object 不应长期要求高码率，而应通过 tier / snapshot / sampling 门控。
- 音频：Unity 麦克风上行 + Gemini/Brain 下行远端音频。当前最大风险是外放回声被 Gemini 当成用户输入，导致复读、打断和 turn-taking 混乱。
- 行为：GOSLO 工具分 Reflex / Intent / Task。GOSLO 自身行为工具必须同步等待结果，不能 fire-and-forget 后口头宣称完成。
- DSG：DSG 是动态场景图/语义工作记忆层。它不等于实时视觉模型，而是把 Gemini 口述、identify_object、未来 A10 感知、用户标签等过滤后写入 L2-B/Graphiti。当前 Graphiti 写入骨架跑通，但实时对话不能依赖慢写入。
- Nanobot：用于长任务/后台研究，不应伪装成 GOSLO 同步识别。异步任务必须明示“稍后告诉你”。
- Sprint4 目标：从“链路能跑”升级到“App 启动与功能入口、音频路由、媒体稳定性、截图识物、协议 V2、模块边界、AR 工作区规则”的前置设计。