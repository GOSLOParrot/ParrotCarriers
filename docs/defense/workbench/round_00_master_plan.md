# 答辩材料制作总体计划

> 记录来源：上一轮 Plan Mode 输出。此文件用于防止上下文压缩后丢失总体计划。

## Summary

目标是把答辩制作拆成四个可控产物：`大纲`、`演讲稿`、`PPT稿`、`PPT/视频展示方案`。

核心原则是先用论文和代码核实“我们到底实现了什么”，再决定哪些内容口头讲、哪些内容放 PPT 图示、哪些只留作答辩问答备用。

已确认的主线应围绕：

- AR场景助手为什么需要多源输入。
- LiveKit/ECP如何保证实时交互闭环。
- DSG/L1.5/L2-B/Graphiti如何组织记忆。
- Reflex/Intent/Task如何区分前台动作和后台任务。

## Key Changes

- 先做“事实核查表”，再写稿：
  - 论文核查：从 `AR+生活助手与智能提醒.docx` 提取背景、创新点、系统架构、核心实现、测试与不足。
  - 代码核查：确认每个流程例子对应真实实现，避免把设想说成完成。
  - 外部术语核查：LiveKit、Obsidian、Graphiti、nanobot 用官方简介做简短解释，技术名词保留但不堆技术栈。
- 大纲采用“问题 → 输入需求 → 总体架构 → 三条核心流程 → 记忆与调度设计 → Demo → 总结”的顺序。
- PPT 和演讲稿分工：
  - 演讲稿负责把逻辑讲顺，解释老师可能不熟悉的词。
  - PPT负责直观展示架构图、数据流、三层行为分派、记忆层级，不放大段文字。
  - 代码细节只做备用，不进入主讲。

## Workflow

1. 调研阶段
   - 整理 `00_user_original_requirements.md` 里的原话需求和注意点。
   - 从论文中提取 6 类材料：研究背景、系统目标、创新点、总体架构、核心设计、实现与测试。
   - 从代码中核查候选流程：
     - 相机模式拍照：Unity Camera Mode → `photo.taken_preview` → HTTP upload → PhotoNode → IntentWorkspace / RefTable。
     - 语音跳舞：`play_dance` / `animate` → LiveKit RPC → ECP command → Unity ACK → Blackboard 状态。
     - Nanobot Task：`message_check_request` / `diary_query_request` / `reminder_request` → Scheduler → Redis Stream → Nanobot Worker → result channel。
     - Graphiti 预加载/填充：`L2BGraph.preload_from_graphiti`、`SceneContextTrigger`、`SSOTEnrichmentTrigger`，作为“记忆回灌/背景填充”例子，但要标清它不是前台RPC动作。
2. 选例阶段
   - 主例子推荐选 3 个：
     - 相机拍照流程：覆盖 AR输入、ECP事件、照片证据、L2-B、IntentWorkspace、RefTable。
     - 语音跳舞流程：覆盖 Intent、RPC、ECP ACK、Blackboard 状态同步。
     - Nanobot消息/日记/提醒流程：覆盖 Task、Scheduler、Redis、后台 Worker。
   - Graphiti触发器流程建议作为第 4 个辅助例子：解释“长期记忆如何回灌到工作记忆”，不抢主线。
   - Reflex/Intent/Task 区分：
     - Reflex：手势停靠、急停，本地低延迟。
     - Intent：语音跳舞、拍照、前台可见动作，需要 ACK 和状态同步。
     - Task：邮件检查、Obsidian日记查询、提醒、资料整理，进入后台队列。
3. 大纲阶段
   - 产物：`docs/defense/drafts/01_outline.md`
   - 格式固定为：`时间 | 内容 | 说什么 | 适合PPT展示`
   - 推荐时长：PPT讲解 8 分钟 + Demo 2 分钟，总体可压缩到 5-10 分钟。
   - 每一段都标注老师理解目标：这一段讲完后，老师应该明白什么。
4. 演讲稿阶段
   - 产物：`docs/defense/drafts/02_speech_script.md`
   - 按大纲展开，不讲代码细节。
   - 每个陌生技术名词只解释一次：
     - LiveKit：实时音视频、RPC、DataChannel的通信底座。
     - SVA/Processor：把视频/感知结果处理成可注入大模型上下文的机制。
     - ECP：前端动作命令与ACK回执协议，避免“模型说完成但前端没完成”。
     - Obsidian：本地优先、Markdown形式的个人知识库。
     - nanobot：HKUDS 的轻量级个人AI助手，在本项目中作为后台任务 Worker。
     - Graphiti：保存 episode/entity/fact 的时间图记忆，用于长期记忆和回灌。
5. PPT稿阶段
   - 产物：`docs/defense/drafts/03_ppt_script.md`
   - 每页只保留 1 个核心信息，优先图示：
     - 第1页：项目标题与一句话目标。
     - 第2页：传统助手不足与AR场景需求。
     - 第3页：总体架构图。
     - 第4页：多源输入与DSG记忆层级。
     - 第5页：相机拍照数据流。
     - 第6页：RPC跳舞/ECP ACK状态闭环。
     - 第7页：Reflex/Intent/Task + Scheduler/Nanobot。
     - 第8页：Graphiti长期记忆与回灌。
     - 第9页：Demo展示安排。
     - 第10页：完成内容、创新点与不足。
6. PPT生成阶段
   - 使用 `codex-ppt` 时遵守确认门：
     - 先确认 PPT 大纲。
     - 再确认视觉风格。
     - 再确认图片生成后端。
     - 先生成一页样张。
     - 样张确认后再批量生成。
   - 当前推荐风格备选：
     - `科研答辩风`：最稳，适合老师快速理解。
     - `清爽专业风`：更像软件工程产品汇报。
     - `手绘技术解释风`：适合画复杂架构，但要避免显得不正式。
   - 默认推荐：`清爽专业风 + 少量手绘技术解释元素`。

## User Decisions

- 决策 1：最终讲解时长  
  默认：PPT讲解 8 分钟 + Demo 2 分钟。若学院要求更短，则压缩为 5-6 分钟讲解 + 2 分钟Demo。
- 决策 2：主流程例子数量  
  默认：3 个主例子 + 1 个辅助Graphiti例子。不要把所有流程都讲成同等重点。
- 决策 3：Graphiti触发器怎么讲  
  默认：讲成“长期记忆回灌/背景填充机制”，不讲成前台可见交互主流程。
- 决策 4：Nanobot怎么讲  
  默认：讲成后台 Worker / Task 执行层，通过 Scheduler 和 Redis 连接，不说成 LiveKit 挂载模块。
- 决策 5：PPT形态  
  默认：先做可编辑的 PPT稿，再用 `codex-ppt` 生成视觉统一版；不直接跳到最终图片式 PPT。

## Test Plan

- 事实检查：
  - 每个流程例子必须能对应到论文段落和代码文件。
  - 标出“已实现”“原型实现”“预留接口/后续工作”，不混说。
- 可读性检查：
  - 每一页 PPT 只能回答一个问题。
  - 每个技术名词第一次出现时必须有一句中文解释。
  - 每段演讲稿都能自然接到下一段。
- 答辩模拟：
  - 8分钟版本读一遍，删除超过时长的细节。
  - 准备 5 个备用问答：LiveKit为什么用、SVA是什么、Graphiti为什么不用普通数据库、Task和Intent区别、nanobot为什么不是挂载模块。
- PPT检查：
  - 大字、少字、图优先。
  - 架构图和数据流图必须让老师不看代码也能理解。
  - Demo页与视频内容对应，不重复解释视频里已经明显展示的动作。

## Assumptions

- 当前先产出制作计划，不直接修改稿件正文。
- 后续制作顺序固定为：事实核查表 → 大纲 → 演讲稿 → PPT稿 → PPT视觉生成。
- 论文和代码以当前工作区为准；如果论文描述与代码冲突，以代码实现为主，论文表述需要修正为更谨慎的说法。
- `codex-ppt` 已安装，但正式作为 skill 使用需要重启 Codex。

## 后续修订记录

- 第1轮后，Nanobot 主例子从“邮件/日记/提醒”修订为“GOSLO派发改日程任务给nanobot”，更能区分 Task 和 Intent。
- 第1轮后，Graphiti预加载不再单独作为主例子，而是归入“触发器协议”的小例子之一。

