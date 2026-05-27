# 模块划分审计 02：需求 / 大纲 / 论文 / 代码实现对照

> 时间：2026-05-22  
> 范围：`docs/defense/drafts/01_outline.md`、`02_speech_script.md`、`03_ppt_script.md`、论文 docx、当前代码实现。  
> 说明：论文段落编号来自本轮对 `C:/Users/Bin/Desktop/毕业论文/AR+生活助手与智能提醒.docx` 的段落提取结果。

## 总结判断

当前 M0-M9 模块划分总体正确，适合作为答辩讲述顺序。

它不是论文目录的逐章复述，而是把论文中的需求、架构、详细设计和实现内容重排成“老师先听得懂，再看得懂架构，再理解创新点”的顺序。这一点符合用户原话：不讲代码细节，主要讲架构设计、数据流、核心设计和例子。

需要修正的不是整体模块边界，而是若干表述风险：

- M1 输入源顺序必须统一成：LiveKit / SVA、nanobot、Google Calendar、Obsidian、CV 扩展。
- nanobot 主线必须讲 Scheduler + Redis + 后台 Worker / gateway，不讲成 LiveKit 前台挂载模块。
- `calendar_change_request` 只是 Intent / Plan/HITL 草稿，不直接改 Google Calendar。
- 当前仓库内 `NanobotConsumer` 是 fallback / L2-only worker；真实 Google Workspace MCP 执行应讲成 nanobot gateway 路径，Demo 前必须确认实际环境。
- Graphiti 分区在论文里可讲 assistant / worker / scene / user；代码常量是 `GOSLO` / `MAID` / `SCENE` / `USER`。

## 已修正项

| 编号 | 问题 | 处理 |
| --- | --- | --- |
| A1 | `01_outline.md` 的 M1 输入源表仍是旧顺序。 | 已改为 LiveKit / SVA、nanobot、Google Calendar、Obsidian、CV 扩展。 |
| A2 | `round_02_research_notes.md` 把 Graphiti 分区写成 `ASSISTANT / WORKER / SCENE / USER`，与代码常量不一致。 | 已改为：论文讲角色分区，代码常量为 `GOSLO / MAID / SCENE / USER`。 |
| A3 | 演讲稿中“真正修改 Google Calendar”容易被理解为当前 fallback worker 已直接修改日程。 | 已改成“日程执行请求进入后台 Task，由 nanobot Worker 或真实 gateway 执行”。 |

## 逐模块审计

| 模块 | 结论 | 论文支撑 | 代码支撑 | 错误 / 风险 | 建议 |
| --- | --- | --- | --- | --- | --- |
| M0 开场与问题 | 正确。先讲“不是普通聊天助手”，符合论文动机。 | 论文 0030、0131、0134、1217。 | 不需要代码细节支撑。 | 不要把系统讲成完整商业级产品。 | 保留当前 0:00-1:30 开场。 |
| M1 背景知识输入源 | 正确，但已修正顺序。它是“认名词”的模块，不是技术栈堆叠。 | 论文 0030、0031、0134、0138。 | `processor_hook.py:6-9`、`nanobot_consumer.py:1-12`、`obsidian_vault.py:1-6`、`task_catalog.py:22-25`。 | CV 扩展不能讲成已完整实现 YOLO/SAM2/DINOv2/ConceptGraph 全 pipeline。英文截图不能压过中文解释。 | PPT 用五页大图，中文大字主导。 |
| M2 总体架构 | 正确。把论文的分层架构压成一张答辩架构图。 | 论文 0030、0031、0134、1217、1218。 | `src/parrot/brain/`、`src/parrot/dsg/`、`src/parrot/memory/`、`src/parrot/scheduler/`、`src/parrot/bus/`；`ModuleManifest` 和 `ModuleMount` 支撑外挂模块概念。 | 论文摘要里有“Worker 模块挂载”，但答辩中不能让老师误解 nanobot 走 LiveKit 前台房间。 | 在架构图中把 nanobot 放在 Scheduler/Redis 后台侧。 |
| M3 LiveKit / SVA / Context 注入 | 正确。应放在总体架构之后，让老师先有模块位置。 | 论文 0135、0138、0031。 | `processor_hook.py:6-9` 明确 SVA-inspired Processor；`livekit_sampler.py:73-74` 支撑低频视频采样；`_rpc_bridge.py` 支撑 LiveKit RPC。 | SVA 只能讲“借鉴 Processor 模式 / 可扩展视觉处理器”，不要讲成独立成熟视觉系统。 | PPT 画 Track / DataChannel / RPC / Processor 几条通道。 |
| M4 ECP 与前台动作闭环 | 正确。跳舞 RPC 例子能很好解释前台 Intent。 | 论文 0795、0803、0900-0902、1220。 | `animate.py:68-78` 包 ECP command 并调用 `animate` RPC；`_rpc_bridge.py:84-110` 镜像 ACK 到 Blackboard；Unity `ParrotRpcHandler.cs` 返回 completed/rejected/timeout。 | `_rpc_bridge.py:87-92` 明说当前 `last_ecp_ack` 还是 legacy dict，不是完整 EcpAck。 | 讲“ACK / 状态闭环已建立”，不要讲“所有命令都有完整统一 EcpAck 模型”。 |
| M5 行为调度与 nanobot Task | 正确，但表述必须谨慎。改日程作为 Task 例子是对的。 | 论文 0803、0906-0909、1219。 | `router.py:5-8`、`:45-48` 是 Reflex / Intent / Nanobot / BrainDirect；`dispatch_task.py:73-88` 说明 Calendar 写操作需确认后派发；`calendar_change_request.py:38-55` 明确它只是草稿；`service.py:108-121` 写入 Nanobot Stream。 | 仓库内 `nanobot_consumer.py:1-12` 是 fallback worker；未走真实 gateway 时不能说已经真实改 Google Calendar。 | 讲“确认后升级为后台 Task，可由 nanobot gateway / Google Workspace MCP 执行”。Demo 前确认是否真展示改日程。 |
| M6 DSG / Graphiti / Episode / Trigger | 正确，但内容很密，45 秒偏紧。 | 论文 0132、0134、0137、0818-0829、0912-0926、1218、1223。 | `triggers/base.py:36-75`、`runner.py:155-165` 支撑 TriggerOutcome；`graphiti_client.py:24-41` 支撑分区；`l2b_graph.py:373-409` 支撑 Graphiti preload，`:456-495` 支撑 episode archive。 | Graphiti / Obsidian 治理还在完善，论文 1223 明确不足。 | 可以保留两张 PPT：一张讲 DSG/Graphiti，一张讲 TriggerOutcome。 |
| M7 L1.5 / Ref / UUID / 拍照例子 | 正确。拍照是讲 Ref/UUID 最直观的例子。 | 论文 1218、1220，以及拍照/Ref/UUID相关详细设计段落。 | `photo.py:14-33` 双通道 preview + asset；`:37-45` 明确不自动生成 ObjectNode；`:338-377` stage PHOTO 并绑定 `PHOTO_PATH`；Unity `FormalCameraModeController.cs:170-182` 触发拍照。 | 不要说“拍照后自动识别出对象并写入确认 ObjectNode”。 | 讲“照片先成为证据入口，后续再识别、确认、归档”。 |
| M8 Demo | 方向正确，但素材状态未完全核验。 | 论文 1131-1157、1220。 | Demo 链路需要以实际视频/截图为准。 | 如果 Demo 不展示改日程，就不要让演讲暗示现场会真实改 Calendar。 | Demo 只承接主线：交互、主动提醒/邮件、后台状态、Obsidian 日记。 |
| M9 总结 | 正确。总结点和论文创新点一致。 | 论文 0031、1217-1230。 | 代码链路覆盖多源输入、ECP、Scheduler、L1.5、Graphiti 原型。 | 不足要诚实：视觉稳定、记忆治理、真实外部模块长期运行。 | 保留“做到什么 + 创新点 + 后续完善”。 |

## 模块顺序是否需要调整

不需要大改。

当前顺序：

```text
M0 问题
M1 输入源认知
M2 总体架构
M3 LiveKit/SVA
M4 ECP 前台闭环
M5 Intent/Task/nanobot
M6 DSG/Graphiti/Trigger
M7 L1.5/Ref/UUID/拍照
M8 Demo
M9 总结
```

这个顺序符合答辩可读性。论文自身更偏“需求 -> 概要设计 -> 详细设计 -> 实现”，如果照论文目录讲会很容易变成正式文档复述。答辩稿现在的顺序是合理重排。

只有一个小建议：M2 总体架构图里提前出现 `Observation / Ref / L1.5 / Episode` 这些词，M6-M7 再展开。这样 M7 虽然排在后面，老师也不会觉得 Ref/UUID 是突然出现的。

## 高风险表述清单

答辩时避免以下说法：

- “nanobot 是挂在 LiveKit Room 里的前台模块。”
- “calendar_change_request 会直接修改 Google Calendar。”
- “fallback NanobotConsumer 已经真实调用 Google Workspace MCP 修改日程。”
- “SVA / YOLO / SAM2 / DINOv2 / ConceptGraph 这条视觉 pipeline 已完整落地。”
- “拍照后系统自动生成可靠 ObjectNode。”
- “Graphiti / Obsidian 的长期记忆治理已经完全解决。”
- “所有 ECP ACK 都已经是完整统一的新协议对象。”

推荐替代表述：

- “nanobot 在本系统主线中是后台任务执行层，调度链路是 Scheduler + Redis Stream；真实 gateway 可连接 Google Workspace MCP。”
- “改日程先生成 Intent / Plan 草稿，确认后才升级成后台 Task。”
- “SVA 是 Processor 模式参考，本项目把这个思路扩展到可进入 DSG 的结构化感知链路。”
- “照片先作为证据 Ref 进入系统，后续再识别、确认或归档。”
- “Graphiti / Obsidian 已建立原型链路和 UUID 绑定思路，长期治理仍是后续完善点。”

## 下一步建议

1. 给 M2 画一版粗架构图草稿，必须把 nanobot 放在后台侧。
2. 给 M3-M7 每个模块补 3-5 个最终可引用的代码行号，避免正式讲稿继续漂移。
3. Demo 资产核验：确认到底展示“邮件/主动提醒”、还是“改日程 Task”，不要两者混讲。
4. 若要展示真实 Google Calendar 修改，必须先确认真实 nanobot gateway / Google Workspace MCP 跑通；否则只讲草稿和派发链路。
