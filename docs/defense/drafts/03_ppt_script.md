# PPT 稿草稿

> 当前文件是 PPT 稿 / deck outline 草稿，符合 `codex-ppt` 后续流程所需的信息结构。  
> 尚未确认最终大纲、视觉样式、图片后端、样张，也没有生成 slide image 或 PPTX。

## 视觉风格

- 白底或近白底。
- 深色中文大字，英文截图只作为素材图。
- 每页最多 1-3 个关键信息。
- 图片不要当花背景，放成清晰截图卡片。
- 字体方向：Aptos / Microsoft YaHei UI / 思源黑体 / Inter 一类，朴素、清晰、高级。

## Slide 1: 项目题目

- Layout role: Cover
- Key points:
  - `AR 生活助手与智能提醒`
  - `从实时交互到场景记忆`
- Visual idea: 白底大标题，右侧放一张 GOSLO / AR Demo 画面或极简设备示意。
- Required images: 待补项目 Demo 封面图。
- Speaker link: M0 开场。

## Slide 2: 为什么传统助手不够

- Layout role: Context / problem
- Key points:
  - `传统助手：文本问答 / 固定提醒`
  - `场景 Agent：理解当前环境和上下文`
  - `目标：在合适时机主动协助`
- Visual idea: 左右对比图；左侧“文本/日程”，右侧“语音+视频+日程+笔记+记忆”。
- Research basis: 论文段落 `[130]-[134]`，见 `round_02_research_notes.md`。
- Speaker link: M0 背景。

## Slide 3: 视频流输入：LiveKit / SVA

- Layout role: Concept explanation
- Key points:
  - `LiveKit：实时音视频 / 数据通道`
  - `SVA：让 Agent 看、听、理解视频`
  - `后续进入 Context / DSG`
- Visual idea: 白底，两张截图并排；截图下方用中文大字标注。不要让英文 README 占主导。
- Required images:
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/livekit/livekit_docs_rooms_tracks.png`（用户截图，待保存）
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/vision_agents_repo_overview.png`（用户截图，待保存）
- Speaker link: M1 背景知识；M3 会展开。
- Caution: 这里只建立印象，不展开 Processor 细节。

## Slide 4: 后台任务输入：nanobot

- Layout role: Concept explanation
- Key points:
  - `nanobot：后台任务 Agent`
  - `用于慢任务 / 多步骤协作`
  - `不作为 LiveKit 前台挂载模块`
- Visual idea: 右侧放 nanobot README 截图，左侧大字说明。
- Required images:
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/nanobot/nanobot_repo_overview.png`（用户截图，待保存）
- Research basis: 官方 HKUDS/nanobot 仓库；`round_02_research_notes.md` §2.6。
- Speaker link: M1 nanobot 背景；M5 会展开。

## Slide 5: 时间上下文：Google Calendar

- Layout role: Concept explanation
- Key points:
  - `Google Calendar`
  - `日程 / 提醒 / 时间上下文`
  - `后台 Task 的真实数据来源`
- Visual idea: 大图放 Calendar 周视图，左上角或左侧加中文大字。白底，不加复杂装饰。
- Required images:
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/google_calendar/google_calendar_week_context.png`（用户截图，待保存）
- Speaker link: M1 Calendar 背景；M5 改日程任务。

## Slide 6: 长期知识来源：Obsidian

- Layout role: Concept explanation
- Key points:
  - `Obsidian`
  - `本地知识库 / 日记`
  - `用户长期可编辑信息来源`
- Visual idea: 大图放 Obsidian 截图，中文说明更大更清楚；可在右下角标注“Demo 中会展示日记”。
- Required images:
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/obsidian/obsidian_official_overview.png`（用户截图，待保存）
- Speaker link: M1 Obsidian 背景；M6 Graphiti/Obsidian。

## Slide 7: CV 扩展输入：从画面到对象和关系

- Layout role: Concept explanation
- Key points:
  - `YOLO：实时检测`
  - `SAM2 / DINOv2：分割与视觉特征`
  - `ConceptGraph：对象与关系组织`
- Visual idea: 三张小截图或一张主图，底部画一条很简单的箭头：`画面 -> 对象 -> 特征 -> 场景图`。
- Required images:
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/sam2_overview.png`（用户截图，待保存）
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/dinov2_overview.png`（用户截图，待保存）
  - `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/conceptgraph_overview.png`（用户截图，待保存）
- Speaker link: M1 CV 背景；M3/M6 会展开。
- Caution: 讲成背景能力方向，不说项目完整采用这条 pipeline。

## Slide 8: 总体架构

- Layout role: Architecture
- Key points:
  - `Unity AR 前端`
  - `LiveKit 实时中枢`
  - `Brain / DSG / Graphiti / Scheduler / nanobot`
- Visual idea: 白底架构图。左侧输入，中央 LiveKit + Brain，右侧记忆与任务；箭头要粗、少、清楚。
- Required images: 自绘架构图，后续生成或手绘。
- Research basis: `round_02_research_notes.md` §2.2-2.6。
- Speaker link: M2 总体架构。

## Slide 9: 核心设计 1：SVA 与 Context 注入

- Layout role: Workflow / concept
- Key points:
  - `视频 Track`
  - `Processor 结构化处理`
  - `注入 LLM / DSG`
- Visual idea: 流程图：`LiveKit Video Track -> Processor -> Context / Observation -> DSG`，旁边标 `DataChannel / RPC`。
- Research basis: `round_02_research_notes.md` §2.3；SVA skill；LiveKit Unity skill。
- Speaker link: M3。
- Caution: SVA 是模式/思路，不夸大实现成熟度。

## Slide 10: 核心设计 2：前台动作闭环

- Layout role: Process example
- Key points:
  - `语音 Intent`
  - `LiveKit RPC`
  - `ACK 写入 Blackboard`
- Visual idea: 用“跳舞”例子画闭环：`用户语音 -> Brain 工具 -> RPC animate -> Unity 动画 -> ACK -> Blackboard`。
- Research basis: `round_01_flow_example_audit.md` 例子 2；`round_02` §2.4。
- Speaker link: M4。
- Caution: 不说所有 ACK 已完全统一。

## Slide 11: 核心设计 2b：Intent 和 Task 分层

- Layout role: Process / comparison
- Key points:
  - `Intent：理解和确认`
  - `Task：后台执行`
  - `Scheduler -> Redis -> nanobot Worker`
- Visual idea: 上半部分画 Intent 草稿，下半部分画 Task 派发；用“改日程”例子。
- Research basis: `round_01_flow_example_audit.md` 例子 3；`round_02` §2.5-2.7。
- Speaker link: M5。
- Caution: `calendar_change_request` 是草稿，确认后才执行后台 Task；若现场没有真实 nanobot gateway / Google Workspace MCP，就只讲派发链路和结果回流，不说已经真实修改 Google Calendar。

## Slide 12: 核心设计 3：DSG / Graphiti / Episode

- Layout role: Architecture / memory
- Key points:
  - `DSG：运行时工作记忆`
  - `Graphiti：长期图记忆`
  - `Episode：带来源的情景记录`
- Visual idea: 左侧当前上下文，右侧长期图记忆；中间用 Episode / Ref 桥接。
- Research basis: `round_02_research_notes.md` §2.2, §2.10；Graphiti skill。
- Speaker link: M6。
- Caution: 讲“原型链路和分区思路”，不说长期记忆治理已完全完成。

## Slide 13: 核心设计 3b：触发器协议

- Layout role: Workflow / system mechanism
- Key points:
  - `TriggerKind`
  - `TriggerOutcome`
  - `Observation / Ref / Plan / Notify / Task`
- Visual idea: 中心一个 Trigger，向外分叉到 Observation、StagedRef、Archive、Plan、Nanobot、Notify。
- Research basis: `round_01_flow_example_audit.md` 例子 4；`round_02` §2.9。
- Speaker link: M6。

## Slide 14: 核心设计 4：拍照后的多源 Ref

- Layout role: Process example
- Key points:
  - `快门不是直接塞给模型`
  - `Preview + Asset 双通道`
  - `PhotoNode / Ref / UUID`
- Visual idea: `快门 -> photo.taken_preview -> upload -> PhotoNode -> StagedRef -> RefTable/UUID`。
- Research basis: `round_01_flow_example_audit.md` 例子 1；`round_02` §2.8。
- Speaker link: M7。
- Caution: 不说自动生成确认 ObjectNode。

## Slide 15: Demo 路线

- Layout role: Demo agenda
- Key points:
  - `前台交互`
  - `主动提醒 / 邮件`
  - `后台状态 + Obsidian 日记`
- Visual idea: 三段式 Demo 时间线，右侧留视频占位。
- Required images/video: Demo 视频待补。
- Speaker link: M8。

## Slide 16: 做到了什么与创新点

- Layout role: Summary
- Key points:
  - `多源输入统一为可追踪数据流`
  - `实时动作有状态闭环`
  - `工作记忆 + 长期记忆 + 后台协作`
- Visual idea: 五个简洁标签：`Ref/UUID`、`SVA Processor`、`ECP/ACK`、`Trigger`、`nanobot Task`。
- Research basis: `round_02_research_notes.md` §3。
- Speaker link: M9。

## Slide 17: 后续完善

- Layout role: Closing / limitation
- Key points:
  - `视觉稳定性`
  - `记忆治理`
  - `更多外部模块`
- Visual idea: 简洁三列，不展开。
- Speaker link: M9 结尾。

## 图片保存状态

当前用户已提供截图，但还需要保存到以下路径后再进入 PPT 制作：

- `docs/defense/ppt_skill_workspace/assets/01_input_sources/livekit/livekit_docs_rooms_tracks.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/vision_agents_repo_overview.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/nanobot/nanobot_repo_overview.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/google_calendar/google_calendar_week_context.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/obsidian/obsidian_official_overview.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/sam2_overview.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/dinov2_overview.png`
- `docs/defense/ppt_skill_workspace/assets/01_input_sources/sva_cv/conceptgraph_overview.png`

## Skill 阶段状态

- Source reading and asset extraction: 进行中。
- Outline confirmation: 未确认。
- Visual style confirmation: 初步为“白底朴素技术答辩”，未最终确认。
- Image backend confirmation: 未进行。
- Sample slide: 未生成。
- Full slide generation: 未开始。
