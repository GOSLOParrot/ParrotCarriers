# Task 5: DSG / Graphiti / GraphRAG / 情景记忆与物理环境数据采集调研

> **任务定位**：这是 Sprint4 前置的最后一个关键 Research。目标不是让 Research 替项目做最终架构决策，而是让它广泛收集“LLM / 机器人 / AR Agent 如何记录、标注、压缩、回放和检索物理环境经验”的工程经验、前沿项目和可借鉴协议。

## 1. 统一背景：ParrotCarriers 当前记忆与场景架构

ParrotCarriers / GOSLO 是一个 AR + LiveKit + Gemini Live + Bus/Brain/DSG/Graphiti/Nanobot 的多模态鹦鹉 Agent。Unity Android 客户端提供 AR 摄像头、麦克风、触控/手势等实时输入；Python Brain Agent 负责实时对话、工具调用、任务调度和长期记忆交互。

当前项目里有两个容易混淆但必须分清的层：

### 1.1 DSG / L2-B：场景工作记忆与情景缓存

- **模块位置**：
  - `src/parrot/dsg/l1_5_protocol.py`：传感器输出协议，定义 `SensorFrame`、`Detection`、`FrameSource`、`DetectionAuthority`。
  - `src/parrot/dsg/l2b_types.py`：L2-B 语义节点/边类型，包含 `SemanticNode`、`EpisodeMarker`、`reference_image_path`、`last_sighting_path`、`provenance_stream_id`、`time_span` 等字段。
  - `src/parrot/dsg/l2b_graph.py`：RustworkX 支撑的运行时语义工作图，负责当前场景内的对象、注意力、情景 episode、Graphiti preload/archive。
  - `src/parrot/dsg/interfaces.py`：DSG ↔ Graphiti 接口层，包含 `preload_object_semantics()`、`update_last_seen()`、`get_expected_objects()`、`emit_trigger()`。
- **定位**：
  - DSG L2-B 是实时/半实时的场景工作记忆，不是长期数据库。
  - 它保存当前会话/当前场景里“哪些对象存在、注意力在哪里、哪些节点属于同一个情景 episode、哪些视觉证据路径可追溯”。
  - 它可以从 Graphiti 预加载已知对象，也可以在 episode 结束后把摘要和可追溯事实归档回 Graphiti。

### 1.2 Graphiti：长期时间图与 GraphRAG 后端

- **模块位置**：
  - `src/parrot/memory/graphiti_client.py`：Graphiti 单例客户端，使用 FalkorDB 后端、Gemini LLM / Embedder / Reranker。
  - 当前 `group_id` 分区：`goslo`、`maid`、`scene`、`user`。
  - `tests/integration/test_graphiti_chain.py`：覆盖 write → search → DSG preload/update 的基本链路。
- **当前使用方式**：
  - 通过 `Graphiti.add_episode(...)` 写入长期记忆。
  - 通过 `Graphiti.search(query=..., group_ids=[...])` 做语义/关键词/图检索。
  - `scene` 分区用于场景/物体相关知识；`user` 分区用于用户/SSOT 相关知识；`goslo` 分区用于 GOSLO 自身情景或对话记忆；`maid` 可用于 Nanobot/女仆后台任务结果。
- **重要限制**：
  - Graphiti 写入可能较慢（此前观察到 `add_episode` 可达 20-46s），不能阻塞实时语音、实时视频或前端体感。
  - Graphiti 不应直接接收每一帧视频或每个检测框；它更适合接收经过 DSG / Nanobot / 用户标注过滤后的 episode、事实、摘要、实体关系和可追溯引用。

### 1.3 L0 Event Stream：事件溯源与投影边界

- **模块位置**：`src/parrot/shared/event_log.py`。
- **设计意图**：
  - L0 Raw Event Stream 是状态变化的 single source of truth。
  - 后续投影到：
    - L1 Blackboard：当前状态快照。
    - L2 Graphiti Episode：gist-level 长期记忆。
    - L3 DSG L2-B Event：fact-level 场景/情景事件。
- **协议字段**：`ts`、`kind`、`layer`、`actor`、`payload`、`provenance_parent`。
- **Research 重点**：请特别关注事件溯源、时间轴、provenance、可回放性、情景分段、长期记忆压缩之间的设计关系。

### 1.4 Obsidian / SSOT 加强方向

项目希望未来能把 Obsidian 或类似个人知识库作为用户可编辑的 SSOT / 外挂知识层：

- DSG 节点已有 `obsidian_uuid` 字段，可把场景对象或用户标注与外部笔记实体关联。
- L2-B 的 `enrich_from_obsidian()` 目前通过 Graphiti 搜索 `scene` / `user` 分区补充对象知识。
- 研究时请关注“人类可编辑知识库（Obsidian/Markdown/Dataview/Local-first notes）如何与 Agent Memory / GraphRAG / Scene Graph 做双向同步”，尤其是冲突解决、事实过期、人工标注优先级和可追溯链接。

## 2. 研究目标：我们到底要学什么

请把重点放在“工程经验与具体设计案例”，不要只给泛泛概念。我们需要知道：

1. 具身智能 / 机器人 / AR Agent 如何把物理世界中的视频、SLAM、对象检测、用户标注、任务结果，转换为可检索、可回放、可长期更新的情景记忆。
2. DSG / Dynamic Scene Graph、Semantic Map、Episodic Memory、GraphRAG、Memory Core、SSOT 之间如何分层，哪些数据应该留在短期场景图，哪些应该进入长期图数据库，哪些应该进入人类可编辑知识库。
3. 如何设计从视频场景数据到 DSG L2-B，再到 Graphiti 的交互协议、时间轴、字段、写入频率、摘要策略和回读策略。

## 3. 广度搜索与自由探索目标

请在具体问题之外保持广泛搜索：

- 机器人长期自主学习、LLM 机器人控制、Embodied AI Memory、Dynamic Scene Graph、Semantic SLAM、Episodic Memory、World Model、GraphRAG、Agent Memory Core、Local-first / SSOT 知识库同步。
- 优先查找有工程细节的项目、论文、开源实现、技术博客、GitHub 讨论、机器人/AR/游戏 AI 系统案例。
- 如果发现比“DSG 缓存 + Graphiti 长期图 + Obsidian SSOT”更优雅的架构，请记录，但不要直接替项目拍板；请说明它适合/不适合 ParrotCarriers 的原因。

## 4. 必须调研的核心问题

### 问题 A：DSG / Semantic Map / SLAM 与 LLM 情景记忆如何分层

请研究机器人和具身智能项目中，实时场景图与长期记忆如何分工：

- Dynamic Scene Graph 通常保存哪些层级？例如地点、房间、表面、对象、人、事件、任务状态。
- SLAM / Semantic SLAM / 3D Map 与 LLM 可读的语义记忆之间如何转换？
- 哪些数据适合实时层保存，哪些数据适合 episode 结束后摘要进入长期记忆？
- 如何处理“看见 / 没看见 / 记忆里应该存在但当前未确认”的不对称逻辑？
- 是否有成熟的时间衰减、置信度、确认状态、证据路径设计？

### 问题 B：视频与场景数据如何采集、标注、压缩成情景 episode

请关注“从连续视频到可记忆事件”的工程做法：

- 如何做事件分段？例如按对话 turn、用户指令、场景变化、对象变化、注意力变化、任务开始/结束来切 episode。
- 每个 episode 需要保存哪些字段？例如 start/end time、参与对象、位置、用户意图、GOSLO 行为、关键帧路径、检测框、OCR、ASR 片段、provenance。
- 视频帧是否保存？保存原图、缩略图、关键帧、embedding、检测结果、caption，还是只保存引用？
- 如何设计人工标注与自动检测的优先级？例如用户手动框选物体、Gemini 描述、YOLO 检测、ReID 确认之间如何仲裁。
- 如何避免把每帧都写入长期图，导致 GraphRAG 噪声过大或成本过高？

### 问题 C：Graphiti / GraphRAG / Memory Core 的最佳实践

请重点研究 Graphiti 和相似 GraphRAG/Memory Core 系统：

- Graphiti 的 `episode`、`entity`、`fact/edge`、temporal validity、provenance、community summary 应如何用于 Agent 长期记忆？
- `group_id` 分区的最佳实践是什么？如何防止场景、用户偏好、对象知识、任务结果之间关系污染？
- 对于 ParrotCarriers，是否应该继续使用类似 `scene/user/goslo/maid` 的分区，还是拆成 `episodic/objects/personality/nanobot_research/obsidian_ssot` 等更细分分区？
- GraphRAG 系统通常如何处理“事实更新”和“事实过期”？例如物体位置改变、用户偏好改变、房间布局变化。
- 长期图如何回灌到实时 DSG？例如启动时 preload、看到对象时 enrich、任务触发时 retrieve、睡眠/后台整理时 consolidate。

### 问题 D：DSG L2-B ↔ Graphiti 的交互协议应该怎么设计

请给出可落地的协议建议，不要只说“写入图数据库”：

- 从 DSG 到 Graphiti：什么事件触发写入？写入什么 payload？是否需要批处理、限流、去重、摘要？
- 从 Graphiti 到 DSG：什么时候 preload / enrich？返回什么格式？如何把长期事实映射回 `SemanticNode` 的 `known_facts`、`confirmation`、`obsidian_uuid`、`reference_image_path`？
- L0 Event Stream 的 `provenance_parent` / `provenance_stream_id` 应如何贯穿：原始事件 → 传感器帧 → L2-B 节点 → Graphiti episode → Obsidian 笔记？
- 是否需要一个独立的 MemoryWriter / SceneMemoryProjector / EpisodeArchiver，避免实时链路直接调用 Graphiti？
- 失败时如何降级？例如 Graphiti 不可用时，L2-B 是否继续工作；后台是否稍后补写；如何避免重复写入。

### 问题 E：Obsidian / SSOT / 人类可编辑记忆如何接入

请研究本地优先知识库与 Agent Memory 的结合经验：

- Obsidian/Markdown 笔记如何作为 SSOT？适合存哪些内容：用户手动命名的对象、房间规则、偏好、项目资料、长期任务说明？
- Graphiti 和 Obsidian 谁是事实来源？不同类型事实是否有不同来源优先级？
- 如何保存双向链接？例如 Graphiti entity UUID、DSG object UUID、Obsidian note path/frontmatter uuid、snapshot path。
- 如何处理人工修改与自动记忆冲突？例如用户在 Obsidian 改了“杯子在厨房”，但 DSG 最近看到杯子在桌上。
- 是否有现成插件/模式可借鉴：Dataview、YAML frontmatter、local vector index、Markdown graph sync、Git-based memory。

## 5. 必须查的资料类型

请优先查：

- Dynamic Scene Graph / Semantic SLAM / Embodied AI Memory 论文与项目。
- LLM 机器人控制项目中的 memory / world model / scene graph 设计。
- Graphiti 官方文档、GraphRAG 实践、Zep / Mem0 / Letta / LangGraph memory / LlamaIndex graph memory 等可比系统。
- 机器人或 AR 应用中视频关键帧、事件时间轴、对象跟踪、人工标注、provenance 的工程实践。
- Obsidian / Markdown / local-first knowledge base 与 AI Agent Memory 的同步方案。

## 6. 输出格式

请按以下结构输出，避免泛泛而谈：

1. **可借鉴项目/论文/系统列表**
   - 名称、链接、它解决的问题、与 ParrotCarriers 的相似点/不同点。
2. **分层架构对照表**
   - 实时场景图、事件日志、长期图记忆、人类 SSOT 分别保存什么。
3. **数据生命周期建议**
   - 从视频帧/用户标注/对话 turn → L2-B → Graphiti → Obsidian 的路径。
4. **字段与协议建议**
   - 给出 2-3 个具体 JSON/表结构示例，例如 `SceneObservationEvent`、`EpisodeArchivePayload`、`GraphitiPreloadResult`。
5. **写入频率与降噪策略**
   - 什么时候写、什么时候不写、如何限流、如何合并、如何处理慢写入。
6. **风险与坑**
   - 噪声污染、过度记忆、隐私、错误事实固化、时间线错乱、图爆炸、实时链路阻塞。
7. **对 ParrotCarriers 的可执行建议**
   - 只给候选建议，按“立即可做 / Sprint4 可做 / P3+ 再做”分类。

## 7. 决策标准（供项目后续筛选）

研究结论应帮助我们判断：

- 是否维持当前“L0 Event Stream → DSG L2-B 工作记忆 → Graphiti 长期时间图 → Obsidian SSOT”的分层。
- Graphiti 分区是否需要从 `goslo/maid/scene/user` 细化为更明确的 `episodic/objects/personality/nanobot_research/obsidian_ssot`。
- 哪些视觉/情景数据只保存在 L2-B，哪些必须归档 Graphiti，哪些应该写入 Obsidian。
- Graphiti 写入是否必须通过后台投影器/归档器，而不是实时对话或视频循环直接写。
- 第一版情景记忆 MVP 应该记录哪些最小字段，才能支撑“GOSLO 记得刚刚/以前在场景中发生过什么”。
