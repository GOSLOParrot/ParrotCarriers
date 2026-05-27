# 第2轮研究笔记：论文、代码实现与答辩重点

> 目标：为下一步“大纲草稿 → 大纲审计 → 演讲稿/PPT稿”提供可恢复的事实基础。当前不是演讲稿终稿，也不是PPT终稿。

## 1. 用户需求重新聚焦

这轮要解决的不是“把所有技术栈列出来”，而是回答三个问题：

1. 这个项目为什么不是普通聊天助手，而是 AR 场景 Agent。
2. 我们做到了什么：多源输入、实时交互、记忆组织、触发协议、后台任务协作。
3. 我们创新在哪里：把 SVA Processor 思路扩展到 DSG 记忆处理器，把多源 Ref / UUID / Graphiti / IntentWorkspace / Scheduler 串成可追踪的数据流。

讲述边界：

- 不讲代码细节，讲架构设计、数据流、模块协作。
- 技术名词保留，但要先定义再展开。
- 例子要来自已实现或有明确代码链路的工具。
- `nanobot` 后台 Worker 不作为 LiveKit 挂载模块主线来讲；主讲 Scheduler / Redis / 后台 Worker 任务链路。
- Graphiti、触发器、Episode、L2-B 等如果实现边界还在演进，要用“原型实现 / 已贯通 / 后续完善”这类谨慎表述。

## 2. 论文中可支撑答辩主线的内容

### 2.1 背景与问题

论文段落 `[130]` 到 `[134]` 支撑开场：

- 传统生活助手多是文本对话或时间提醒，缺少对真实场景的理解。
- AR 生活助手要把“时间提醒”升级为“情景提醒”。
- 系统需要同时处理语音、视频、拍照、标注、场景状态、日程、笔记、历史记忆。
- 本项目不是单独做聊天机器人，也不是单独做图数据库，而是把实时多模态交互、DSG、Graphiti/GraphRAG、Obsidian 这几类能力整合起来。

建议讲法：

> 我们的核心问题不是让模型回答得更长，而是让助手知道“当前发生了什么、这些信息从哪里来、哪些需要暂存、哪些值得长期记住、什么时候该提醒用户”。

### 2.2 多源输入与 DSG

论文段落 `[131]`、`[142]` 支撑 DSG 主线：

- DSG 可以把对象、人物、空间、事件、语义关系组织成图。
- 项目把 DSG 扩展为多源 Ref 接入层、L1.5 池、L2-B 语义工作记忆图、Graphiti 长期图记忆。
- 输入来源包括 Obsidian、视觉检测、语音转写、工具输出、通信事件、Google 日程、ECP 事件等。

建议讲法：

> DSG 在这里不是单纯的机器人地图，而是运行时记忆组织层。它负责把不同来源的信息先变成可追踪的 Observation / Ref，再决定进入短期工作记忆、暂存区，还是长期图记忆。

### 2.3 LiveKit、SVA Processor 与实时链路

论文段落 `[137]`、`[148]`、`[149]`、`[150]` 支撑实时通信主线：

- LiveKit 基于 WebRTC，可提供 Room、Participant、Track、DataChannel、RPC 等能力。
- 本项目用 LiveKit 做实时通信中枢：音视频轨负责感知数据，DataChannel 承载 ECP 事件与状态，RPC 触发前端动作。
- SVA Processor 思路可解释为：实时音视频流不是只给大模型直接看，也可以由处理器以受控频率处理，再把结构化结果注入 Agent 上下文。

代码补充：

- `src/parrot/bus/processor_hook.py` 定义 `BaseProcessor`，说明设计受 SVA Processor pattern 启发：订阅 LiveKit VideoTrack，处理帧，通过 DataChannel / Redis 发布结果。
- `src/parrot/brain/vision/livekit_sampler.py` 是房间级低帧率视频采样器，说明系统除了原生视频输入，还在建设可审计的视频证据路径。

谨慎点：

- 不要把 SVA 讲成一个单独已经完全成熟的视觉大模型系统。应讲成“借鉴 SVA Processor 模式，并在本系统中扩展为可进入 DSG 的处理链路”。

### 2.4 ECP 与前台动作闭环

论文段落 `[899]` 到 `[902]` 支撑 ECP：

- 后端通过 RPC 调 Unity 的飞行、动画、视频档位、截图等能力。
- Unity 负责房间连接、音视频发布、下行命令接收、ECP 事件和状态。
- ECP 重点是命令状态、过期时间、ACK。工具调用不能假设前端成功，必须拿到 completed / rejected / expired 等结果。

代码依据：

- `src/parrot/brain/tools/animate.py:133`：`play_dance()`。
- `src/parrot/brain/tools/animate.py:68`：命令类型是 `EcpCommandKind.ANIMATE`。
- `src/parrot/brain/tools/animate.py:78`：通过 `call_unity_rpc(method="animate")`。
- `src/parrot/brain/tools/_rpc_bridge.py:84`：RPC 结果镜像到 Blackboard。
- `src/parrot/brain/tools/_rpc_bridge.py:108`：写入 `tick/last_rpc_ack`。
- `src/parrot/brain/tools/_rpc_bridge.py:270`：无论成功失败都会镜像结果。

建议讲法：

> ECP 解决的是“模型说执行了”和“前端真的执行了”之间的状态一致性问题。

### 2.5 Reflex / Intent / Task 三层行为

论文段落 `[139]`、`[905]` 到 `[908]`、`[1218]` 支撑三层行为：

- Reflex：手势停靠、急停、本地状态变化等低延迟动作。
- Intent：语音指令、拍照、框选、飞行控制、工作区切换、主动提醒等前台行为，需要回执和界面/语言同步。
- Task：资料整理、消息检查、日程草稿生成或执行、Graphiti 预加载、多智能体协作等后台任务。

代码依据：

- `src/parrot/scheduler/router.py:6` 到 `:8`：路由顺序是 Reflex、Intent、DispatchToNanobot。
- `src/parrot/scheduler/router.py:45` 到 `:47`：行为树节点顺序。
- `src/parrot/scheduler/nodes.py:24`：`DispatchToNanobot`。
- `src/parrot/scheduler/task_catalog.py:23` 到 `:29`：calendar 和 nanobot 任务类型。

建议讲法：

> 这个分层不是为了复杂，而是为了不让所有动作都等大模型。该立即反应的直接反应，该前台同步的拿 ACK，该后台慢慢做的交给 Task。

### 2.6 Nanobot 边界

论文段落 `[907]`、`[908]` 支撑 nanobot 的角色：

- nanobot 是后台 Agent team 执行层。
- 它不是主 Brain，也不直接控制 Unity。
- 负责复杂资料整理、多步骤计划、外部模块协作。

代码依据：

- `src/parrot/brain/tools/dispatch_task.py:47`：发布到 `CH_SCHEDULER_COMMANDS`。
- `src/parrot/scheduler/service.py:121`：Scheduler 写入 `STREAM_NANOBOT_DISPATCH`。
- `src/parrot/bus/nanobot_consumer.py:89`：Worker 从 Redis Stream 读取任务。
- `src/parrot/bus/nanobot_consumer.py:136`：结果发布到 `CH_NANOBOT_RESULTS`。
- `src/parrot/bus/nanobot_consumer.py:42` 到 `:47`：当前 fallback consumer 是 L2-only worker，通过 Redis 注册和心跳，不是 L1 LiveKit Participant。

答辩建议：

- 可以说：`nanobot` 在本系统中承担后台任务执行层，主链路是 Scheduler + Redis Stream。
- 不建议说：`nanobot` 是 LiveKit Room 里挂载的前台模块。
- 如果需要讲“模块挂载”，只讲总体 bus/mount 设计，并强调具体 nanobot 主任务链路走 Redis。

### 2.7 日程修改作为 Task 例子

用户已指定用“GOSLO 给 nanobot 一个改日程任务”来体现 Task，而不是用提醒混讲。

代码依据：

- `src/parrot/brain/tools/calendar_change_request.py:25`：Intent 层日程变更草稿工具。
- `src/parrot/brain/tools/calendar_change_request.py:38` 到 `:53`：只生成 Plan/HITL 草稿，不写 Google Calendar，不派发 nanobot。
- `src/parrot/brain/tools/calendar_change_request.py:135`：草稿保存 `suggested_nanobot_task_type`。
- `src/parrot/brain/tools/calendar_change_request.py:202` 到 `:211`：下一步是用户确认或 Plan/HITL 后再选择执行路线。
- `src/parrot/brain/tools/dispatch_task.py:82` 到 `:88`：`calendar_create` / `calendar_patch` / `calendar_delete` 使用 Nanobot Google Workspace MCP。

建议讲法：

> 用户说“帮我把会议改到晚上”，这只是 Intent，因为系统还在理解和确认。真正执行时，确认后的 `calendar_patch` 才是 Task，交给 Scheduler 和 nanobot 后台处理。

### 2.8 相机拍照作为多源 Ref 例子

论文段落 `[894]` 到 `[897]`、`[1145]` 支撑拍照链路。

代码依据：

- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/FormalCameraModeController.cs:170`：相机模式 `CapturePhotoFromCameraMode()`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/FormalCameraModeController.cs:182`：调用 `homeToolController.CapturePhoto()`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Photo/PhotoController.cs:19`：发布 `photo.taken_preview`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Photo/PhotoController.cs:286`：发布预览事件。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Photo/PhotoController.cs:587`：HTTP 上传关联 preview event id。
- `src/parrot/brain/observer/photo.py:21`：预览 upsert 成 L2-B `PhotoNode`。
- `src/parrot/brain/observer/photo.py:27`：完整图片上传后 `photo.asset_uploaded`。
- `src/parrot/brain/observer/photo.py:356`：stage `StagedRefKind.PHOTO`。
- `src/parrot/brain/observer/photo.py:377`：绑定 `RefKind.PHOTO_PATH`。

谨慎点：

- 不要说拍照必然自动识别出 ObjectNode。代码里 PhotoNode 与 ObjectNode 是分开的。
- 可以说“照片成为证据和后续识别/确认的入口”。

### 2.9 触发器协议

论文段落 `[925]` 到 `[930]` 支撑 Episode 与 Graphiti 回灌；论文段落 `[907]` 可支撑 Task 与 Graphiti 预加载。

代码依据：

- `src/parrot/dsg/triggers/base.py:36`：`TriggerKind`。
- `src/parrot/dsg/triggers/base.py:44`：`TriggerOutcome`。
- `src/parrot/dsg/triggers/base.py:71` 到 `:75`：输出可包含 Observation、BucketOp、ArchiveRequest、StagedRef、PlanProposal。
- `src/parrot/dsg/triggers/runner.py:155`：统一处理 TriggerOutcome。
- `src/parrot/dsg/triggers/runner.py:159` 到 `:165`：处理顺序是 bucket、Observation、StagedRef、Archive、Plan、Nanobot、Notify。
- `src/parrot/dsg/triggers/scene_context_trigger.py:1`：历史场景/Graphiti 回灌触发器。
- `src/parrot/dsg/triggers/ssot_enrichment_trigger.py:1`：从 Obsidian/Graphiti 补充不确定节点。
- `src/parrot/brain/photo_awareness.py:1`：Photo Awareness 是 preview-ref bridge。
- `src/parrot/brain/observer/photo.py:462`：拍照预览后进入 Awareness。

建议讲法：

> 触发器协议回答“事件发生后系统能自动做什么”。输出不止提醒，还可以写观察、暂存 Ref、归档 episode、生成 Plan、派发后台任务或通知前台。

### 2.10 Graphiti、Obsidian、Episode

论文段落 `[136]`、`[911]` 到 `[913]`、`[925]` 到 `[930]`、`[1217]`、`[1222]` 支撑 Graphiti/Obsidian：

- GraphRAG 利用实体关系、时间边、事实来源进行结构化检索。
- Graphiti 提供 episode/entity/fact 抽象，适合保存带时间和来源的记忆。
- 论文中可讲成 assistant / worker / scene / user 等角色分区；当前代码常量名是 `GOSLO`、`MAID`、`SCENE`、`USER`，其中 `GOSLO` 对应助手侧长期记忆，`MAID` 对应后台 Worker / nanobot 侧记忆。
- L2-B 可从 Graphiti 预加载背景，也可把已完成 episode 归档。
- Obsidian 是本地 Markdown 知识库，适合作为用户可编辑的信息来源。

代码依据：

- `src/parrot/memory/graphiti_client.py:24` 到 `:41`：Graphiti 分区常量，当前为 `GOSLO` / `MAID` / `SCENE` / `USER` 等。
- `src/parrot/dsg/l2b_graph.py:373`：`preload_from_graphiti()`。
- `src/parrot/dsg/l2b_graph.py:409`：预加载节点是 `BACKGROUND`。
- `src/parrot/brain/tools/query_memory.py:1`：Graphiti 自然语言搜索工具。
- `src/parrot/brain/obsidian_vault.py`：本地 Obsidian vault 读取与 frontmatter 处理。
- `src/parrot/dsg/ingest/user_tag_filter.py`：Obsidian note 转 Observation 的过滤与 UUID 绑定规则。

谨慎点：

- 论文里说 Graphiti/Obsidian 绑定仍需更成熟的治理机制，答辩里可以讲“已建立原型链路和分区/UUID绑定思路”，不要讲成已经解决所有长期记忆治理问题。

## 3. 推荐答辩重点

优先级从高到低：

1. 总体架构：Unity AR 前端、LiveKit 实时中枢、Brain、DSG、Scheduler、Graphiti、Nanobot 各自位置。
2. 数据流：语音/视频/拍照/日程/Obsidian 如何变成 Observation、Ref、IntentWorkspace、L2-B、Graphiti。
3. 三个流程例子：拍照、语音跳舞、改日程 Task。
4. 触发器协议：解释主动提醒和 Graphiti 预加载不是散乱功能。
5. 创新点：多源 Ref 准入 + UUID、SVA Processor 到 DSG 记忆处理器、ECP/ACK 状态一致性、Reflex/Intent/Task 三层行为、Graphiti 长期图记忆接入。
6. 不足和后续：视觉/空间感知稳定性、Graphiti 记忆治理、外部模块生态。

## 4. 建议顺序

最可读的顺序是：

1. 先讲为什么需要场景 Agent。
2. 再讲场景 Agent 需要哪些输入。
3. 再讲总体架构，各模块站位。
4. 先用 LiveKit/ECP/SVA 讲实时交互底座。
5. 再进入 DSG/Graphiti 记忆层。
6. 用拍照流程把多源 Ref 讲实。
7. 用触发器协议讲主动行为和可扩展性。
8. 用改日程 Task 讲 Scheduler / Blackboard / nanobot 后台协作。
9. Demo 与总结。

这个顺序的好处：

- 老师先知道“为什么需要这些东西”，再听技术名词。
- SVA 不在开头硬讲，而是在 LiveKit/Processor 段落解释，后面自然过渡到 DSG 记忆处理器。
- 触发器放在记忆层后面，因为 TriggerOutcome 会用到 Observation、StagedRef、Plan、Archive 等概念。
- nanobot 放在行为调度段落，避免与 LiveKit 模块挂载、主动提醒混淆。

## 5. 仍需后续决策

1. Graphiti 预加载当前展示到什么程度：作为“已贯通的查询/预加载链路”，还是只作为设计与原型链路。
2. PPT 是否单独给 Obsidian / Graphiti / nanobot 做“术语解释卡”，还是融入架构图旁边的小注释。
3. Demo 里是否真的展示改日程 Task。如果不展示，也可以只在演讲中作为架构例子。
4. 是否需要补官方定义来源：LiveKit、Obsidian、nanobot、Graphiti。后续进入 PPT/演讲稿时建议补一轮官方仓库/官网资料。
