# 架构决策日志 (Architecture Decision Record)

> 用途: 记录本轮设计讨论中的关键决策、转折点和被否决的方案
> 给谁看: 给未来的自己 + 新项目的 AI 助手加载上下文
> 原始对话: Cursor agent-transcripts (本项目内部保留)

---

## ADR-001: 废弃旧 DSG 设计，全新架构

- **背景**: 旧项目直连 Gemini WebSocket + XML 注入，DSG 只有 L1/L2 两层
- **决策**: 从零开始设计，不复用旧代码，只继承部分概念 (RustworkX、Graphiti)
- **理由**: LiveKit Agents 提供了更好的基础设施；旧 Gemini 交互模式已过时
- **否决方案**: 在旧项目上渐进改造 → 拒绝，技术债太重

## ADR-002: DSG 四层仿生架构 (用户提出的关键转折)

- **背景**: 初始方案是 L2-A=RustworkX 空间图 + L2-B=Graphiti 被动缓存
- **用户洞察**: "L2-B 不应该是被动缓存，应该也是 RustworkX 图，有注意力机制和触发器"
- **决策**: L2-B 升级为 RustworkX 活图 + 仿生注意力系统，Graphiti 降为后端存储
- **新增 L3**: 用户提出需要一个"前额叶接口"来做 Gemini 事件分割
- **理由**: 仿生设计 (背侧/腹侧通路) 更清晰地分离了"在哪"和"是什么"的职责
- **影响**: 这是整个架构最大的一次升级，所有后续设计基于此四层结构

## ADR-003: 稳定性门控 (StabilityGate)

- **背景**: 用户在旧项目用摄像头测试时出现"严重跳变"
- **用户洞察**: "手持环境和 SVA 固定视角完全不同，很多视觉功能只在稳定时才该运行"
- **决策**: 设计 4 级门控 (Lost/Shaking/Moving/Stable) + On-Demand 模式
- **否决方案**: 照搬 SVA 的全时处理 → 拒绝，帧模糊时会产生大量错误 track
- **关键学习**: ARCore 的 TrackingState 和 NotTrackingReason 是天然的门控信号

## ADR-004: 前端设备 = 安卓手机

- **决策**: 明确目标设备为安卓手机 (非头显/iOS)
- **影响**: ARCore (非 ARKit)、所有视觉模型在云端、IMU 噪声较大需调参

## ADR-005: 场景管理 (室外/室内/桌面)

- **用户需求**: MVP 先做家里+桌面，但要为场景切换预留位置
- **决策**: SceneProfile 配置化 + switch_scene Tool + L2 折叠/展开
- **关键设计**: 场景折叠 = 序列化 RustworkX 图 + 保存注意力状态；展开时有"久别重逢"增益
- **归属模块**: L1 SceneManager (因为 L1 拥有 ARCore 遥测)
- **MVP 范围**: 只实现 DESKTOP + INDOOR，OUTDOOR 留 Phase 2

## ADR-006: LiveKit 事件可获取 Gemini 完整上下文

- **用户担忧**: "不清楚能不能拿到 Gemini 的上下文和思维链"
- **调研结论**: `conversation_item_added` 捕获每条对话，`function_tools_executed` 捕获每次 Tool Call
- **决策**: L3 Observer 同时从 LiveKit 事件和 L2-B 触发器获取数据，合流为 Timeline
- **否决方案**: 依赖 Observer 独立猜测 Gemini 在想什么 → 不需要，LiveKit 已提供数据

## ADR-007: Graphiti 5 分区 (group_id 隔离)

- **用户担忧**: "怕关系混乱，物体/关键词/情景混在一起"
- **调研发现**: Graphiti 原生支持 group_id 命名空间隔离
- **决策**: 5 个分区 — episodic / objects / personality / vocabulary / nanobot_research
- **关键设计**: source_description 引导不同分区的三元组提取策略 (角色化提取)

## ADR-008: 鹦鹉人设 = SOUL + 模式叠加

- **用户需求**: 维护鹦鹉人设，可能需要管家模式等角色切换
- **参考**: OpenClaw SOUL.md (可编程灵魂)
- **决策**: ParrotSoul (静态核心 + Graphiti personality 动态记忆) + BehaviorMode Flag 叠加
- **否决方案 A**: 换 SOUL 文件 → 身份边界模糊
- **否决方案 B**: LiveKit Agent Handoff → 上下文丢失、人格不一致
- **关键洞察**: 管家模式是"同一只鹦鹉戴管家帽子"，不是换一只鹦鹉

## ADR-009: 模块通信 = 混合模式

- **决策**: 管道(感知链) + 导演(L3↔Gemini) + 黑板+PubSub(Redis) + 分区黑板(Graphiti)
- **参考**: Inworld AI Director Layer、LLM Blackboard 论文 (2025)、CrewAI 角色编排
- **关键设计**: Observer 拆分为 4 个独立消费者 (Perception/Conversation/Atmosphere/Archive)

## ADR-010: 后端调度器 = py-trees 行为树

- **用户发现**: "任务调度涉及很复杂的并行/中断/优先级"
- **澄清**: 前端状态机 (动画) ≠ 后端状态机 (决策)，是两个不同的东西
- **决策**: 后端用 py-trees 行为树 + 4 通道资源锁；前端用 Unity Animator HFSM + 多动画层
- **参考**: Subsumption Architecture (Brooks)、Halo AI、The Sims Utility AI、FlexBE OBE/OCS 分离
- **MVP 降级**: Phase 1-2 用简单三级路由，Phase 3 升级到 py-trees

## ADR-011: 前后端同步 = 权威服务器 + 客户端预测

- **决策**: 后端是权威 (做所有决策)，前端是执行器 (动画+物理) + 预测器 (延迟掩盖)
- **参考**: Gabriel Gambetta 权威服务器教程、Unity Netcode 客户端预测
- **DataChannel 协议**: 后端→前端 (body_cmd/head_cmd/emotion_cmd)，前端→后端 (telemetry/gesture/anim_event)
- **客户端预测**: 手势→立刻播放预测动画→后端确认后平滑过渡

## ADR-012: 物体体积感知与鹦鹉运动约束 (场景推演审计)

- **背景**: 场景推演发现 fly_to 缺失；用户追问"鹦鹉怎么知道物体多大？怎么避免飞进墙里？"
- **调研**: ARCore 在无 LiDAR 安卓手机上: 平面检测(好)、单目深度图(粗糙±30cm)、3D BBox(实验性)
- **决策**: 三层近似 — Tier A: AR 平面(可靠) → Tier B: 深度+SAM2 mask(粗略) → Tier C: 3D BBox(受限)
- **MVP 范围**: 鹦鹉在 AR 平面上行走/跳舞 + 平面间飞行 + 平面边缘不越界。停在具体物体上留 Phase 2
- **关键约束**: 精确 3D 碰撞需要 LiDAR，安卓手机不在计划内

## ADR-013: 物理恒常性与视觉模型能力边界 (场景推演审计)

- **用户洞察**: "鹦鹉无法认出场景，地图是缺失和难以识别的"
- **决策**: 飞往视野外物体的能力是**可选的**，取决于 ARCore 锚点有效性和视觉模型能力
- **设计原则**: L2 节点状态需更丰富 (不只是 VISIBLE/LOST)，核心是**物理恒常性** — 离开视野 ≠ 消失
- **能力边界声明**: 不假设全局 SLAM/地图匹配可用；DSG 功能按"能力探测"动态启停

## ADR-014: 场景推演优先级重排 (用户审计)

- **变更**: #4(场景退化) 和 #5(自动跟随) 从 P0 降为 P2 (后期细节设计)
- **确认 P0**: #9(APP 生命周期) + #13(网络降级) 为 MVP 必须
- **新增 MVP 需求**: 鹦鹉在平面上行走和跳舞

## ADR-015: DSG 节点类继承体系 — 借鉴 Spark-DSG 但适配 AR 环境

- **背景**: 之前的节点设计是扁平的 `SpatialNode` / `SemanticNode` 两个 dataclass，缺乏继承体系
- **调研**: Spark-DSG C++ 源码 (`node_attributes.h`) 有完整的 6 级继承: NodeAttributes → SemanticNodeAttributes → ObjectNodeAttributes/RoomNodeAttributes/PlaceNodeAttributes/AgentNodeAttributes → KhronosObjectAttributes
- **决策**: L2-A 采用 `DSGNode → SpatialNode → ObjectNode/SurfaceNode/ZoneNode/HandNode/ParrotAnchorNode`；L2-B 采用 `DSGNode → SemanticNode → ObjectSemanticNode/SurfaceSemanticNode/...`
- **否决方案**: 完全扁平 (不继承) → 代码重复多、扩展难；直接用 Spark-DSG → C++ 依赖、API 假设 3D 点云输入
- **关键设计**: L2-A/L2-B 共享 `DSGNode` 基类但分支独立，通过 UUID 关联

## ADR-016: Graphiti 自定义实体类型

- **背景**: Graphiti 默认会提取通用 EntityNode，但我们需要结构化的物体/人物/地点知识
- **调研**: Graphiti 2025 年已支持通过 Pydantic BaseModel 定义自定义实体和边类型，`add_episode()` 接受 `entity_types` / `edge_types` / `edge_type_map` 参数
- **决策**: 定义 PhysicalObject/Place/Person/Habit/Concept 五种实体类型 + OwnershipEdge/UsageEdge/LocationEdge 三种边类型
- **关键约束**: 受保护字段不能做自定义属性 (`uuid`, `name`, `group_id` 等)；所有自定义属性必须 Optional
- **与 L2-B 的关系**: L2-B `ObjectSemanticNode` 的持久化版本就是 Graphiti `PhysicalObject`

## ADR-017: 触发器分层过滤 — 避免信息洪水

- **背景**: L1 30fps 帧处理，如果每帧都推事件到 Gemini 会造成刷屏
- **决策**: 四级过滤链 — L1(NoiseFilter) → L2-A(仅有意义变化) → L2-B(attention>阈值) → L3(_is_significant())
- **事件格式**: `L1Event`(物理) → `L2AEvent`(空间) → `L2BTrigger`(语义) → `ContextInjection`(文本)
- **关键设计**: 每层有独立的过滤逻辑和阈值，由 SceneProfile 控制

## ADR-018: 场景特化 — 共享类体系 + 不同配置

- **背景**: Desktop 和 Indoor 的节点类型相同，但距离阈值、触发规则、注意力参数差异大
- **决策**: 不为场景创建不同的节点子类，而是通过 SceneProfile 参数和 TriggerRules 策略类特化行为
- **否决方案**: 为 Desktop/Indoor 各写一套 Node → 大量代码重复
- **关键设计**: `DesktopTriggerRules` / `IndoorTriggerRules` 策略类控制什么事件值得上报

## ADR-019: L1 三层缓冲 (Stability + Label + Position)

- **背景**: 当前 L1 只有 StabilityGate 一层缓冲，标签跳变和位置抖动直接推到 L2-A 造成噪声
- **决策**: 增加 LabelBuffer (滑动窗口投票, 5帧) + PositionBuffer (EMA平滑 + 空间阈值)
- **设计**: 每个缓冲器 <30 行代码，极简；参数由 SceneProfile 控制
- **否决方案**: 更复杂的卡尔曼滤波 → MVP 阶段过度

## ADR-020: 节点置信度 = 6 维加权评分

- **背景**: 需要一个综合指标回答"这个节点可信吗？"
- **决策**: tracking(0.30) + position(0.25) + identity(0.20) + memory(0.10) + anchor(0.10) + temporal(0.05) 加权
- **每个维度有明确的输入**: Tier/blur/light → tracking; FeatureMapQuality/anchor → position; votes/ReID/Graphiti → identity
- **用途**: 影响 L2-B 注意力权重、L3 是否报告给 Gemini、fly_to 目标可信度

## ADR-021: 方位感知 = 罗盘 + ARCore Pose 互校

- **用户问题**: "传感器能否分清方位来认识场景？"
- **调研结论**: 磁力计可提供绝对方向(磁北)，但室内精度受限(±5-15°，干扰时更差)
- **决策**: 实现 SpatialOrientation 模块，能做到"前方有桌子"但做不到 SLAM 导航
- **互校机制**: 罗盘 heading 和 ARCore yaw 差异 > 20° 时判定磁场干扰，放弃绝对方向

## ADR-022: 节点生命周期区分短暂遮挡 vs 真正离开

- **背景**: 用户转头 2 秒和走到另一个房间不应该触发相同的节点状态处理
- **决策**: 遮挡计时器 — <3s 直接恢复(不做ReID), 3-30s 需 ReID, >30s OUT_OF_VIEW
- **ANCHORED 特殊处理**: 有锚点的节点不受转头影响，只有明确被移走才改状态
- **TTL 差异化**: 大家具永不删除，小物品 30min TTL，手部 10s TTL

## ADR-027: 确认存在 vs 确认不存在的不对称处理

- **用户洞察**: "确认笔记本在桌上"和"确认笔记本不在桌上"流程完全不同
- **认识论基础**: 看到=强证据(false positive 低); 没看到=弱证据(可能被挡/光照差/没往那看)
- **决策**: EvidenceAccumulator 对负面证据施加 4 个限制条件:
  1. `NEGATIVE_REQUIRES_FRUSTUM`: 预期位置必须在视锥体内
  2. `tier >= 3`: 视觉必须在最可靠状态
  3. `light_level >= 100`: 暗环境扣分减弱至 30%
  4. `NEGATIVE_COOLDOWN = 10s`: 不能连续扣分
- **确认存在**: ~2s (几帧正面证据即可)
- **确认不存在**: 30s~2min (需要持续的、条件合格的负面累积)
- **设计原则**: 宁假阳不假阴

## ADR-028: 细粒度识别 = Gemini 裁切图, 不引入新模型

- **用户问题**: YOLO-World 只能检测 "bottle"/"cup", 无法识别奶茶品牌/手办型号/药品名
- **方案**: 裁切物体 mask 区域, 作为图像发给已有的 Gemini 通道做详细描述
- **不引入新模型**: Gemini 本身就具备 OCR + 商品识别 + 常识推理能力, 足够用
- **触发时机**: 用户驱动 / Gemini focus_on 后主动 / NEW_UNEXPECTED 自动触发
- **结果存储**: ObjectNode.fine_description 字段, 标签权威链中属 gemini_described 级别
- **不会混乱**: 它是对现有 YOLO 标签的补充而非替代; 95% 时间不运行

---

## ADR-023: NodeState 新增 EXPECTED — 幽灵节点的正式身份

- **背景**: 预加载场景时节点存在于记忆/锚点中但未视觉确认
- **决策**: 新增 `NodeState.EXPECTED` 状态, 通过 `EvidenceAccumulator` 累积确认
- **流程**: EXPECTED → (证据累积>0.6) → ACTIVE; EXPECTED → (30s 无确认 / 累积<-0.3) → OUT_OF_VIEW
- **否决方案**: 直接用 ACTIVE (太乐观, 报告不存在的物体) 或 LOST (太悲观, 丢弃记忆)

## ADR-024: 证据累积式确认, 非全有全无

- **用户问题**: "多因素证据会不会导致混乱？有时一个条件就够了"
- **决策**: 贝叶斯式分数累积: SAM2(+0.25) + YOLO匹配(+0.15) + ReID(+0.20) + 位置(+0.15) + Surface(+0.10) + 锚点(+0.15) + 记忆(+0.05)
- **关键设计**: 用户确认 = +1.0 (一击必杀); 阈值: >0.6 确认, <-0.3 否定 (幽灵)
- **不会混乱**: 每条证据独立加分, 只有一个判定出口 (confirmed/ghost/uncertain)

## ADR-025: ExpectationChecker — 预期偏离作为一等触发器

- **背景**: 主动感知需要"预期", "笔记本不见了"比"我看到了杯子"更有价值
- **决策**: L2-A 扫描完成后运行 ExpectationChecker, 产生 EXPECTATION_VIOLATED 触发器
- **4种偏离**: OBJECT_MISSING / OBJECT_DISPLACED / NEW_UNEXPECTED / COUNT_CHANGED
- **预期来源**: 当前会话(高可靠) > 上次会话(中) > Graphiti长期(低)

## ADR-026: 视觉模型标签权威链

- **背景**: YOLO-World / DINOv2 ReID / Gemini / 用户可能给出不同标签
- **决策**: 严格权威: user_named > gemini_identified > reid_confirmed > yolo_voted > yolo_single
- **每个时刻只有一个标签** (class_label), 高权威覆盖低权威; 完整历史在 class_votes

---

## 讨论中涌现的关键参考项目

| 项目 | 首次提及原因 | 学到什么 |
|:-----|:-----------|:---------|
| LiveKit Agents | 基础设施选型 | AgentSession, DataChannel, Events, Handoff, Task |
| SVA (Stream Vision Agents) | 视觉处理器模式 | Processor 分发, 帧率控制, 上下文注入 |
| Spark-DSG / Hydra | L2-A 分层空间图 | Objects→Surfaces→Zones 三层分级 |
| FROSS | L2-A 位置表示 | 3D 高斯 (均值+协方差) |
| Graphiti | 长期记忆 | group_id 分区, Leiden 社区, 三元组提取 |
| OpenClaw | 鹦鹉人设 | SOUL.md, MEMORY.md, 可编程灵魂 |
| Inworld AI | 多角色交互 | Director Layer, 长期记忆矛盾消解 |
| CrewAI | 模块通信 | 角色化 Agent, 四层记忆, 作用域隔离 |
| py-trees | 后端调度器 | Python 行为树, 黑板, 并行/序列 |
| Subsumption (Brooks) | 优先级设计理念 | 层级行为, 高层抑制低层 |
| Gabriel Gambetta | 前后端同步 | 权威服务器, 客户端预测 |
| Hindsight (2025 论文) | 记忆架构 | 四网络记忆: 事实/经验/摘要/信念 |
| LLM Blackboard (2025 论文) | 多 Agent 协作 | 黑板自愿响应, 13-57% 提升 |
| ConceptGraphs (ICRA 2024) | L2-A 节点设计 | 开放词汇3D场景图, 多视角融合, CLIP embedding |
| 3DSSG (Stanford) | L2-A 关系标注 | ON/NEAR/IN/ABOVE 标准化空间关系体系 |
| Microsoft GraphRAG | L2-B 社区检测 | Leiden社区 + 层级摘要, SearchFilters |

---

## ADR-029: LiveKit Unity SDK 选型修正

- **日期**: 2026-02-24
- **状态**: 已决策
- **背景**: 原以为 LiveKit Unity SDK 仅支持 WebGL，需要为 Android 原生另做桥接
- **发现**: `livekit/client-sdk-unity` (v1.3.3) 原生支持 Android/iOS/Windows/macOS/Linux，功能包含 RPC、文本流、字节流、视频发布
- **决策**: 直接使用 `client-sdk-unity` 原生 SDK，不走 WebGL
- **影响**: 简化了前端架构，RPC 可替代部分 DataChannel 手动协议; 文本流可用于上下文注入

## ADR-030: Zep×LiveKit vs Graphiti 自托管 (已决策)

- **日期**: 2026-02-24
- **状态**: **已决策 → 方案 B (Graphiti 自托管)**
- **背景**: `zep-livekit` 包提供 `ZepUserAgent` + `ZepGraphAgent`，但依赖 `zep-cloud` SDK
- **深入发现**:
  - zep-livekit 强制依赖 Zep Cloud API (不支持纯自托管 Graphiti)
  - Zep Community Edition 已废弃 (2025)
  - 包仅 v0.1.0, 月下载 ~200, 成熟度不足
  - Graphiti 本身 22k+ stars, 独立可用 (Apache 2.0)
  - group_id 命名空间在 Graphiti 原生支持, 可满足多角色分区
- **决策**: MVP 用 Graphiti 自托管 (Docker + Neo4j), 参考 zep-livekit 源码实现简化版集成
- **核心理由**:
  1. 数据必须自己持有, 不依赖第三方云 (Zep Cloud 是黑盒)
  2. Neo4j Browser (localhost:7474) 提供图谱可视化和手动编辑能力, 后续可在此基础上建控制台
  3. Graphiti 本身 22k+ stars, Apache 2.0, 足够成熟
  4. zep-livekit 源码可作为 LiveKit↔记忆系统 集成的参考模板
- **影响**: 不被 Zep Cloud 绑定; 需自建 LiveKit ↔ Graphiti 桥接; Neo4j 可视化能力即刻可用

## ADR-031: Livia 论文作为架构参考

- **日期**: 2026-02-24
- **状态**: 已记录 (已完整阅读论文)
- **背景**: 发现 Livia (arXiv:2509.05298, UC Berkeley+NYU, 2025-08) 与我们的项目高度相似
- **关键对照**: 模块化AI代理(≈Observer拆分), TBC记忆压缩(≈Graphiti归档), DIMF重要性过滤(≈L2-B注意力), AR具身(≈鹦鹉)
- **值得借鉴**: TBC 层级时间窗归档策略; DIMF 用户反馈保留 ("别忘了这个!"); 评估框架 (50用户/4周/Cohen's κ)
- **决策**: 将 Livia 纳入核心参考, TBC 策略用于 Archive Observer, DIMF 用户纠正纳入记忆设计

## ADR-032: LiveKit Tool Forwarding 替代手动 DataChannel 协议

- **日期**: 2026-02-24
- **状态**: 已决策
- **背景**: 原设计 Gemini Tool Call (fly_to/focus_on 等) 通过手动 DataChannel JSON 协议传给 Unity
- **发现**: LiveKit 原生支持 `@function_tool` → `perform_rpc()` → Unity `RegisterRpcMethod()` 模式
- **优势**: 类型安全 (method+payload) / 超时控制 / 错误码 / 双向返回值 / 官方 Unity 示例
- **决策**: Gemini Tool Call 统一通过 RPC 转发到 Unity, 不再手写 DataChannel JSON 协议
- **影响**: 大幅简化前后端通信代码; DataChannel 仅保留给高频 telemetry (Lossy 模式)
