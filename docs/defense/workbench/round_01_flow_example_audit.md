# 第1轮审查产物：流程例子可讲性核查

## 核查结论

当前建议采用“三个主流程 + 一个核心协议组”的组合：

1. 主例子：相机模式拍照后流程。
2. 主例子：语音指令触发 RPC 跳舞。
3. 主例子：GOSLO 派发“改日程”任务给 nanobot 的后台 Task 流程。
4. 核心协议组：触发器协议，以及它如何支撑 Photo Awareness、Graphiti 回灌、主动提醒等不同触发场景。

这样安排的原因是：前三个例子分别覆盖 AR输入、前台动作闭环、后台协作任务；触发器不应被压缩成“Graphiti预加载”一个例子，而应作为核心设计来讲，重点说明系统可以按事件、周期、启动、按需等方式扩展新触发器。

## 例子 1：相机模式拍照后流程

| 判断项 | 结论 |
| --- | --- |
| 是否适合主讲 | 适合 |
| 讲述定位 | 用一个拍照动作解释多源输入如何进入记忆层 |
| 适合演讲稿 | 适合，作为第一个完整数据流例子 |
| 适合PPT | 非常适合，画成“快门 → 预览事件 → 图片上传 → PhotoNode → Ref绑定”的数据流 |
| 需要谨慎 | 不要说拍照会自动生成确认的ObjectNode；代码里明确 PhotoNode 和 ObjectNode 分开 |

代码依据：

- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/FormalCameraModeController.cs:170`：相机模式下 `CapturePhotoFromCameraMode()`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/UI/FormalCameraModeController.cs:182`：调用 `homeToolController.CapturePhoto()`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Photo/PhotoController.cs:19`：发布 `photo.taken_preview`。
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Photo/PhotoController.cs:587`：HTTP上传时带 preview event id。
- `src/parrot/brain/observer/photo.py:15`：预览事件走 `photo.taken_preview`。
- `src/parrot/brain/observer/photo.py:21`：Brain把预览 upsert 成 L2-B 的 PhotoNode。
- `src/parrot/brain/observer/photo.py:27`：上传完成后发布 `photo.asset_uploaded`。
- `src/parrot/brain/observer/photo.py:356`：照片路径 stage 到 IntentWorkspace。
- `src/parrot/brain/observer/photo.py:377`：照片路径绑定到 L1.5 RefTable 的 `PHOTO_PATH`。

建议讲法：

> 这个例子说明，AR里一次看似简单的拍照，并不是直接把图片塞给大模型，而是拆成轻量预览事件和完整图片资产两条通道。预览先让系统知道“发生了一次拍照”，完整图片再异步上传，最后进入PhotoNode、IntentWorkspace和RefTable，成为后续可追踪的证据来源。

## 例子 2：语音指令触发 RPC 跳舞

| 判断项 | 结论 |
| --- | --- |
| 是否适合主讲 | 适合 |
| 讲述定位 | 用最直观的前台动作解释 Intent、LiveKit RPC、ECP ACK 和 Blackboard |
| 适合演讲稿 | 适合，容易让老师理解前后端同步 |
| 适合PPT | 适合，画成“语音意图 → 工具 → RPC → Unity动画 → ACK → 黑板状态” |
| 需要谨慎 | 不要讲成所有状态都有完整 EcpAck；当前 `tick/last_ecp_ack` 仍是 legacy ack dict 镜像 |

代码依据：

- `src/parrot/brain/tools/animate.py:133`：`play_dance()` 工具。
- `src/parrot/brain/tools/animate.py:68`：命令类型为 `EcpCommandKind.ANIMATE`。
- `src/parrot/brain/tools/animate.py:78`：通过 `call_unity_rpc(method="animate")` 下发。
- `src/parrot/brain/tools/_rpc_bridge.py:84`：RPC结果镜像到 Blackboard。
- `src/parrot/brain/tools/_rpc_bridge.py:108`：写入 `tick/last_rpc_ack`。
- `src/parrot/brain/tools/_rpc_bridge.py:110`：有ECP状态时写入 `tick/last_ecp_ack`。
- `src/parrot/brain/tools/_rpc_bridge.py:270`：无论成功失败都把结果写入状态面。

建议讲法：

> 当用户说“跳个舞”时，系统不是只在后端说一句“已执行”，而是把它变成一个前台意图动作。Brain调用跳舞工具，经LiveKit RPC下发到Unity，Unity执行后返回ACK，后端再把结果写入Blackboard。这样语言反馈、角色动作和系统状态能对齐。

## 例子 3：GOSLO 派发“改日程”任务给 nanobot 的后台 Task 流程

| 判断项 | 结论 |
| --- | --- |
| 是否适合主讲 | 适合 |
| 讲述定位 | 解释 Task 和 Intent 的差异，顺便引出 Scheduler、行为树、Redis、nanobot 协作 |
| 适合演讲稿 | 适合，但要用一个具体任务讲，不要抽象讲一堆队列 |
| 适合PPT | 非常适合，画成“Brain → Scheduler → BT Router → Redis Stream → Nanobot Worker → Result” |
| 推荐具体任务 | GOSLO 给 nanobot 一个改日程任务，例如把某个日程改到另一个时间 |
| 需要谨慎 | nanobot 后台 Worker 不作为 LiveKit 挂载模块挂载来讲；这里走 Scheduler / Redis 任务链 |
| 需要区分 | `calendar_change_request` 是前台 Intent / Plan草稿；真正执行 `calendar_patch` / `calendar_create` / `calendar_delete` 才是后台 Task |

代码依据：

- `src/parrot/brain/tools/calendar_change_request.py:25`：`calendar_change_request` 工具。
- `src/parrot/brain/tools/calendar_change_request.py:38`：生成 Google Calendar 变更决策草稿。
- `src/parrot/brain/tools/calendar_change_request.py:50`：该工具只 stage 草稿，不直接写 Calendar / Graphiti。
- `src/parrot/brain/tools/calendar_change_request.py:53`：审批后可转成 `calendar_create`、`calendar_patch` 或 `calendar_delete`。
- `src/parrot/brain/tools/calendar_change_request.py:135`：草稿里保存 `suggested_nanobot_task_type`。
- `src/parrot/brain/tools/dispatch_task.py:47`：发布到 `CH_SCHEDULER_COMMANDS`。
- `src/parrot/brain/tools/dispatch_task.py:87`：`calendar_fetch` / `calendar_create` / `calendar_patch` / `calendar_delete` 使用 Nanobot Google Workspace MCP。
- `src/parrot/scheduler/router.py:6`：行为树优先级从 Reflex 到 Intent 到 Nanobot。
- `src/parrot/scheduler/router.py:45`：树节点顺序包含 `HandleReflex`、`HandleIntent`、`DispatchToNanobot`。
- `src/parrot/scheduler/nodes.py:24`：`DispatchToNanobot` 节点。
- `src/parrot/scheduler/task_catalog.py:29`：`NANOBOT_TASK_TYPES`。
- `src/parrot/scheduler/service.py:121`：写入 `STREAM_NANOBOT_DISPATCH`。
- `src/parrot/bus/nanobot_consumer.py:136`：Nanobot结果发布到 `CH_NANOBOT_RESULTS`。

建议讲法：

> 这里我不用“提醒”来举 nanobot 的例子，因为提醒本身也会出现在触发器里，容易混淆。我用“改日程”来说明 Task：用户先表达意图，GOSLO生成一个日程变更草稿并等待确认；确认后，真正改 Google Calendar 的动作不阻塞前台对话，而是作为 `calendar_patch` 这类后台任务交给 Scheduler，再派发给 nanobot Worker 执行。

## 例子 4：触发器协议，而不是单个触发器例子

| 判断项 | 结论 |
| --- | --- |
| 是否适合主讲 | 适合，但应作为核心设计讲，不是只讲一个Graphiti例子 |
| 讲述定位 | 说明系统如何把不同事件变成可扩展的后台/半后台处理协议 |
| 适合演讲稿 | 适合，用“触发器可以干什么”来连接主动提醒、相机Aware、Graphiti回灌 |
| 适合PPT | 非常适合，画成 TriggerKind → TriggerOutcome → 多种后续动作 |
| 需要谨慎 | Photo Awareness 在代码中是照片预览事件后的策略桥，不是普通 RPC；Graphiti预加载也不是用户前台动作 |

代码依据：

- `src/parrot/dsg/triggers/base.py:36`：`TriggerKind`，触发器类型。
- `src/parrot/dsg/triggers/base.py:44`：`TriggerOutcome`，触发器统一输出。
- `src/parrot/dsg/triggers/base.py:71`：触发器可以提交 Observation。
- `src/parrot/dsg/triggers/base.py:72`：触发器可以执行 bucket 操作。
- `src/parrot/dsg/triggers/base.py:73`：触发器可以发起 archive request。
- `src/parrot/dsg/triggers/base.py:74`：触发器可以 stage refs。
- `src/parrot/dsg/triggers/base.py:75`：触发器可以生成 plan request。
- `src/parrot/dsg/triggers/runner.py:155`：TriggerRunner 统一处理 TriggerOutcome。
- `src/parrot/dsg/triggers/runner.py:159`：处理顺序包括 bucket、Observation、StagedRef、Archive、Plan、Nanobot、通知。
- `src/parrot/brain/photo_awareness.py:1`：Photo Awareness 是相机预览后的策略与 preview-ref bridge。
- `src/parrot/brain/photo_awareness.py:49`：Photo Awareness 有 `UNAWARE_RECORDED`、`AWARE_SILENT`、`AWARE_REACT`。
- `src/parrot/brain/observer/photo.py:462`：照片预览后调用 Photo Awareness。
- `src/parrot/dsg/l2b_graph.py:373`：`preload_from_graphiti()`。
- `src/parrot/dsg/l2b_graph.py:409`：预加载节点 salience 为 `BACKGROUND`。
- `src/parrot/dsg/triggers/scene_context_trigger.py:1`：Scene Context Trigger 查询相似历史场景。
- `src/parrot/dsg/triggers/ssot_enrichment_trigger.py:1`：SSOT Enrichment Trigger 从 Obsidian/Graphiti 补充对象信息。
- `src/parrot/brain/tools/query_memory.py:1`：Graphiti 自然语言记忆查询工具。

建议讲法：

> 触发器不是某一个固定功能，而是一套可扩展协议。它可以在启动、定时、事件发生或按需调用时运行，输出也不是只有“提醒用户”一种，而是可以提交Observation、暂存Ref、生成计划、请求归档、派发后台任务或者通知前台。相机模式里的Photo Awareness、Graphiti的自然语言搜索/预加载、以及主动提醒，都可以作为这套机制能做什么的例子。

### 触发器协议建议拆成三个小例子

| 小例子 | 适合讲什么 | PPT画法 |
| --- | --- | --- |
| 相机模式 Photo Awareness | 事件触发后，系统可以记录照片证据，并在安全时机让GOSLO意识到这张照片 | `photo preview → awareness policy → staged PHOTO ref / notice` |
| Graphiti自然语言搜索 / 预加载 | 长期记忆可以被搜索或回灌到当前L2-B工作记忆 | `Graphiti → BACKGROUND nodes → 当前上下文` |
| 主动提醒触发器 | 触发器可以根据消息、日程或场景状态决定是否提醒 | `TriggerOutcome → notify / plan / observation` |

## 黑板和任务调度器如何体现

建议只在两个地方体现，不单独拉一大段讲：

1. 在“语音跳舞”例子中讲 Blackboard：
   - 作用：保存前端动作执行结果和失败原因。
   - 讲法：`ACK不是只返回给工具，而是写入共享状态，让后续回复知道前端到底完成没有。`

2. 在“GOSLO派发改日程任务给nanobot”例子中讲 Scheduler：
   - 作用：判断任务是 Reflex、Intent、Nanobot Task，还是 Brain direct。
   - 讲法：`Scheduler像行为分派入口，行为树先看是否低延迟反射，再看是否前台意图，再看是否后台任务。`

## 第1轮待用户审查的问题

1. Nanobot 主例子已改为“GOSLO派发改日程任务给nanobot”，是否确认？
2. 触发器是否按“协议 + 三个小例子”来讲：Photo Awareness、Graphiti搜索/预加载、主动提醒？
3. 下一轮大纲里是否把“触发器协议”放在 DSG / Graphiti 之前，还是放在记忆层之后？
