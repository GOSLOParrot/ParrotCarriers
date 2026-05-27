# 图片来源清单：1:30-2:30 场景 Agent 需要哪些输入

## PPT 使用方式

这一段不适合做成技术栈清单。PPT 应该负责“让老师看见这些东西是什么”，演讲稿负责“把这些输入和我们的架构设计连起来”。

风格要求：截图只作为素材，不作为整页背景。页面用白底、深色字、正常字体，整体朴素清晰。图片不够干净时就缩成卡片，旁边放大字说明。

当前推荐做五页大图版；如果后续时间被压缩，再合并成两页或一页。

| 页 | 作用 | 图片 |
| --- | --- | --- |
| 背景知识页 1：视频流 | 让老师知道 LiveKit 和 VisionAgents 是什么。 | 用户提供的 LiveKit 截图 + VisionAgents 截图，放 `livekit/` 和 `sva_cv/`。 |
| 背景知识页 2：nanobot | 让老师知道 nanobot 是后台任务 Agent / Worker 模式参考。 | 用户提供或后续补充的 HKUDS/nanobot 官方仓库 README 截图，放 `nanobot/`。 |
| 背景知识页 3：Google Calendar | 让老师知道 Calendar 是日程和时间上下文。 | 用户提供的 Calendar 周视图截图，放 `google_calendar/`。 |
| 背景知识页 4：Obsidian | 让老师知道 Obsidian 是本地知识库和日记工具。 | 用户提供的 Obsidian 官网截图，放 `obsidian/`。 |
| 背景知识页 5：CV 扩展输入 | 让老师知道现代 CV 能把画面变成对象、特征和关系。 | YOLO / SAM2 / DINOv2 / ConceptGraph 官方图或自绘组合图，放 `sva_cv/`。 |
| 备用页：这些输入怎么进入 Agent | 从“认识工具”过渡到“理解架构”。 | 一张简化流向图：外部输入源 -> 通道 / 协议 -> Observation / Ref / Task -> DSG / Graphiti。 |

如果时间只能放一页，就保留五个小卡片，并在演讲里用 20 秒补一句“后面的架构图会把这些输入统一到 Observation、Ref、Task 里”。

## 当前用户已提供图片的保存建议

| 当前图片 | 建议文件名 | 放置目录 | 页面用途 |
| --- | --- | --- | --- |
| LiveKit GitHub README 截图 | `livekit_repo_overview.png` | `livekit/` | 视频流页，与 VisionAgents 一起放。 |
| VisionAgents GitHub README 截图 | `vision_agents_repo_overview.png` | `sva_cv/` | 视频流页，说明 Agent 可以 watch/listen/understand video。 |
| nanobot GitHub README 截图 | `nanobot_repo_overview.png` | `nanobot/` | nanobot 单页，大图 + 后台任务 Agent / Worker。 |
| Google Calendar 周视图截图 | `google_calendar_week_context.png` | `google_calendar/` | Calendar 单页，大图 + 日程 / 时间上下文。 |
| Obsidian 官网截图 | `obsidian_official_overview.png` | `obsidian/` | Obsidian 单页，大图 + 本地知识库 / 日记。 |
| SAM2 项目页或 README 截图 | `sam2_overview.png` | `sva_cv/` | CV 扩展页，说明对象分割。 |
| DINOv2 项目页或 README 截图 | `dinov2_overview.png` | `sva_cv/` | CV 扩展页，说明视觉特征。 |
| ConceptGraphs 项目页或 README 截图 | `conceptgraph_overview.png` | `sva_cv/` | CV 扩展页，说明对象关系和场景图。 |

## 素材候选

| 对象 | 推荐图片 | 来源 URL | 本项目中怎么讲 |
| --- | --- | --- | --- |
| LiveKit | GitHub 仓库封面或 Room / Participant / Track 文档截图。 | https://github.com/livekit/livekit ; https://docs.livekit.io/intro/basics/rooms-participants-tracks/ ; https://docs.livekit.io/transport/data/ | 实时音视频和数据通信底座。本项目里语音、视频、RPC、DataChannel 都经由它组织。 |
| Google Calendar | 官方 Calendar 周视图、事件详情或任务图。 | https://workspace.google.com/products/calendar/ | 用户真实生活的时间上下文。日程不是普通数据库，而是提醒和后台 Task 的触发来源。 |
| Obsidian | 官方首页/帮助页截图，优先选 Daily notes、链接笔记、Graph 或 Canvas。 | https://obsidian.md/ ; https://help.obsidian.md/ | 用户长期可编辑的本地知识库和日记来源。后续 Demo 可补我们自己的 Obsidian 日记截图。 |
| nanobot | HKUDS/nanobot GitHub README 截图，或仓库 WebUI / 功能说明部分。 | https://github.com/HKUDS/nanobot | 后台任务执行模式参考。本项目中主讲 Scheduler + Redis + nanobot Worker，不讲成 LiveKit 前台挂载模块。 |
| SVA / CV Processor | Vision Agents GitHub README 或自绘 Processor 简图。 | https://github.com/GetStream/Vision-Agents ; https://visionagents.ai/ | 视频不是只“给模型看”，也可以被 Processor 变成结构化结果，再注入 LLM 或 DSG。 |
| SAM2 | Meta SAM2 项目页或 GitHub README 图。 | https://ai.meta.com/research/sam2/ ; https://github.com/facebookresearch/sam2 | 说明“分割图像和视频中的对象”。 |
| DINOv2 | Meta DINOv2 GitHub / Demo / Blog 图。 | https://github.com/facebookresearch/dinov2 ; https://dinov2.metademolab.com/ | 说明“提取稳健视觉特征，可用于多种视觉任务”。 |
| ConceptGraphs | ConceptGraphs 官方项目页或 GitHub README 可视化图。 | https://concept-graphs.github.io/ ; https://github.com/concept-graphs/concept-graphs | 说明“把多帧视觉结果组织成开放词汇 3D 场景图”。 |
| YOLO | Ultralytics YOLO 官方文档或 GitHub。 | https://docs.ultralytics.com/ ; https://github.com/ultralytics/ultralytics | 备用：说明实时检测，不作为当前主图优先项。 |

## 准备优先级

1. 必须准备：用户已给的 LiveKit、VisionAgents、Obsidian、Google Calendar 四张图。
2. 必须补：nanobot 官方 GitHub / README 截图 1 张。
3. CV 页建议补：SAM2 + DINOv2 + ConceptGraphs 中至少 1 张强视觉图；优先 ConceptGraphs 或 SAM2。
4. 建议准备：我们自己的 Obsidian 日记截图 1 张，放在 `project_demo/`，用于和 Demo 段落衔接。
5. 可后补：Graphiti / DSG 图，不放在这一段，放到后面的核心设计页。

## 截图注意

- 官方网页截图用于解释“这是什么”；我们自己的截图用于解释“我们怎么用它”。
- Google Calendar 和 Obsidian 的项目截图必须打码，不能出现真实私人日程、姓名、邮箱、密钥或路径。
- nanobot 图要选官方 GitHub / README，不用第三方介绍页做主图。
- SVA 如果没有合适官方图，宁可自绘简图，不要用不明来源图片。
