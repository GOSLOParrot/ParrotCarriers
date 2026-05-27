# 核心设计 1/2/3 详细稿：7 分钟压缩版

> 用途：单独服务于压缩后的答辩 PPT。  
> 当前口径：前面的开场、背景、输入源不变；总体架构前先用两页讲 SVA Processor / Context 注入、LiveKit Room / Participants / Tracks 与模块接入。  
> 因此这里的“核心设计 1/2/3”不再重复讲 SVA 和 LiveKit 基础，而是集中讲三个能体现系统设计价值的机制。

## 0. 位置和总时间

总时长目标：7 分钟以内，其中 Demo 视频 1 分 30 秒。

核心设计放在总体架构之后、Demo 之前，建议总时长约 1 分 30 秒。

| 时间 | PPT | 内容 | 核心例子 |
| --- | --- | --- | --- |
| 3:50-4:25 | 核心设计 1 | ECP / RPC / ACK 前台动作闭环 | 语音指令让角色跳舞 |
| 4:25-5:00 | 核心设计 2 | Reflex / Intent / Task 与 nanobot 后台任务 | 改日程任务 |
| 5:00-5:22 | 核心设计 3 | DSG / Graphiti / Trigger / Ref / UUID 记忆证据链 | 拍照流程 |
| 5:22-5:30 | Demo 过渡 | 告诉老师视频中看什么 | 前台交互、主动提醒、后台状态、Obsidian |

如果现场能多给 30 秒，可以把核心设计 3 扩到 40 秒，因为 DSG、Graphiti、Trigger、Ref/UUID 都比较密。

## 1. 三个核心设计的主线判断

压缩以后，核心设计不要讲成“技术栈列表”，而要讲成三个回答：

1. 前台动作如何确认真的执行了？
   - 答案：ECP / RPC / ACK / Blackboard。
   - 例子：语音指令让角色跳舞。

2. 前台意图和后台慢任务如何分开？
   - 答案：Reflex / Intent / Task 分层，确认后的 Task 交给 Scheduler / Redis / nanobot。
   - 例子：改日程。

3. 场景信息如何留下来并被后续触发？
   - 答案：DSG 工作记忆、Graphiti 长期记忆、TriggerOutcome、多源 Ref / UUID。
   - 例子：拍照。

这三个设计连起来，老师能理解：

- 用户说了什么，不只是被模型回答，而是会变成 Intent。
- 前端做没做，不靠口头假设，而是要有 ACK。
- 慢任务不阻塞 AR 交互，而是升级为后台 Task。
- 场景信息不是临时看一眼，而是变成可追踪证据和记忆。

## 2. 核心设计 1：ECP / RPC / ACK 前台动作闭环

### 2.1 这一页解决什么问题

AR 助手的前台动作必须有状态回执。

后端说“我执行了”没有意义，真正重要的是 Unity 前端是否完成、拒绝或超时。ECP / RPC / ACK 解决的是模型意图、前端动作、后端状态之间的一致性。

### 2.2 PPT 标题和页面文案

标题：

```text
前台动作必须有状态回执
```

页面主文案：

```text
Intent：用户要做一个前台动作
RPC：后端把动作发给 Unity
ACK：Unity 回写完成、拒绝或超时
```

Takeaway：

```text
不是“模型说做了”，而是“前端确认做了”。
```

### 2.3 图怎么画

建议画一条横向流程线：

```text
用户语音
  -> Brain 识别 Intent
  -> LiveKit RPC
  -> Unity Action
  -> ACK
  -> Blackboard
  -> Brain 反馈用户
```

视觉重点：

- `Intent`、`RPC`、`ACK` 三个词加蓝色强调。
- `Blackboard` 放在流程末端，表示状态被写入共享状态面。
- 不要画很多通信细节，保留一条主线。

### 2.4 例子：语音指令让角色跳舞

例子定位：

- 用来解释前台 Intent。
- 用来解释 LiveKit RPC。
- 用来解释 ECP / ACK。
- 用来解释 Blackboard 为什么需要存在。

事件流程：

| 步骤 | 发生什么 | 讲法 |
| --- | --- | --- |
| 1 | 用户说“跳个舞” | 这是一个前台动作意图，不是后台任务。 |
| 2 | Brain 识别为 Intent | 系统知道用户希望 Unity 角色执行动作。 |
| 3 | Brain 调用动画工具 | 工具把动作包装成前台命令。 |
| 4 | 通过 LiveKit RPC 发给 Unity | RPC 用来触发前端动作。 |
| 5 | Unity 播放动画 | 真正执行发生在前端。 |
| 6 | Unity 返回 ACK | 告诉后端完成、拒绝或超时。 |
| 7 | ACK 写入 Blackboard | 后续回复能知道前端真实状态。 |

### 2.5 压缩演讲稿：约 35 秒

```text
第一个核心设计是前台动作闭环。

在 AR 系统里，后端不能只说“我已经执行了”。比如用户让助手跳舞，系统会先把语音识别成一个前台 Intent，再通过 LiveKit RPC 发给 Unity。Unity 真正执行动画以后，会返回 ACK，告诉后端这个动作是完成、拒绝还是超时。这个结果会写入 Blackboard，成为共享状态。

这样做的意义是，语言回复、前端动画和后端状态能对齐，避免模型说执行了，但前端其实没有完成。
```

### 2.6 详细解释稿：可用于答辩追问

```text
ECP 这部分主要解决状态一致性问题。因为 AR 前端和后端 Agent 是分开的，后端生成一个动作意图以后，不能默认 Unity 一定成功执行。LiveKit RPC 负责把动作发给 Unity，Unity 执行后返回 ACK。ACK 再进入 Blackboard，让后端和后续工具都能看到前端真实状态。

所以 ECP 不是单纯的通信协议，而是一种前台动作闭环。它让系统知道某个动作到底完成了、被拒绝了，还是超时了。
```

### 2.7 谨慎表述

不要说：

- “所有前台命令都已经完全统一为最终版 EcpAck。”
- “只要 Brain 调了工具，Unity 就一定执行成功。”

推荐说：

- “当前系统已经建立 RPC 结果到 Blackboard 的状态闭环。”
- “ACK 机制用于减少前后端状态漂移。”

### 2.8 内部依据，不在台上念

- `src/parrot/brain/tools/animate.py` 中 `play_dance()` 走动画工具。
- `src/parrot/brain/tools/animate.py` 将动作包装为 `EcpCommandKind.ANIMATE` 并通过 `call_unity_rpc(method="animate")` 下发。
- `src/parrot/brain/tools/_rpc_bridge.py` 将 RPC 成功、失败、超时等结果镜像到 `tick/last_rpc_ack`，并在 ECP 场景写入 `tick/last_ecp_ack`。
- 现有代码注释明确 `last_ecp_ack` 仍是 legacy ack dict 镜像，所以答辩里不要夸成所有 ACK 已完全统一。

## 3. 核心设计 2：Reflex / Intent / Task 与 nanobot 后台任务

### 3.1 这一页解决什么问题

系统不能把所有动作都交给同一个流程处理。

有些动作需要立即反应，有些动作需要前台回执，有些动作耗时长、依赖外部系统，应该交给后台执行。Reflex / Intent / Task 分层解决的是“动作应该在哪一层处理”的问题。

### 3.2 PPT 标题和页面文案

标题：

```text
前台意图和后台任务要分层
```

页面主文案：

```text
Reflex：本地快速反应
Intent：前台动作，需要 ACK
Task：后台慢任务，交给 Scheduler / Redis / nanobot
```

Takeaway：

```text
确认前是 Intent，确认后才升级为 Task。
```

### 3.3 图怎么画

建议用左侧三层阶梯 + 右侧任务链。

左侧：

```text
Reflex
本地快速反应

Intent
前台用户动作

Task
后台慢任务
```

右侧：

```text
Intent Draft
  -> Confirm
  -> Scheduler
  -> Redis Stream
  -> nanobot Worker / gateway
  -> Result
```

视觉重点：

- `Intent Draft -> Confirm -> Task` 是最重要的箭头。
- `nanobot` 放在后台任务侧，不画进 LiveKit Room 的前台参与者里。

### 3.4 例子：改日程任务

例子定位：

- 用来解释 Intent 和 Task 的区别。
- 用来解释 Scheduler / Redis / nanobot 的位置。
- 用来避免把 nanobot 讲成 LiveKit 前台模块。

事件流程：

| 步骤 | 发生什么 | 讲法 |
| --- | --- | --- |
| 1 | 用户说“把会议改到晚上” | 这是自然语言意图，不能马上执行。 |
| 2 | Brain 生成日程变更草稿 | 仍然是 Intent / Plan 草稿。 |
| 3 | 用户确认修改内容 | 确认是安全边界。 |
| 4 | 确认后升级为 Task | 例如 `calendar_patch`。 |
| 5 | Scheduler 接收任务 | 判断任务类型和派发路径。 |
| 6 | 写入 Redis Stream | 让后台 Worker 异步消费。 |
| 7 | nanobot Worker / gateway 执行 | 处理 Google Calendar 这类外部任务。 |
| 8 | 结果回流前台 | 用户看到任务执行结果。 |

### 3.5 压缩演讲稿：约 35 秒

```text
第二个核心设计是行为分层。

我把动作分成 Reflex、Intent 和 Task。Reflex 是本地快速反应；Intent 是前台用户动作，需要状态回执；Task 是耗时的后台任务。比如用户说“把会议改到晚上”，系统不会直接修改 Calendar，而是先生成日程变更草稿，让用户确认。确认以后，真正的修改请求才升级成 Task，通过 Scheduler 和 Redis 派发给 nanobot Worker 或 gateway。

这样前台 AR 交互不会被慢任务卡住，后台任务也有明确的执行边界。
```

### 3.6 详细解释稿：可用于答辩追问

```text
Reflex、Intent、Task 的区别主要是执行位置和风险不同。

Reflex 面向本地快速反应，比如低延迟状态变化。Intent 面向用户正在看见的前台动作，比如拍照、切换模式、角色动作，所以要有 ACK。Task 面向慢任务和外部任务，比如日程修改、资料整理、消息检查，这类任务不应该阻塞当前对话，而应该进入后台任务系统。

改日程这个例子里，calendar_change_request 更准确地说只是生成草稿和建议任务类型。真正执行 Calendar 修改，要等用户确认后，再派发成 calendar_patch 这类后台任务。
```

### 3.7 谨慎表述

不要说：

- “用户一说改日程，系统就直接修改 Google Calendar。”
- “calendar_change_request 会直接写 Calendar。”
- “nanobot 是 LiveKit Room 里的前台挂载模块。”
- “fallback NanobotConsumer 已经真实调用 Google Workspace MCP 修改日程。”

推荐说：

- “改日程先生成 Intent / Plan 草稿，确认后才升级为后台 Task。”
- “nanobot 在本系统主线里承担后台任务执行层。”
- “主链路是 Scheduler + Redis Stream + nanobot Worker / gateway。”

### 3.8 内部依据，不在台上念

- `src/parrot/brain/tools/calendar_change_request.py` 生成 Google Calendar 变更草稿，并保存建议的 nanobot task type。
- `calendar_change_request` 的代码注释明确：它 stage 草稿，不直接写 Calendar / Graphiti。
- `src/parrot/brain/tools/dispatch_task.py` 将任务发布到 `CH_SCHEDULER_COMMANDS`。
- `src/parrot/scheduler/router.py` 的行为树顺序包含 `HandleReflex`、`HandleIntent`、`DispatchToNanobot`。
- `src/parrot/scheduler/service.py` 将任务写入 `STREAM_NANOBOT_DISPATCH`。
- `src/parrot/bus/nanobot_consumer.py` 从 Redis Stream 读取任务，并将结果发布回 `CH_NANOBOT_RESULTS`。

## 4. 核心设计 3：DSG / Graphiti / Trigger / Ref / UUID 记忆证据链

### 4.1 这一页解决什么问题

AR 场景里的信息不能只是临时输入。

语音、视频、照片、日程、笔记和工具结果都需要有来源、有标识、可追踪，后续才能被检索、确认、归档或触发提醒。DSG / Graphiti / Trigger / Ref / UUID 解决的是“信息如何进入记忆并形成证据链”的问题。

### 4.2 PPT 标题和页面文案

标题：

```text
多源信息要变成可追踪证据
```

页面主文案：

```text
DSG：运行时工作记忆
Graphiti：长期图记忆
Trigger：把事件变成后续动作
Ref / UUID：绑定来源和证据
```

Takeaway：

```text
拍照不是直接得出结论，而是先形成可追踪证据。
```

### 4.3 图怎么画

建议这一页不要画太复杂。用“拍照证据链”做主图，旁边放三个小出口。

主图：

```text
按下快门
  -> photo.taken_preview
  -> 完整图片异步上传
  -> PhotoNode
  -> StagedRef PHOTO
  -> RefTable / UUID
```

右侧三个出口：

```text
进入 DSG 工作记忆
触发 TriggerOutcome
后续归档到 Graphiti
```

视觉重点：

- `Ref / UUID` 放在中间偏后的位置，作为证据绑定点。
- `TriggerOutcome` 画成一个分叉：Observation / Ref / Archive / Plan / Notify / Task。
- 不要把 Graphiti 画成已经治理完善的万能记忆库。

### 4.4 例子：相机模式按下快门

例子定位：

- 用来解释多源 Ref。
- 用来解释 UUID。
- 用来解释照片和 ObjectNode 的边界。
- 顺带连接 Trigger 和 Graphiti。

事件流程：

| 步骤 | 发生什么 | 讲法 |
| --- | --- | --- |
| 1 | 用户在相机模式按下快门 | 一次 AR 场景输入发生。 |
| 2 | 前端发布轻量预览事件 | 系统先知道“发生了拍照”。 |
| 3 | 完整图片异步上传 | 图片资产不阻塞前台。 |
| 4 | 后端创建或更新 PhotoNode | 记录照片节点，不等于确认对象。 |
| 5 | 暂存 PHOTO 类型 Ref | 照片成为可追踪证据。 |
| 6 | 绑定 RefTable / UUID | 后续可以检索、确认、归档。 |
| 7 | 触发器决定后续动作 | 可以记录 Observation、暂存 Ref、归档 Episode、生成计划、派发 Task 或通知前台。 |
| 8 | 必要时进入 Graphiti | 长期保存时要带来源和情景。 |

### 4.5 压缩演讲稿：约 22 秒

```text
第三个核心设计是记忆和证据链。

以拍照为例，按下快门后，系统不会直接把图片当成确定结论塞给模型，而是先产生预览事件，再异步上传完整图片。后端把它记录成 PhotoNode，并暂存为 PHOTO 类型 Ref，再用 UUID 绑定。后续触发器可以基于这个 Ref 去记录 Observation、归档 Episode、生成提醒，或者回灌到 Graphiti。
```

### 4.6 详细解释稿：可用于答辩追问

```text
DSG 在这里是运行时工作记忆，不只是地图。它接收当前会话里的语音、视觉、照片、日程、笔记和工具结果，把它们组织成 Observation 和 Ref。

Graphiti 负责更长期的图记忆，适合保存 Episode、Entity 和 Fact。Trigger 则是事件发生后的统一处理协议。它的输出不止提醒，也可以提交 Observation、暂存 Ref、请求归档、生成 Plan，或者派发后台 Task。

拍照流程能把这几个概念串起来：照片先成为 Ref 和 UUID 绑定的证据，后续再根据触发器和上下文决定是否识别、确认、归档或提醒。
```

### 4.7 谨慎表述

不要说：

- “拍照后系统会自动生成可靠 ObjectNode。”
- “照片一上传就成为长期记忆里的确定事实。”
- “Graphiti / Obsidian 的长期记忆治理已经完全解决。”
- “触发器就是提醒功能。”

推荐说：

- “照片先作为证据 Ref 进入系统，后续再识别、确认或归档。”
- “Graphiti / Obsidian 已建立原型链路和 UUID 绑定思路，长期治理仍是后续完善点。”
- “触发器是一套事件处理协议，可以产生 Observation、Ref、Archive、Plan、Notify 或 Task。”

### 4.8 内部依据，不在台上念

- `src/parrot/brain/observer/photo.py` 中注释明确了 `photo.taken_preview` 和 `photo.asset_uploaded` 的双通道。
- `photo.py` 明确 PhotoNode 是新的节点类型，和 ObjectNode 区分，不自动提升为确认对象。
- `src/parrot/brain/photo_awareness.py` 将照片预览事件和 awareness policy / staged photo ref 连接起来。
- `src/parrot/dsg/triggers/base.py` 定义 `TriggerKind` 和 `TriggerOutcome`。
- `src/parrot/dsg/triggers/runner.py` 统一处理 bucket、Observation、StagedRef、Archive、Plan、Nanobot、Notify 等结果。
- `src/parrot/dsg/l2b_graph.py` 支持从 Graphiti preload，也支持 episode archive。
- `src/parrot/memory/graphiti_client.py` 当前分区常量是 `GOSLO`、`MAID`、`SCENE`、`USER`，答辩里可以讲角色分区，不要把代码常量讲错。

## 5. 三页之间的转场

### 从总体架构页转到核心设计 1

```text
前面这张架构图说明了模块站位。接下来我不按代码模块讲，而是用三个流程说明这套架构真正解决了什么问题。
```

### 核心设计 1 转核心设计 2

```text
前台动作解决的是“看得见的动作是否完成”。但还有一些任务不是前台立刻完成的，比如改日程，所以需要第二个设计：行为分层。
```

### 核心设计 2 转核心设计 3

```text
前两页讲的是动作怎么执行。第三页讲的是信息怎么留下来，因为 AR 助手不只是做动作，还要记住场景证据。
```

### 核心设计 3 转 Demo

```text
所以视频里我希望老师重点看三件事：前台交互是否能闭环，主动提醒和后台任务是否分层，以及 Obsidian / 记忆结果是否能体现上下文回流。
```

## 6. 7 分钟现场版完整口播

下面这一段可以直接接在总体架构两页后面讲。

```text
接下来我用三个核心流程说明这套架构具体解决了什么问题。

第一个是前台动作闭环。在 AR 系统里，后端不能只说“我已经执行了”。比如用户让助手跳舞，系统会先把语音识别成一个前台 Intent，再通过 LiveKit RPC 发给 Unity。Unity 真正执行动画以后，会返回 ACK，告诉后端这个动作是完成、拒绝还是超时。这个结果会写入 Blackboard，成为共享状态。这样语言回复、前端动画和后端状态能对齐。

第二个是行为分层。我把动作分成 Reflex、Intent 和 Task。Reflex 是本地快速反应；Intent 是前台用户动作，需要状态回执；Task 是耗时的后台任务。比如用户说“把会议改到晚上”，系统不会直接修改 Calendar，而是先生成日程变更草稿，让用户确认。确认以后，真正的修改请求才升级成 Task，通过 Scheduler 和 Redis 派发给 nanobot Worker 或 gateway。这样前台交互不会被慢任务卡住。

第三个是记忆和证据链。以拍照为例，按下快门后，系统不会直接把图片当成确定结论塞给模型，而是先产生预览事件，再异步上传完整图片。后端把它记录成 PhotoNode，并暂存为 PHOTO 类型 Ref，再用 UUID 绑定。后续触发器可以基于这个 Ref 去记录 Observation、归档 Episode、生成提醒，或者回灌到 Graphiti。

所以接下来 Demo 里，我主要展示前台交互、主动提醒或邮件流程、后台状态，以及 Obsidian 日记或记忆结果。
```

## 7. PPT 页数建议

7 分钟版建议核心设计只占 3 页：

| 页 | 标题 | 主图 | 例子 |
| --- | --- | --- | --- |
| 核心设计 1 | 前台动作必须有状态回执 | Intent -> RPC -> Unity -> ACK -> Blackboard | 跳舞 |
| 核心设计 2 | 前台意图和后台任务要分层 | Reflex / Intent / Task + Scheduler / Redis / nanobot | 改日程 |
| 核心设计 3 | 多源信息要变成可追踪证据 | 快门 -> Preview -> PhotoNode -> Ref / UUID -> Trigger / Graphiti | 拍照 |

如果时间不足，可以把核心设计 3 和 Demo 过渡合并：

- 核心设计 3 只讲“拍照先成为 Ref，不是直接变成结论”。
- Graphiti / Trigger 只在图上出现，口头一句带过。

## 8. 可能的老师追问与回答

### 问：为什么需要 ACK？模型不是已经调用工具了吗？

答：

```text
因为工具调用成功不等于 Unity 前端执行成功。AR 前端可能拒绝、超时或者状态不一致，所以需要 ACK 回写，让后端知道动作真实结果。
```

### 问：nanobot 在系统里到底是什么位置？

答：

```text
在本项目主线里，nanobot 是后台任务执行层，不是 LiveKit Room 里的前台模块。前台由 Unity 和 Brain 通过 LiveKit 交互，确认后的慢任务再通过 Scheduler 和 Redis 交给 nanobot Worker 或 gateway。
```

### 问：改日程是不是直接改 Google Calendar？

答：

```text
不是直接改。自然语言阶段先生成 Intent / Plan 草稿，需要用户确认。确认后才升级成 calendar_patch 这类后台 Task，再由后台执行层处理。
```

### 问：拍照后系统是不是立刻识别出了物体？

答：

```text
不是。拍照后首先得到的是 PhotoNode 和 PHOTO Ref，表示一条可追踪证据。后续可以再识别、确认、归档，但不能把未确认照片直接讲成可靠 ObjectNode。
```

### 问：Graphiti 记忆是不是已经完全解决了？

答：

```text
当前可以说已经建立了 Graphiti 原型链路、分区和 UUID 绑定思路，但长期记忆治理仍然是后续完善方向。
```

## 9. 最终取舍

保留：

- ECP / RPC / ACK：最能体现 AR 前台交互不是空口承诺。
- Reflex / Intent / Task：最能体现前后台协作和 nanobot 位置。
- DSG / Graphiti / Trigger / Ref / UUID：最能体现项目不是普通聊天助手，而是场景 Agent。

压缩：

- SVA / LiveKit 基础知识放在总体架构前两页，不在核心设计里重复讲。
- Graphiti 细节不展开到 Entity / Fact / 分区常量，只讲“长期图记忆”和“Episode”。
- Trigger 不展开所有类型，只讲“事件后统一处理协议”。

删除或只在问答讲：

- 代码文件路径。
- 具体 Redis channel / stream 名称。
- 所有内部类名和枚举细节。
- CV 扩展 pipeline 的完整落地说法。
