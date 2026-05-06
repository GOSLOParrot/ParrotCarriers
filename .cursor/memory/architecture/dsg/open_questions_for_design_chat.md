---
status: ratified
category: workspace-snapshot
status_note: "Chat 2（L1.5 预加载 Node 池 + 状态生命周期 + L2-B 简单升级）需要回答的开放问题清单。本文不回答，仅列出问题；本工作区 sign off 后，由 Chat 2 把每条问题对应的设计稿追加到 architecture/dsg/ 下的设计文档。"
last_reviewed: 2026-05-04
ai_priority: high
ai_audience: "Chat 2（DSG L1.5 池设计 chat） — 入场必读，本文是设计要回答的问题清单"
parent_doc: "workspace_index.md"
---

# 待 Chat 2 回答的开放问题清单

> **本文用途**：把"DSG 当前理解快照"暴露出的设计空缺，按 4 个主题集中列出。Chat 2（L1.5 池设计 + lifecycle 差异化 + L2-B 简单升级）的设计稿要逐条回答。
>
> **本文不做**：不回答问题、不投票、不预判答案。
>
> **范围边界**：A10 入口侧的视觉门控（IoU / CLIP / ReID / 多帧 vote）由 [ConceptGraph SKILL](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md) 承载；本文**不重复** A10 入口问题，仅列出"A10 接入到 L2-B 时的接口面问题"。

---

## §0 用户已决事项汇总（截至 2026-05-06）

> 本文 Q1.1-Q3.4 第一问的用户回答已固化到 [dsg_decisions_master.md](dsg_decisions_master.md)。**Chat 2 入场不再讨论已决事项**，直接以 master 为 SSOT；本文保留 Q&A 原文便于追溯。

| 已决主题 | 在 master 哪一节 |
|:--|:--|
| L1.5 池定位 = 多源 Node 出口管理层 | §1.1 |
| 防爆炸三层门控（A10 端 / L1.5 入池 / L2-B 入图） | §1.2 |
| 桌面分桶（1 主桶 + Obsidian 设定桶 + Google 日程桶）| §1.5 |
| 淘汰算法 priority：特殊节点状态 > 父类节点状态 > 时间 | §1.4 |
| Obsidian 三分类（Ref-加强 / 设定-日常 / 设定-Roleplay） | §3.2 |
| GOSLO 主动发现 priority < USER_EXPLICIT + 短 TTL | §3.3 |
| IDENTIFY_OBJECT lastSeen 永久 + 状态字段简化 | §3.4 |
| GEMINI_ORAL 拆"泛泛之谈" vs "当前场景实体" | §3.4 |
| USER_EXPLICIT 拆 USER_VERBAL / USER_UI | §3.4 |
| `_SOURCE_PRIORITY` 留切换开关 | §3.1 |
| 跨 source 状态机 — 桌面起步共用一套 / 测试期不衰减 | §3.5 |
| 状态变更 observability 三路全开（EcpEvent / obs_log / trigger）| §3.6 |
| **注意力实现路径**：字段层 + RustworkX 机制层**双开放**（混合实施由 Chat 2 调研裁决）| §4 |
| **工作记忆延迟归档**：对话期间不写 Graphiti / 对话结束序列化 / nanobot 闲时统一过滤+LLM | §5 |
| P3 边界（A10 / VPS / 软件建图 / 不可能事件 / 同类第二实例）| §6 |

> 上述 `provisional-revisit-after-L2-design` 状态条目，Chat 2 sign off 后**必须回审**（详见 master §8）。

---

## §1 主题 1 — L1.5 预加载 Node 池

###背景知识

1.我们要先做L1.5和L2-B升级，还是LineB配置（带 ASR 的非原生 Gemini Live 的另一条LiveKit流式语音Agent管线，更能验证后续我们协议升级的，两件事不互相阻塞，但我想知道是否要先完成某一个？）
2.架构里给一些Node轻松 地 按照模式或者 来源 又或者 个人偏好 注意力 等增添一些临时的加强自定义加强或减弱的节点状态 又或者是 参数 和 仿生设计。目前架构缺失什么。最好的办法是什么呢？ 简单地添加不同类型的字段？生命周期？状态？Episode的事件区域折叠和折叠后如何快速连通。内存足够需不需要折叠。。 又或者是RustworkX里通过cluster 或者一些规则和集合来实现功能？包括一些注意力联想通道等仿生设计通过一些RustworkX的机制来完成，RustworkX本就可以用来设定一些社会模型lab实验，我们只是改成用它来实现仿生功能设计。
目前我们的L2组织方式只是用单RustworkX
而L1.5Node列表（相当于来源得到的出口） 可能包括实时计算目前状态和数据（比如记录目前结点的状态数据，比如可信度？），不同来源类型的结点有不同的来源，也可能有不同的置信度规则和状态以及LifeCycle，但不同来源的Node是可能确认为同一结点的，否则可能导致冲突
我们前期调研的的决策和设计是通过加权投票算法来确认是否确信，用后续time等因素的来设计状态变动决策。
但还没有确定预加载池的加载策略，我们要注意策略，我们的软件设计补充是为了低样本全发现已知物体，所以L2-B对新物体的确认应该是在确认不是已知物体，需要注意置信度门控和投票A10 L1.5得到的确认那层置信度投票，有置信度慢慢叠加，但不能出现慢慢确认导致置信度慢慢长时间慢慢随机地增长导致的
且需要注意、或者确认与目前事件相关后才进入L2防止结点爆炸，
虽然桌面场景物体在十几个二十几个根本不会爆炸，所以不同场景应该有不同的策略，桌面会场景爆炸只可能是门控（就算视频采样端的门控加上前端UnityApp门控）设计有问题又或者是，同一个物体被识别成立不同Node，这是各个信息源
L1需要考虑的，在DSG工作区需考虑但与目前任务无关。
3.L2-A构建简单的空间地图而不是导航级别的（导航级别的需要我们用其他软件建图导入并加上多次VPS对齐才能在L2-A再具体实现，是后期任务）
与L2-B的边界是什么呢？要升级成预加载池了，
4.2、3两点说明的问题对目前任务有用的是：
L2-B有多来源的，不只有A10的物体节点信息。
，L1 、 L1.5 和 L2 层需要更清晰的职责和能力边界，L1.5是来源结果，但不同来源的来演结果怎么统一成一列不冗余能匹配对应好UUID的节点，不冲突，是否需要能由不同的置信度和L1信息源来管理，需要具Node类型等等进行分类来决策吗？
5.一些觉得和配置可以先按照桌面场景来，不要过度工程和消耗注意力了。

### Q1.1 池的物理形态

> 当前 L1.5 是**纯合同**层（`SensorFrame` Pydantic frozen），没有"池子"实体。

- 池物理上落在哪里？（in-memory dict / Redis Hash / 单独进程 / `L2BGraph` 内的子集？）
- 池的所有权（owner）：DSG 模块单例？per-session？per-Episode？
- 是否需要 `L1_5Pool` 这个新类，还是把池语义合并进 `L2BGraph`？

相当于L1.5出口得到的Node的列表，但是改成更灵活的池（我不确定？）
因为L2-B跟RustworkX绑的太死，而我不确定，如果要不要多家一层池来灵活管理
Node的出口。用池来连接和指向内存预加载的信息
得看具体的RustworkX机制
因为L2-B不只有物体节点，来源多种多样。改成池方便管理
所以后面
不管把当日Google一键加入Node参与L2-B联想和触发器。
还是一键导入开关加入Obsidian设定节点（不是UUID绑定的加强节点，而是你说的永久权威的Obsidian来源节点）

### Q1.2 入池条件

- 哪些事件会让节点入池？（识别到 / 用户标注 / Obsidian 同步 / Graphiti preload / 主动好奇？）
- 入池时的 `confirmation` 默认值矩阵（按 source 不同？）
- 入池是否需要"幂等键"（label / uuid / spatial bbox）以防重复创建？
类似于触发器，场景切换，Obsidian设定节点。。总之是一大堆预加载触发事件。

### Q1.3 出池条件

- TTL 触发：多久未 attend → 出池？（Opus 19 §2.2 给的"30s未见 → OUT_OF_VIEW"是否仍合理？）
- 池上限：池大小达到多少时主动淘汰？淘汰策略（LRU / LFU / priority）？
- 主动出池：episode close 时哪些节点出池、哪些归档进 Graphiti？
这种得具体场景需要具体设计的内容。别太过度工程了，我们先完成桌面场景
按照2C8G计算。
我们的时间轴和数据标注、观察者记录Episode和事件、对话（包括对话引用到的相关信息和节点、当时的节点快照记录，都能记录下来）只要记录当前的状态就够了。不需要把池记录整个时间轴
对话相关、位置变化（这个当成就改了，虽然也要经过一次过滤器模块，但是绕过了LLM提取三元组）、的留档下来，
至于UUID绑定信息和内存的Ref信息（容易时效），硬盘的Ref信息（也可能失效，但不太容易失效）
性能应该够用，

### Q1.4 状态分桶

- 池内是否按 `confirmation` 分桶（EXPECTED / TENTATIVE / CONFIRMED 三桶）？
- 还是按 `salience` 分桶（FOREGROUND / ACTIVE / BACKGROUND / PERIPHERAL）？
- 还是不分桶，统一存？
桌面先不管，后续再具体场景具体设计
先一个桶，再多来一个Obsidian设定Node桶（设定提示词，不是绑定了graphiti的UUID加强Ref），和一个一键导入Goodgle日程Node（当你想要被提醒的时候？）。
当然这些应该可以一键从RustworkX删除。
总之看你想不想把一些信息源加入工作记忆L2-B的联想机制和触发器等的RustworkX机制作用层。

### Q1.5 优先级 / 大小限制

- 池总大小（节点数 / 字节数）上限？
- 同 kind 的子池是否要分别限上限（如 PERSON ≤ 20 / OBJECT ≤ 50 / EVENT ≤ 30）？
- 触发淘汰时，是否优先淘汰低 priority + 低 salience + 老 last_attended？
哎，桌面场景没那么多性能瓶颈
具体场景具体设计
淘汰策略：
具体节点特殊状态 > 父类节点状态（比如置信度 是否是对话相关 幽灵节点、当前未用的节点删除 ） > 时间
有观察者记录好有用的信息快照存到内存后面先存起来到硬盘待nanobot等对话结束并且系统闲时会启动存入graphiti流程，移除池子的部分不会导致后续留档到graphiti找不到。

### Q1.6 与 L2-B 的关系

- "L1.5 池"和"L2-B `L2BGraph`"是同一物（视图）还是分两层？
- 若分两层，节点的 source-of-truth 在哪？（L1.5 入池 → 升入 L2-B 主图？）
- 若同一物，"L1.5 池"是不是只是 `L2BGraph` 加了 partition 概念？
和你说的差不多，相当于为了L2-B加了一层方便管理的池。
目前为了L2-B设计，节点source of truth 由外部源来控制节点状态，比如AR 和 A10的最后存在位置，。
对于A10 和不同来源的节点合并或者位置冲突，记住L2-B的设计职能是发现后续再设置规则（比如桌面以AR 锚点为主？）：
A10内的CV Flow自己有一层节点合并；记忆中物体的通过UUID对齐；新物体发现防止爆炸只有注意力足够才能进入池子，或按照大种类的背景Node合并（比如杯子等，你不仔细看就是杯子，仔细看才是一杯星巴克的星冰乐）。
用于内存管理，方便查找和指向Ref，也方便一键增删外部源节点。
L2-A后续自己设计于此无关
新物体发现只有注意力足够在进入L2-B，看着一样的物体位置冲突或者报出一个大的冲突，比如一个不可能事件（比如电视瞬移了）报错不进入L1.5状态标为不可信，L2-B提示GOSLO，可以向当用户确认为是同类的第二个物体才进入，这部分目前不需要设计，是后续设计。

---

### Q1.7 工作记忆延迟归档时机（**2026-05-06 新增 — 用户已决约束**）

> 用户原话："工作记忆不会在当场的对话中就通过 Graphiti 存档到 nanobot，快照和 Episode 等会而是先存起来到内存或者硬盘，等对话结束后 且 nanobot 闲时 / 夜间空闲时 才启动存档流程"。详见 [dsg_decisions_master §5](dsg_decisions_master.md)。

**已决约束**（ratified）：

- 对话期间：L2-B + 内存快照 + Ref 表 + 时间轴标注**不写 Graphiti**
- 对话结束：序列化到硬盘
- nanobot 闲时 / 夜间：统一过滤器（含 MemoryValidity）+ LLM → 写 Graphiti

**仍 deferred-to-design 的子问题**（Chat 2 回答）：

- 序列化 schema（JSON / JSONL 字段集）
- 硬盘路径约定（建议 `data/conversations/{conv_id}/...`）
- 对话边界判定（什么算"对话结束"— 用户离开 / 长 idle / 显式信号？）
- nanobot 闲时检测信号（与 nanobot skill 协同）
- 与现有 `l2b_graph.py:start_episode()` 立即 archive 路径的冲突解决方案
- 与 `runner.py:commit_observation` 内 `TODO(S4.B)` 描述的修正

**deferred-to-P3 的子问题**：

- MemoryValidity 过滤器具体 Ebbinghaus 衰减公式 + 置信度阈值（[`module_map_p2 §11.2`](../module_map_p2.md)）

---

## §2 主题 2 — 状态生命周期差异化（按 source）

### Q2.1 Obsidian 来源（USER_TAG_OBSIDIAN）

- 是否需要"权威永久"标记（不可被低 authority 覆盖 / 永不衰减 / 永不 GHOST）？
- Obsidian 节点是否走"push-style 增量同步"直通 L2-B（绕过 Graphiti 中转）？
- Obsidian 节点的 `source_meta` 是否要装 `{obsidian_path, file_mtime, double_link_count}` 等元数据？
需要，设定节点人工维护，但来源权威永久更应该我更想为设定节点
大致按照使用分三种
一种是加强Ref源之一，需要UUID绑定，不是节点而是节点的Ref
一种是真实存在和概念与状态，比如介绍一下家里的沙发和大家具，公用的场景，可以绑定UUID 和作为其他节点的引用，协作的一些设定Ref，可以绑定UUID节点，可以永久权威。相当于是日常使用的设定节点。
一种是自定义设定节点，永久权威，人工管理，不日常使用，打开roleplay模式时存在graphiti的自定义区不污染生活区graphiti，可以自己写设定把你的家设定成中世纪，把一些物品设定成XXX的roleplay模式节点。
（与Google日程一键导入节点其实类似）我们分桶就先分出来的就是这两个。。
但需要区分Obsidian设定节点


### Q2.2 GOSLO 主动发现来源

- **Q2.2.a 关键决策**：是否新增 ObservationSource enum 值（如 `GOSLO_AUTONOMOUS`）？还是用 `source_meta.triggered_by` 字段细分？还是分配给独立的新 filter？
- 主动发现节点 vs 被用户问出来的节点（同样走 IDENTIFY_OBJECT 但触发方不同）的优先级怎么排？
主动发现节点 < 被用户问出来的节点，我现在不知道是否GOSLO使用了这个工具就会说话，毕竟这个工具是主动发现会阻塞对话，再看吧。
- 主动发现节点是否要短 TTL（避免 GOSLO 好奇刷屏）？
非常需要
- 主动发现节点是否参与 episode（影响 Graphiti 归档量）？
主动发现参与L2-B，也参与观察者和时间轴的数据标注啊，记录快照会记录对话激活的Node和Ref等信息，和L3，甚至天气用户情绪状态等。。。

### Q2.3 已有 source（IDENTIFY_OBJECT / GEMINI_ORAL / USER_EXPLICIT / MOCK）

- IDENTIFY_OBJECT 命中节点：多久未再见到要不要降回 TENTATIVE？多久要不要 GHOST？
上次见lastSeen到是永久保存的，但除了这个字段，节点状态感觉没有那么多必要，主要需要按照具体场景具体设计，因为对话持续时间好像有个上限，平时不会用那么久，而graphiti前有一个有效期预测模块（也就是graphiti前的那个）

- GEMINI_ORAL 实体：是否应区分"泛泛之谈"vs"当前场景实体"？要不要短 TTL？
确实需要区分

- USER_EXPLICIT：是否拆 USER_VERBAL / USER_UI 二级分类？
这个可以有

- 5 个 source 走同一 `_SOURCE_PRIORITY` 数值表是否仍合理？
这样后续肯能需要依靠场景切换或者其他触发器和GOSLO状态等的信息，来切换数值，所以可以留个开关

### Q2.4 未来 A10 来源（**2026-05-06 用户已决：推迟到 P3 / A10 独立设计 chat**）

- A10 接入时 `register_source_meta_factory("cv_a10", ...)` 装哪些字段？（参考 [ConceptGraph SKILL §3.4](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)：`clip_ft / track_id / num_frames_seen / vlm_object_tag / bbox_3d_center / last_seen_frame`）

只需要，我们再设计Node基础类（父类）的时候考虑一下A10接入时的扩展性就行了吗？
我现在不是很确定

- A10 节点是否需要**自动 confidence decay**（ConceptGraph SKILL §8a Q8 外观漂移问题）？这会触发 [ADR-L1.5-001 §4.1 第 2 条升级条件](../adr_l1_5_source_dispatch_extension_space_20260504.md)。
- A10 与现有 IDENTIFY_OBJECT 节点的合并策略（`reid_hash` 跨 source ReID）？
目前对已有和记忆中的的Node是UUID来合并。对于新物体，以及内存先发现物体，我们目前的是先看内存描述和图片frame用LLM进行对比并入。而A10的出口是L1.5入口，还没经由graphiti等的记录，没有已绑定的UUID，没有描述，只有大类和临时的技术栈memory Bank来track和临时的id，无法赋予UUID，所以会导致冲突，我们到时候对已有物体和简单样本（可能有专门的样本库），进行绑定UUID需要适配好绑定和确认机制，然后再把新物体和没样本匹配的任务留到p3....。比如以及A10怎么夸区来认出对比图片库，是不是该把高质量图片帧给加入A10样本库或者拉进工作流（这些都是需要单开的设计，A10部分的设计）
至于目前先解决的合并冲突，我们A10部分SAM2 + DINO2 的CV Flow的理念是，为了L2-A，低样本甚至零样本全发现记忆里的物体和新物体，具体设计需要多看看，后续简单导航和VPS来设定的，应该有自己的一套设计。只要能靠UUID让graphiti和L2-B给 L2-A给套上一层info就行，目前没必要全发现记录新物体到L2-B，冲突不严重。
要我先决策

研究这个不如到了A10独立设计阶段 还需要先看看怎么适配AR坐标手机传感器数据 和 SAM2 + DINOv2 和ConceptGraph 和 其他软件建图和禁飞区导入Map到Unity并导航+VPS 三者呢，这些都是p3要搞的。。

### Q2.5 跨 source 状态机

- 是否所有 source 共享统一状态机（EXPECTED → ACTIVE → PERIPHERAL → GHOST）？还是各 source 子状态机？
哎，目前先一样的，不代表后续会一样。到时候看要按照Node种类搞还是。那是之后的事情了
我们得先做完桌面场景物体节点/ 第一种抽象节点的 两个状态机闭环，按需求和场景填补好设计空白

- GHOST 转换条件：单 source 单维 evidence_score 阈值 vs 多因素综合（[Opus 19 §2.3](../../../docs/InfoCollections/Opus/19_anomaly_ghost_expectation_vision.md)）？
- novelty 衰减是否启用？衰减半衰期？（[Opus 17 §0.2 H](../../../docs/InfoCollections/Opus/17_dsg_node_and_trigger_design.md)）
- habituation 累加是否启用？
测试的时候先不衰减吧，桌面场景物体不多。后期好加的。


### Q2.6 状态变更的 observability

- 状态转换是否要发 EcpEvent 通知 Unity？（Phase 4 wire 已锁，加新 EcpEventType 需新 ADR）
- 状态转换是否要写 `obs_log`（已有 `log_obs_event` 基础设施）？
- 状态转换是否要触发 trigger（如 `ATTENTION_DECAY` → 让 Brain 知道节点不再活跃）？

为了覆盖测试可以都写一点测试需求的

---

## §3 主题 3 — L2-B 组织方式简单升级（保留复杂仿生空间）

### Q3.1 单图 vs 多图

- 当前是单 `PyDiGraph`；是否拆"短期池子图 + 长期记忆图"（避免 working memory 太大慢搜索）？
我们桌面一个足够了，但后期我们有Node生命周期，池管理，和RustworkX的Scene切换/时间轴切换 的有相关的子图折叠，通道和Cluster的设计啊
- 是否按 NodeKind 拆子图（PERSON / OBJECT / EVENT / PHOTO 各自一图）？还是按 episode 拆？
L2-B最主要的目的就算联系各个Node作为潜意识，后面你可以自己开个冗余子图，但主图除了特殊Node种类最好不要分。
- 跨子图的边怎么处理（特别是 PART_OF_EPISODE / HAS_PHOTO 这类天然跨边的关系）？
RustworkX有Cluster和子图和Cluster的折叠设计机制，联系也有跨子图和Cluster的跃迁通道设计。

### Q3.2 索引 / 查询

- 当前查询路径：`get_node_by_label`（线性扫描）；要不要建 label 反向索引？
- 当前注意力查询：`query_by_attention`（线性 sort）；节点数 >100 时是否瓶颈？
- 是否引入"按 source 查询"路径（runner 当前线性扫描所有节点找 obsidian_uuid 匹配）？
按照需求和建议来。符合我们的需求就行，最好，配置轻松方便？（不方便就算了），因为后面依旧是具体场景具体优化的问题，不要过分消耗注意力和过度工程

### Q3.3 衰减 / 注意力扩散

- 是否启用 attention 衰减（每 tick 自动 -0.05 之类）？
- 是否启用注意力扩散（高 attention 节点把邻居拉高）？— 这是 Opus 17 §5.3 Posner 模型的"top-down focus"
- 衰减 / 扩散的执行节奏（每 EcpState tick / 每秒 / 每帧）？
这些都是L2-B的组织方式和仿生设计，我们需要现在需要先确定好的是，几种触发器，几种算法，可用的RustworkX机制和匹配的组织方式不是吗？

> **2026-05-06 修正**：注意力实现路径**双开放**（字段层 vs RustworkX 机制层）— 由 Chat 2 调研 4 新 skill 后裁决；详见 [dsg_decisions_master §4](dsg_decisions_master.md) + [dsg_current_state_distilled §5.4](dsg_current_state_distilled.md)。**测试期不衰减**已 ratified，长期参数 deferred-to-design。

### Q3.4 复杂仿生空间留白

> 用户原话："简单升级，留有复杂仿生设计空间"。

- 当前 L2-B 简单升级**不实施**：(a) 多模态联想 (b) 期望-实际差驱动的 GHOST (c) 多因素 evidence 加权
- 但要**预留位置**：哪些字段 / 接口 / 注释要在简单升级时加，让 Phase 5+ 仿生升级可以"插入"而不重构？
同Q3.3所说

> **2026-05-06 修正**：仿生路径选项已由 4 新 skill（[dsg-rustworkx-master](../../../skills/dsg-rustworkx-master/SKILL.md) §3 4 范式 / [dsg-l2b-node-organization-options](../../../skills/dsg-l2b-node-organization-options/SKILL.md) §6.5 P1-P4 / [dsg-attention-schema-papers](../../../skills/dsg-attention-schema-papers/SKILL.md)）给出选项库；Chat 2 在 4 个候选 + 混合中选 + 规划字段 / 接口 / 注释预留位置。

### Q3.5 与 EpisodeMarker 的边界

- Episode 关闭时是否影响节点 lifecycle？（如 episode 关闭时把所有 ACTIVE 降回 PERIPHERAL）
应该是需要的，模拟注意力自然减弱自然是有必要的，记录好这个问题，我们后续可以单独开一个设计。这个能力很好加没有相关的架构问题。所以现在不重要
但这个衰减需要更仿生一点，这样设计不够自然，目前我的设计还是更倾向于通过RustworkX的机制 比如子图/Cluster/折叠 等的L2-B组织方式来模拟，我们可以先归纳出RustworkX的能力边界和方式，你的计划也一起在最后作为可行方案和仿生设计通道补充好就行了。
这部分应该单开在仿生设计那块？应该也是一些P2.5 ~ P3的事情了，目前应该不阻碍架构和协议升级。

- Episode 跨度内的"短瞬性"节点（如 PHOTO）是否在 close 时自动归档？
- 多 Episode 同时存在（嵌套 / 并行）的可能性是否要保留？（当前 `_current_episode_id` 单值，不支持嵌套）


---

## §4 主题 4 — 与现有锁的交互

### Q4.1 ADR-L1.5-001 §4.1 子类化触发条件核对

设计完成后**必须**回答：

- 是否触发 ① ≥3 字段差异 → 走 typed model 升级？
- 是否触发 ② ≥2 source 行为多态（如 A10 自动 decay vs Obsidian 不 decay）→ 走 SemanticNode 子类化？
- 是否触发 ③ isinstance 反复手写 → 走 typed dispatch？

如果**任一触发**：Chat 2 设计稿需要起新 ADR `supersedes: [ADR-L1.5-001]`，明确 axis。
如果**全部未触发**：在设计稿中显式声明 "ADR-L1.5-001 §4.1 三条触发器仍未满足，继续走 meta dict + factory hybrid"。

### Q4.2 Phase 4 §8 决策锁不动性核对

设计稿落代码前**必须**核对未触动以下任一项（[entry §8](../sprint4_phase4_entry_20260430.md)）：

- L1：NodeKind 6 项 / EdgeKind 8 项不增删（任何新增需新 schema_version）
- L7：PhotoEvent 不自动建 ObjectNode
- L9：Δ_focus=0.2 / Δ_bbox=1.0 / threshold=1.0；阈值器在 dsg/attention 不塞 BB
- L11：identify_object 1.9s 总预算
- L13：dsg/attention/__init__ 不 export Attention 类符号

### Q4.3 跨语言守护核对

- 设计是否动 `EcpEventType` / `EcpEventSource` / topic 常量？若动，`test_cs_parity` 4/4 守护**必失败**，需同步改 C# DTO + 起新 ADR。
- 当前期望：**不动 wire**（按 ADR-L1.5-001 §2.1 Q1 决策，source dispatch 仅 Python）。

### Q4.4 Observer / Attention 边界核对（[parrot_behavior_rules §3.7](../../parrot_behavior_rules.md)）

- 设计是否让 Observer 写 SemanticNode.attention？❌ 违反边界
- 设计是否让 Attention 抓帧 / 写 Graphiti？❌ 违反边界
- attention/threshold.py 是否塞 BB？❌ 违反 L9 锁

### Q4.5 测试基线维持

- 当前 234/234 pytest 基线（含 ADR-L1.5-001 +11 项）
- 设计落地后新增测试**最低**预期：
  - L1.5 池入/出池 happy path
  - 各 source factory 注册 + 取出
  - lifecycle 状态转换（EXPECTED → ACTIVE → GHOST 等）
  - 与已有 cs_parity / 11 项 source dispatch 测试 0 冲突

---

## §5 答题输出格式（给 Chat 2 的提示）

Chat 2 完成设计后**应**产出：

- `architecture/dsg/dsg_l1_5_pool_and_lifecycle_design_<date>.md` — 设计稿（按本文 §1-§4 顺序逐条回答）
- 必要时新 ADR：`architecture/adr_dsg_lifecycle_<topic>_<date>.md` — 若触发 ADR-L1.5-001 §4.1 升级
- 测试占位（不实施）：`tests/test_dsg/test_l1_5_pool_lifecycle.py` 测试设计

**Chat 2 设计稿不需要**：

- 不实施代码（实施留独立 chat）
- 不写完成报告（完成报告在实施 chat sign off 后）

详见 [sprint4_phase4_downstream_chat_dispatch_plan_20260504.md §1.1 Chat 2](../sprint4_phase4_downstream_chat_dispatch_plan_20260504.md)。

---

## §6 引用

- 当前理解快照：[dsg_current_state_distilled.md](dsg_current_state_distilled.md)
- Source × lifecycle 现状：[source_x_lifecycle_status.md](source_x_lifecycle_status.md)
- Opus 蒸馏：[opus_dsg_residual_intent.md](opus_dsg_residual_intent.md)
- ADR-L1.5-001：[../adr_l1_5_source_dispatch_extension_space_20260504.md](../adr_l1_5_source_dispatch_extension_space_20260504.md)
- ConceptGraph SKILL：[../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md](../../../skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md)
- Phase 4 锁：[../sprint4_phase4_entry_20260430.md §8](../sprint4_phase4_entry_20260430.md)
- 行为边界：[../../parrot_behavior_rules.md](../../parrot_behavior_rules.md)
