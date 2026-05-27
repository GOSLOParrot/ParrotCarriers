# 调研：1:30-2:30 场景 Agent 需要哪些输入

## 目标

这一分钟不是介绍全部技术栈，而是给老师补齐理解后续架构设计所需的背景知识。

需要让老师快速知道：

1. 这些输入源分别是什么。
2. 它们为什么和“场景 Agent”有关。
3. 它们后面会如何进入统一架构：LiveKit 通道、日程 / 笔记 / 任务、SVA/CV 处理器，最后变成 Observation、Ref、Task、Episode。

## 推荐讲述策略

### PPT 负责“识别”

PPT 上用官方图片和极短标签：

| 卡片 | 标签 |
| --- | --- |
| LiveKit / SVA | 实时音视频 + 视觉 Agent |
| nanobot | 后台任务 Agent |
| Google Calendar | 时间上下文 / 日程 |
| Obsidian | 本地笔记 / 日记 |
| YOLO / SAM2 / DINOv2 / ConceptGraph | CV 扩展输入 |

不要在 PPT 上堆定义。每个卡片 1 张图 + 1 行字即可。

### 演讲稿负责“连接”

演讲稿用下面这种口径：

> 为了让 AR 助手理解场景，它不能只听一句话。它需要实时音视频作为感知入口，需要 Google Calendar 提供时间上下文，需要 Obsidian 提供用户长期笔记和日记，需要 nanobot 这类后台 Agent 执行慢任务，也需要 SVA / CV Processor 把视频流转成结构化结果。后面的架构设计，就是解决这些输入如何被统一成可追踪的 Observation、Ref、Task 和 Episode。

这段应控制在 45 到 60 秒，避免开始讲细节。

## 调研结果

| 对象 | 官方依据 | 对大纲的用法 |
| --- | --- | --- |
| LiveKit | 官方 README 说明它面向开发者提供实时 video、audio、data；官方文档把 Room、Participant、Track 列为基础概念，并说明 data API 可用于文本、文件、RPC、Data tracks、状态同步。 | 用来解释系统为什么有实时音视频、RPC、DataChannel 这类通道。 |
| Google Calendar | Google Workspace Calendar 页面提供官方产品界面图，强调 online calendar、事件、任务、共享日历、Meet 协作、Gmail 事件同步等能力。 | 用来解释“时间上下文”和智能提醒来源。 |
| Obsidian | Obsidian 官网和帮助页可作为官方来源；适合用界面图解释本地笔记、日记、链接和图谱。 | 用来解释用户长期可编辑知识库，不要让老师误以为只是普通文档。 |
| nanobot | HKUDS/nanobot GitHub README 说明它是 lightweight open-source AI agent，支持 chat channels、memory、MCP 和 deployment paths。 | 用来解释后台 Worker / 多步骤任务执行模式；同时明确不把它当 LiveKit 前台挂载模块。 |
| Vision Agents / SVA | GetStream/Vision-Agents README 说明它用于构建能 watch/listen/understand video 的多模态 Agent，并把 YOLO / Roboflow 与 Gemini/OpenAI 等实时结合。 | 用来解释 SVA Processor 思路：视频可以被受控采样、检测、结构化，再注入 LLM 或 DSG。 |

## 推荐 PPT 画法

### 方案 A：五页大图版（当前推荐）

用户补充要求：字要大、图要大、只留下背景印象；后面核心设计第一点再讲明白。因此这一段可以拆成 5 张背景知识页，而不是硬塞成一页小字拼盘。

风格补充：这些截图不能当花背景用。PPT 应使用白底、深色字、正常高级的无衬线字体；截图作为页面中的证据图或产品图嵌入，旁边配一句大字说明即可。整体要素一点、普通一点，不做黑底网页风格延展。

| 页 | 标题 | 使用图片 | 大字说明 | 演讲稿作用 |
| --- | --- | --- | --- | --- |
| 1 | 视频流：实时音视频和视觉 Agent | 用户提供的 LiveKit GitHub 截图 + VisionAgents GitHub 截图 | `LiveKit：实时音视频 / 数据通道`；`VisionAgents：让 Agent 看、听、理解视频` | 让老师先知道“视频流”和“视觉处理器”是什么，后面再讲 SVA 与 Context 注入。 |
| 2 | nanobot：后台任务 Agent | 用户提供或后续补充的 HKUDS/nanobot 官方仓库 README 截图 | `nanobot：后台任务执行 / 多步骤协作` | 引出后面 Task、Scheduler、Redis、nanobot Worker，不把 nanobot 讲成 LiveKit 前台挂载模块。 |
| 3 | Google Calendar：时间上下文 | 用户提供的 Google Calendar 周视图截图 | `Google Calendar：日程 / 提醒 / 时间上下文` | 让老师理解日程是智能提醒和后台任务的真实数据来源。 |
| 4 | Obsidian：本地知识库和日记 | 用户提供的 Obsidian 官网截图；后续可补项目自己的日记截图 | `Obsidian：本地 Markdown 笔记 / 日记 / 知识链接` | 让老师理解 Obsidian 不是普通文档，而是用户可编辑的长期知识来源。 |
| 5 | CV 扩展输入：从画面到对象 | SAM2 官方图 / DINOv2 官方图 / ConceptGraphs 项目图三选一或组合成简图 | `SAM2：分割图像和视频中的对象`；`DINOv2：提取稳健视觉特征`；`ConceptGraph：把对象组织成场景图` | 留下“CV 不只是看图，而是把画面变成对象、特征和关系”的印象。 |

这五页每页都应该是“大图 + 大字”，每页只讲 10 到 15 秒。不要放密集表格，不要放完整定义。

版式优先级：

1. 白底 + 深色标题。
2. 截图放在页面主体区域，不铺满背景。
3. 每页只写 1 句主说明。
4. 图片如果太花，就缩成卡片，让页面背景保持干净。

### CV 页选型判断

| 选项 | 是否建议做主图 | 理由 |
| --- | --- | --- |
| SAM2 + DINOv2 + ConceptGraph | 推荐 | 最贴合“场景 Agent”：SAM2 表示对象分割，DINOv2 表示视觉特征，ConceptGraph 表示对象/关系组织。注意讲成“能力方向 / 背景知识”，不要讲成项目已经完整采用这条流水线。 |
| 直接用 SAM2 | 可用 | 最直观，老师容易理解“把物体从画面里分出来”。缺点是只说明分割，不说明对象关系和长期记忆。 |
| 直接用 YOLO | 备用 | 最容易解释“实时检测”，而且 VisionAgents 截图里已经出现 YOLOPoseProcessor；但 YOLO 更像检测器示例，不如 ConceptGraph 贴近 DSG/场景图主线。 |
| 只用 ConceptGraph | 谨慎 | 影响力和相关性强，但概念较复杂；如果没有 SAM2/DINOv2 或检测/分割铺垫，老师可能不容易一眼理解。 |

当前建议：CV 页主标题用 `CV 扩展输入：从画面到对象和关系`。画法采用 `SAM2 分割对象 -> DINOv2 提取视觉特征 -> ConceptGraph 组织场景图`。如果图太复杂，就只放 SAM2 大图，并用右下角小标签写 `后续可进入 ConceptGraph / DSG`。

### 方案 B：一页完成（压缩备用）

标题：`场景 Agent 需要认识哪些输入？`

布局：

```text
LiveKit        Google Calendar       Obsidian
实时通道        时间上下文             笔记/日记

nanobot        SVA / CV Processor     YOLO/SAM2/ConceptGraph
后台任务        视频结构化处理          CV 扩展输入
```

页脚一句：

```text
这些不是零散工具，而是后续架构里的 Observation / Ref / Task / Episode 来源。
```

优点：节奏快，适合 1 分钟。缺点：你现在要求图和字都要大，这个方案不如五页大图版。

### 方案 C：两页折中

第 1 页：`输入源是什么`

- 五张官方图卡片。
- 只解释名词。

第 2 页：`输入如何进入架构`

```text
LiveKit 音视频 / Data / RPC
Google Calendar 日程
Obsidian 笔记/日记
nanobot 后台任务
SVA / CV Processor 结构化结果
        ↓
Observation / Ref / Task / Episode
        ↓
DSG 工作记忆 + Graphiti 长期记忆
```

优点：老师更容易理解后续架构图。缺点：占用约 1 分钟以上。

## 结论

当前阶段建议先采用方案 A，并准备方案 B 的第二页作为备用。如果后续发现老师对技术背景不熟，就用两页；如果答辩时间被压缩，就只放一页输入源卡片。
