# 大纲审计 01

## 审计对象

- `docs/defense/drafts/01_outline.md`
- 对照材料：`docs/defense/00_user_original_requirements.md`
- 本轮新增注释：`1:30-2:30 场景 Agent 需要哪些输入` 需要官方介绍、简介和图。

## 总体结论

当前大纲整体符合原话里的主线要求：

- 按“时间 / 内容 / 说什么”组织。
- 没有写完整演讲稿和 PPT 稿，没有越过当前职责。
- 保留了 LiveKit、SVA、ECP、Graphiti、DSG、Obsidian、nanobot 等技术名词。
- 核心设计部分按原话顺序写了 SVA、ECP/行为调度/nanobot、Graphiti/DSG/触发器、L1.5/多源 Ref/UUID。
- 例子已融入核心设计，而不是单独堆在最后。

## 发现的问题

| 位置 | 问题 | 严重度 | 修正建议 |
| --- | --- | --- | --- |
| 1:30-2:30 场景 Agent 需要哪些输入 | 原稿只是列出语音、视频、Google、Obsidian、nanobot、CV 等输入，没有明确要求官方简介和图片。 | 中 | 需要把这一段改成“多源输入视觉介绍”：每个陌生名词配官方一句话解释和官方图。 |
| 1:30-2:30 -> 3:40-4:35 的衔接 | SVA 原本只在核心设计里出现，前面缺少直观铺垫。 | 中 | 在 1:30-2:30 先用“更多元 CV / SVA 输入”做直观引入，3:40 后再讲实现机制。 |
| nanobot 表述 | 原稿已经避免把 nanobot 写成 LiveKit 挂载模块，但 1:30-2:30 里还不够明确它是后台任务执行模式。 | 低 | 在输入源介绍表里标注：nanobot 讲后台 Worker / 任务执行模式，不讲成 LiveKit 前台模块。 |
| PPT 图示需求 | 原话明确强调 PPT 要直观，不是论文式白底黑字流程图。原稿没有在 1:30-2:30 记录图示要求。 | 中 | 增加“官方图 / 仓库图 / 产品界面图 / SVA Pipeline 图”的材料要求。 |

## 官方材料候选

| 对象 | 推荐来源 | 可用内容 |
| --- | --- | --- |
| LiveKit | `https://github.com/livekit/livekit`；`https://docs.livekit.io/intro/basics/rooms-participants-tracks/`；`https://docs.livekit.io/transport/data/` | 仓库封面、实时音视频数据简介、Room / Participant / Track、RPC / DataChannel 等数据通道说明。 |
| Google Calendar | `https://workspace.google.com/products/calendar/`；Google Play 官方 Calendar 页面 | Google Calendar 官方界面图、周视图、事件详情、任务、共享日历、Meet 协作。 |
| Obsidian | `https://obsidian.md/`；`https://obsidian.md/help/` | 官方首页截图、Daily / Notes / Graph / Canvas、私有本地 Markdown 笔记说明。 |
| nanobot | `https://github.com/HKUDS/nanobot` | 官方仓库封面、WebUI 预览图、轻量开源 AI agent 简介、chat channels / memory / MCP / deployment 能力。 |
| SVA / CV Processor | `https://github.com/GetStream/Vision-Agents`；`https://visionagents.ai/`；LiveKit Agents Vision 文档 | real-time vision agent、processor pipeline、视频流到模型或处理器的直观说明。 |

## 已执行修正

- 已更新 `docs/defense/drafts/01_outline.md` 的 `1:30-2:30` 行。
- 已新增 `## 1.1 需求注释：1:30-2:30 多源输入介绍`，把官方介绍和图示要求记录进大纲。

## 当前判断

修正后，这份大纲更符合原话需求：既不是枯燥列技术栈，也能让老师先知道这些陌生技术和工具是什么，再进入总体架构和核心设计。
