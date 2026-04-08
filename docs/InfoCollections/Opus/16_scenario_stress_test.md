# 需求场景推演：状态机与调度器压力测试

> 目的: 用真实使用场景推演当前架构设计，找到遗漏和破绽
> 原则: 场景来自真实需求，不是为了凑状态机而编

---

## 场景 1: 深夜桌前工作 (最基本的长时间场景)

### 情景

用户晚上 11 点坐在书桌前用笔记本电脑工作，手机架在支架上运行 AR 鹦鹉。持续 2 小时。中间偶尔喝口水、看看手机、伸个懒腰。

### 推演

```
00:00  用户打开 APP，手机对着桌面
       L1: Tier 3 (稳定) → 全功能扫描 → 发现 8 个物体
       L2-A: 构建桌面空间图 (笔记本、显示器、杯子、键盘...)
       L2-B: 为每个物体注册语义节点 + Graphiti preload
       L3 → Gemini: "[SCENE] 桌面场景：检测到显示器、键盘、鼠标、蓝色杯子..."
       Gemini (鹦鹉): "哇，主人今晚又要加班啊！桌上东西都在老位置呢"

00:05  一切稳定，鹦鹉空闲
       BT: 空闲子树 → idle_animation + curiosity_scan
       前端: 鹦鹉在桌角停着，偶尔歪头看东西

00:30  用户拿起杯子喝水
       L1: SAM2 追踪到杯子 mask 移动
       L2-A: update_pos("blue_cup") → 新位置在用户手部附近
       L2-A: add_relation("blue_cup", "HELD_BY", "user_hand")
       L2-B: attention↑ (物体移动) → trigger: OBJECT_MOVED
       L3: 判断是否显著 → attention > 0.5 → 推送给 Gemini
       Gemini: (看到杯子移动，但这很日常) → 不说话，或者小声"嗯~"
```

### 🔴 发现的问题

**问题 1: 长时间无事件时的资源浪费**

2 小时内大部分时间桌面没变化。L1 视觉管线在 Tier 3 下 SAM2 始终以 15-30fps 运行，但帧间差异为零。

**缺失**: 没有设计"活动降频"机制——当 L1 输出的 `has_meaningful_change()` 连续 N 秒返回 False 时，应该自动降到低频模式 (如 2fps)，而不是持续 30fps 烧 GPU。

```
补丁: L1 需要一个 ActivityThrottle
  连续无变化 > 5s  → 降到 5fps
  连续无变化 > 30s → 降到 1fps
  任何变化 → 立刻恢复 30fps
```

**问题 2: 鹦鹉长时间沉默的"存在感"问题**

鹦鹉没事做时只有 idle 动画。如果 30 分钟不说话也不动，用户会忘记它的存在，或觉得它死机了。

**缺失**: 没有设计"自主微行为"——鹦鹉在空闲时应该有低频的自发行为 (整理羽毛、看看窗外、轻声哼歌)，这不在当前行为树中。

```
补丁: 空闲子树需要增加 AutonomousMicroBehavior
  每 3-5 分钟触发一次随机微行为
  由 AtmosphereState 的 mood 影响选择
  不发出声音 (不打扰工作)，只做动画
```

**问题 3: 管家模式的"2小时提醒"触发机制不明**

BUTLER_INSTRUCTIONS 说"如果主人工作超过 2 小时，提醒休息"——但谁负责计时？Gemini 不维护精确计时器。

**缺失**: 管家模式的定时提醒需要一个**后端 Timer 模块**，不能依赖 Gemini 自觉。

```
补丁: BehaviorMode.BUTLER 激活时注册 Timer 到后端
  Timer 到期 → L3 ContextInjector 推送: "[BUTLER_REMINDER] 主人已连续工作 120 分钟"
  Gemini 收到后自然地提醒
```

---

## 场景 2: 用户边走边说话 (移动中的对话)

### 情景

用户拿着手机从书桌起身，走向厨房，边走边问鹦鹉"我那个泡茶的壶放哪了"。

### 推演

```
00:00  用户坐在桌前 (DESKTOP 场景)
       鹦鹉停在桌角

00:01  用户拿起手机起身
       ARCore: velocity 突增到 0.8 m/s
       StabilityGate: Tier 3 → Tier 2 (缓慢移动)
       L1: 停止新物体发现，只保持已有追踪
       → 但桌面物体迅速离开视野，SAM2 追踪全部丢失

00:02  用户开始说话: "我那个泡茶的壶放哪了"
       LiveKit: 用户语音 → Gemini (正常对话通道)
       同时:
       - StabilityGate: Tier 1-2 之间跳变 (走路抖动)
       - L2-A: 所有桌面物体 → LOST (离开视野)
       - 场景切换: 应该从 DESKTOP → INDOOR？

       Gemini 思考: 需要查 Graphiti "茶壶" → 调用 query_scene 或 memory_search
       Gemini: "让我想想... 你的茶壶上次我看到是在厨房的台子上！"

00:03  到达厨房
       ARCore: 新的平面检测
       L1: 速度降低 → Tier 2/3 → 开始扫描新环境
       L2-A: 构建新的空间图 → 发现茶壶？
```

### 🔴 发现的问题

**问题 4: 场景切换的触发时机模糊**

用户起身走动时，什么时候触发 `switch_scene("indoor")`？当前设计是 Gemini Tool Call 手动切换，但：
- 用户在说话，Gemini 忙着回答"茶壶在哪"，没空调 switch_scene
- 自动检测要到 Phase 2 才做
- 桌面场景没有折叠，旧的空间图节点全变成 LOST 但没归档

**缺失**: 需要一个**被动场景退化**机制——当 L2-A 中 >70% 的节点变为 LOST 超过 10 秒，自动触发场景折叠，不需要等 Gemini 调用 switch_scene。

```
补丁: SpatialGraph 自检:
  if count(LOST) / count(ALL) > 0.7 and duration > 10s:
      auto_fold_current_scene()
      notify_L3("scene_degraded", reason="most_objects_lost")
      L3 → Gemini: "[SCENE_ALERT] 大部分物体丢失，可能已离开当前场景"
```

**问题 5: 飞行中的鹦鹉去哪了？**

鹦鹉之前停在桌角。用户起身走到厨房——鹦鹉的 AR 锚点是桌角的位置。现在相机对着厨房，桌角在身后。

**缺失**: 鹦鹉在 AR 空间中的"跟随"行为。当用户移动超过一定距离，鹦鹉应该自动飞到用户附近 (新场景中的某个停靠点)。当前行为树没有**自动跟随**的子树。

```
补丁: 行为树需要增加一个"跟随"子树
  Condition: 鹦鹉与相机距离 > 2m 且 持续 > 3s
  Action: 
    1. 在相机前方找一个 AR 平面作为新停靠点
    2. fly_to(new_perch_point)
    3. 或者: 如果没有合适平面，悬停在肩膀位置
  优先级: 介于 Reflex 和 Command 之间
```

**问题 6: 说话和移动同时发生时的 Gemini 视频输入质量**

Gemini Realtime 的 video_input 在用户走路时收到的是模糊晃动的帧。Gemini 可能基于模糊帧做出错误判断。

**缺失**: StabilityGate 只控制了 L1 的视觉处理器，但没有控制 **Gemini 的视频采样率** (`video_sampler`)。在 Tier 1-2 时应该降低发给 Gemini 的帧率或暂停视频发送。

```
补丁: StabilityGate 应该同时影响 Gemini 的 video_sampler
  Tier 3: 正常采样 (~1fps 说话时, ~0.3fps 沉默时) ← LiveKit 默认
  Tier 2: 降低到 0.2fps
  Tier 1: 暂停视频发送 (只保持音频)
  Tier 0: 暂停视频
  实现: 自定义 video_sampler 替换 LiveKit 默认的 VoiceActivityVideoSampler
```

---

## 场景 3: 用户展示新物品 (主动交互)

### 情景

用户拿起一个新买的手办放到桌上，对鹦鹉说"看看这个！"

### 推演

```
00:00  桌面稳定 (DESKTOP, Tier 3)

00:01  用户拿起手办移到桌面中心
       L1 Discoverer: YOLO-World 检测到新物体 → "figure/toy"
       L1 Identifier: DINOv2 提取特征 → 未匹配已知物体 → 新 UUID

00:02  L2-A: add_object("figure_001", position, class="figure")
       L2-B: register_object → Graphiti.search("figure") → 无历史
             → attention = 1.0 (NEW_OBJECT, 最高新奇度)
             → trigger: NEW_OBJECT
       L3: → Gemini: "[SCENE] 发现新物体: figure (未识别, 高注意力)"

00:03  用户说 "看看这个"
       Gemini 同时收到:
         - 用户语音 "看看这个"
         - 视觉上下文 [SCENE] 新物体
       Gemini: "哦！这是什么呀？看起来像个手办... 好酷！是谁的角色？"

00:04  用户说 "是高达"
       Gemini: 理解了
       → Tool: focus_on("figure_001")  ← 想仔细看看
       → L1 On-Demand: 对 figure_001 做高精度 DINOv2 提取
       → Gemini 可能说: "原来是高达！哪个型号的？"

00:05  用户说 "RX-78-2, 帮我记着"
       Gemini: → Tool: dispatch_task("vocabulary_learn", {term: "RX-78-2", category: "高达型号"})
       → Nanobot: 写入 vocabulary 分区 + objects 分区
```

### 🔴 发现的问题

**问题 7: focus_on 之后的 L1 行为不明确**

Gemini 调用 `focus_on("figure_001")` 后，当前设计只是提升了 L2-B 的注意力权重。但 L1 端没有收到"对这个物体做更仔细观察"的指令。

当前 On-Demand 模式的描述是"立即对指定目标执行 DINOv2 特征提取"——但**特征提取完之后呢**？

**缺失**: focus_on 应该触发一个**短期注视行为**:
1. 命令前端鹦鹉头部转向该物体 (head_cmd: look_at)
2. L1 对该物体做一次高精度分析
3. 分析结果注入给 Gemini (不只是 L2-B 权重提升)

```
补丁: CognitiveInterface.handle_focus_on 应该做三件事:
  1. l2b.gemini_focus(uuid)  ← 已有
  2. DataChannel: {type: "head_cmd", cmd: "look_at_object", uuid}  ← 新增
  3. l1.on_demand_analysis(uuid) → 结果 → ContextInjector  ← 新增
```

**问题 8: "帮我记着"是一个未定义的 Tool**

用户说"帮我记着"，Gemini 需要把"这个手办是 RX-78-2"写入记忆。当前 Tool 列表有 `event_end`、`focus_on`、`switch_scene`、`query_scene`、`dispatch_task`——但没有直接的 **"记住这个事实"** Tool。

Gemini 得用 dispatch_task 间接做，但这走的是 Nanobot 异步流程，对于"记住手办叫 RX-78-2"这种简单事实太重了。

**缺失**: 需要一个轻量的 `remember_fact` Tool，直接写入 Graphiti 对应分区，不走 Nanobot。

```python
@function_tool
async def remember_fact(subject: str, fact: str, category: str = "objects") -> str:
    """记住一个事实。用于用户明确要求记住某事，或你认为值得记住的信息。

    Args:
        subject: 主体 (如物体名称、用户名、地点)
        fact: 要记住的事实
        category: "objects" | "personality" | "vocabulary"
    """
    group_id = {"objects": "objects", "personality": "personality",
                "vocabulary": "vocabulary"}.get(category, "objects")
    await graphiti.add_episode(
        name=f"fact_{subject}",
        episode_body=f"{subject}: {fact}",
        group_id=group_id,
        source_description=f"用户明确要求记住的{category}信息",
    )
    return f"已记住: {subject} - {fact}"
```

---

## 场景 4: 用户手机来电 (系统级中断)

### 情景

鹦鹉正在和用户聊天，突然手机来电。

### 推演

```
00:00  鹦鹉正在说话: "我觉得你桌上的——"
       BT: 对话子树 active, body idle (站在桌角)

00:01  手机来电 → 安卓系统弹出来电界面
       可能发生:
       A) APP 被来电覆盖 (部分遮挡或全部进入后台)
       B) 音频焦点被来电抢占
       C) ARCore 可能暂停或降级
```

### 🔴 发现的问题

**问题 9: APP 生命周期管理完全未设计**

安卓手机上来电、切后台、锁屏、通知弹窗都会影响 APP。当前架构没有任何 **APP 生命周期处理**：

- APP 进入后台 → Unity 暂停 → WebRTC 连接怎么办？
- 音频焦点被抢 → Gemini 的语音输出到哪去了？
- 用户接完电话回来 → 鹦鹉应该知道"主人刚接了个电话"还是假装什么都没发生？

**缺失**: 需要一个 `AppLifecycleManager`:

```
补丁:
Unity 端:
  OnApplicationPause(true) →
    1. DataChannel: {type: "lifecycle", state: "paused"}
    2. 降低 WebRTC 码率 (音视频低质量保持连接)
    3. 暂停 AR 渲染 (省电)

  OnApplicationPause(false) →
    1. DataChannel: {type: "lifecycle", state: "resumed"}
    2. 恢复正常码率
    3. 重启 ARCore

Python 端:
  收到 "paused" →
    1. StabilityGate → Tier 0 (全部暂停)
    2. 通知 L3: "用户暂时离开"
    3. Gemini 的对话暂存 (不中断 session)

  收到 "resumed" →
    1. StabilityGate 恢复正常
    2. L3 → Gemini: "[SYSTEM] 用户回来了 (离开了 X 秒)"
    3. Gemini 自然地欢迎回来 (如果离开时间短就不提)
```

---

## 场景 5: 两只手都忙 (手势歧义)

### 情景

用户左手拿着手机 (运行 APP)，右手端着一杯咖啡。用户想让鹦鹉飞到手上，但只能做出右手张开的动作——而右手正拿着杯子。

### 推演

```
00:00  用户右手端着咖啡
       L1: 追踪到杯子在右手区域
       L2-A: "cup" HELD_BY "right_hand"

00:01  用户把咖啡放下，右手张开
       手势检测: open_hand (right)
       BT 反射子树: 检测到张手 → fly_to_hand

       但: 鹦鹉应该飞到右手吗？
       - 右手刚放下杯子，手可能还湿
       - 左手拿着手机 (相机)，不可能放下
```

### 🔴 发现的问题

**问题 10: 手势→行为的映射太简单**

当前设计：`open_hand` → 立刻 `fly_to_hand`。没有考虑：
- **哪只手**？(左手拿着手机不可能飞)
- **手的状态**？(刚放下东西的手 vs 空闲的手)
- **确认**？(用户可能只是伸懒腰张了一下手)

**缺失**: 手势需要**意图确认**而不是直接执行。

```
补丁: 反射子树的手势处理应该分两步
  Step 1 (前端预测): 播放"抬头看向手"动画 (低成本，不移动)
  Step 2 (后端判断):
    - 检查目标手是否空闲 (L2-A 中没有 HELD_BY 关系)
    - 检查手势持续时间 > 0.5s (排除偶然动作)
    - 如果不确定 → Gemini 决定: "主人，你是想让我过去吗？"
  Step 3: 确认后才 fly_to
```

---

## 场景 6: "飞到杯子上"，但杯子刚被拿走 (目标失效)

### 情景

用户说"飞到那个蓝色杯子上"，但杯子在 3 秒前被室友拿走了。

### 推演

```
00:00  蓝色杯子在桌上
       L2-A: "blue_cup" at position (0.5, 0.3, -0.8), state=VISIBLE

00:03  室友拿走杯子 (但用户没注意)
       L1: SAM2 追踪丢失 "blue_cup"
       L2-A: "blue_cup" state → LOST
       L2-B: attention↓ for "blue_cup"
       L3 trigger → Gemini: "[SCENE] 蓝色杯子丢失"

00:05  用户: "飞到那个蓝色杯子上"
       Gemini: 调用 navigate? focus_on?
       → 目标 UUID 在 L2-A 中是 LOST 状态
```

### 🔴 发现的问题

**问题 11: 没有 "fly_to_object" Tool**

当前 Tool 列表没有"飞到某个物体上"的指令。只有 `focus_on` (看) 和 `event_end` (归档)。

Gemini 要让鹦鹉飞到杯子上，需要：
1. 查询杯子位置 (query_scene)
2. 发出导航指令 (???)

**缺失**: 需要一个 `fly_to` Tool 和一个 `perch_on` Tool。

```python
@function_tool
async def fly_to(target: str, description: str = "") -> str:
    """命令鹦鹉飞到某个位置或物体旁边。

    Args:
        target: 物体 UUID 或 "hand_left"/"hand_right"/"shoulder"
        description: 目的描述 (用于日志)
    """
    position = await resolve_target(target)  # 从 L2-A 查位置
    if position is None:
        return f"找不到目标 {target}，它可能已经不在视野中了"
    await dispatcher.dispatch_body_command("fly_to", target=position)
    return f"正在飞向 {target}"
```

**问题 12: 目标失效时的优雅降级**

如果杯子 LOST，`fly_to` 返回"找不到"，Gemini 应该怎么回应？这依赖 Gemini 的 instructions。

**缺失**: SOUL instructions 中需要有目标失效的处理指导。

```
补丁: ParrotSoul instructions 增加:
  "如果 fly_to 返回找不到目标，向主人解释情况并提供帮助:
   - 如果你之前看到过这个物体，说出最后看到的位置
   - 如果物体刚消失不久，可以说'好像刚刚被拿走了'"
```

---

## 场景 7: 弱网环境 (WiFi 不稳定)

### 情景

用户在家中移动，经过了 WiFi 信号弱的区域 (厕所、阳台)。网络延迟从 50ms 飙升到 500ms，丢包率 10%。

### 推演

```
00:00  正常对话中，鹦鹉在说话

00:01  进入弱网区域
       WebRTC: 自适应降码率
       音频: 可能断续
       视频: 帧率下降或冻结
       DataChannel: 部分消息丢失 (Unreliable 通道)

00:05  网络恢复
```

### 🔴 发现的问题

**问题 13: 网络质量对系统的影响未设计**

LiveKit WebRTC 自带自适应码率，但我们的上层系统没有感知网络状态。

**缺失**: 需要一个 `NetworkQualityMonitor`。

```
补丁:
  1. 监听 LiveKit 的连接质量事件
  2. 网络差时:
     - 降低 Gemini video_sampler 帧率
     - DataChannel 遥测从 10Hz 降到 2Hz
     - 告诉 L3: "网络不佳" → Gemini 缩短回复长度
  3. 网络断开时:
     - 前端: 显示"连接中断"提示，播放鹦鹉"断线"动画 (如头上冒问号)
     - 后端: 保持 session 不关闭 (等待重连)
  4. 重连后:
     - 前端: 发送最新 AR 状态 (全量同步)
     - 后端: L3 → Gemini: "[SYSTEM] 网络恢复，断开了 X 秒"
```

---

## 场景 8: Gemini 超时或限流 (云端故障)

### 情景

用户正在和鹦鹉对话，Gemini API 突然变慢 (5秒无响应) 或返回 429 限流。

### 推演

```
00:00  用户: "你觉得这本书怎么样？"
00:01  Gemini: ...... (无响应)
00:05  超时
```

### 🔴 发现的问题

**问题 14: Gemini 不可用时鹦鹉变"死鸟"**

当前架构中 Gemini 是唯一的对话引擎。如果 Gemini 宕机，鹦鹉完全失去对话能力。

**缺失**: 需要 **Gemini 降级方案**:

```
补丁:
  Tier 1 降级: LiveKit FallbackAdapter (已知) → 备用 LLM
  Tier 2 降级: 无 LLM 可用时 → 预录的固定回复
    "嗯... 我脑子好像有点不转了，等我一下..."
    (同时前端播放鹦鹉晕头转向动画)
  Tier 3 降级: 长时间不可用 → 进入"离线伴侣"模式
    只响应手势 (反射子树不依赖 Gemini)
    不对话，但保持存在感 (自主微行为)
```

---

## 场景 9: 多人在场 (未设计但必然发生)

### 情景

用户在客厅对着鹦鹉说话，室友走过来问"这是什么 APP？"

### 推演

```
00:00  用户和鹦鹉聊天

00:01  室友走近
       L1: YOLO-World 检测到新的 "person"
       L2-A: add_object("person_002")
       L2-B: trigger: NEW_OBJECT (person)
       → Gemini: "[SCENE] 发现新的人"

00:02  室友开始说话
       LiveKit STT: 无法区分是谁在说话
       Gemini 收到的语音: 混杂了两个人的声音
```

### 🔴 发现的问题

**问题 15: 完全没有多人处理**

当前假设整个系统只有一个用户。但真实家庭环境中多人在场是常态。

**缺失 (Phase 2+, 但现在需要预留接口)**:

```
补丁 (MVP 最低要求):
  1. 当 L1 检测到 person (非用户) 时，不崩溃
  2. L3 → Gemini: "[SCENE] 有其他人在场" (让 Gemini 自己判断怎么处理)
  3. LiveKit STT 如果支持 speaker_id (diarization)，使用它
  4. 如果不支持，至少让 Gemini 知道"可能有其他人在说话"

补丁 (Phase 2+):
  - 用户注册/声纹识别
  - 只响应注册用户的语音
  - 对其他人保持礼貌但不深度互动
```

---

## 发现汇总

### 遗漏清单

| # | 遗漏 | 严重性 | 归属模块 | MVP 需要？ |
|:--|:-----|:-------|:---------|:----------|
| 1 | L1 活动降频 (无变化时降低帧率) | 中 | L1 StabilityGate | ✅ 省 GPU |
| 2 | 鹦鹉自主微行为 (空闲时的存在感) | 中 | BT 空闲子树 | ✅ 体验 |
| 3 | 管家模式定时器 (后端 Timer) | 低 | L3 / BehaviorMode | Phase 2 |
| 4 | 被动场景退化 (物体大量丢失→自动折叠) | 高 | L2-A + SceneManager | ✅ 必须 |
| 5 | 鹦鹉自动跟随 (用户移动时) | 高 | BT 新子树 | ✅ 核心体验 |
| 6 | StabilityGate 联动 Gemini video_sampler | 中 | L1 + AgentSession | ✅ 质量 |
| 7 | focus_on 联动前端头部 + L1 深度分析 | 中 | L3 + Protocol | ✅ 完整性 |
| 8 | remember_fact 轻量 Tool | 中 | Tools | ✅ 基础功能 |
| 9 | APP 生命周期管理 (后台/来电/锁屏) | 高 | Unity + Protocol | ✅ 安卓必须 |
| 10 | 手势意图确认 (不要一张手就飞) | 中 | BT 反射子树 | ✅ 防误触 |
| 11 | fly_to / perch_on Tool | 高 | Tools + Scheduler | ✅ 核心功能 |
| 12 | 目标失效时的 SOUL 指导 | 低 | ParrotSoul | ✅ 体验 |
| 13 | 网络质量监控和降级 | 高 | NetworkMonitor | ✅ 安卓必须 |
| 14 | Gemini 不可用降级方案 | 中 | AgentSession | Phase 2 |
| 15 | 多人在场最低处理 | 中 | L1 + L3 | ✅ 不崩溃 |

### 按优先级排序的 MVP 必须修补项

```
P0 (不修就没法用):
  #9  APP 生命周期 — 安卓来电就崩 ★用户确认 MVP 必须
  #11 fly_to Tool  — 鹦鹉不能飞就不是鹦鹉 (含体积/禁飞区问题, 见用户审计)
  #13 网络降级     — 手机弱网很常见 ★用户确认 MVP 必须

P1 (不修体验很差):
  #1  活动降频      — GPU 白烧
  #2  自主微行为    — 鹦鹉像死了一样
  #6  视频采样联动  — 走路时 Gemini 看模糊帧
  #7  focus_on 完整 — 看了但鹦鹉没反应
  #8  remember_fact — 基础记忆功能
  #10 手势确认      — 经常误触发
  #15 多人不崩溃    — 家里总有其他人

P2 (后期细节设计时解决):
  #3  管家定时器
  #4  被动场景退化 — ★用户反馈: L2 节点状态可更丰富，核心是物理恒常性 (后期)
  #5  鹦鹉自动跟随 — ★用户反馈: 行为树/模式可扩展解决 (后期)
  #12 目标失效指导
  #14 Gemini 降级
```

---

## 用户审计反馈 (2026-02-24)

### 对 #4 和 #5 的重新定位

用户反馈: #4 (被动场景退化) 和 #5 (自动跟随) **不是 P0**。理由:
- L2 节点状态设计可以更丰富 (VISIBLE / LOST / OCCLUDED / OUT_OF_VIEW / REMEMBERED 等)，关键是保证**物理恒常性** (Object Permanence) — 物体离开视野不等于消失
- 行为树和模式足够灵活，跟随/飞往视野外物体等行为可以在后期细化
- 这些是后期节点设计和行为细节，不阻塞 MVP

**但用户提出了一个更深层的洞察**: 当 #4 和 #5 结合时——比如指令"飞到刚才的杯子"（出现过但现在视野外）：
- 可以飞往 ARCore 记录的原位置 (如果锚点还在)
- 也可以查 Graphiti/DSG 的记忆位置
- 到了之后如果物体还在 → 正常停靠；如果消失了 → 做出困惑/寻找的动作

**关键约束**: 鹦鹉**无法真正认出场景/地图**。视觉模型能识别物体但不能做 SLAM 级别的全局定位。所以：
- 飞到"记忆中的位置" → 取决于 ARCore 锚点是否还有效
- 场景识别/地图匹配 → 困难，功能可选
- 这些能力的边界由**视觉模型能力 + DSG 模块能力**共同决定，不应该在架构中假设它一定可用

### 对 #11 的深化: 物体体积与禁飞区

用户提出核心问题: **鹦鹉怎么知道物体有多大？怎么避免飞进墙里或停在太小的东西上？**

#### ARCore / AR Foundation 在安卓手机上的体积感知能力

| 能力 | ARCore (无LiDAR安卓) | AR Foundation 封装 | 精度 |
|:-----|:---------------------|:-------------------|:-----|
| **平面检测** | ✅ 水平/垂直平面 + 边界多边形 | `ARPlaneManager` | 好 (cm 级) |
| **深度图** | ✅ 单目深度估计 (算法，非硬件) | `AROcclusionManager` | 一般 (±10-30cm) |
| **环境网格** | ⚠️ 有限 (需 ToF 或算法深度) | `ARMeshManager` | 粗糙 |
| **3D BoundingBox** | ⚠️ AR Foundation 6.0+ 有接口，但 ARCore 后端支持有限 | `ARBoundingBoxManager` | 实验性 |
| **Scene Semantics** | ✅ 像素级语义分割 (11类) | ARCore 原生 API | 好 (但仅室外) |

**结论**: 安卓无 LiDAR 手机的体积感知**很弱**。精确的 3D BoundingBox 和环境网格主要是 LiDAR 设备 (iPad Pro, iPhone Pro) 的能力。

#### 我们的方案: 分层近似

```
体积估算的三层方案 (精度递降, 可用性递增):

Tier A: AR 平面 (可靠)
  ✅ 安卓手机可用
  → 鹦鹉知道哪里有平面可以落脚 (桌面、地板、架子)
  → 平面有边界多边形 → 鹦鹉不会飞出桌面边缘
  → MVP 的核心运动基础: 鹦鹉在平面上行走/跳舞/停靠

Tier B: 深度图 + SAM2 mask (粗略)
  ✅ 安卓手机可用
  → SAM2 给出物体的 2D mask → 知道物体在屏幕上占多大
  → ARCore 深度图给出物体距离 → 结合 mask 粗估 3D 尺寸
  → 精度: ±30% (杯子大小可分辨，但不精确)
  → 用途: 判断"这个物体大到够鹦鹉站" vs "太小了站不下"

Tier C: 3D BoundingBox (理想但受限)
  ⚠️ 安卓手机上不可靠
  → 如果设备支持 → 精确的 3D 碰撞体
  → 如果不支持 → fallback 到 Tier B
```

#### 禁飞区设计

```python
class NavigationConstraints:
    """鹦鹉导航约束 (前端 Unity 侧)"""

    MIN_PERCH_AREA = 0.01   # 平方米, 物体表面至少这么大才能停
    MIN_FLY_HEIGHT = 0.05   # 米, 不能贴着平面飞
    MAX_FLY_HEIGHT = 2.0    # 米, 不飞到天花板

    def can_perch_on(self, target) -> bool:
        """判断能否停在某个目标上"""
        if target.type == "ar_plane":
            return True  # 平面总是可以停的
        if target.type == "object":
            # 用 SAM2 mask 面积 + 深度图估算物体顶面面积
            estimated_area = target.mask_area * target.depth_scale
            return estimated_area > self.MIN_PERCH_AREA
        return False

    def get_safe_position(self, target_pos, planes) -> Vector3:
        """在目标附近找一个安全的停靠点"""
        # 优先: 目标物体所在平面的表面
        # 次选: 目标附近最近的 AR 平面
        # 兜底: 目标上方悬停
        ...
```

#### 对 MVP 的影响

用户确认: **在平面上运动和跳舞是 MVP 需求**。

```
MVP 运动能力:
  ✅ 在 AR 平面上行走 (桌面、地板)  → 基于 ARPlaneManager
  ✅ 在平面上跳舞/表演动作           → Unity Animator + 平面约束
  ✅ 从一个平面飞到另一个平面         → 简单抛物线路径
  ✅ 平面边缘检测 (不走出桌面)        → AR 平面边界多边形

  ⚠️ 停在具体物体上 (杯子顶部)      → 需要 Tier B 体积估算, Phase 2
  ⚠️ 精确避障 (绕过显示器飞)         → 需要深度图碰撞, Phase 2
  ❌ 精确 3D 碰撞 (知道杯子把手在哪) → 需要 LiDAR, 不在计划内
```
