# P2 里程碑: 记忆共享 + Scheduler 增强 + DSG 耦合层

> 最后更新: 2026-04-20
> 状态: **代码就绪** — 待一次 Castle 线上 P2 拉起（FalkorDB 容器 + Graphiti 端到端） + AR 项目搭建
> 下一步：见 `active_context.md` §下一步 本周关键路径
> 计划文件: `c:\Users\Bin\.cursor\plans\p2_development_roadmap_70d9e51c.plan.md`

---

## 一、P2 目标摘要

P2 的核心目标是为后续独立模块开发建立三大前提：

1. **Graphiti 记忆共享** — FalkorDB 替代 Neo4j，4 个 group_id 分区，Brain/Nanobot 双向读写
2. **Scheduler 增强** — BehaviorMode 动态切换 + Context Injector 上下文注入
3. **DSG 耦合层** — 非独立模块，用模拟 L1 输出走通 DSG↔Graphiti↔Brain 真实接口链路

---

## 二、关键架构决策

### D-P2-1: FalkorDB 替代 Neo4j

| 指标 | FalkorDB | Neo4j |
|:-----|:---------|:------|
| 内存占用 | ~100-500MB | ~2.7GB (JVM) |
| P50 延迟 | 36ms | 469ms |
| 查询语言 | Cypher (兼容) | Cypher |
| Graphiti 支持 | `graphiti-core[falkordb]` 原生 | 原生 |

Castle 2C8G 下 Neo4j 会吃掉 2.7GB+，FalkorDB 基于 Redis 协议只需 ~100-500MB。

### D-P2-2: DSG 是耦合子系统，不是独立模块

DSG 通过触发器、预加载、Graphiti 直写等路径和 Graphiti/Brain 紧密耦合：
- 发现物体 → 查 Graphiti `scene` 分区预加载语义
- 追踪物体 → **绕过 LLM 直写 Graphiti** 更新 last_seen
- 触发器 (NEW/MISSING/DISPLACED) → Context Injector → Brain 上下文注入
- P2 用模拟 L1 输出走真实后续接口，真实视觉管线接入时只替换数据源

### D-P2-3: Gemini 4 条通信通道 + 路由策略

| 通道 | 机制 | P2 用途 |
|:-----|:-----|:--------|
| 用户语音 | LiveKit → Gemini 直连 | 不变 |
| `generate_reply(instructions=...)` | Redis Pub/Sub → Brain | **主动通知**（场景变化、物体消失） |
| `session.update_instructions()` | 更新 system prompt | **静默注入**（记忆、BehaviorMode 切换） |
| Tools 返回值 | Gemini 调 tool → 结果返回 | **按需查询**（remember, query_memory, query_scene） |

不是所有信息都要过 Scheduler，按需查询走 tool、静默注入走 update_instructions、主动通知走 generate_reply。

### D-P2-4: Obsidian 是人写的 SSOT，不是代码生成的

- 每个物体一个 .md，frontmatter 含 `uuid` 绑定 Graphiti 节点
- 文件组织方式随意，怎么方便怎么来
- 核心价值：人类说明 + UUID → Graphiti scene 分区 → ExpectationChecker ground truth

### D-P2-5: Graphiti group_id 分区

| 分区 | 用途 | 写入方 |
|:-----|:-----|:-------|
| `goslo` | GOSLO 鹦鹉大小姐的对话记忆 | Brain remember tool / ConversationWriter |
| `maid` | 猫娘女仆的对话记忆 | Nanobot parrot_bus channel |
| `scene` | 场景物体信息 (DSG) | DSG interfaces / Obsidian 同步脚本 |
| `user` | 用户偏好与画像 | Brain remember tool (importance=high) |

---

## 三、实现清单与完成状态

### P2-Alpha: 基础设施 ✅

| 任务 | 状态 | 关键文件 |
|:-----|:-----|:---------|
| FalkorDB Docker 容器 | ✅ | `infra/docker-compose.yml`, `infra/docker-compose.dev.yml` |
| FalkorDB 配置 | ✅ | `src/parrot/shared/config.py` → `FalkorDBConfig` |
| 环境变量模板 | ✅ | `infra/env-castle.template` (+FALKORDB_HOST/PORT) |
| 部署脚本更新 | ✅ | `infra/deploy-castle.sh` (+memory extra, +health check) |
| 依赖声明 | ✅ | `pyproject.toml` → `graphiti-core[falkordb,google-genai]` |
| Graphiti 客户端单例 | ✅ | `src/parrot/memory/graphiti_client.py` |
| group_id 4 分区 | ✅ | `src/parrot/memory/graphiti_client.py` → `PARTITIONS` |
| Brain `remember` tool | ✅ | `src/parrot/brain/tools/remember.py` |
| Brain `query_memory` tool | ✅ | `src/parrot/brain/tools/query_memory.py` |
| ConversationWriter 自动归档 | ✅ | `src/parrot/memory/conversation_writer.py` |
| Nanobot 对话写入 maid 分区 | ✅ | `nanobot/channels/parrot_bus.py` → `_archive_to_graphiti()` |

### P2-Beta: Scheduler 增强 ✅

| 任务 | 状态 | 关键文件 |
|:-----|:-----|:---------|
| BehaviorMode 动态切换 | ✅ | `src/parrot/brain/mode_watcher.py` |
| `set_mode` tool (Gemini 可调) | ✅ | `src/parrot/brain/tools/set_mode.py` |
| Redis Pub/Sub 模式通知 | ✅ | `src/parrot/shared/constants.py` → `CH_BEHAVIOR_MODE` |
| Context Injector 骨架 | ✅ | `src/parrot/brain/context_injector.py` |
| 记忆注入 (goslo+user 分区) | ✅ | `context_injector.py` → `inject_memory()` |
| 场景注入 (DSG 触发) | ✅ | `context_injector.py` → `inject_scene()` |
| 主动通知 (generate_reply) | ✅ | `context_injector.py` → `inject_notification()` |
| 周期轮询 (定时刷新) | ✅ | `context_injector.py` → `_periodic_poll()` |
| ParrotSoul 指令更新 | ✅ | `src/parrot/brain/soul.py` → 新增 remember/query 说明 |

### P2-Gamma: DSG 耦合层 ✅

| 任务 | 状态 | 关键文件 |
|:-----|:-----|:---------|
| DSG 数据类型 | ✅ | `src/parrot/dsg/types.py` (TriggerType, ObjectInfo, L1DetectionResult, SceneTrigger) |
| DSG↔Graphiti 接口层 | ✅ | `src/parrot/dsg/interfaces.py` |
| ├ preload_object_semantics | ✅ | 查 Graphiti scene 分区预加载语义 |
| ├ update_last_seen | ✅ | 绕过 LLM 直写 Graphiti 位置信息 |
| ├ get_expected_objects | ✅ | 搜索某 zone 预期物体列表 |
| ├ emit_trigger | ✅ | 发布 SceneTrigger 到 CH_DSG_EVENTS |
| └ publish_scene_update | ✅ | 发布场景摘要到 CH_DSG_SCENE_UPDATE |
| ExpectationChecker | ✅ | `src/parrot/dsg/expectation_checker.py` |
| L1 输出模拟脚本 | ✅ | `src/scripts/sim_dsg_desktop.py` |
| Obsidian→Graphiti 同步 | ✅ | `src/scripts/sync_obsidian_to_graphiti.py` |
| DSG 触发器监听 (Brain 侧) | ✅ | `src/parrot/dsg/trigger_listener.py` |
| `query_scene` tool | ✅ | `src/parrot/brain/tools/query_scene.py` |
| Brain Agent 全量集成 | ✅ | `src/parrot/brain/agent.py` (wired all P2 components) |

### P2-Delta: 集成验证 ✅

| 任务 | 状态 | 关键文件 |
|:-----|:-----|:---------|
| 集成测试套件 | ✅ | `tests/integration/test_graphiti_chain.py` |
| ├ remember→query 往返 | ✅ | `test_remember_and_query` |
| ├ 分区隔离验证 | ✅ | `test_scene_partition_isolated` |
| ├ DSG preload 接口 | ✅ | `test_dsg_preload_interface` |
| └ DSG update_last_seen | ✅ | `test_dsg_update_last_seen` |

### 用户任务 ⏳

| 任务 | 状态 |
|:-----|:-----|
| fly 动画 (Minecraft 风格) | ⏳ 待制作 |
| dance 动画 | ⏳ 待制作 |
| idle 动画 | ⏳ 待制作 |

---

## 四、新增文件清单

```
src/parrot/memory/
├── __init__.py                    # 包初始化
├── graphiti_client.py             # Graphiti 单例 + FalkorDB driver + 分区定义
└── conversation_writer.py         # 对话自动归档 (批量写 Brain / 即时写 Nanobot)

src/parrot/brain/
├── mode_watcher.py                # BehaviorMode Redis 订阅 → 动态切换
├── context_injector.py            # 记忆/场景/通知 → Gemini 上下文注入
└── tools/
    ├── remember.py                # @function_tool: 写入 Graphiti
    ├── query_memory.py            # @function_tool: 搜索 Graphiti
    ├── query_scene.py             # @function_tool: 查询场景物体
    └── set_mode.py                # @function_tool: 切换 BehaviorMode

src/parrot/dsg/
├── types.py                       # TriggerType, ObjectInfo, SceneTrigger 等
├── interfaces.py                  # DSG↔Graphiti 双向接口
├── expectation_checker.py         # EXPECTED vs 观测对比 → 触发器
└── trigger_listener.py            # Brain 侧 Redis 订阅 → Context Injector

src/scripts/
├── sim_dsg_desktop.py             # L1 输出模拟 (桌面场景)
└── sync_obsidian_to_graphiti.py   # Obsidian .md → Graphiti scene 分区

tests/integration/
└── test_graphiti_chain.py         # Graphiti 全链路集成测试
```

## 五、修改文件清单

| 文件 | 修改内容 |
|:-----|:---------|
| `infra/docker-compose.yml` | +FalkorDB 容器 (6380:6379, 512MB) |
| `infra/docker-compose.dev.yml` | +FalkorDB 容器 (本地开发) |
| `infra/env-castle.template` | +FALKORDB_HOST/PORT |
| `infra/deploy-castle.sh` | +memory extra, +FalkorDB health check |
| `pyproject.toml` | memory 依赖 → `graphiti-core[falkordb,google-genai]` |
| `src/parrot/shared/config.py` | +FalkorDBConfig dataclass |
| `src/parrot/shared/constants.py` | +CH_BEHAVIOR_MODE |
| `src/parrot/brain/agent.py` | +ConversationWriter/ModeWatcher/ContextInjector/TriggerListener 集成 |
| `src/parrot/brain/soul.py` | +remember/query_memory/query_scene 工具说明 |
| `src/parrot/brain/tools/__init__.py` | +4 个新 tool 注册 |
| `src/parrot/dsg/__init__.py` | 更新 docstring |
| `nanobot/channels/parrot_bus.py` | +_archive_to_graphiti() (maid 分区) |

---

## 六、新增 Redis 通道

| 常量 | 值 | 用途 | 生产者 | 消费者 |
|:-----|:---|:-----|:-------|:-------|
| `CH_BEHAVIOR_MODE` | `parrot.brain.behavior_mode` | BehaviorMode 切换通知 | set_mode tool / 外部 | mode_watcher → Brain |
| `CH_DSG_EVENTS` | `parrot.dsg.events` (P1 已预留) | DSG 触发器事件 | DSG interfaces | trigger_listener → Context Injector |
| `CH_DSG_SCENE_UPDATE` | `parrot.dsg.scene_update` (P1 已预留) | 场景摘要更新 | DSG interfaces | trigger_listener → Context Injector |

---

## 七、数据流总览

```
┌─────────────┐     remember/query     ┌──────────────────┐
│  Brain Agent │◄──────────────────────►│    Graphiti      │
│  (Gemini)    │     tools              │  (FalkorDB)      │
│              │                        │                  │
│  ┌─────────┐ │   update_instructions  │  ┌────────────┐  │
│  │Context  │◄├───────────────────────►│  │goslo 分区  │  │
│  │Injector │ │                        │  │maid 分区   │  │
│  └────▲────┘ │                        │  │scene 分区  │  │
│       │      │                        │  │user 分区   │  │
└───────┼──────┘                        │  └────────────┘  │
        │                               └───────▲──────────┘
        │  CH_DSG_EVENTS                        │
        │  CH_DSG_SCENE_UPDATE                  │ preload / update_last_seen
        │                                       │
┌───────┴──────┐                        ┌───────┴──────────┐
│  Trigger     │◄───────────────────────│  DSG Interfaces  │
│  Listener    │   emit_trigger         │  (耦合层)         │
└──────────────┘                        └───────▲──────────┘
                                                │
                                        ┌───────┴──────────┐
                                        │  L1 模拟脚本     │
                                        │  (sim_dsg_desktop)│
                                        └──────────────────┘

┌──────────────┐     _archive_to_graphiti    ┌──────────────┐
│  Nanobot     │────────────────────────────►│  Graphiti     │
│  (猫娘/GOSLO)│     add_episode (maid/goslo)│  (FalkorDB)   │
└──────────────┘                             └──────────────┘

┌──────────────┐     sync_obsidian_to_graphiti  ┌───────────┐
│  Obsidian    │───────────────────────────────►│  Graphiti  │
│  (.md+UUID)  │     add_episode (scene)        │  (scene)   │
└──────────────┘                                └───────────┘
```

---

## 八、Castle 部署变更

```
Castle ECS (2C8G) 进程布局:
┌─────────────────────────────────────────┐
│  Docker:                                │
│  ├── Redis         (127.0.0.1:6379)     │
│  ├── LiveKit Server (0.0.0.0:7880/7881) │
│  └── FalkorDB      (127.0.0.1:6380)  ← NEW │
│                                         │
│  tmux sessions:                         │
│  ├── brain:  Brain Agent (Gemini Live)  │
│  ├── maid:   Nanobot Worker (猫娘)      │
│  └── goslo-chat: GOSLO Chat (Telegram)  │
└─────────────────────────────────────────┘
```

---

## 九、P2.5 架构决策

### D-P2.5-DISCOVER: Tool 按需发现优先，A10 全发现后补

**为什么先打通 identify_object tool 这条"有意识发现"通路？**

| 维度 | Tool 按需发现 (P2.5) | A10 全发现 (P3+) |
|:-----|:-------------------|:-----------------|
| 触发方式 | Gemini 主动调用 tool | 视觉管线持续运行 |
| 对话阻塞 | 有感知停顿 (Gemini 说"让我看看") | **不阻塞** — 潜意识运行 |
| 精度 | 高 (Gemini Flash 看截图) | 中 (YOLO-World + DINOv2) |
| 成本 | 低 (按需调用) | 高 (持续 GPU) |
| 依赖 | 只需 Graphiti | 需要 A10 GPU + SAM2 + YOLO-World |

**关键约束**: 如果先做 A10 通路，所有后续设计都会围绕"持续视觉管线"设计，
tool 通路会被忽略。但 tool 通路有独立价值 —— 它是 Gemini 的"有意识观察"，
等价于人类主动看某样东西，不同于潜意识的视觉扫描。

**两条通路的关系**:
```
A10 全发现 (潜意识) ─→ DSG L2-A/L2-B ─→ Context Injector ─→ Gemini 被动接收
                                                              ("桌上多了个东西")
Tool 按需发现 (有意识) ─→ identify_object ─→ Gemini 主动触发
                                              ("让我看看这是什么")
两者共享 Graphiti 数据模型，互不冲突，先后都需要。
```

### D-P2.5-L2B: L2-B = Graphiti 适配的 RustworkX 工作记忆

| 设计点 | 决策 |
|:-------|:-----|
| 数据模型 | SemanticNode 适配 Graphiti EntityNode 字段 + 运行时扩展 (attention, episode) |
| 图引擎 | RustworkX PyDiGraph — Python 对象作节点/边, UUID→index O(1) 映射 |
| 与 Graphiti 关系 | 预加载 Graphiti → L2-B (启动), 归档 L2-B episode → Graphiti (结束) |
| 与 L2-A 关系 | UUID 共享, SPATIAL_CONTEXT 边类型连接, 事件通知 (不耦合) |
| Episode 分割 | 双路: Gemini tool 主导 (有意识) + 触发器自动 (潜意识) |
| 触发器设计 | 4 种触发模式 (STARTUP/PERIODIC/EVENT_DRIVEN/ON_DEMAND), Nanobot 是主要执行者 |
| 后续扩展 | 联想机制/注意力衰减/MemoryValidity 不在本次范围, 接口已预留 |

### D-P2.5-BEHAVIOR: 鹦鹉行为状态分离

- 行为状态规则文件: `.cursor/memory/parrot_behavior_rules.md`
- 身体(Unity) / 头部(Unity独立层) / 认知(Python) 三层独立
- 兼容矩阵定义哪些动作可以并行，优先级链定义冲突时谁让谁
- 状态机设计遵循 Opus 14 的 4 通道资源锁模型 (body/voice/vision/background)

---

## 十、P2.5 实现清单

### Phase 0: P2 审计修复 ✅

| 修复 | 文件 |
|:-----|:-----|
| ContextInjector mode 同步 | `context_injector.py` + `mode_watcher.py` |
| DSG object_id UUID 绑定 | `dsg/interfaces.py` |
| Nanobot 双前缀修复 | `nanobot/channels/parrot_bus.py` |
| GOSLO Chat 归档 | `src/scripts/start_goslo_chat.py` |
| PLAYFUL mode 指令 | `soul.py` |

### Phase 1: AR 视频流 ✅

| 任务 | 文件 |
|:-----|:-----|
| ARVideoPublisher (Unity) | `unity/.../LiveKit/ARVideoPublisher.cs` |
| Brain Agent video_input=True | `src/parrot/brain/agent.py` |
| sim_unity_client --video 模式 | `src/scripts/sim_unity_client.py` |

### Phase 2: Gemini 按需物体发现 ✅ (已增强)

| 任务 | 文件 |
|:-----|:-----|
| identify_object 三模式 tool | `src/parrot/brain/tools/identify_object.py` |
| ├ match: 快速 Graphiti 匹配 | 查 scene + user 分区 |
| ├ save_new: 保存新物体 | 写入 scene 分区 + UUID |
| └ deep_search: 后台研究 | dispatch_task → Nanobot research |
| Soul 指令更新 | `src/parrot/brain/soul.py` |

### Phase 3: XR Hands + 飞到手指 ✅

| 任务 | 文件 |
|:-----|:-----|
| XRHandTracker (Unity) | `unity/.../XRHands/XRHandTracker.cs` |
| PerchOnHand (Unity) | `unity/.../XRHands/PerchOnHand.cs` |
| 手部遥测解析 (Python) | `src/parrot/brain/telemetry_receiver.py` |

### 行为状态规则 ✅

| 任务 | 文件 |
|:-----|:-----|
| 状态机 + 兼容矩阵 + 冲突规则 | `.cursor/memory/parrot_behavior_rules.md` |

### Phase 4: L2-B 语义工作记忆 ✅

| 任务 | 文件 |
|:-----|:-----|
| SemanticNode/Edge/EpisodeMarker 数据类型 | `src/parrot/dsg/l2b_types.py` |
| L2BGraph (RustworkX) 工作记忆管理器 | `src/parrot/dsg/l2b_graph.py` |
| ├ 预加载 Graphiti → 内存图 | `preload_from_graphiti()` |
| ├ Obsidian SSOT 充实 | `enrich_from_obsidian()` |
| ├ Episode 归档到 Graphiti | `archive_episode_to_graphiti()` |
| └ 注意力/场景摘要查询 | `query_by_attention()`, `build_scene_summary()` |
| 触发器框架 | `src/parrot/dsg/triggers/` |
| ├ 基类 + Runner | `triggers/base.py`, `triggers/runner.py` |
| ├ 日程触发器 (Google Calendar) 三层提醒 | `triggers/calendar_trigger.py` |
| ├ SSOT 充实触发器 | `triggers/ssot_enrichment_trigger.py` |
| ├ 场景上下文检索触发器 | `triggers/scene_context_trigger.py` |
| └ 消息提醒触发器 (Gmail) | `triggers/message_trigger.py` |
| manage_episode tool (Gemini 主导) | `src/parrot/brain/tools/manage_episode.py` |

### Phase 5: P2.5 审计修复 ✅

| 修复 | 文件 | 问题 |
|:-----|:-----|:-----|
| TriggerRunner 真正启动 | `agent.py` | Runner 未 start()，触发器全部是死代码 |
| L2-B 预加载集成到 Agent 启动 | `agent.py` | Graphiti 预加载从未执行 |
| identify_object → L2-B 双向接入 | `identify_object.py` | match/save_new 未更新 L2-B |
| save_new 发出 new_object 触发事件 | `identify_object.py` | SSOT 触发器无法响应新发现 |
| deep_search 先存 L2-B 节点 | `identify_object.py` | 返回信息称"已记录"但未记录 |
| Nanobot result_channel 路由 | `nanobot_consumer.py` | 触发器结果无法路由到对应 trigger |
| CH_TRIGGER_RESULTS 新通道 | `constants.py` + `runner.py` | 触发器需要专用结果通道 |
| TriggerRunner → generate_reply | `runner.py` | 触发器通知无法到达 Gemini |
| CalendarTrigger 三层提醒 | `calendar_trigger.py` | 原版只有列表式提醒 |
| ├ Digest (日程总览) | — | 启动/定期的整体日程摘要 |
| ├ Prep (30 min 前) | — | 临近事件的准备提醒 |
| └ Imminent (5 min 前) | — | 紧急即刻提醒 |
| Quiet hours (23:00–07:00) | `calendar_trigger.py` | 安静时段不打扰 |
| Cooldown (同事件同层级不重复) | `calendar_trigger.py` | 防止重复提醒轰炸 |
| 自然语言通知风格 | `calendar_trigger.py` | 非列表，融入对话 |
| MessageNotificationTrigger (Gmail) | `message_trigger.py` | 新增: 重要消息摘要提醒 |
| episode_id 防冲突 | `l2b_types.py` | 秒精度 → 加 uuid4 hex |
| start_episode 自动归档旧 episode | `l2b_graph.py` | 静默关闭未手动 end 的 episode |
| clear() 清理 _episodes | `l2b_graph.py` | 内存泄漏修复 |
| Salience.ALERT 级别 | `l2b_types.py` | 日程紧急提醒需要 |
| ConfirmationStatus.TENTATIVE | `l2b_types.py` | 新发现物体的初始状态 |
| SSOT 触发器支持 TENTATIVE | `ssot_enrichment_trigger.py` | 新发现可充实 |
| Agent disconnect 清理 runner | `agent.py` | 防止房间断开后触发器空跑 |

---

## 十一、P2 原有后续待办

- [ ] Castle 部署 FalkorDB + 全链路线上验证
- [ ] git push 双仓库 (ParrotCarriers + nanobot)
- [ ] 用户完成 fly/dance/idle/thinking 动画 → Unity 替换 Cube
- [ ] Cursor 工作区规则: `.cursor/rules/` 模块隔离策略
- [ ] 新 skill 收集: AR Foundation, XR Interaction Toolkit
- [ ] 猫娘 cron 任务: 定时读取 Obsidian vault 变更 → Gemini Flash 补充三元组
- [ ] 三级调度 Priority 子树 (reflex > intent > task)
- [ ] ResourceLockManager 骨架 (body 通道互斥)

## 十二、P3 前瞻

- MemoryValidity (记忆管家): 信息有效期鉴定 + Ebbinghaus 衰减（Graphiti 之前的过滤/筛选层）
- Skill Distillation (技能提炼): 重复工作流 → 自动提炼为 skill
- Obsidian MCP 双向交互
- DSG 真实视觉管线 (A10 GPU) — A10 全发现是潜意识通路，不阻塞对话
- 群聊 (Telegram 群 + LobeChat)
- identify_object 增强: Gemini Flash 截图匹配 (有参考图片的物体)
- 会话结束/空闲时: 物体发现信息经过过滤模块 → 持久化到 Graphiti

---

## 十三、运行命令速查 (P2 新增)

```bash
# FalkorDB 本地开发
docker compose -f infra/docker-compose.dev.yml up -d   # 含 FalkorDB

# DSG 桌面模拟
python src/scripts/sim_dsg_desktop.py                   # 全场景模拟
python src/scripts/sim_dsg_desktop.py --scenario new    # 只模拟物体出现
python src/scripts/sim_dsg_desktop.py --scenario missing # 只模拟物体消失

# Obsidian 同步到 Graphiti
python src/scripts/sync_obsidian_to_graphiti.py --vault /path/to/obsidian/objects

# Graphiti 集成测试
pytest tests/integration/test_graphiti_chain.py -v      # 需要 FalkorDB 运行

# Brain Agent (已集成 P2 全部组件)
python -m parrot.brain.agent dev                        # 自动挂载 ConversationWriter + ModeWatcher + ContextInjector + TriggerListener
```
