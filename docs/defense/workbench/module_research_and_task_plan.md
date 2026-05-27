# 模块化调研与双稿任务表

> 用途：后续每一轮都按模块推进。每个模块先核论文/代码/官方资料，再同步更新演讲稿和 PPT 稿。  
> 原则：PPT 负责直观理解，演讲稿负责把图和架构逻辑连起来；重要信息必须大字清晰，不用小字堆定义。

## 总体边界

- 不讲代码细节，讲架构设计、数据流、模块协作。
- 技术名词保留，但必须解释清楚，不能只是堆技术栈。
- 例子必须来自论文或代码中能支撑的链路。
- `nanobot` 主线是后台 Worker / Redis / Scheduler，不讲成 LiveKit 前台挂载模块。
- Graphiti / L2-B / Trigger 等演进中内容要用“原型链路 / 已贯通 / 后续完善”这类谨慎说法。
- PPT 风格：白底、深色字、正常高级字体、大图但不铺花背景。

## 模块划分

| 模块 | 时间 | 演讲目标 | PPT 目标 | 当前依据 | 风险边界 |
| --- | --- | --- | --- | --- | --- |
| M0 开场与问题 | 0:00-1:30 | 说明项目不是普通聊天助手，而是 AR 场景生活助手。 | 1-2 页，用问题对比建立场景。 | 原话 1/2；`round_02_research_notes.md` §2.1。 | 不夸大成完整商业产品。 |
| M1 背景知识输入源 | 1:30-2:30 | 让老师先认识 LiveKit/SVA、nanobot、Google Calendar、Obsidian、CV 扩展。 | 5 页大图；中文介绍必须存在感强。 | `input_sources_research.md`；官方网页/仓库截图。 | 英文截图不能压过中文大字。 |
| M2 总体架构 | 2:30-3:40 | 把 Unity AR、LiveKit、Brain、DSG、Graphiti、Scheduler、Redis、nanobot 放到同一张图里。 | 一张架构图，不做论文式密集流程图。 | `round_02_research_notes.md` §2.2-2.6。 | 不把 nanobot 画成 LiveKit Room 前台模块。 |
| M3 核心设计 1：LiveKit/SVA/Context 注入 | 3:40-4:35 | 解释视频流怎么进入大模型和处理器，为什么不只是“给模型看”。 | 通道图：Track / Data / RPC / Processor / Context。 | `.cursor/skills/client-sdk-unity`；`.cursor/skills/sva-vision-agents`；`round_02` §2.3。 | SVA 讲成模式/思路，不讲成已经完全成熟的独立系统。 |
| M4 核心设计 2：ECP 与前台动作闭环 | 4:35-5:20 | 用“语音跳舞”解释 Intent、RPC、ACK、Blackboard。 | 流程图：语音 -> 工具 -> RPC -> Unity -> ACK -> Blackboard。 | `round_01_flow_example_audit.md` 例子 2；`round_02` §2.4。 | 不说所有状态都有完整 EcpAck；当前 ACK 有 legacy 镜像。 |
| M5 核心设计 2b：行为调度与 nanobot Task | 5:20-6:25 | 用“改日程”解释 Intent 与 Task 差异，讲 Scheduler / Redis / nanobot Worker。 | 流程图：Intent 草稿 -> 确认 -> Scheduler -> Redis Stream -> Worker -> Result。 | `round_01` 例子 3；`round_02` §2.5-2.7。 | `calendar_change_request` 是草稿，不直接改 Calendar。 |
| M6 核心设计 3：DSG / Graphiti / Episode / Trigger | 6:25-7:10 | 说明工作记忆、长期记忆、触发器协议如何组织。 | 图：TriggerKind -> TriggerOutcome -> Observation / Ref / Archive / Plan / Notify。 | `round_02` §2.9-2.10；Graphiti / DSG skills。 | Graphiti/Obsidian 治理不要讲成完全解决。 |
| M7 核心设计 4：L1.5 / Ref / UUID / 拍照例子 | 7:10-7:40 | 用相机快门说明多源 Ref 和证据链。 | 数据流图：快门 -> preview -> upload -> PhotoNode -> StagedRef -> RefTable/UUID。 | `round_01` 例子 1；`round_02` §2.8。 | 不说拍照必然生成确认的 ObjectNode。 |
| M8 Demo | 7:40-9:20 | 展示交互、邮件/主动提醒、后台和 Obsidian 日记。 | Demo 路线页 + 视频嵌入页。 | 原话 Demo 要求；现有 demo 素材待补。 | 不在 Demo 中讲代码。 |
| M9 总结 | 9:20-10:00 | 总结做到什么、创新点和后续完善。 | 一页总结：多源输入、实时闭环、记忆组织、触发协议、后台协作。 | `round_02` §3。 | 后续不足要诚实：视觉稳定、记忆治理、外部模块。 |

## 双稿同步规则

| 输出 | 每个模块必须包含 |
| --- | --- |
| 演讲稿 | 该段要说的中文句子、过渡句、老师理解判断、谨慎表述。 |
| PPT 稿 | 页码、标题、3 条以内大字信息、图示/图片需求、与演讲稿对应关系、素材路径。 |

## 下一轮优先核查

1. M1 图片素材是否全部保存到 `ppt_skill_workspace/assets/01_input_sources/`。
2. M2 总体架构图是否需要先手绘一版模块位置。
3. M3-M7 每个核心流程是否需要补最新代码行号，避免和当前实现漂移。

## 最新审计记录

- `module_audit_02.md`：已完成需求 / 大纲 / 论文 / 代码实现对照。结论是 M0-M9 模块划分总体正确，属于合理的答辩讲述重排；已修正 M1 输入源顺序、Graphiti 分区常量表述、Calendar Task 过度表述。
