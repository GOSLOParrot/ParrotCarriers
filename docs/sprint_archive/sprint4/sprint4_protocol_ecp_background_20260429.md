# Sprint 4 Protocol / ECP 背景锚点

> 日期：2026-04-29  
> 状态：背景锚点  
> 用途：保留 Sprint4 协议升级、数据流设计、DSG/Graphiti/Obsidian 边界、BT/行为树路线的当前共识。后续正式协议稿应从本文出发，而不是从测试束或零散聊天重新推导。

## 1. 当前阶段判断

Sprint3 真机 smoke 已完成，结果已提炼到 `docs/test/p2_5/sprint3_effective_lessons_for_sprint4_zh.md`。后续不再继续堆 Runtime HUD / SelfTest / Dev.unity 测试束；这些只能作为测试留档和事故经验。

Sprint4 的当前目标是：

- 统一数据流连接健壮性设计：LiveKit / Unity AR Foundation / 前后台 / 重连 / 音频设备切换 / 外放回声风险。
- 完成协议 V2 / ECP 设计：从纯 RPC 升级到目标驱动、状态同步、可过期命令、前端状态机回执。
- 明确 DSG L2-B / Graphiti / Obsidian / Ref 的最小接口与写入边界。
- 再用四个 App 工具验证协议能力：核心对话与飞手指、按需发现物体、Focus / Bounding Box、照相机功能。

AR App 初版 App Flow / UI 以 `docs/sprint4_research/result/03_App_Flow_and_UI_Layout_Design.md` 为当前基线：个人自用 Demo，2D 像素 Meta UI，HUD 与工具柜对角线布局，工具柜包含设置、相机模式、2D 工作区、Focus 放大镜 / Bounding Box 等道具入口。

## 2. 用户关键原话摘录

以下原话用于防止后续设计跑偏。不是完整聊天记录，只保留会影响架构判断的句子。

> 我已经完成了真机测试，测试结果也已提炼为有用信息，具体后续要在 Sprint4 的完善阶段同步完善 AR 工作区升级。

> AR app 设计作为初期设计已经足够，为验证升级协议能力，我们需要分阶段完成约四个工具：核心功能，对话、简单指令库（比如我比一个手势）、和飞到手指；按需发现物体升级；注意力集中，Focus 放大镜和 bounding box 道具的后端接口设计；照相机功能。

> 数据流设计的三个内容中，视频流有大致设计，但需要完成保持连接健壮性的策略设计、音频接入设备切换设计等。

> ECP 的设计就是我们要完成的，我不知道能学什么项目啊，需要找一个足够和我们架构、使用场景也贴合，LiveKit 能力贴合的。

> Obsidian 只作为人类补充的，通过 UUID（我也不确定，但我先用一对一，一对多 Ref，可以以后再找找 Obsidian 自己的相关能力）绑定到 graphiti 的主要以用户自己来维护和驱动的物体信息补充，即 Ref 文件之一。

> 也可能有其他 Ref 资料，比如给一个 Episode 或 Node Ref 一个日记，或 Ref 几张照片。

> DSG / DSG L2-B / L3 是工作记忆，对应人脑的潜意识的内容，不一定要把所有内容完整地填充到 DSG 中。

> DSG 一定有的功能是一个根据场景和情景生成的一个巨大的潜意识索引（当然有包括一些细节内容），相当于操作系统中的内存。Node 有自己的生命周期。相当于设计操作系统。

> graphiti 相当于能被检索并（几乎直接填充）进到 DSG 的依赖源/信息源之一，因为设计要求需要 DSG Node 尽量对 graphiti 的 Node 有适配，所以我希望 graphiti Node 的 UUID 绑定和填充是效率高的、优化的。

> 至于 Ref 设计，我知道目前 graphiti 有相关的能力吧。（你应该理解，意思是有 UUID 作为 Node 绑定设计，但 Ref 不一定使用 UUID！！）

> 找到数据流连接健壮性设计 / Unity AR Foundation LiveKit 的各个能力；ECP 设计怎么升级目前状态机同步架构；DSG L2-B 检索得到重要的 graphiti 内容 / Ref 文件或内容并填充到或绑定到 Node 上。三个任务的交集和完成需求的先决条件。

> 对和我们的任务调度器目前设计、鹦鹉行为、Reflex / Intent / Task 三层设计、BT 行为树，和后面扩展成不同状态用不同的独立行为树的 BT 森林，路线有什么关系影响和冲突吗？还是说这就是计划里的一部分，我希望任务里有我的这条路线做对比。

## 3. 当前理解与固定口径

### 3.1 ECP 不是替代 Scheduler / BT

ECP 是 Brain / Scheduler 到 Unity 前端执行层的协议出口，负责目标命令、状态同步、过期、取消、回执和失败原因。

Scheduler、Reflex / Intent / Task、BT Router、未来 BT 森林负责决策与仲裁：

- 谁有权发命令。
- 事件属于哪个时间尺度。
- 是否需要 Gemini 等待。
- 多个行为意图冲突时谁赢。
- 何时把失败升级给 Gemini。

Unity 前端状态机负责本地执行：

- 根据身体 / 头部 / 认知状态兼容矩阵决定 accepted / queued / rejected。
- 处理 micro-lock、动画过渡、过期丢弃。
- 把真实执行结果通过 ECP ack 回灌。

因此，ECP、BT、Unity 状态机是三段链路，不是竞争架构。

## 4. 三层调度与 ECP 的关系

现有调度层定义见 `.cursor/memory/parrot_behavior_rules.md` 和 `src/parrot/scheduler/router.py`。

| 层 | 时间尺度 | 典型事件 | ECP 关系 |
|:--|:--|:--|:--|
| Reflex | ms-s | 手势飞到手指、紧急停止、手消失飞回 | 可直接生成低延迟 ECP goal；不等 Gemini，但必须 ack 回灌身体状态 |
| Intent | s-min | `fly_to`、`animate`、`set_video_tier`、`identify_object`、`focus_region` | 用户 / Gemini 主动触发时必须同步等 applied / rejected / expired；后台自主调节可静默 |
| Task | min+ | Nanobot research、长文档处理、记忆整理 | 不应伪装成已完成的身体 / 感知行为，只返回 task id 或后续结果 |

ECP 的核心约束来自 `parrot_behavior_rules.md` 的 tool 体感红线：

> tool 的同步/异步行为必须和 GOSLO 说出口的话一致。

也就是说：

- GOSLO 自身行为：必须在本轮 tool 返回中得到结果。
- 异步委派任务：必须明说“我派出去了，稍后告诉你”。
- 不允许 fire-and-forget 后却说“我已经完成”。

## 5. BT 森林路线

当前 `src/parrot/scheduler/router.py` 是浅层 Selector：

```text
HandleReflex -> HandleIntent -> DispatchToNanobot -> HandleBrainDirect
```

Sprint4 不需要立刻实现完整 BT 森林，但协议必须允许它自然扩展。

推荐路线：

1. Sprint4：单棵浅层 Router + 少量 Reflex / Intent 子树。
2. 后续：按状态或功能拆子树，例如 `HandPerchTree`、`DesktopIdleTree`、`ConversationTree`、`CameraModeTree`、`FocusToolTree`。
3. 更远期：按 `Scene` / `BehaviorMode` / `VisualState` / `BodyState` 选择不同 BT forest root。
4. 所有树最终输出统一 `EcpCommand`，由 Arbiter 生成唯一前端目标。

这样做可以让后端行为复杂度增长，但 Unity 只需要理解稳定 ECP 合同。

## 6. DSG / Graphiti / Obsidian / Ref 边界

### DSG L2-B / L3

DSG L2-B / L3 是场景工作记忆、注意力、潜意识工作区和巨大潜意识索引。它像操作系统内存，不要求完整持久化全部细节。

Node 有生命周期：被预加载、被观察、被确认、被遗忘、被归档。实时循环应先进入 L2-B / ObsLog / EventEnvelope，而不是直接写 Graphiti。

### Graphiti

Graphiti 是长期时间图和可检索信息源。它可以被高效检索并预加载到 DSG L2-B，也可以接收 EpisodeArchiver / MemoryWriter 从工作记忆投影出的摘要。

Graphiti node UUID 是和 DSG Node 适配的关键锚点之一。目标是让 Graphiti 内容能尽量高效填充或绑定到 L2-B Node，而不是每次靠自由文本重新匹配。

### Obsidian

Obsidian 是人类维护的 Ref / SSOT，不是实时自动写入目标。

Obsidian 可作为 Graphiti Node、DSG Node、Episode、Snapshot、Photo 的 Ref 资料来源。Ref 不一定使用 UUID，但绑定关系必须稳定可追踪。

### RefBinding 最小理解

RefBinding 是“资料引用关系”，不是事实本身。它可绑定：

- Graphiti node。
- L2-B node。
- Episode。
- Snapshot / Photo。
- Obsidian file / block / frontmatter。
- 外部 URI。
- 日记或人工注释。

Ref 可以是路径、URI、frontmatter id、block id、用户手动命名锚点。不要强行要求所有 Ref 都 UUID 化。

## 7. 三条任务的交集

三条任务：

1. 数据流连接健壮性。
2. ECP 状态机同步升级。
3. DSG L2-B 从 Graphiti / Ref 中检索、填充、绑定重要内容。

它们的交集是统一事件与状态面：

- `EventEnvelope` 记录因果。
- `Blackboard` 保存当前状态。
- `EcpCommand` / `EcpAck` 表达目标与执行结果。
- `SnapshotEvent` / `SightingEvent` 表达感知证据。
- `Observation` / `IngestRunner` 进入 L2-B。
- `RefBinding` 连接长期图、工作记忆和人工资料。

如果没有这层统一面，四个 App 工具会各自发明接口，最终协议污染。

## 8. 四个 Sprint4 验证工具顺序

### 8.1 核心功能：对话、简单指令库、飞到手指

验证：

- Line A Gemini Live 对话继续可用。
- 手势 / DataChannel / Reflex 能触发 `perch_to_finger`。
- ECP 能表达目标命令、过期、拒绝、完成。
- Unity 前端状态机能回执真实身体状态。

### 8.2 按需发现物体升级

依据 `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`。

验证：

- `captureSnapshot` 能产生可追溯证据。
- `SnapshotEvent` / `SightingEvent` 能关联 turn、node、ref。
- `identify_object` 保持同步体感闭环。
- L2-B 快速候选 + Graphiti 扩搜 + reference image 绑定可行。

### 8.3 Focus 放大镜 / Bounding Box

验证：

- 用户拖拽 / 放置的注意力区域能进入后端。
- 它应作为 `AttentionHint` / `SightingEvent`，提升候选权重。
- 它不应直接把物体写成 CONFIRMED。
- 拖动过程走 lossy DataChannel，松手确认走 reliable / RPC。

### 8.4 照相机功能

验证：

- 用户照片与认知层 snapshot 分流。
- 用户照片可作为 Ref 资料绑定到 PhotoEvent / Episode / Node。
- 不把所有照片默认当作场景事实写入 Graphiti。

## 9. 外部参考取舍

不要继续寻找一个可照抄的项目。ParrotCarriers 的 ECP 更适合组合以下机制：

- LiveKit RPC：可靠 request/response，用于 `send_goal` / `captureSnapshot` / `setVideoTier`。
- LiveKit DataChannel：lossy 用于手势 / pose / bounding box 拖动，reliable 用于小型状态同步。
- ROS Action 语义：goal / accepted / feedback / result / cancel / preempt，作为目标驱动控制的概念参考。
- Unity / 游戏状态机：本地自治、micro-lock、过期丢弃、动画过渡、状态回执。
- py-trees BT：后端策略选择、guard、selector、subtree / forest 扩展。

## 10. 不允许误读

- 不要从 `Dev.unity`、Runtime HUD、自检按钮、WebCam fallback 反推正式 App 启动流程。
- 不要把 ECP 理解成“更复杂 RPC 名字表”。
- 不要让 Graphiti 接收实时帧循环。
- 不要把 Obsidian 当自动写入数据库；它是人类维护的 Ref/SSOT。
- 不要让 BT 森林直接暴露给 Unity；Unity 只看 ECP。
- 不要让 Gemini 看到内部 BT 节点名或调度细节；它只需要知道当前状态、失败原因和必要上下文。
- 不要让 `identify_object` 回到“火即忘 + 承诺话术”的错误组合。

