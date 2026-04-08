# 任务调度器 · 状态机 · 前后端同步

> 生成日期: 2026-02-24
> 核心问题:
> 1. Nanobot 角色切换 (管家模式等) 怎么实现最好？
> 2. 任务调度器怎么处理并行/串行/中断/优先级？前后端状态机是什么关系？
> 3. 前端 Unity 和后端 Python 的状态机怎么同步？

---

## 0. 你的直觉是对的：这确实混淆了两件事

你提到的"复杂的状态和优先级/打断处理"——实际上涉及**两个不同的状态机**，它们分布在前端和后端，职责完全不同：

```
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│   前端状态机 (Unity)              │    │   后端状态机 (Python)             │
│   "鹦鹉的身体怎么动"              │    │   "鹦鹉的大脑怎么想"              │
│                                   │    │                                   │
│   关注: 动画、物理、渲染            │    │   关注: 感知、决策、记忆            │
│   帧率: 60fps                     │    │   帧率: 事件驱动                   │
│   延迟容忍: <16ms                 │    │   延迟容忍: <500ms                │
│   工具: Unity Animator/BT         │    │   工具: Python asyncio + Redis    │
│                                   │    │                                   │
│   例: "播放飞行动画"               │    │   例: "决定飞到哪只手上"           │
│   例: "避障 + 路径平滑"            │    │   例: "把杯子信息告诉 Gemini"      │
│   例: "落地时的弹跳效果"           │    │   例: "调度 Nanobot 查资料"        │
└─────────────┬───────────────────┘    └─────────────┬───────────────────┘
              │                                       │
              └──────── DataChannel (JSON) ───────────┘
                     权威服务器: 后端
                     前端: 预测 + 执行动画
```

**你没有混淆**——你只是发现了一个真实的架构难点。下面分别拆解。

---

## 1. Nanobot 角色切换

### 1.1 三种方案对比

| 方案 | 实现方式 | 优点 | 缺点 |
|:-----|:---------|:-----|:-----|
| **A: 换 SOUL 文件** | 同一个 Nanobot 进程加载不同配置 | 简单、轻量、共享状态 | 角色边界模糊，难测试 |
| **B: 启动新 Agent** | LiveKit Agent Handoff 切换到不同 Agent | 干净隔离、LiveKit 原生支持 | 上下文丢失风险、冷启动延迟 |
| **C: 模式切换 (推荐)** | 同一只鹦鹉，不同的"行为模式"叠加 | 保持单一身份、模式可叠加、渐进式切换 | 需要自己设计模式管理器 |

### 1.2 推荐方案 C: 行为模式叠加

**关键洞察**: 管家模式不是"变成另一只鹦鹉"，而是"同一只鹦鹉戴上了管家帽子"。

这借鉴了 **Brooks 包容架构 (Subsumption Architecture)** 的核心思想：行为层可以叠加，高层可以抑制低层，但低层始终在运行。

```python
from enum import Flag, auto

class BehaviorMode(Flag):
    """行为模式: 可叠加的 Flag"""
    BASE = auto()        # 基础模式: 好奇、闲逛、看东西
    COMPANION = auto()   # 伴侣模式: 陪伴、聊天、情感响应
    BUTLER = auto()      # 管家模式: 主动提醒、任务跟踪、日程管理
    RESEARCHER = auto()  # 研究者模式: 深度查询、信息汇总
    PLAYFUL = auto()     # 玩耍模式: 游戏、学舌、模仿

class ParrotModeManager:
    """鹦鹉行为模式管理器: 模式可叠加，不互斥"""

    def __init__(self, soul: ParrotSoul):
        self._soul = soul
        self._active_modes = BehaviorMode.BASE | BehaviorMode.COMPANION
        self._mode_configs: dict[BehaviorMode, ModeConfig] = {}

    def activate(self, mode: BehaviorMode):
        """叠加一个行为模式"""
        self._active_modes |= mode
        self._refresh_instructions()

    def deactivate(self, mode: BehaviorMode):
        """移除一个行为模式 (BASE 不可移除)"""
        if mode != BehaviorMode.BASE:
            self._active_modes &= ~mode
            self._refresh_instructions()

    def _refresh_instructions(self):
        """根据当前活跃模式组合 Gemini instructions"""
        instruction_parts = [self._soul.core_instructions]

        if BehaviorMode.BUTLER in self._active_modes:
            instruction_parts.append(BUTLER_INSTRUCTIONS)
        if BehaviorMode.RESEARCHER in self._active_modes:
            instruction_parts.append(RESEARCHER_INSTRUCTIONS)
        if BehaviorMode.PLAYFUL in self._active_modes:
            instruction_parts.append(PLAYFUL_INSTRUCTIONS)

        self._soul.current_instructions = "\n\n".join(instruction_parts)

# 模式指令片段示例
BUTLER_INSTRUCTIONS = """
## 管家职责 (当前已激活)
- 注意时间: 如果主人工作超过 2 小时，提醒休息
- 跟踪待办: 如果主人提到"要做的事"，记录下来
- 主动汇报: Nanobot 完成任务时，主动告知结果
- 注意环境: 光照变暗时提醒开灯
"""

RESEARCHER_INSTRUCTIONS = """
## 研究者职责 (当前已激活)
- 当主人问到不确定的事情时，主动调用 dispatch_task 让 Nanobot 去查
- 汇报研究结论时要简洁但附带关键细节
- 如果发现与已知信息矛盾的新信息，主动指出
"""
```

### 1.3 为什么不用 LiveKit Agent Handoff？

LiveKit Agent Handoff 适合**完全不同的角色** (客服→技术支持→销售)。但鹦鹉的"管家模式"和"伴侣模式"不是不同的角色——它们是**同一角色的不同侧面**。

用 Handoff 会导致：
- 上下文丢失 (换 Agent 后前面的对话可能丢失)
- 人格不一致 (两个 Agent 的 instructions 可能冲突)
- 切换延迟 (需要新 Agent 冷启动)

**但是**——如果未来鹦鹉需要调用一个**专门的工具型 Agent** (比如"翻译模式"需要专门的翻译 LLM)，那就应该用 LiveKit Task：

```python
# 短期任务: 用 LiveKit Task 处理，完成后回到主 Agent
translate_task = Task(
    instructions="将以下内容翻译成英文...",
    tools=[translation_tool],
)
# Task 完成后自动回到鹦鹉主 Agent，上下文保持
```

### 1.4 Nanobot 的角色

Nanobot Worker 本身**不需要角色切换**——它是纯后台任务执行器。它的"角色"由任务类型决定：

```python
@dataclass
class NanobotTask:
    task_id: str
    task_type: str           # "research" | "memory_consolidation" | "vocabulary_learn" | "reminder_check"
    payload: dict
    priority: int = 5        # 1(最高) - 10(最低)
    soul_context: dict = {}  # 携带鹦鹉当前的 SOUL 偏好
    timeout: float = 300     # 秒
```

Nanobot 根据 `task_type` 选择不同的执行策略，但始终是"鹦鹉的潜意识在工作"，不是另一个 Agent。

---

## 2. 任务调度器设计

### 2.1 你说得对：这很复杂

鹦鹉面对的任务场景：

| 场景 | 涉及的任务 | 是否可并行 | 中断行为 |
|:-----|:----------|:----------|:---------|
| 正在飞行途中，用户突然说话 | 飞行 + 语音响应 | **可并行** (继续飞 + 同时说话) | 飞行不中断 |
| 正在说话，用户伸出手 | 语音 + 手势反射 | **可并行** (说完当前句子 + 准备飞向手) | 语音可能被打断 |
| 正在桌面模式，用户开始走动 | 桌面追踪 + 场景切换 | **串行** (先暂停桌面 → 切换场景) | 桌面追踪中断 |
| Nanobot 正在查资料，又来了新任务 | 研究A + 研究B | **可并行** (多个 Worker) | 不互相中断 |
| 用户说"别动"，鹦鹉正在飞 | 飞行动画 + 冻结指令 | **串行** (立即停止飞行) | **高优先级中断** |
| 鹦鹉正在"看"物体，Gemini 要回话 | 视觉分析 + 语音生成 | **可并行** (视觉管线和对话管线独立) | 不互相中断 |

### 2.2 学什么技术来解决这个问题

#### 游戏 AI 的三大范式

| 范式 | 核心思想 | 适用场景 | 代表 |
|:-----|:---------|:---------|:-----|
| **有限状态机 (FSM/HFSM)** | 状态 + 转换条件 | 简单的、状态少的行为 | Unity Animator (已经是 HFSM) |
| **行为树 (Behavior Tree)** | 优先级分支 + 条件/序列/并行 | 复杂的、可组合的行为 | Halo、TLOU；py-trees (Python)；Unity Behavior Graph |
| **效用 AI (Utility AI)** | 为每个行为打分，选最高分 | 需要"权衡"多目标的决策 | The Sims; 可与 BT 结合 |

**还有一个重要的启发**:

| 范式 | 核心思想 | 对我们的启发 |
|:-----|:---------|:-----------|
| **包容架构 (Subsumption)** | 层级化行为，高层抑制低层，低层始终运行 | 鹦鹉的反射层(闪避) > 导航层(飞行) > 社交层(聊天) > 好奇层(探索) |

#### 机器人领域的两个经典框架

| 框架 | 特点 | 对我们的学习价值 |
|:-----|:-----|:---------------|
| **py-trees** (Python) | Python 行为树库，支持黑板、并行、优先级；广泛用于 ROS 机器人 | **后端调度器可以直接用** |
| **FlexBE** (ROS) | 分层状态机 + 操作员监控界面；OBE(机上执行) + OCS(远程控制) | 架构模式可借鉴：OBE=前端Unity，OCS=后端Python |

### 2.3 我们的调度器架构：分层行为树

现有架构图中的调度器（旧稿中常写作 Dispatcher）是一个简单的 Reflex/Intent/Task 三级路由。需要升级为**分层行为树 + 包容架构的混合体**。

```
后端调度器 (Python 侧 — "脊髓 + 小脑")
═══════════════════════════════════════

不管理动画/物理 (那是前端的事)
只管理: 决策、任务分配、资源锁、前端指令下发

┌─────────────────────────────────────────────────┐
│             Behavior Tree (根节点)                │
│                                                   │
│  Selector (优先级从高到低)                         │
│  │                                                │
│  ├─ [Guard: 紧急] 安全子树                        │
│  │   ├─ Condition: 用户说"停/别动"               │
│  │   └─ Action: freeze_all()                     │
│  │       → DataChannel: {cmd: "freeze"}           │
│  │                                                │
│  ├─ [Guard: 反射] 反射子树                        │
│  │   ├─ Condition: 手势检测到张手                  │
│  │   └─ Sequence:                                 │
│  │       1. lock_body("fly")                      │
│  │       2. DataChannel: {cmd: "fly_to_hand", ...}│
│  │       3. wait_until("arrived")                 │
│  │       4. unlock_body("fly")                    │
│  │                                                │
│  ├─ [Guard: 语音] 对话子树                        │
│  │   └─ (由 LiveKit AgentSession 直接管理)         │
│  │       Gemini 的 speaking/listening/thinking     │
│  │                                                │
│  ├─ [Guard: 导航] 导航子树                        │
│  │   ├─ Condition: 有导航目标                      │
│  │   └─ Sequence:                                 │
│  │       1. plan_path(target)                     │
│  │       2. DataChannel: {cmd: "navigate", path}  │
│  │       3. wait_until("reached")                 │
│  │                                                │
│  └─ [Default] 空闲子树                            │
│      ├─ Parallel:                                 │
│      │   ├─ idle_animation_cycle()                │
│      │   └─ curiosity_scan() (看看周围)            │
│      └─ (可被任何高优先级打断)                      │
│                                                   │
│  ──── 并行始终运行 (不参与优先级选择) ────          │
│  Parallel (与主树并行):                             │
│  ├─ vision_pipeline.tick()     (L1-L3 始终运行)    │
│  ├─ nanobot_queue.check()      (后台任务始终处理)   │
│  └─ atmosphere.tick()          (氛围始终更新)       │
└─────────────────────────────────────────────────┘
```

### 2.4 关键设计：哪些可以并行，哪些不行

```
┌──────────────────────────────────────────────────┐
│                资源锁模型                          │
│                                                    │
│  Body Channel (身体通道) — 互斥                    │
│  ├─ fly_to_hand     ┐                              │
│  ├─ navigate_to     ├─ 只能选一个 (用 Redis Lock)  │
│  ├─ perch_on        ┘                              │
│  └─ freeze          ← 最高优先级，打断一切           │
│                                                    │
│  Voice Channel (语音通道) — 半互斥                  │
│  ├─ gemini_speaking  ← 可被用户打断                 │
│  └─ tts_playing      ← 可与身体动作并行             │
│                                                    │
│  Vision Channel (视觉通道) — 独立                   │
│  └─ L1→L2→L3 管线   ← 始终运行，不受其他通道影响   │
│                                                    │
│  Background Channel (后台通道) — 独立               │
│  └─ Nanobot Workers  ← 始终运行，多个可并行         │
└──────────────────────────────────────────────────┘
```

实现为 Redis 分布式锁：

```python
class ResourceLockManager:
    """资源锁管理器: 确保互斥操作不冲突"""

    CHANNELS = {
        "body": {"max_concurrent": 1},
        "voice": {"max_concurrent": 1},
        "vision": {"max_concurrent": 1},   # 管线整体一个
        "background": {"max_concurrent": 5}, # Nanobot 可多个并行
    }

    async def try_lock(self, channel: str, task_id: str, priority: int) -> bool:
        """尝试获取资源锁。如果优先级更高，可以抢占当前占用者"""
        current = await self._redis.hget(f"lock:{channel}", "holder")
        if not current:
            await self._redis.hset(f"lock:{channel}", mapping={
                "holder": task_id, "priority": priority,
            })
            return True

        current_priority = int(await self._redis.hget(f"lock:{channel}", "priority"))
        if priority < current_priority:  # 数字越小优先级越高
            await self._preempt(channel, current, task_id, priority)
            return True

        return False

    async def _preempt(self, channel: str, victim_id: str, new_id: str, new_priority: int):
        """抢占: 通知被抢占的任务中止"""
        await self._redis.publish(f"preempt:{victim_id}", "abort")
        await self._redis.hset(f"lock:{channel}", mapping={
            "holder": new_id, "priority": new_priority,
        })
```

### 2.5 中断和优先级矩阵

| 当前行为 → | freeze | fly_to_hand | navigate | speak | idle |
|:-----------|:-------|:------------|:---------|:------|:-----|
| **freeze 请求** | 保持 | **中断** | **中断** | **中断** | **中断** |
| **fly_to_hand 请求** | 拒绝 | 排队 | **中断** | 并行 | **中断** |
| **navigate 请求** | 拒绝 | 排队 | 替换 | 并行 | **中断** |
| **speak 请求** | 拒绝 | 并行 | 并行 | 打断上句 | 并行 |
| **idle 恢复** | 排队 | — | — | — | 保持 |

优先级数值 (小=高):

```python
class TaskPriority:
    EMERGENCY = 1   # freeze, avoid_collision
    REFLEX = 2      # fly_to_hand (手势反射)
    COMMAND = 3     # navigate (用户命令)
    SOCIAL = 5      # speak (对话)
    PROACTIVE = 7   # curiosity_scan, idle_look
    BACKGROUND = 9  # nanobot_research
```

### 2.6 可学习的参考项目和框架

| 项目/框架 | 技术 | 学什么 |
|:----------|:-----|:-------|
| **py-trees** (Python) | 行为树 + 黑板 + 并行节点 | **后端调度器的核心框架**；成熟的 Python BT 实现，原生支持 ROS 但可独立使用 |
| **Unity Behavior Graph** (Unity 6) | 可视化行为树 | **前端状态机**；Unity 原生支持，设计师友好 |
| **FlexBE** (ROS) | 分层状态机 + OBE/OCS 分离 | **前后端分离架构**；OBE(机器人端)≈Unity, OCS(控制端)≈Python |
| **Halo AI** (GDC 演讲) | 行为树 + 优先级中断 | 伙伴 NPC 的中断/恢复设计 |
| **The Sims** | Utility AI + 行为队列 | 多需求权衡 (饥饿 vs 社交 vs 好奇) → 鹦鹉的自主行为选择 |
| **Subsumption (Brooks)** | 层级化行为 + 抑制 | 反射层>导航层>社交层>好奇层 的分层优先级 |
| **Gabriel Gambetta** (博客) | 权威服务器 + 客户端预测 | **前后端状态同步**的经典教程 |

---

## 3. 前端与后端的状态机分工

### 3.1 核心原则：后端是权威，前端是执行+预测

借鉴游戏网络架构的 **权威服务器 (Authoritative Server)** 模式：

```
后端 (Python): 权威服务器
  ✓ 做所有决策 (飞到哪、说什么、关注什么)
  ✓ 管理资源锁 (谁在占用身体通道)
  ✓ 维护 DSG 图 (L1→L2→L3)
  ✗ 不做动画插值
  ✗ 不做物理模拟
  ✗ 不做路径平滑

前端 (Unity): 执行器 + 预测器
  ✓ 执行动画 (Animator)
  ✓ 物理模拟 (NavMesh, 碰撞)
  ✓ 路径平滑 (贝塞尔曲线)
  ✓ 客户端预测 (手势识别到→立刻播放抬头动画，不等后端确认)
  ✗ 不做高层决策
  ✗ 不管 DSG
  ✗ 不管 Graphiti
```

### 3.2 前端状态机 (Unity Animator / Behavior Graph)

前端的状态机是**纯动画/物理层面**的，它不"思考"——它只执行后端的指令并保证动画流畅。

```
Unity 前端状态机 (Hierarchical State Machine)
├── TopLevel
│   ├── Idle (默认)
│   │   ├── Idle_Perch      (停在某处)
│   │   ├── Idle_LookAround (左看右看)
│   │   └── Idle_Preen      (整理羽毛)
│   │
│   ├── Flying (在飞)
│   │   ├── Fly_ToTarget     (飞向目标)
│   │   ├── Fly_Hover        (悬停)
│   │   └── Fly_Land         (着陆)
│   │
│   ├── Interacting (与用户互动)
│   │   ├── Interact_OnHand  (站在手上)
│   │   ├── Interact_Nuzzle  (蹭蹭)
│   │   └── Interact_Dance   (跳舞)
│   │
│   └── Frozen (冻结)
│       └── (所有动画暂停，保持最后一帧)
│
├── HeadLayer (头部独立层 — 可与身体并行)
│   ├── Head_Forward
│   ├── Head_LookAt (注视某物体)
│   └── Head_Tilt (歪头)
│
└── WingLayer (翅膀独立层)
    ├── Wing_Folded
    ├── Wing_Flapping
    └── Wing_Spread
```

**关键**: 头部和翅膀是**独立的动画层**，可以与身体状态并行。鹦鹉可以一边飞一边看向某个物体。

### 3.3 后端状态机 (Python — 行为决策)

后端不管动画——它管的是**高层意图**：

```python
from enum import Enum

class ParrotIntent(Enum):
    """鹦鹉当前的高层意图"""
    IDLE = "idle"                   # 无特定目标
    FLYING_TO = "flying_to"         # 正在飞向某处
    PERCHING = "perching"           # 停在某物体/手上
    OBSERVING = "observing"         # 正在注视某物体
    CONVERSING = "conversing"       # 正在对话中
    EXECUTING_TASK = "executing"    # 正在执行 Nanobot 任务
    FROZEN = "frozen"               # 冻结

class ParrotState:
    """后端维护的鹦鹉状态 (权威状态)"""
    intent: ParrotIntent = ParrotIntent.IDLE
    target_uuid: str | None = None        # 当前目标物体/位置
    target_position: tuple | None = None  # 世界坐标
    body_lock_holder: str | None = None   # 谁锁住了身体通道
    voice_active: bool = False            # 是否在说话
    current_scene: SceneType = SceneType.DESKTOP
    active_modes: BehaviorMode = BehaviorMode.BASE | BehaviorMode.COMPANION
```

### 3.4 前后端状态同步协议

通过 LiveKit DataChannel 传输 JSON 消息，分为两种：

#### 后端→前端: 指令 (Command)

```python
# 后端发出高层指令，前端负责执行细节

# 身体指令
{"type": "body_cmd", "cmd": "fly_to", "target": [1.2, 0.8, -0.5], "speed": "normal"}
{"type": "body_cmd", "cmd": "perch_on", "anchor_id": "hand_left"}
{"type": "body_cmd", "cmd": "freeze"}
{"type": "body_cmd", "cmd": "unfreeze"}
{"type": "body_cmd", "cmd": "idle"}

# 头部指令 (可与身体并行)
{"type": "head_cmd", "cmd": "look_at", "target": [0.5, 1.0, -0.3]}
{"type": "head_cmd", "cmd": "look_at_object", "uuid": "blue_cup"}
{"type": "head_cmd", "cmd": "tilt", "angle": 15}

# 表情/状态指令
{"type": "emotion_cmd", "emotion": "curious", "intensity": 0.8}
{"type": "emotion_cmd", "emotion": "happy", "intensity": 0.6}
```

#### 前端→后端: 遥测 + 事件 (Telemetry & Events)

```python
# AR 遥测 (10Hz, unreliable DataChannel)
{
    "type": "ar_telemetry",
    "tracking_state": "Tracking",
    "camera_velocity": 0.05,
    "camera_angular_velocity": 0.12,
    "planes_detected": 3,
}

# 手势事件 (事件驱动, reliable DataChannel)
{"type": "gesture_event", "gesture": "open_hand", "hand": "left", "position": [0.3, 0.9, -0.2]}
{"type": "gesture_event", "gesture": "close_hand", "hand": "left"}

# 动画完成回调
{"type": "anim_event", "event": "fly_arrived", "at": [1.2, 0.8, -0.5]}
{"type": "anim_event", "event": "land_complete"}

# 用户交互事件
{"type": "ui_event", "action": "tap_object", "uuid": "blue_cup"}
```

### 3.5 客户端预测 (延迟掩盖)

后端决策需要时间 (Gemini 思考 ~200ms，网络 ~50ms)。前端不能傻等——要用**客户端预测**掩盖延迟：

```csharp
// Unity 端: 客户端预测示例
public class ParrotPrediction : MonoBehaviour
{
    // 检测到手势后立即执行预测动画，不等后端确认
    void OnGestureDetected(GestureEvent evt)
    {
        if (evt.gesture == "open_hand")
        {
            // 预测: 后端大概率会发 fly_to_hand
            // 立刻播放"抬头看向手"的动画 (低成本，不影响位置)
            headAnimator.Play("LookAt_Hand");
            wingAnimator.Play("Wing_ReadyToFly");

            // 但不移动! 等后端确认目标位置后再飞
            pendingPrediction = "fly_to_hand";
        }
    }

    // 后端确认到达后，校正状态
    void OnBackendCommand(BodyCommand cmd)
    {
        if (cmd.cmd == "fly_to" && pendingPrediction == "fly_to_hand")
        {
            // 预测正确: 直接从当前预测动画过渡到飞行
            StartFlyTo(cmd.target);
            pendingPrediction = null;
        }
        else if (pendingPrediction != null)
        {
            // 预测错误: 取消预测动画，执行实际指令
            CancelPrediction();
            ExecuteCommand(cmd);
        }
    }
}
```

### 3.6 前后端完整交互流程示例

```
用户伸出手                                     鹦鹉正在桌上闲逛
    │                                              │
    ▼                                              │
[Unity] 手势检测: open_hand                        │
    │                                              │
    ├─(1) 客户端预测: 立刻播放"抬头看手"动画 ────────→ 头部转向手
    │                                              │
    ├─(2) DataChannel → 后端:                       │
    │   {"type": "gesture_event",                  │
    │    "gesture": "open_hand",                   │
    │    "hand": "left",                           │
    │    "position": [0.3, 0.9, -0.2]}             │
    │                                              │
    ▼                                              │
[Python] 行为树 Tick:                               │
    反射子树 → Condition: open_hand ✓               │
    → try_lock("body", "fly_to_hand", priority=2)  │
    → lock 成功 (之前是 idle, priority=9)           │
    │                                              │
    ├─(3) DataChannel → 前端:                       │
    │   {"type": "body_cmd",                       │
    │    "cmd": "fly_to",                          │
    │    "target": [0.3, 0.9, -0.2],               │ ← 目标=手的位置
    │    "speed": "fast"}                          │
    │                                              │
    ▼                                              │
[Unity] 收到 fly_to:                               │
    预测正确! 从"抬头看手"平滑过渡到飞行动画 ─────→ 飞向手
    │                                              │
    │ (飞行途中, Gemini 开始说话)                    │
    │                                              │
[Python] Gemini: "哦！主人要我过去吗？来了来了！"     │
    │   (voice 通道和 body 通道并行)                │
    │                                              │
    ▼                                              │
[Unity] 到达手掌位置                                │
    {"type": "anim_event", "event": "fly_arrived"} │
    │                                              │
[Python] unlock_body("fly_to_hand")                │
    DataChannel: {"type": "body_cmd",              │
                  "cmd": "perch_on",               │
                  "anchor_id": "hand_left"}        │
    │                                              │
[Unity] 播放停落动画 ────────────────────────────→ 站在手上
```

---

## 4. py-trees 作为后端调度器的可行性

### 4.1 为什么选 py-trees

| 特性 | py-trees | 自己实现 |
|:-----|:---------|:---------|
| 行为树核心 (Selector/Sequence/Parallel) | ✅ 成熟稳定 | 需要从头写 |
| 黑板 (共享状态) | ✅ 内置 | 需要接 Redis |
| 可视化调试 | ✅ ASCII/dot 渲染 | 需要自己做 |
| Python 原生 | ✅ | — |
| 与 asyncio 集成 | ⚠️ 需要适配 | 可直接 async |
| 社区 + 文档 | ✅ 活跃 (2025 发布 2.4.0) | — |

### 4.2 集成方案

```python
import py_trees

class ParrotBehaviorTree:
    """鹦鹉后端行为树: 使用 py-trees"""

    def __init__(self, session: AgentSession, lock_mgr: ResourceLockManager):
        self._session = session
        self._lock_mgr = lock_mgr
        self._blackboard = py_trees.blackboard.Client(name="Parrot")
        self._tree = self._build_tree()

    def _build_tree(self) -> py_trees.trees.BehaviourTree:
        root = py_trees.composites.Selector(
            name="Root",
            memory=False,
            children=[
                self._build_emergency_subtree(),   # 最高优先级
                self._build_reflex_subtree(),       # 反射
                self._build_command_subtree(),       # 用户指令
                self._build_social_subtree(),        # 对话
                self._build_idle_subtree(),          # 空闲
            ],
        )

        # 并行始终运行的子系统
        always_on = py_trees.composites.Parallel(
            name="AlwaysOn",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(),
            children=[
                VisionPipelineTick(),    # L1-L3
                NanobotQueueCheck(),     # 后台任务
                AtmosphereTick(),        # 氛围更新
            ],
        )

        top = py_trees.composites.Parallel(
            name="TopLevel",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(),
            children=[root, always_on],
        )

        return py_trees.trees.BehaviourTree(root=top)

    async def tick(self):
        """主循环: 10Hz tick"""
        self._tree.tick()
```

### 4.3 项目结构更新

```
agent/
├── dispatcher/                   # 调度层 (升级)
│   ├── __init__.py
│   ├── behavior_tree.py          # 🆕 py-trees 行为树 (后端调度核心)
│   ├── resource_locks.py         # 🆕 资源锁管理器 (body/voice/vision/background)
│   ├── task_priority.py          # 🆕 优先级定义和中断矩阵
│   ├── router.py                 # 保留: Reflex/Intent/Task 路由 (现在是 BT 的叶节点)
│   └── redis_bus.py              # 保留: Redis 通信
│
├── protocol/                     # 🆕 前后端通信协议
│   ├── __init__.py
│   ├── commands.py               # 后端→前端 指令定义
│   ├── telemetry.py              # 前端→后端 遥测定义
│   └── events.py                 # 前端→后端 事件定义
```

---

## 5. 参考项目汇总

| 项目 | 学习内容 | 适用层 |
|:-----|:---------|:-------|
| **py-trees** | Python 行为树，黑板，并行/序列/选择器 | 后端调度器核心 |
| **Unity Behavior Graph** | 可视化行为树/状态机 | 前端动画状态机 |
| **FlexBE** | OBE/OCS 分离架构，分层状态机 | 前后端分工模式 |
| **Subsumption Architecture** | 层级行为 + 抑制/包容 | 优先级中断设计理念 |
| **Gabriel Gambetta 系列** | 权威服务器 + 客户端预测 + 状态调和 | 前后端状态同步 |
| **Halo AI (GDC)** | 行为树 + 伙伴 NPC 中断/恢复 | 同伴 AI 的中断设计 |
| **The Sims** | Utility AI + 需求评分 | 鹦鹉自主行为选择 (好奇/社交/休息) |
| **LiveKit Tasks** | 短期任务 + Agent Handoff | 特殊能力临时调用 |

---

## 6. 决策总结

| 设计决策 | 选择 | 理由 |
|:---------|:-----|:-----|
| Nanobot 角色切换 | **模式叠加** (不换 Agent) | 保持单一身份，模式可组合，借鉴包容架构 |
| 后端调度器 | **py-trees 行为树** + 资源锁 | 成熟库、支持并行/中断/黑板、Python 原生 |
| 前端状态机 | **Unity Animator HFSM** + 多层 (身体/头/翅膀) | 动画层独立，支持并行动画 |
| 前后端通信 | **权威服务器模式**: 后端决策 → DataChannel 指令 → 前端执行 | 单一数据源、避免冲突 |
| 延迟掩盖 | **客户端预测**: 手势→立即播放预测动画 → 后端确认/校正 | 用户感知零延迟 |
| 通道模型 | 4 通道 (body/voice/vision/background) + Redis Lock | 清晰的并行/互斥规则 |
| 中断优先级 | Emergency > Reflex > Command > Social > Proactive > Background | 安全第一，反射优先 |

---

## 7. MVP vs 后期

### MVP (Phase 1-2) 实现

- [x] 简单的 Reflex/Intent/Task 三级路由 (不用 py-trees)
- [x] body_cmd / head_cmd DataChannel 协议
- [x] Unity Animator HFSM (Idle/Flying/Perching)
- [x] Redis 资源锁 (body 通道)
- [x] 基础客户端预测 (手势→抬头)

### Phase 3+ 升级

- [ ] py-trees 行为树替换简单路由
- [ ] 完整 4 通道资源锁
- [ ] 中断优先级矩阵
- [ ] Utility AI 评分 (鹦鹉自主行为选择)
- [ ] 行为模式叠加 (BUTLER/RESEARCHER/PLAYFUL)
- [ ] 多 Nanobot Worker 并行
- [ ] 前端预测/调和 (Gabriel Gambetta 模式)

### 后期深入研究

- [ ] py-trees 与 asyncio 集成方案
- [ ] Unity Behavior Graph vs 传统 Animator 的取舍
- [ ] Utility AI 评分函数设计 (好奇/社交/休息的权衡曲线)
- [ ] Nanobot 任务依赖图 (任务 B 依赖任务 A 的结果)
