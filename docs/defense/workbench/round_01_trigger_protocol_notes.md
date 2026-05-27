# 第1轮补充：触发器协议讲法

## 为什么触发器要单独讲

触发器不是某一个具体功能，而是系统里“什么时候自动做事、做完后交给谁”的协议层。

它可以解释三类问题：

1. 为什么助手不是只等用户问，而是能主动感知事件。
2. 为什么主动提醒、照片感知、Graphiti回灌不是散乱功能，而是同一类机制。
3. 为什么后续可以继续扩展新触发器，而不用重写主Brain逻辑。

## 触发器协议的核心表达

建议演讲稿里用这句话作为定义：

> 触发器协议负责把“系统里发生了某个事件”转换成后续动作。这个动作可以是写入观察、暂存证据、生成计划、请求归档、派发后台任务，或者在合适时机通知GOSLO。

## 代码里的协议形状

| 组件 | 作用 | 可讲程度 |
| --- | --- | --- |
| `TriggerKind` | 定义触发方式：启动、周期、事件、按需 | 可以口头讲，不展示代码 |
| `TriggerOutcome` | 定义触发器输出：Observation、bucket操作、StagedRef、Archive、Plan、Nanobot、通知 | 适合PPT画成输出分流图 |
| `TriggerRunner` | 统一运行触发器并处理结果 | 适合讲成“触发器调度器” |

代码依据：

- `src/parrot/dsg/triggers/base.py:36`：`TriggerKind`。
- `src/parrot/dsg/triggers/base.py:44`：`TriggerOutcome`。
- `src/parrot/dsg/triggers/base.py:71`：`commit_observations`。
- `src/parrot/dsg/triggers/base.py:74`：`staged_refs`。
- `src/parrot/dsg/triggers/base.py:75`：`plan_request`。
- `src/parrot/dsg/triggers/runner.py:155`：`_process_result()`。
- `src/parrot/dsg/triggers/runner.py:159`：处理顺序。

## 三个适合讲的触发器例子

| 例子 | 说明什么 | 注意边界 |
| --- | --- | --- |
| 相机模式 Photo Awareness | 拍照预览出现后，系统可以把照片作为短期上下文或证据暂存起来 | 它是相机预览事件后的Awareness策略桥，不要说成普通RPC命令 |
| Graphiti自然语言搜索 / 预加载 | 长期记忆可以通过搜索或预加载进入当前工作记忆，成为背景信息 | 不要说成用户点一下就必然完成全部Graphiti写入 |
| 主动提醒触发器 | 消息、日程或场景状态满足条件后，系统可以选择提醒、暂存、计划或派发任务 | 不要和Nanobot改日程Task混淆 |

## 和 Nanobot Task 的关系

触发器可以派发后台任务，但这不等于所有 Nanobot 任务都是触发器。

答辩里建议这样区分：

- `GOSLO主动派发改日程任务`：用于讲 Task / Scheduler / Nanobot 协作。
- `触发器触发主动提醒`：用于讲触发器协议和主动行为。

这样可以避免“Nanobot”和“提醒”在两个地方出现后让老师误以为它们是同一个机制。

## PPT建议

触发器协议页可以画成：

```text
TriggerKind
STARTUP / PERIODIC / EVENT_DRIVEN / ON_DEMAND
        ↓
Trigger
        ↓
TriggerOutcome
Observation / StagedRef / Plan / Archive / Nanobot Task / Notify
        ↓
Examples
Photo Awareness / Graphiti Recall / Proactive Reminder
```

