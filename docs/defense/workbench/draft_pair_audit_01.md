# 双稿自审 01：演讲稿与 PPT 稿是否符合原话需求

## 已符合

- 已按用户指定顺序安排 `1:30-2:30` 背景知识页：LiveKit / SVA、nanobot、Google Calendar、Obsidian、CV 扩展。
- 已把这一段拆成 5 张大图页，而不是一页小字技术栈；每页只保留一个大中文判断句。
- PPT 稿明确采用白底 / 近白底、深色中文大字、正常字体；英文截图只作为证据图，不作为花背景。
- 演讲稿和 PPT 稿按模块同步：PPT 负责让老师看见“这是什么”，演讲稿负责解释“它怎么进入架构”。
- 核心设计部分已经融入例子：跳舞 RPC/ACK、改日程 Task、拍照 Ref/UUID、Trigger 输出协议。
- 每个模块已在任务表中标注需要回核的论文/代码依据，避免后续只凭印象讲。

## 对应关系

| 演讲模块 | PPT 页 |
| --- | --- |
| M0 开场与问题 | Slide 1-2 |
| M1 背景知识输入源 | Slide 3-7 |
| M2 总体架构 | Slide 8 |
| M3 SVA 与 Context 注入 | Slide 9 |
| M4 ECP 与前台动作闭环 | Slide 10 |
| M5 Intent / Task / nanobot | Slide 11 |
| M6 DSG / Graphiti / Trigger | Slide 12-13 |
| M7 Ref / UUID / 拍照 | Slide 14 |
| M8 Demo | Slide 15 |
| M9 总结 | Slide 16-17 |

## 仍需注意

- 当前只是双稿草稿，没有生成 PPTX，也没有生成 slide images，符合 `codex-ppt` 的前置审批要求。
- 用户在对话里给了截图，但还没有落到本地素材目录；后续制作 PPT 前必须保存到 `docs/defense/ppt_skill_workspace/assets/01_input_sources/`。
- Google Calendar 和 Obsidian 的真实项目截图必须打码，不能暴露私人日程、姓名、邮箱、路径或密钥。
- CV 页要讲成“扩展输入 / 背景能力方向”，不要说项目已经完整实现 YOLO + SAM2 + DINOv2 + ConceptGraph pipeline。
- Graphiti、L2-B、Trigger、nanobot Worker 等内容要继续保持“原型链路 / 已贯通 / 后续完善”的谨慎口径。
- 下一轮需要逐模块补最新代码行号和论文段落引用，尤其是 M3-M7 核心设计页。
