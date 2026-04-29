# Task 6: DSG 作为仿生潜意识工作区、联想触发器与 LLM 上下文注入调研

> **任务定位**：本任务研究 DSG L2-B 作为“仿生潜意识工作区”应如何组织信息、触发联想、形成情绪/注意力倾向，并在合适时机把信息推入 LLM / Gemini Live 的前台上下文。  
> **重要边界**：请不要把重点放在具体图数据结构或实现技术栈上。我们关注的是认知组织模式、触发机制、上下文注入通道和 LLM 黑盒反馈规律。

## 1. 背景：ParrotCarriers 当前认知分层

ParrotCarriers / GOSLO 是一个 AR + LiveKit + Gemini Live + Bus/Brain/DSG/Graphiti/Nanobot 的多模态鹦鹉 Agent。

当前架构倾向把系统理解成一个具身智能体：

- **Unity / AR / 摄像头 / 麦克风**：身体与感官。
- **DSG / L2-B**：场景工作记忆、注意力、联想、潜意识活动区。
- **Graphiti / Obsidian**：长期记忆、个人知识库、可追溯事实。
- **Gemini Live / LLM**：前台语言意识、对话、解释、决策表达。
- **任务调度器 / py-trees / Nanobot**：行动选择、后台任务、长程计划。
- **ECP / Unity 前端状态机**：把高层意图同步为前端动作、动画和可见反馈。

过去我们有一个隐含假设：**DSG 与 LLM 是某种同构关系**，即 DSG 中的节点/边/注意力活动可以近似映射到 LLM 能理解的上下文和思考过程。现在需要更客观地修正这个假设：

- DSG 与 LLM 可能是“相似但不同构”的系统。
- DSG 更像外部化、可控、可追溯的潜意识/工作记忆。
- LLM 是黑盒语言推理器，能接收被压缩、格式化、排序后的上下文，但不一定按 DSG 的内部结构推理。
- 因此关键问题不是“DSG 如何等价于 LLM 思维”，而是：**什么样的 DSG 信号，应该在什么时机，以什么形式注入给 LLM，才能稳定地影响 GOSLO 的注意力、情绪、联想和行动？**

## 2. 与 Task 5 的区别

Task 5 研究的是：

- 视频/场景数据如何记录、标注、压缩成情景 episode。
- DSG L2-B 与 Graphiti / GraphRAG / Obsidian 如何存储和回灌。
- 重点是“数据生命周期、长期记忆、GraphRAG、SSOT”。

本任务研究的是：

- L2-B 内部应如何组织“潜意识活动”。
- 哪些刺激会变成联想、提醒、情绪、注意力提升或主动通报。
- 哪些内容应该进入 Gemini Live / LLM 上下文，哪些只留在潜意识层。
- LLM 收到不同类型提示词/上下文/工具结果/状态同步后，通常会产生什么行为偏差或反馈。

## 3. 研究目标

请围绕三个主方向调查：

1. **LLM 黑盒对上下文注入的响应规律**  
   研究 LLM / VLM / Gemini Live / SVA 等系统在收到场景摘要、情绪标签、注意力对象、记忆片段、工具结果时，会如何改变回答、行动和主动性。

2. **当前可用注入通道与实践经验**  
   调查 Gemini Live / LiveKit Agents / SVA / Realtime Agent 系统中，开发者实际上有哪些上下文注入通道：system instruction、session state、chat context update、tool result、function call result、DataChannel event、participant attributes、audio/video stream、turn-level prompt injection 等。

3. **DSG L2-B 的仿生组织模式**  
   研究潜意识工作区应该如何组织：注意力、显著性、情绪价、联想扩散、触发器、习惯化、惊奇/新奇、场景恢复、未完成意图、主动提醒、梦境/后台整理等。

## 4. 广度搜索与自由探索目标

请广泛搜索以下方向，不要只停留在“Agent Memory”泛泛概念：

- Global Workspace Theory / Conscious Access / Attention Schema / Cognitive Architecture / ACT-R / SOAR / Blackboard Architecture。
- LLM Agent 的 context injection、memory retrieval、salience ranking、reflection、emotional state prompt、tool result injection 实践。
- Stream Vision Agent / Video Agent / Realtime Multimodal Agent 如何把视觉事件注入 LLM。
- 游戏 AI / 虚拟角色 / 伴侣 Agent 如何设计“潜意识触发器”：例如角色突然想起某事、看到物体产生联想、情绪改变语气、后台任务完成后自然插话。
- 机器人/AR Agent 中，什么情况下系统应该主动打断用户，什么情况下只在内部更新状态。

如果发现比“DSG 潜意识 → Context Injector → LLM 前额叶”更好的模式，请记录并说明它为什么适合或不适合 ParrotCarriers。

## 5. 必须调研的核心问题

### 问题 A：DSG L2-B 应该如何组织“潜意识工作区”

请研究仿生认知和工程系统中，潜意识/工作记忆层通常包含什么：

- 注意力对象：当前最重要的物体、人物、任务、空间区域。
- 显著性：新奇、危险、用户刚提到、视觉上突出、任务相关、情绪相关。
- 联想边：某物让 GOSLO 想起某段记忆、某个任务、某个偏好、某个未完成事件。
- 情绪/动机：好奇、担心、兴奋、无聊、困惑、想提醒用户。
- 习惯化：常见物体不再反复通报；久别重逢或异常变化时重新升权。
- 未完成意图：后台任务、用户承诺、待提醒事项、未闭合 episode。
- 场景恢复：回到桌面/房间时恢复上次关注对象和上下文。

请给出 2-3 种可借鉴组织方式，例如：

- 认知黑板 / Global Workspace。
- 情绪-注意力加权图。
- Trigger + Salience Queue。
- Working Memory + Episodic Recall。

### 问题 B：什么信息应该从潜意识进入 LLM / 前额叶

请重点研究“进入意识”的条件：

- 什么样的场景变化应该主动注入给 LLM？
- 什么样的信息只应该更新 DSG，不应该打扰对话？
- 触发注入的阈值如何设计？例如 salience、novelty、emotion、task relevance、user intent、time since last mention。
- 如何避免 LLM 被频繁视觉事件打断，导致注意力漂移或话题混乱？
- 如何设计“轻提示 / 强提示 / 主动插话 / 只更新内部状态”四种等级？

请特别关注：

- 看到新物体、旧物体消失、物体位置变化、用户手动框选、后台任务完成、时间/天气/日程触发、情绪状态变化时，哪些应该进入 LLM。
- LLM 是否应该知道“这是潜意识联想”而不是“用户明确说的事实”。
- 注入内容是否应该携带置信度、来源、有效期、可打断性。

### 问题 C：LLM 黑盒收到不同注入内容后，会产生什么反馈

请研究 LLM / Gemini Live / Realtime Agent 的实践经验：

- 当 system prompt 注入长期人格状态时，LLM 行为如何变化？
- 当 chat context 注入场景摘要时，LLM 是否会过度提及视觉内容？
- 当 tool result 注入事实时，LLM 是否更容易把低置信度内容当确定事实？
- 当注入 emotion tag / mood / motivation 时，LLM 是否会风格漂移或过度表演？
- 当注入大量物体列表时，LLM 是否会忽略对话重点？
- 如何写 prompt / context 才能让 LLM 把 DSG 信息当作“可用背景”，而不是每次都显式复述？

请输出具体的提示词样式、失败案例和实践建议，而不是只给概念。

### 问题 D：当前可用注入通道与限制

请调查 Gemini Live、LiveKit Agents、SVA / Video Agent、Realtime Agent 常见注入通道：

- 会话级 system instruction / session instruction。
- turn-level context / chat context update。
- tool result / function response。
- participant attributes / state sync。
- DataChannel / telemetry event。
- audio/video stream 本身。
- 后台任务完成事件。

请比较这些通道适合注入什么：

- 稳定人格和长期规则。
- 当前场景摘要。
- 高显著性视觉事件。
- 低频情景记忆。
- 用户偏好和 Obsidian/SSOT 事实。
- 后台任务完成通知。
- 前端动作状态和 ECP 执行反馈。

请特别说明：

- 哪些通道是实时强注入，容易打断当前 turn。
- 哪些通道适合静默更新状态。
- 哪些通道适合在下一轮对话自然体现。
- 哪些通道不适合承载高频视觉事件。

### 问题 E：与任务调度器、ECP、前端状态机的同步边界

这是次要问题，只作为背景调查：

- DSG 的潜意识触发器什么时候只影响注意力，什么时候升级为任务调度器事件？
- 哪些触发器应该进入 py-trees / Scheduler，哪些只应该进入 Context Injector？
- ECP 是否需要承载“情绪/注意力/动机”这种软状态，还是只承载前端可执行动作？
- 前端动画状态（思考、惊讶、看向某物、提醒用户）如何与 DSG 的潜意识状态保持松耦合同步？
- 后台 Nanobot 完成任务时，是直接注入 LLM、先进入 DSG 潜意识队列，还是通过任务调度器决定是否通报？

请不要在这里展开完整协议设计；只收集边界与常见坑。

## 6. 必须查的资料类型

请优先查：

- Global Workspace / cognitive architecture / blackboard system 在 AI Agent 中的工程化应用。
- LLM context injection、memory retrieval、agent reflection、salience ranking 的论文、博客、开源项目。
- Gemini Live / LiveKit Agents / SVA / realtime multimodal agent 的上下文注入实践。
- 虚拟角色、游戏 AI、伴侣 Agent 的情绪、注意力、主动插话、后台联想设计。
- 机器人/AR Agent 中视觉事件注入 LLM 的设计经验。

## 7. 输出格式

请按以下结构输出：

1. **核心结论摘要**
   - 说明 DSG 与 LLM 为什么不应被视为完全同构，以及可采用的工程近似关系。
2. **可借鉴项目/论文/系统**
   - 名称、链接、与 ParrotCarriers 的相似点、可借鉴点。
3. **潜意识工作区组织模式**
   - 给出 2-3 种组织方式，并说明优缺点。
4. **进入 LLM / 前额叶的触发条件**
   - 给出触发等级：静默更新、轻提示、强提示、主动插话。
5. **上下文注入通道对照表**
   - 通道、适合内容、风险、使用频率、是否会打断对话。
6. **LLM 黑盒反馈规律与 Prompt 建议**
   - 给出具体 prompt/context 格式建议，以及常见失败案例。
7. **对 ParrotCarriers 的候选建议**
   - 按“立即可做 / Sprint4 可做 / P3+ 再做”分类。

## 8. 后续筛选标准

研究结果应帮助我们判断：

- L2-B 第一版是否应以 `attention / salience / novelty / emotion / association / pending_intent` 为核心组织字段。
- Context Injector 应该怎样从 L2-B 选择少量信息注入给 Gemini Live。
- 哪些触发器应进入任务调度器，哪些只影响 GOSLO 的语气、动作或注意力。
- 该如何避免视觉/记忆信息过量注入导致 LLM 注意力漂移。
- GOSLO 的“潜意识联想”如何表现得自然，而不是像系统日志一样打断用户。
