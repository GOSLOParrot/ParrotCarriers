# 演讲稿大纲

> 当前只完成“大纲”这一份，不写完整演讲稿，不写 PPT 稿，不提前定死图稿。  
> 写法严格按原话要求：按“时间 / 内容 / 说什么”组织；保留技术名词，但重点讲清楚架构、数据流、核心设计和例子；不讲代码细节。

## 0. 时间口径

- PPT + 视频主体按 8 到 10 分钟准备，其中 Demo 视频控制在 2 分钟以内。
- 如果现场总时长按 15 到 20 分钟执行，主要拉长“核心设计”和“例子解释”部分，不新增无关技术栈列表。

## 1. 演讲主线总表

| 时间 | 内容 | 说什么 |
| --- | --- | --- |
| 0:00-0:40 | 开场：项目目标 | 先说明项目不是普通聊天助手，而是面向 AR 场景的生活助手与智能提醒系统。核心问题是让助手理解“我现在在哪里、看到了什么、正在做什么、什么信息值得提醒”。 |
| 0:40-1:30 | 背景：传统助手不足 | 传统助手多依赖文本、日程或单次对话，缺少真实场景输入、长期记忆和前后台协作。我们的目标是把“被动问答”变成“能理解场景并主动协助”的 Agent。 |
| 1:30-2:30 | 场景 Agent 需要哪些输入 | 按当前确认顺序讲输入源：LiveKit / SVA、nanobot、Google Calendar、Obsidian、YOLO / SAM2 / DINOv2 / ConceptGraph 等 CV 扩展。这里需要做成“老师能一眼看懂的输入来源介绍”，不是只念技术名词：每个输入源都要配官方简介和直观图片，再说明这些输入如何进入场景 Agent。 |
| 2:30-3:40 | 总体架构与技术栈位置 | 讲 Unity AR 前端、LiveKit 实时通信、Brain Agent、DSG 工作记忆、Graphiti 长期记忆、Scheduler、Redis、nanobot 后台 Worker 的位置关系。这里解释技术名词，但只解释到能理解架构为止。 |
| 3:40-7:40 | 核心设计 | 按原话的 4 个核心设计点展开：SVA 与 LLM 注入；ECP 同步、行为调度和前后台协作；Graphiti / DSG / Episode / 触发器；L1.5、多源 Ref、UUID 与外部模块挂载。例子要嵌入这里，不单独堆在最后。 |
| 7:40-9:20 | Demo 展示 | Demo 主要展示交互、邮件或主动提醒、一小段后台状态、Obsidian 日记或记忆相关结果。Demo 不讲代码，只把刚才的架构设计落到可见流程上。 |
| 9:20-10:00 | 总结：做到什么与创新点 | 总结我们做到的不是单个功能，而是 AR 多模态输入、实时动作闭环、长期记忆、触发器协议、后台任务协作串成了一条可追踪的数据流。最后点出后续仍可完善：视觉稳定性、记忆治理、更多外部模块。 |

## 1.1 需求注释：1:30-2:30 多源输入介绍

> 新增要求：这一段必须先让老师知道“这些外部输入源是什么”，再过渡到“为什么场景 Agent 需要它们”。PPT 上应使用官方来源的简介和图片，避免老师听到新名词时没有参照物。

| 输入源 / 技术 | 需要讲清楚什么 | PPT 图示需求 | 注意 |
| --- | --- | --- | --- |
| LiveKit / SVA | LiveKit 是实时音频、视频、数据通信底座；SVA / Processor 说明视频流不只是直接给模型看，也可以变成结构化事件或上下文注入。 | LiveKit 官方图 + Vision Agents / Processor pipeline 直观示意。 | 这里只做“它是什么”的入口，详细的 Room、RPC、数据通道放到后面的架构和 SVA/ECP 段落。 |
| nanobot | 它是轻量级开源 AI agent，可作为后台任务执行和多实例 agent 模式参考；本项目里不要说成 LiveKit 前台挂载模块。 | HKUDS/nanobot 官方 GitHub 仓库封面或 WebUI 预览图。 | 重点讲“后台 Worker / 任务执行模式”，不要把上游所有聊天平台能力都塞进本项目。 |
| Google Calendar | 它代表用户真实生活中的日程数据，是智能提醒和后台任务协作的重要外部数据源。 | Google Calendar 官方界面图：周视图、事件详情、任务或共享日历。 | 不讲成 Google 产品介绍，重点是“日程是场景 Agent 的时间上下文”。 |
| Obsidian | 它是本地笔记 / 日记 / Markdown 知识库，代表用户长期可编辑的个人知识来源。 | Obsidian 官方界面图，最好能选日记 / Daily notes / 笔记链接 / Graph 这类画面。 | Demo 里可以再展示我们自己的 Obsidian 日记；这里先用官方图让老师知道 Obsidian 是什么。 |
| YOLO / SAM2 / DINOv2 / ConceptGraph | 它们用来说明更多元的 CV 输入：检测、分割、视觉特征和对象关系组织。 | 官方项目图或自绘“画面 -> 对象 -> 特征 -> 场景图”简图。 | 讲成背景能力方向，不说项目已经完整实现整条 CV pipeline。 |

补充版式判断：如果一页里图片和文字太小，这一段可以拆成 5 张背景知识 PPT：LiveKit / SVA、nanobot、Google Calendar、Obsidian、CV 扩展输入。每页大图加一句大字说明，只留下印象，不在这里讲透；核心设计第一点再讲 SVA / Processor / LLM 注入。

## 2. 核心设计部分展开

| 时间 | 内容 | 说什么 |
| --- | --- | --- |
| 3:40-4:35 | 1. SVA 是什么，以及怎么和 LLM 注入 | 先解释 SVA 不作为生硬术语抛出，而是“实时音视频流进入 Agent 的处理方式”。LiveKit 提供 Room、音视频 Track、DataChannel、RPC；SVA Processor 思路是在实时流旁边挂处理器，用受控频率处理视频或音频，再把结构化结果注入大模型上下文或 DSG。这里要讲清楚：视频不只是“给模型看”，也可以变成可审计、可追踪的事件和证据。 |
| 4:35-5:40 | 2. ECP 同步 / 行为调度 / 前后台模块协作 | 讲 ECP 解决“后端说执行了”和“Unity 前端真的执行了”之间的一致性问题。语音指令“跳舞”作为 Intent 例子：语音意图 -> 工具调用 -> LiveKit RPC -> Unity 执行动画 -> ACK 回来 -> Blackboard 记录状态。再讲上升通道等级：低延迟本地动作是 Reflex；需要前台确认和回执的是 Intent；耗时、外部执行或多步骤协作才升级为 Task。 |
| 5:40-6:25 | 2 的例子补充：GOSLO 派发任务给 nanobot | 把“改日程”作为 Task 例子，而不是用提醒混讲。用户说“把会议改到晚上”先是 Intent，因为系统要理解和确认；确认后的日程执行请求，例如 `calendar_patch`，才是后台 Task。流程是 Brain / IntentWorkspace -> Scheduler -> Redis Stream -> nanobot Worker / gateway -> 结果回流。这里明确：nanobot 后台 Worker 不作为 LiveKit 前台挂载模块来讲，主线是 Scheduler + Redis + 后台执行层。 |
| 6:25-7:10 | 3. Graphiti 长期记忆、DSG 工作记忆、Episode 和触发器协议 | 讲 DSG 是运行时工作记忆，不是单纯地图；Graphiti 是带时间和来源的长期图记忆，适合保存 Episode、实体、事实和分区。触发器协议回答“事件发生后系统能自动做什么”：可以提交 Observation、暂存 Ref、归档 Episode、生成 Plan、派发 nanobot Task 或通知前台。例子放在这里：Photo Awareness、Graphiti 自然语言搜索/预加载、主动提醒都不是零散功能，而是 TriggerKind -> TriggerOutcome 的不同落点。 |
| 7:10-7:40 | 4. L1.5、多源 Ref、UUID 与外部模块挂载 | 用“相机模式按下快门”作为多源 Ref 例子：按下快门后先产生轻量预览事件，再异步上传完整图片；系统先得到 PhotoNode / staged PHOTO ref / PHOTO_PATH 绑定，之后才能作为后续识别、Graphiti 归档或主动提醒的证据。这里要谨慎说：拍照不是立刻生成确定 ObjectNode，而是先让照片成为可追踪证据。最后收束到多源 Ref + UUID 的意义：不同来源的信息不会散落，而是能被绑定、检索、升级和回灌。 |

## 3. 核心设计里的例子放置

| 例子 | 放在核心设计哪里 | 用来说明什么 |
| --- | --- | --- |
| 相机模式拍照后流程 | 第 4 点：L1.5、多源 Ref、UUID | 说明 AR 输入如何变成可追踪证据：preview event、图片资产、PhotoNode、StagedRef、RefTable / UUID。 |
| 语音 RPC 跳舞 | 第 2 点：ECP 与前台 Intent 闭环 | 说明前台动作需要 RPC、ACK、Blackboard 状态同步，不能只靠模型口头承诺。 |
| GOSLO 改日程任务给 nanobot | 第 2 点补充：Task 与后台协作 | 区分 Intent 和 Task：理解与确认是 Intent，确认后的 Calendar 修改才交给 Scheduler / nanobot 执行。 |
| 触发器协议三小例 | 第 3 点：Graphiti / DSG / Episode / 触发器 | 说明触发器可以支撑 Photo Awareness、Graphiti 预加载、主动提醒，不是单个固定功能。 |

## 4. 当前不展开的内容

- 不讲代码函数细节、文件路径和内部键名，除非答辩问答追问。
- 不把所有技术栈做成枯燥清单；技术名词只在架构和流程里解释。
- 不把 nanobot 说成 LiveKit Room 里的前台挂载模块。
- 不把 Graphiti / Obsidian / L2-B 讲成已经解决所有长期记忆治理问题，只讲已建立原型链路、分区和 UUID 绑定思路。
- 不提前写完整演讲稿和 PPT 稿，后续按这份大纲继续细化。
