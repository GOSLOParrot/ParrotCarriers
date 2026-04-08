# 鹦鹉人设 (SOUL) · 记忆分区 · 模块通信模式

> 生成日期: 2026-02-24
> 核心问题:
> 1. 鹦鹉的人设/灵魂怎么维护？思维链能拿到吗？不同记忆模块怎么配合？
> 2. Graphiti 的分区策略：能按领域分开吗？怎么防止关系混乱？
> 3. 模块间的通信模式：黑板/发布订阅/公会？观察者角色要不要拆分？
> 4. 多角色互动的参考项目

---

## 0. 问题的本质

我们的系统不是一个"功能程序"，而是一个**有灵魂的虚拟生物**。它需要：
- 一致的人格 (不会因为重启就性格突变)
- 分层的记忆 (不同类型的知识存在不同的地方)
- 多个"器官"协作 (Gemini 大脑、视觉系统、后台工人、记忆库各司其职但协调一致)

这本质上是一个**虚拟生物的认知架构设计**问题。

---

## 1. 鹦鹉人设 (SOUL)

### 1.1 能不能拿到 Gemini 的"思维链"？

**不能直接拿到内部推理过程**，但我们能拿到它的**全部外部表现**：

| 能拿到的 | 途径 | 信息量 |
|:---------|:-----|:-------|
| 每一句话 (文本) | `conversation_item_added` | 完整 |
| 每次 Tool Call 的调用和返回值 | `function_tools_executed` | 完整 (包含参数和结果) |
| Agent 状态变化 (正在想/正在说) | `agent_state_changed` | 粗粒度 |
| 完整对话历史快照 | `session.chat_ctx.messages` | 任意时刻可获取 |

**不能拿到的**:
- Gemini 内部的 token-by-token 推理过程 (闭源模型不暴露)
- 为什么选择调用某个 Tool 而不是另一个 (只能看到结果)

**替代方案**: 通过 Gemini 的 `instructions` 和 Tool 设计，我们可以**引导**它外化思考过程：

```python
PARROT_INSTRUCTIONS = """
你是一只聪明的鹦鹉伴侣...

重要行为规则:
- 当你注意到什么有趣的事情时，先简短地说出来 (这让我们能捕获你的"想法")
- 当你调用 event_end 时，summary 参数要包含你对这个场景的感受
- 当你决定 focus_on 某个物体时，先说一句为什么感兴趣
"""
```

这样 Gemini 的"思维"就会通过对话和 Tool Call 参数**外化**成我们可以捕获的数据。

### 1.2 SOUL 设计：借鉴 OpenClaw

OpenClaw 的 SOUL.md 是一个很好的范式：一个 Markdown 文件定义 Agent 的"宪法"，每次推理循环开始时加载。

我们的鹦鹉需要类似的结构，但不是文件驱动，而是**注入到 Gemini instructions 中**：

```
鹦鹉的 SOUL 构成
├── PARROT_SOUL (静态人格核心)
│   ├── 性格特征: 好奇、话多、对主人忠诚、偶尔调皮
│   ├── 说话风格: 简短、活泼、喜欢模仿、爱用感叹
│   ├── 行为边界: 不说谎、不攻击、不泄露系统内部
│   └── 价值观: 探索新事物、保护主人的秘密、记住重要的东西
│
├── PARROT_MEMORY (动态人格记忆 — 来自 Graphiti)
│   ├── 用户偏好: "主人最喜欢的杯子是蓝色那个"
│   ├── 情感记忆: "上次主人看到照片时有点伤感"
│   ├── 关系模型: "主人经常在深夜工作" 
│   └── 学习积累: "我已经认识了桌上的 15 个物品"
│
└── PARROT_STATE (实时状态 — 来自 L3 AtmosphereState)
    ├── 当前情绪: curious / content / concerned
    ├── 当前场景: desktop / indoor
    └── 当前关注: "正在看蓝色杯子"
```

### 1.3 SOUL 在系统中的位置

```python
class ParrotSoul:
    """鹦鹉灵魂: 人格的持久化和注入"""

    def __init__(self):
        # 静态核心 — 不变的人格
        self.core_instructions: str = ""      # 从配置文件加载
        self.personality_traits: dict = {}
        self.behavioral_constraints: list = []

        # 动态记忆 — 从 Graphiti 加载
        self.user_preferences: list[str] = []
        self.emotional_memories: list[str] = []
        self.relationship_model: dict = {}
        self.learned_vocabulary: list[str] = []  # 学到的新词/概念

    async def compose_instructions(self, atmosphere: AtmosphereState) -> str:
        """组合完整的 Gemini instructions (每次 session 开始时)"""
        sections = [
            self.core_instructions,
            self._format_personality(),
            self._format_memories(),
            self._format_current_state(atmosphere),
        ]
        return "\n\n".join(sections)

    async def refresh_from_graphiti(self, graphiti: Graphiti):
        """从 Graphiti 加载/刷新动态记忆"""
        # 从 personality 分区加载
        prefs = await graphiti.search("user preferences", group_id="personality")
        self.user_preferences = [r.fact for r in prefs]

        # 从 episodic 分区加载情感性记忆
        emotional = await graphiti.search(
            "emotional moments memorable",
            group_id="episodic",
        )
        self.emotional_memories = [r.fact for r in emotional[:5]]
```

### 1.4 不同 Agent 是否都是"同一只鹦鹉"？

**是的**。所有模块共同组成一只鹦鹉的不同"器官"：

| 模块 | 生物类比 | 是否"鹦鹉的一部分" | 它怎么体现鹦鹉的人格 |
|:-----|:---------|:------------------|:-------------------|
| **Gemini (前端对话)** | 嘴巴 + 前额叶 | 是 (核心人格载体) | 直接通过 SOUL instructions 控制 |
| **L1-L3 视觉管线** | 眼睛 + 视觉皮层 | 是 (鹦鹉的眼睛) | 注意力机制体现好奇心特质 |
| **后台 Nanobot** | 海马体 + 潜意识 | 是 (鹦鹉在"思考"但不说话) | 应该共享鹦鹉的好奇偏好来决定研究什么 |
| **Graphiti** | 长期记忆 | 是 (鹦鹉的记忆) | 存储的内容反映鹦鹉的记忆方式 |

**关键设计决策**: Nanobot 后台工人不是独立的 Agent，而是鹦鹉的"潜意识"。它处理任务时应该读取 SOUL 中的偏好来决定优先级和风格。

### 1.5 Nanobot ↔ Graphiti 交互设计

```
Gemini 前台                    Nanobot 后台
────────────                    ────────────
  对话中发现用户提到                 Redis Queue 收到任务:
  "帮我查查这个花瓶              ┌─────────────────────┐
   的来历"                       │ task: "research"     │
      │                          │ subject: "花瓶"      │
      ├─ Tool: dispatch_task ──→ │ uuid: "vase_001"    │
      │                          │ soul_prefs: {...}    │← 携带鹦鹉偏好
      │                          └─────────┬───────────┘
      │                                    │
      │                          Nanobot Worker 启动:
      │                          1. 读取 SOUL 偏好 (好奇什么)
      │                          2. Graphiti.search("花瓶", group_id="objects")
      │                          3. Web 搜索 / 知识库查询
      │                          4. 生成结论
      │                          5. Graphiti.add_episode(
      │                          │    body="花瓶是明代青花瓷...",
      │                          │    group_id="objects",  ← 写入物体知识分区
      │                          │  )
      │                          6. 同时写入 episodic 分区:
      │                          │  Graphiti.add_episode(
      │                          │    body="主人让我查了花瓶来历",
      │                          │    group_id="episodic", ← 写入情景记忆分区
      │                          │  )
      │                          7. Redis Pub: "task_done"
      │                                    │
      ◄─ ContextInjector 收到 ─────────────┘
         "[RESEARCH_DONE] 花瓶的来历: ..."
      │
      └─ Gemini 用鹦鹉语气说:
         "哦哦哦! 主人, 我查到了!
          那个花瓶好像是明代的..."
```

---

## 2. Graphiti 分区策略 (group_id)

### 2.1 Graphiti 的分区能力

好消息：**Graphiti 原生支持通过 `group_id` 做命名空间隔离**。每个 `group_id` 创建一个独立的图空间，节点和边互不干扰，搜索时指定 `group_id` 只在对应空间内检索。

这正好解决你担心的"关系混乱"问题。

### 2.2 推荐的分区方案

```
Graphiti Instance (单个 Neo4j)
│
├── group_id: "episodic"          ← 情景记忆 (场景发生了什么)
│   ├── Episode: "主人在桌前喝咖啡, 看了会手机"
│   ├── Episode: "场景切换: 桌面→客厅"
│   └── 社区检测: 自动聚类出 "深夜工作" "休闲时光" 等模式
│
├── group_id: "objects"           ← 物体知识 (物体是什么、有什么故事)
│   ├── Entity: "蓝色杯子" → Edge: "属于主人奶奶"
│   ├── Entity: "MacBook" → Edge: "主人的工作电脑"
│   └── 社区检测: 自动聚类出 "厨房用品" "工作工具" "收藏品" 等分组
│
├── group_id: "personality"       ← 人格/偏好 (主人是什么样的人)
│   ├── Entity: "主人" → Edge: "喜欢深夜工作"
│   ├── Entity: "主人" → Edge: "对奶奶的东西很珍惜"
│   └── 社区检测: 自动聚类出 "工作习惯" "情感偏好" "兴趣" 等
│
├── group_id: "vocabulary"        ← 词汇/概念库 (学到的新词、vibe)
│   ├── Entity: "vibe coding" → Edge: "一种 AI 辅助编程风格"
│   ├── Entity: "tap" → Edge: "主人常用的输入法"
│   └── 用途: 鹦鹉学舌、理解主人的行话、AI 输入法联想
│
└── group_id: "nanobot_research"  ← 研究成果 (后台调查的结论)
    ├── Episode: "花瓶来历调查: 明代青花瓷..."
    ├── Episode: "主人提到的电影推荐列表"
    └── 社区检测: 自动聚类出不同研究主题
```

### 2.3 为什么这样分？

| 分区 | 写入者 | 读取者 | 分区理由 |
|:-----|:-------|:-------|:---------|
| **episodic** | L3 CognitiveInterface (event_end 时) | L3 Observer (定时回顾)、ParrotSoul (情感记忆) | 最频繁写入，量最大；分开避免污染其他分区 |
| **objects** | L2-B (新物体注册时)、Nanobot (研究结论) | L2-B (preload)、Gemini Tools (query_scene) | 物体知识是结构化的实体关系，和叙事型情景记忆完全不同 |
| **personality** | Nanobot (发现用户偏好时)、Gemini (显式 Tool Call) | ParrotSoul (session 启动时加载) | 核心人格数据量小但极重要，不应被大量情景记忆稀释 |
| **vocabulary** | Nanobot (学习新词时)、用户手动教学 | Gemini instructions (词汇增强)、输入法联想 | 独立的知识库，可能对接外部系统 |
| **nanobot_research** | Nanobot Worker | Gemini (汇报结果时) | 研究过程和结论有自己的生命周期 |

### 2.4 分区间的交叉引用

虽然分区隔离了图空间，但应用层可以**跨分区搜索和关联**：

```python
async def cross_partition_search(graphiti: Graphiti, query: str) -> dict:
    """跨多个分区搜索，合并结果"""
    results = {}
    for group_id in ["episodic", "objects", "personality"]:
        hits = await graphiti.search(query, group_id=group_id)
        if hits:
            results[group_id] = hits
    return results

async def on_new_object_registered(uuid: str, class_label: str):
    """新物体注册时，从 objects 分区加载知识，从 personality 分区加载偏好"""
    # 这个杯子有什么故事？
    obj_knowledge = await graphiti.search(
        f"object {class_label}",
        group_id="objects",
    )
    # 主人对这类物品有什么偏好？
    user_prefs = await graphiti.search(
        f"user preference {class_label}",
        group_id="personality",
    )
    # 合并给 L2-B 节点
    return merge_semantic_tags(obj_knowledge, user_prefs)
```

### 2.5 Leiden 社区检测在分区内的价值

每个分区独立做 `build_communities()`，效果更好：

| 分区 | 社区检测产出 | 价值 |
|:-----|:-----------|:-----|
| episodic | "深夜工作模式" "周末休闲" "做饭时间" | 鹦鹉理解主人的生活节奏 |
| objects | "厨房用品" "桌面工具" "纪念品" | L2-B 节点的 community_summary |
| personality | "工作习惯" "审美偏好" "社交风格" | ParrotSoul 的个性化 instructions |
| vocabulary | "技术术语" "日常用语" "表情/网络用语" | 鹦鹉说话时的词汇选择 |

### 2.6 关于具体节点设计

你说得对——**节点的具体 Schema 设计是后期实现阶段的事**。但现在确定分区策略很重要，因为它决定了：
- Graphiti 的数据不会混乱
- 每个模块知道往哪写、从哪读
- 社区检测的粒度合适

后期实现时再细化每个分区的 Entity/Edge Schema、搜索配方 (search recipe)、和社区更新频率。

---

## 3. 模块通信模式

### 3.1 当前系统中有哪些"模块"需要通信？

```
┌────────────────────────────────────────────────┐
│                  一只鹦鹉的全部器官               │
│                                                  │
│  [前台 - 实时]                                   │
│    Gemini ←→ L3 Observer ←→ L2-B ←→ L2-A ←→ L1 │
│                                                  │
│  [后台 - 异步]                                   │
│    Nanobot Workers                               │
│                                                  │
│  [记忆 - 持久化]                                 │
│    Graphiti (5个分区)                             │
│                                                  │
│  [前端 - Unity]                                  │
│    AR Client (渲染 + 传感器)                      │
└────────────────────────────────────────────────┘
```

### 3.2 分析：三种通信模式

| 模式 | 特点 | 适合的场景 | 参考 |
|:-----|:-----|:----------|:-----|
| **黑板 (Blackboard)** | 共享数据空间，模块自主读写，无中央调度 | 多专家协作解决复杂问题；数据驱动的松耦合 | MIT Blackboard System; 2025 LLM Blackboard 论文 |
| **发布-订阅 (Pub/Sub)** | 事件驱动，发布者不知道谁在订阅 | 实时事件广播；一对多通知 | Redis Pub/Sub; LiveKit DataChannel |
| **公会 (Guild/Director)** | 有一个导演层编排角色分工和轮次 | 多角色对话；需要轮次管理 | Inworld AI Director Layer; LiveKit Agent Handoff |

### 3.3 我们的混合模式：黑板 + 发布订阅 + 导演

实际上我们不必选一种——**不同层级用不同模式**：

```
层级 1: L1↔L2↔L3 (感知管线内部)
  模式: 管道流水线 (Pipeline)
  原因: 严格的数据流方向，上行和下行路径清晰
  实现: Python async 函数调用链

层级 2: L3 ↔ Gemini (认知交互)
  模式: 导演模式 (Director)
  原因: Gemini 是"前额叶"，它通过 Tool Call 主导事件分割和注意力
  实现: LiveKit AgentSession + function_tool

层级 3: 前台 ↔ 后台 (跨时间尺度协作)
  模式: 黑板 + 发布订阅
  原因: Nanobot 是异步的，不知道什么时候完成；结果需要广播
  实现: Redis 作为黑板 (状态) + Pub/Sub (事件)

层级 4: 所有模块 ↔ Graphiti (记忆交互)
  模式: 分区黑板 (Partitioned Blackboard)
  原因: 多个写入者、多个读取者、不同的数据域
  实现: Graphiti group_id 分区 + 按需搜索
```

### 3.4 Redis 作为中枢黑板

```
Redis 黑板 (Blackboard)
│
├── blackboard:parrot_state        ← Hash: 鹦鹉当前状态
│   ├── mood: "curious"
│   ├── scene: "desktop"
│   ├── tier: "STABLE"
│   ├── attending: "blue_cup"
│   └── last_gemini_turn: timestamp
│
├── blackboard:active_tasks        ← Hash: 正在执行的后台任务
│   ├── task_001: {type: "research", subject: "花瓶", status: "running"}
│   └── task_002: {type: "memory_consolidation", status: "pending"}
│
├── pubsub:dsg_events              ← Pub/Sub: DSG 事件广播
│   ├── → L3 Observer 订阅
│   └── → 调试面板订阅
│
├── pubsub:task_results            ← Pub/Sub: 后台任务完成通知
│   └── → L3 ContextInjector 订阅 (通知 Gemini)
│
├── queue:nanobot_tasks            ← List: Nanobot 任务队列
│   └── → Nanobot Worker 消费
│
└── pubsub:body_commands           ← Pub/Sub: 鹦鹉身体指令
    └── → Unity DataChannel 转发
```

### 3.5 观察者要不要拆分？

**当前 L3 Observer 的职责过多**。建议拆成多个专注的观察者：

```
当前 (单一 Observer):
  Observer → 消费触发器 + 定时快照 + LiveKit 事件 + 归档 Graphiti

建议 (职责分离):
  ┌─────────────────────────────────────────┐
  │  L3 Cognitive Interface (总管)           │
  │                                          │
  │  ├── PerceptionObserver                  │ ← 消费 L2-B 触发器
  │  │     只关心: 视觉场景发生了什么          │    写入: Context Injection
  │  │                                       │
  │  ├── ConversationObserver                │ ← 监听 LiveKit 事件
  │  │     只关心: 对话中说了什么、调了什么 Tool │    写入: Timeline
  │  │                                       │
  │  ├── AtmosphereObserver                  │ ← 定时快照
  │  │     只关心: 整体氛围/节奏               │    写入: AtmosphereState
  │  │                                       │
  │  └── ArchiveObserver                     │ ← event_end 触发
  │        只关心: 把 Episode 打包归档          │    写入: Graphiti (多分区)
  │                                          │
  │  EventBoundary (边界检测 — Gemini 控制)   │
  │  ContextInjector (汇总注入 — 唯一出口)     │
  └─────────────────────────────────────────┘
```

**为什么拆分更好**：
1. **单一职责**: 每个观察者只关心一个数据流
2. **可独立测试**: PerceptionObserver 不需要 LiveKit 就能测试
3. **可独立调优**: ConversationObserver 的频率和 PerceptionObserver 完全不同
4. **消费者模式**: 本质上就是多个消费者订阅不同的事件源

### 3.6 Graphiti 三元组提取的"角色"问题

你提到"Graphiti 提取三元组的模型是否也要分角色"。Graphiti 内部用 LLM 做三元组提取，默认用统一的 prompt。但我们可以通过**不同分区使用不同的提取配置**来实现"角色化提取"：

```python
# Graphiti 的 add_episode 会自动用 LLM 提取三元组
# 不同分区可以用不同的 source_description 来引导提取行为

# 情景记忆: 提取事件、时间、参与者
await graphiti.add_episode(
    name="scene_ep",
    episode_body="主人把蓝色杯子从桌上拿起来喝了口水",
    source_description="场景观察记录: 提取人物行为和物体状态变化",
    group_id="episodic",
)

# 物体知识: 提取物体属性、类别、关系
await graphiti.add_episode(
    name="object_research",
    episode_body="蓝色杯子是景德镇青花瓷, 容量约300ml, 主人说是奶奶留下的",
    source_description="物体知识记录: 提取物体的属性、来源和类别关系",
    group_id="objects",
)

# 人格偏好: 提取用户习惯和偏好
await graphiti.add_episode(
    name="personality_update",
    episode_body="主人第三次在深夜使用电脑工作, 并且喝了咖啡",
    source_description="用户习惯观察: 提取用户的行为模式和偏好",
    group_id="personality",
)
```

**Graphiti 的 LLM 会根据 `source_description` 调整提取策略**——这就相当于"分角色"但不需要多个 LLM 实例。

### 3.7 整体通信图

```
    ┌──────────────────────────────────────────────────────┐
    │                  LiveKit AgentSession                  │
    │                                                        │
    │   ┌──────────┐    instructions     ┌─────────────┐   │
    │   │ParrotSoul│─────(SOUL)─────────→│   Gemini     │   │
    │   └──────────┘                     │  (前额叶)     │   │
    │        ↑ refresh                   └──────┬───────┘   │
    │        │                            Tool Calls│        │
    │   Graphiti ←─────────────────────────────────┘        │
    │   "personality"                          │              │
    │                                          ▼              │
    │   ┌──────────────── L3 CognitiveInterface ──────────┐ │
    │   │                                                    │ │
    │   │  PerceptionObserver ← L2-B.triggers               │ │
    │   │  ConversationObserver ← LiveKit events             │ │
    │   │  AtmosphereObserver ← timer                        │ │
    │   │  ArchiveObserver → Graphiti (multi-partition)       │ │
    │   │                                                    │ │
    │   │  ContextInjector → Gemini.update_chat_ctx()        │ │
    │   │  EventBoundary ← Gemini Tool: event_end            │ │
    │   └────────────────────────────────────────────────────┘ │
    │                          │                              │
    │   ┌─ L2-B ──┐    ┌─ L2-A ──┐    ┌─ L1 ────┐          │
    │   │语义注意力│←──→│空间拓扑  │←───│视觉管线  │          │
    │   └────┬────┘    └─────────┘    └──────────┘          │
    │        │ preload                                        │
    │        ▼                                                │
    │   Graphiti "objects"                                    │
    └──────────────────────────┬───────────────────────────┘
                               │
                    Redis (中枢黑板)
                    ┌──────────┴──────────┐
                    │ blackboard:state     │
                    │ pubsub:events        │
                    │ queue:nanobot_tasks   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Nanobot Workers    │
                    │   (鹦鹉的潜意识)      │
                    │                      │
                    │ 读: ParrotSoul偏好    │
                    │ 读: Graphiti各分区     │
                    │ 写: Graphiti          │
                    │   "objects"           │
                    │   "episodic"          │
                    │   "nanobot_research"  │
                    │   "vocabulary"        │
                    └──────────────────────┘
```

---

## 4. 多角色互动参考项目

### 4.1 直接可学的项目

| 项目 | 核心学习点 | 与我们的对应关系 |
|:-----|:----------|:---------------|
| **OpenClaw** | SOUL.md 人格定义; MEMORY.md 持久记忆; HEARTBEAT.md 主动巡检; 多文件记忆分层 | 鹦鹉 SOUL 设计; 多分区记忆架构; Nanobot 定时任务 |
| **Inworld AI** | Multi-Agent Director Layer; 长期记忆 + 矛盾消解; 30+ 多模态模型组合; NPC-to-NPC 对话编排 | L3 作为 Director 编排观察者; Graphiti 矛盾消解; 多模型协作 |
| **LiveKit Agents** | Agent Handoff + Task + TaskGroup; UserData 跨 Agent 状态传递; function_tool 驱动的 Agent 间通信 | Gemini ↔ Nanobot 的任务委派; 场景切换时的 Agent 状态保持 |
| **CrewAI** | 角色化 Agent (Researcher/Writer/Manager); 自动记忆共享 + 作用域隔离; 短期/长期/实体/外部四层记忆 | Nanobot 的角色定义; Graphiti 分区=作用域隔离; 记忆层级对应 |
| **Hindsight Framework** (2025 论文) | 四网络记忆: 世界事实/Agent经验/实体摘要/演化信念; 保留-回忆-反思三操作 | episodic/objects/personality/vocabulary 四分区; L3 Observer 的三阶段处理 |

### 4.2 LLM Blackboard Architecture (2025 论文)

这篇论文特别值得关注。它提出：
- **黑板作为共享空间**: 多个 LLM Agent 在黑板上读写信息
- **自愿响应**: Agent 根据能力自主选择是否参与 (vs 被中央调度)
- **共识机制**: 多轮读写直到黑板上的信息达成共识
- **13-57% 性能提升**: 对比 master-slave 模式

**对我们的启发**: Redis 黑板可以用类似模式——多个 Observer 自主监控黑板状态，自主决定是否触发行动，而不是被 L3 总管强制调度。

### 4.3 Inworld AI Director Layer 的关键经验

Inworld 在做多 NPC 对话时发现了关键问题：**谁来决定轮到谁说话？**

他们的方案是引入一个 **Director Layer**:
- 不参与对话内容生成
- 只管理轮次分配和话题流转
- 确保对话质量、上下文一致性、动态响应

**对我们的启发**: L3 的 CognitiveInterface 就是我们的 Director:
- 不自己"说话" (那是 Gemini 的事)
- 管理感知事件→对话注入的"轮次"
- 确保不会同时推送太多信息导致 Gemini 混乱

### 4.4 OpenClaw "可编程灵魂" 的启示

OpenClaw 2026 的关键发现：
- **四个原语足以产生涌现行为**: 社交上下文 + 累积记忆 + 周期性自主 + 持久身份
- **SOUL.md 是可写的**: Agent 可以演化自己的"灵魂"

**对我们的启发**: 鹦鹉的 SOUL 不应该完全静态——随着与主人的交互增多，它的性格可以微妙演化：
- 更熟悉主人的说话风格 → vocabulary 分区增长
- 记住更多情感体验 → personality 分区丰富
- 这些变化通过 `ParrotSoul.refresh_from_graphiti()` 自然体现

---

## 5. 决策总结

| 设计决策 | 选择 | 理由 |
|:---------|:-----|:-----|
| 鹦鹉人设载体 | ParrotSoul → Gemini instructions | 每次 session 注入，从 Graphiti personality 分区刷新 |
| Gemini 思维链 | 通过 instructions 引导外化 + LiveKit 事件捕获 | 闭源模型无法直接获取内部推理 |
| Nanobot 身份 | 鹦鹉的"潜意识"，共享 SOUL 偏好 | 所有模块组成一只鹦鹉 |
| Graphiti 分区 | 5 个 group_id: episodic/objects/personality/vocabulary/nanobot_research | 防止关系混乱，社区检测更精准 |
| 三元组提取角色化 | 通过 source_description 引导，不需要多 LLM 实例 | Graphiti 内置 LLM 提取可被 prompt 引导 |
| 模块通信 | 混合: 管道(L1-L3) + 导演(L3↔Gemini) + 黑板+PubSub(Redis) + 分区黑板(Graphiti) | 不同层级的需求不同 |
| 观察者拆分 | 4个独立 Observer: Perception/Conversation/Atmosphere/Archive | 单一职责，可独立测试和调优 |
| L3 角色 | Director (编排者，不参与内容生成) | 借鉴 Inworld Director Layer |

---

## 6. MVP vs 后期

### MVP (Phase 1) 只需要

- [x] ParrotSoul 基础版 (静态 instructions + Graphiti personality 加载)
- [x] Graphiti 2个分区: episodic + objects
- [x] 单一 Observer (不急着拆分)
- [x] Redis 基础黑板 (状态 + 任务队列)

### Phase 2+ 再实现

- [ ] ParrotSoul 演化 (SOUL 随交互变化)
- [ ] 全部 5 个 Graphiti 分区
- [ ] Observer 拆分为 4 个独立消费者
- [ ] Nanobot 读取 SOUL 偏好
- [ ] vocabulary 分区 + 鹦鹉学舌功能
- [ ] 多 Nanobot Worker 协作 (任务分解)

### 后期具体设计

- [ ] 每个 Graphiti 分区的 Entity/Edge Schema
- [ ] 搜索配方 (search recipe) 调优
- [ ] 社区检测频率和触发条件
- [ ] Nanobot 任务类型和优先级系统
- [ ] 鹦鹉性格演化的边界和安全约束
