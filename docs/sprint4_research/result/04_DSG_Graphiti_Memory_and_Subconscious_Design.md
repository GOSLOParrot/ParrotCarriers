# 04. DSG / Graphiti / ECP 协议 V2 有效信息提炼

> **定位**：本文件只提炼 DeepResearch 中对 ParrotCarriers 有用的设计注意事项、坑点和可借鉴功能。  
> **不是**：协议规范、Sprint4 实施计划、字段冻结稿、模块重构建议。  
> **已删去**：完整 JSON payload 草案、阶段路线图、与当前 Sprint4 决策冲突的“现在做/不做”判断。

## 1. 已有架构前提

ParrotCarriers 已经有自己的 V1 设计基础：

- `identify_object` 是 **GOSLO 按需感知 Intent tool**，需要同步体感闭环：抓帧/比对/返回结果后再说话。
- A10 / DSG 自动发现是 **潜意识路径**，不阻塞对话，不等同于 `identify_object`。
- Nanobot 是 **Task / 后台路径**，可慢写、可闲时写、可 session 结束后写，但不能伪装成本轮同步识别结果。
- DSG L2-B 已有语义注意力、节点生命周期、触发器、Graphiti preload/archive 的早期设计。
- Graphiti 在当前架构中是长期记忆后端，不是实时视觉路径；查询顺序应优先当前内存/DSG 工作记忆，再查 Graphiti。

因此，本轮调研只用于升级 **协议 V2 的接口问题意识**：状态同步怎么做、DSG 和 Graphiti 怎么接、ECP 有什么坑、证据链和有效期如何表达。

## 2. ECP / 状态同步的有效信息

### 2.1 状态同步要同步“目标”和“实际”

调研中最有价值的一点是：协议不能只传“我要做什么”，还要能区分：

- 后端期望状态：Brain / Scheduler / Gemini 想让前端进入什么状态。
- 前端实际状态：Unity Animator / AR / audio pipeline 真实进入了什么状态。
- 中间态：queued、playing、settling、rejected、timeout、cancelled。
- 过期态：指令到达时场景、时间、对象或用户 turn 已经变了。

对当前架构的意义：

- `set_video_tier` 已经验证了这个原则：Blackboard 不能早于 Unity `applied` 就宣称成功。
- `identify_object` 也需要同样原则：GOSLO 不能在没有 snapshot / match / unknown 结果前说“这是 XX”。
- 未来自建 ASR/TTS 后，`LISTENING / THINKING / SPEAKING` 也不能只由 LLM 文本状态决定，需要音频实际播放、barge-in、TTS 结束事件参与。

### 2.2 ECP 常见坑

- **fire-and-forget 伪装同步完成**：最典型就是 tool 派出后台任务却让 GOSLO 像已经看完一样回答。
- **状态源冲突**：Brain 认为在 `SPEAKING`，但前端音频已经被打断；Unity 认为动画完成，但后端还在等待。
- **延迟指令过期**：LLM 说“看左边那个东西”时，用户镜头已经移走。
- **软状态和硬动作混在一起**：情绪、注意力、好奇心不应和 `fly_to`、`setVideoTier`、`animate` 这类可执行动作混成同一种命令。
- **Any State 式乱跳**：前端状态机如果无条件响应所有后端命令，会出现动画撕裂、队列堆积、死锁或错位表演。

### 2.3 值得考虑的推荐字段

这些不是协议定义，只是调研中反复出现的有用功能字段：

| 推荐字段/概念 | 建议位置 | 代表功能 | 理由 |
|:--|:--|:--|:--|
| `command_id` | ECP command / tool result | 串起下发、ack、timeout、取消 | 避免多条指令交错时无法归因 |
| `issued_at` / `received_at` | ECP command / frontend ack | 判断延迟和过期 | 处理“指向空气”的迟到动作 |
| `expires_at` / TTL | ECP command / context injection | 指令或背景失效时间 | 场景和 turn 变化后自动丢弃 |
| `target_state` | Brain→Unity | 后端期望进入的状态 | 和实际状态对比 |
| `observed_state` | Unity→Brain | 前端真实状态 | 防止世界线分叉 |
| `status` | ack/result | applied、queued、rejected、timeout、cancelled | tool 体感闭环必需 |
| `reason` | ack/result | 拒绝、降级、失败原因 | 让 GOSLO 能正确解释失败 |
| `interruptible` | animation / speech / task | 是否可被打断 | 支撑状态机微锁和排队 |
| `source_turn_id` | tool/context/timeline | 绑定对话 turn | 自建 ASR/TTS 后尤其重要 |

## 3. Gemini Live 原生管线与自建 ASR/TTS 的适配问题

当前 Gemini Live 原生管线已跑通，但协议 V2 需要给第二条线预留统一事件口径。

### 3.1 需要统一的事件

推荐把 Gemini Live 原生事件和未来自建 ASR/TTS 事件都折叠成同一类 timeline event：

- 用户开始说话。
- 用户结束说话。
- 转写片段产生。
- 转写最终确认。
- Gemini / LLM 开始思考。
- tool call 开始/结束。
- TTS / 远端语音开始播放。
- TTS / 远端语音结束播放。
- barge-in / interruption。
- snapshot 捕获。
- DSG evidence 绑定。

### 3.2 关键问题

- 谁是 `SPEAKING` 的权威？LLM 生成完文本、TTS 开始、远端音频开始播放、还是 Unity 实际听到音频？
- 谁是 `LISTENING` 的权威？VAD、ASR、Gemini turn detector、还是用户按键/Push-to-talk？
- 自建 ASR/TTS 后，tool call 与用户语音时间线如何对齐？
- 如果用户打断时，正在执行的 ECP 动作、TTS、DSG 注入应该如何取消或降级？

这些问题应进入协议 V2 的状态同步审查，而不是等自建管线实现后再补。

## 4. DSG ↔ Graphiti 的联系：有效问题

### 4.1 Graphiti 检索结果如何填充回 DSG

这是需要设计的问题，不应被 Research 草率定死。

需要回答：

- Graphiti search 命中的内容是直接写入 L2-B node，还是作为候选 enrichment 挂起？
- 命中的长期事实进入 L2-B 后，confirmation 应该是 `EXPECTED`、`TENTATIVE` 还是只作为 `known_facts` 背景？
- Graphiti 返回内容是否需要有效期过滤？如果事实过期或来源很旧，是否降低权重？
- Obsidian 人工事实和 Graphiti 自动事实同时命中时，如何排序？
- 查询结果是否应带 `source` / `group_id` / `valid_time` / `confidence`，避免 LLM 把旧事实当当前视觉事实？

### 4.2 DSG 什么时候写 Graphiti

有效原则：

- Graphiti 可以慢，甚至 session 结束后写。
- Graphiti 写入不应阻塞 `identify_object` 的同步体感。
- 高价值事实可入队；低价值视觉噪声留在 L2-B 或直接丢弃。
- 自动发现路径和按需识别路径要分开记录来源。

需要特别防止：

- 单帧 CV 结果直接写长期图。
- Gemini 口述视觉内容直接写成 confirmed 事实。
- Nanobot 后台结果回流时覆盖按需识别的同步结果。
- 同一物体多次轻微变化造成长期图节点爆炸。

### 4.3 推荐字段/概念

| 推荐字段/概念 | 建议位置 | 代表功能 | 理由 |
|:--|:--|:--|:--|
| `graphiti_uuid` | L2-B node | 长期图实体引用 | L2-B preload/enrich 需要回指 |
| `group_id` | Graphiti query/write | 分区隔离 | 防止 scene/user/goslo/maid 混乱 |
| `valid_from` / `valid_until` | Graphiti fact / L2-B enrichment metadata | 事实有效期 | 对应物体位置、偏好、场景关系变化 |
| `source_description` | Graphiti episode | 来源说明 | 区分 identify_object、A10、Nanobot、Obsidian |
| `provenance_event_id` | L2-B / Graphiti episode | 追溯到 L0 Event | 审计和回放需要 |
| `obsidian_uuid` | L2-B / Graphiti entity | 人工 SSOT 对齐 | 人类编辑与自动观察冲突时需要 |

## 5. Graphiti 存放建议与图爆炸问题

### 5.1 Graphiti 适合存什么

适合：

- 用户明确命名、纠正、标注的内容。
- `identify_object` 按需路径产生的可追溯确认事实。
- session / episode 结束后的摘要。
- Nanobot 后台任务结论。
- 对象长期属性：用途、来历、通常位置、用户关系、情感权重。
- 事实有效期变化：以前在哪里、现在在哪里、什么时候改变。

不适合：

- 每帧检测框。
- 高频 attention 波动。
- 未确认的单帧 CV 推断。
- 临时 UI/HUD 状态。
- 原始图片二进制。

### 5.2 图爆炸风险

调研中最有价值的坑点是：长期图爆炸通常不是因为数据多，而是因为 **同一实体被反复创建成不同节点**。

常见原因：

- 视角、光照、遮挡导致同一物体描述不同。
- 文本 embedding 把“蓝色杯子”“陶瓷杯”“马克杯”当成不同物体。
- 缺 reference image / ReID 证据，无法跨会话确认同一实例。
- 低置信度自动检测直接写入长期图。
- 分区太粗或太细：太粗会污染，太细会跨分区找不到同一实体。

你们已有的 **有效期过滤器 / confirmation / expectation checker** 是正确方向。调研补充的建议是：

- 物体位置变化不要覆盖旧事实，应让旧事实过期。
- “未发现”不是“不存在”，只有在预期存在 + 主动搜索 + 证据足够时才形成 absence 事件。
- 长期图写入前应做候选实体搜索，避免重复建点。
- 自动降噪和合并可以放到 Nanobot / idle window，不进入实时链路。

## 6. Reference 文件、高质量样本、向量库的位置问题

有效建议：

- Graphiti 不存图片和视觉向量，只存引用、描述、时间事实、实体关系。
- Reference image 是视觉身份基准，应该在文件/对象存储中。
- Sighting image 是最近证据，可短期保存、可清理。
- 高质量样本图库属于视觉/ReID 层，未来可能与 A10 / DINOv2 / 向量库关联。

推荐位置概念：

| 内容 | 建议位置 | 功能 | 理由 |
|:--|:--|:--|:--|
| reference image | `data/snapshots/objects/{object_uuid}/reference.jpg` | 对象身份基准图 | 支撑 L0/L1 图像比对 |
| sighting image | `data/snapshots/sightings/{date}/...jpg` | 最近一次看到的证据 | 支撑审计和短期复核，可 TTL |
| high-quality samples | `data/snapshots/objects/{object_uuid}/samples/` | 多角度样本 | P3/A10/ReID 使用 |
| visual embedding | 待定：FAISS/LanceDB/SQLite/Parquet | 视觉相似检索 | 属于 A10/ReID，不属于 Graphiti |
| textual facts | Graphiti | 长期语义/时间图 | 支撑 GraphRAG 检索 |
| human-editable facts | Obsidian / Markdown | 人类 SSOT | 可读、可编辑、可审计 |

## 7. DSG 潜意识与 Context Injector 的坑点

已有 V1 里 L2-B trigger 已经有 `NOVELTY_ALERT`、`ATTENTION_PEAK`、`MEMORY_MATCH`、`REUNION` 等方向。调研的有效补充是：**触发器不等于都要告诉 LLM**。

需要区分：

- 只更新 L2-B。
- 更新 Blackboard / Scheduler 状态。
- 进入 Context Injector 作为背景。
- 主动让 GOSLO 说出来。
- 触发 ECP 动作。

主要坑点：

- 频繁视觉事件进入 Gemini，会造成注意力漂移。
- 低置信度联想如果不标注来源，会被 LLM 当成事实。
- “情绪/注意力”属于软状态，不应直接变成 Unity 动作。
- Nanobot 任务完成不一定立刻插话，应看当前用户 turn 和认知状态。

推荐字段/概念：

| 推荐字段/概念 | 建议位置 | 代表功能 | 理由 |
|:--|:--|:--|:--|
| `trigger_type` | L2-B trigger | 触发器类型 | 对齐已有 Opus trigger 设计 |
| `attention_weight` | L2-B node / trigger | 是否值得上报 | 已有设计，可继续沿用 |
| `reason` | trigger payload | 为什么触发 | 便于调试和 LLM 理解 |
| `confidence` | trigger / context injection | 置信度 | 防止 tentative 被当事实 |
| `should_say_aloud` | context candidate | 是否建议说出口 | 避免系统日志式插话 |
| `expires_at` | context candidate | 背景有效期 | 防止旧联想污染下一轮 |

## 8. 对 `04` 原提炼稿的修正结论

原 `04` 中以下内容仍有价值：

- Graphiti 不进实时链路。
- L2-B 是工作记忆，Graphiti 是长期时间图。
- Obsidian 应作为人类可编辑 SSOT，而不是 AI 自动乱写区。
- 图爆炸、事实固化、视觉噪声、上下文过载是核心风险。
- Context Injection 需要来源、置信度、是否说出口、有效期。

原 `04` 中以下内容不应作为协议：

- 完整 JSON payload 示例。
- “立即可做 / Sprint4 可做 / P3+”的实施路径判断。
- 未验证的指标、公式、Research 自动生成的协议字段。
- 把 Graphiti 写入和 DSG 工作记忆混成一条强制同步链。

## 9. 后续应聚焦的问题

这些是协议 V2 需要回答的问题，而不是本文件要替你回答：

1. `identify_object` 的 L0/L1/L2 三段返回结果，如何与 ECP / THINKING 体感绑定？
2. `captureSnapshot` 的结果如何成为 DSG、Graphiti、reference image 三方都能追溯的证据？
3. L2-B 从 Graphiti 检索得到的内容，什么时候填进 node，什么时候只作为候选背景？
4. 有效期过滤器如何作用于 Graphiti 回灌事实和 DSG 当前观测？
5. 自建 ASR/TTS 与 Gemini Live 原生管线如何统一 turn timeline？
6. Nanobot 回流结果什么时候进入 L2-B，什么时候进入 Graphiti，什么时候进入 Gemini 上下文？
7. ECP 如何表达软状态和硬动作的边界，避免“情绪/注意力”直接变成前端动作命令？
