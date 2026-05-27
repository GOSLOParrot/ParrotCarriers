# 第1轮总结与下一轮背景

## 本轮已经固化的事情

### 工作方式

- 不一次性完成大纲、演讲稿和PPT稿。
- 每一轮先调研论文和代码，再产出审查材料，确认后再进入下一轮。
- 后续三份正式稿分别是：
  - `drafts/01_outline.md`：大纲。
  - `drafts/02_speech_script.md`：演讲稿。
  - `drafts/03_ppt_script.md`：PPT稿。
- `codex-ppt` 已安装，但正式用作 skill 需要重启 Codex。
- 上一轮总体 Plan 已固化在 `round_00_master_plan.md`，后续不要只依赖聊天上下文。

### 固定边界

- 答辩重点讲架构设计、数据流、核心机制，不讲代码细节。
- 技术名词保留，但要解释清楚，不能枯燥罗列技术栈。
- `nanobot` 后台 Worker 不作为 LiveKit 挂载模块讲。
- 论文和代码不一致时，下一轮审计以代码实现为准，论文表述要收敛成谨慎说法。
- 触发器不是单个功能点，而是可扩展协议。

## 当前确定的流程例子

### 例子1：相机模式拍照后流程

所属核心设计：

- 多源输入接入。
- PhotoNode / IntentWorkspace / RefTable。
- L1.5 + L2-B 的证据和Ref绑定。

作用：

- 说明 AR 场景里一次“拍照”如何进入系统记忆。
- 用来讲“不是直接把图片塞进大模型”，而是预览事件和完整图片资产分流。

顺序位置：

- 放在总体架构之后、DSG记忆层之前或开头，用来把老师带入数据流。

### 例子2：语音 RPC 指令跳舞

所属核心设计：

- LiveKit RPC。
- ECP命令和ACK。
- Blackboard状态同步。
- Intent层前台动作。

作用：

- 说明“语音意图 → 工具调用 → Unity动作 → ACK → 状态同步”的前台闭环。
- 用来解释为什么系统不是“模型说执行了就算完成”，而是需要前后端状态一致。

顺序位置：

- 放在 LiveKit / ECP / 前端控制机制里讲。

### 例子3：GOSLO 派发“改日程”任务给 nanobot

所属核心设计：

- Scheduler。
- Reflex / Intent / Task 三层行为。
- Plan/HITL。
- Redis任务链。
- Nanobot后台协作。

作用：

- 作为 Nanobot Task 的主例子。
- 比“提醒”更适合区分 Task 和 Intent：
  - Intent：用户表达改日程，GOSLO理解并生成日程变更草稿。
  - Task：确认后把 `calendar_patch` / `calendar_create` / `calendar_delete` 交给后台 Worker 执行。

顺序位置：

- 放在行为调度和前后台协作机制里讲。
- 不与触发器主动提醒混在一起讲。

### 例子4：触发器协议

所属核心设计：

- TriggerKind。
- TriggerOutcome。
- TriggerRunner。
- DSG触发器协议。
- Photo Awareness / Graphiti回灌 / 主动提醒。

作用：

- 说明触发器不是一个固定功能，而是一套“事件发生后系统可以自动做什么”的协议。
- 说明后续可以随时设计新触发器，不需要重写主Brain。

顺序位置：

- 放在 DSG / Graphiti / 主动提醒之间。
- 建议先讲 DSG 和 L1.5 / L2-B 的记忆层，再讲触发器如何把事件转成 Observation、StagedRef、Plan、Archive、Nanobot Task 或 Notify。

触发器下面的小例子：

- 相机模式 Photo Awareness：拍照预览后暂存照片上下文或提醒GOSLO。
- Graphiti自然语言搜索 / 预加载：长期记忆回灌到当前L2-B背景。
- 主动提醒触发器：消息、日程、场景状态满足条件后触发提醒或计划。

## 下一轮建议的讲述顺序

下一轮写大纲时，建议采用这个顺序：

1. 开场：传统生活助手不足，为什么AR场景助手需要“情景理解”。
2. 输入需求：语音、视频、拍照、场景、Google日程、Obsidian、Graphiti、外部Worker。
3. 总体架构：Unity AR客户端、LiveKit、Brain、Scheduler、DSG、Graphiti、Nanobot各自位置。
4. LiveKit / ECP / SVA：先讲实时交互底座，再用“语音跳舞”说明前台Intent闭环。
5. DSG记忆层：讲 Observation、L1.5、RefTable、IntentWorkspace、L2-B、Graphiti。
6. 相机拍照流程：作为多源Ref和照片证据的完整数据流例子。
7. 触发器协议：讲 TriggerKind / TriggerOutcome / TriggerRunner，以及 Photo Awareness、Graphiti回灌、主动提醒。
8. Scheduler / Nanobot：讲 Reflex / Intent / Task 三层，用“改日程任务”说明后台协作。
9. Demo安排：交互、邮件/主动提醒、后台和Obsidian日记。
10. 总结：完成了什么、创新在哪里、哪些是原型阶段后续工作。

## 下一轮任务

下一轮不是直接写完整演讲稿，而是做“大纲调研 + 大纲审计”：

1. 从论文里提取可直接支撑大纲的内容：
   - 研究背景。
   - 总体架构。
   - 创新点。
   - 核心实现。
   - 测试和不足。
2. 从代码里继续核实四个例子的边界：
   - 哪些已经完成。
   - 哪些是原型链路。
   - 哪些只能作为后续工作或备用问答。
3. 产出大纲草稿：
   - 格式：`时间 / 内容 / 说什么 / PPT怎么展示 / 老师应理解什么 / 需要谨慎的表述`。
4. 对大纲做一次审计：
   - 是否顺序可读。
   - 是否主次清楚。
   - 是否有技术堆砌。
   - 是否把 Task / Intent / Trigger / Nanobot / LiveKit 挂载讲混。

## 下一轮重点审计问题

- SVA 是在前面总体讲清楚，还是在 LiveKit / Processor 段落里讲清楚。
- 触发器协议放在 DSG 之后是否更顺。
- 相机拍照流程放在 DSG 前还是 DSG 后更容易理解。
- Graphiti预加载要讲到什么深度，避免显得像没有完成。
- Nanobot 改日程流程里 Plan/HITL 要讲多细，避免老师误会系统自动乱改日程。
