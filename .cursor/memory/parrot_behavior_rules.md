---
status: ratified
category: reference
status_note: "GOSLO 行为模式入口：状态机 + Reflex/Intent/Task + 同步 tool 体感红线 + 工具注册表。Sprint3/4 继续补充，完成后冻结为 app 行为规则。"
last_reviewed: 2026-04-25
---

# GOSLO 鹦鹉行为状态规则

> 维护者: 用户 + AI
> 创建: 2026-04-13
> 用途: 定义鹦鹉的行为状态机、动作兼容矩阵、冲突解决规则、行为工具同步/异步语义
> 对应代码: Unity 前端状态机 + Python 后端调度器
> 参考: Opus 14 (调度器+状态机), Opus 17 (DSG触发器), 包容架构

---

## 0. 行为规则索引与分层口径

本文件是 GOSLO 行为模式的入口。其他文档可以展开细节，但新增行为工具或状态机规则时，必须回到这里登记其层级、是否阻塞对话、失败反馈和用户可感知语义。

相关文档：

| 文档 | 负责内容 | 本文件引用点 |
|:-----|:---------|:-------------|
| `.cursor/memory/architecture/ar_feature_vision.md` | 三层意识分发、视觉门控、Blackboard 注入原则 | §0.1 / §0.2 |
| `.cursor/memory/architecture/sprint2_completion_report_20260423.md` | Intent 层、Router 只 ack、BB writer 归属 | §0.1 |
| `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md` | tool 同步/异步体感红线、按需识别路径 | §0.3 / §4.3 |
| `.cursor/memory/architecture/sprint3_simulation_audit_20260423.md` | `set_video_tier`、动态 rebuild、仿真路径审计 | §4.3 |
| `.cursor/skills/livekit-unity-video-publish/SKILL.md` | Unity 主视频源、Tier、首帧/新鲜帧门 | §4.3 |

### 0.1 调度层：Reflex / Intent / Task

调度层回答“事件由谁处理、时间尺度多长、是否是 GOSLO 自身行为”：

| 调度层 | 时间尺度 | 典型事件 | Gemini 是否直接等待 | 代码入口 |
|:------|:---------|:---------|:---------------------|:---------|
| `Reflex` | ms-s | open_palm、紧急避障、低层身体反应 | 否 | `scheduler.router.HandleReflex` |
| `Intent` | s-min | 切视频档位、视觉状态调节、行为模式调整 | **用户/tool 主动触发时要等待结果；后台自动调节可静默** | `PerceptionSupervisor` / Brain tools |
| `Task` | min+ | Nanobot research、长记忆整理、异步后台工作 | 否；必须明示“我派出去/稍后告诉你” | `dispatch_task` / Scheduler |

关键区别：`Intent` 不是“都 fire-and-forget”。后台自主 Intent 可以静默写 BB；但 Gemini tool 主动触发的 Intent 是 GOSLO 自身行为，必须同步等待可感知结果或明确失败。

### 0.2 意识层：潜意识 / 自主行动 / 通报

意识层回答“Gemini 是否需要知道”：

| 意识层 | 用途 | 默认策略 |
|:------|:-----|:---------|
| 层① `Subconscious` | 记录事实、审计、反思 | 总是记录，不打扰对话 |
| 层② `Autonomous Action` | 代码/状态机自己处理 | 成功通常不说，失败或分歧再升级 |
| 层③ `Conscious Report` | 明确送入 Gemini 上下文 | 用户可见分歧、失败、用户主动动作、影响 Gemini 话术事实时使用 |

`tick/last_rpc_ack` 是层③失败反馈面。成功无需多嘴；失败必须让 GOSLO 知道，避免它说“我飞过去了/我切好了”但 Unity 实际没做到。

### 0.3 Tool 体感红线

**tool 的同步/异步行为必须和 GOSLO 说出口的话一致。**

| tool 方式 | 允许话术 | 是否合格 |
|:----------|:---------|:---------|
| 同步等待结果 | “我看了/我切好了/没成功，因为...” | ✅ |
| 异步委派任务 | “我派女仆去查了，稍后告诉你” | ✅ |
| 异步 fire-and-forget 却说已完成 | “我切好了/这是 XX” | ❌ |

因此，凡是注册为 GOSLO 自身行为的 tool，必须在同一次 tool 返回中给出 `applied / rejected / timeout / no_target / unchanged` 这类结果，不把成功/失败只留给后续 `last_rpc_ack`。

## 1. 状态定义

### 1.1 身体状态 (Body State) — 互斥

鹦鹉在任意时刻只能处于一个身体状态。

| 状态 | 描述 | Unity 动画 | 可被打断 |
|:-----|:-----|:----------|:---------|
| `IDLE` | 空闲，站在某处 | idle, idle_look, preen | 任何状态可打断 |
| `FLYING` | 正在飞行中 | fly, fly_hover | 仅 FREEZE 可打断 |
| `PERCHING` | 落地/停靠中 (着陆过渡) | land, perch | 完成后自动→IDLE |
| `PERCHED_ON_HAND` | 站在手上 | perch (手部跟踪模式) | 手消失→FLYING(返回) |
| `DANCING` | 跳舞/表演中 | dance, wing_flap | 语音可打断 |
| `FROZEN` | 冻结 (用户说"别动") | 保持最后一帧 | 仅 UNFREEZE 解除 |

### 1.2 头部状态 (Head State) — 独立层，可与身体并行

| 状态 | 描述 | 兼容身体状态 |
|:-----|:-----|:-----------|
| `HEAD_FORWARD` | 头朝前 | 全部 |
| `HEAD_LOOK_AT` | 注视某物/某人 | 全部 (飞行中也可看) |
| `HEAD_TILT` | 歪头思考 | IDLE, PERCHED_ON_HAND |
| `HEAD_NOD` | 点头 | IDLE, PERCHED_ON_HAND |

### 1.3 认知状态 (Cognitive State) — 后端，独立于身体

| 状态 | 描述 | 对语音的影响 |
|:-----|:-----|:-----------|
| `LISTENING` | 听用户说话 | 不说话 |
| `THINKING` | Gemini 正在处理 (tool调用等) | 不说话，可以歪头 |
| `SPEAKING` | 正在说话 | 占用语音通道 |
| `IDLE_MIND` | 无特定认知任务 | 可说可不说 |

---

## 2. 动作兼容矩阵

"✅可并行 / ❌互斥 / ⚠️条件允许"

### 2.1 身体×语音

| 身体状态 ↓ / 语音 → | 说话 | 听 | 静默 |
|:-----|:---|:---|:-----|
| IDLE | ✅ | ✅ | ✅ |
| FLYING | ✅ 可以边飞边说 | ✅ | ✅ |
| PERCHED_ON_HAND | ✅ 可以边站边说 | ✅ | ✅ |
| DANCING | ⚠️ 说完当前句后暂停舞蹈，或等舞蹈间隙再说 | ✅ | ✅ |
| FROZEN | ❌ 冻结时不说话 | ✅ 但不回应 | ✅ |

### 2.2 身体×头部

| 身体状态 ↓ / 头部 → | 歪头思考 | 注视物体 | 点头 | 朝前 |
|:-----|:---|:---|:---|:---|
| IDLE | ✅ | ✅ | ✅ | ✅ |
| FLYING | ❌ 飞行中不歪头 | ✅ 可以看目标 | ❌ | ✅ |
| PERCHED_ON_HAND | ✅ | ✅ | ✅ | ✅ |
| DANCING | ❌ 跳舞有自己的头部动画 | ❌ | ❌ | ❌ |
| FROZEN | ❌ | ❌ | ❌ | 保持冻结 |

### 2.3 认知×身体

| 认知状态 ↓ / 身体 → | IDLE | FLYING | PERCHED | DANCING | FROZEN |
|:-----|:---|:---|:---|:---|:---|
| THINKING | ✅ 歪头 | ✅ 继续飞 | ✅ 歪头 | ⚠️ 暂停舞蹈 | ❌ |
| SPEAKING | ✅ | ✅ 边飞边说 | ✅ 边站边说 | ⚠️ 见2.1 | ❌ |
| LISTENING | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## 3. 冲突解决规则

### 3.1 动画 RPC 冲突

**场景**: 后端发了 `animate("dance")`，但鹦鹉正在思考(THINKING)

| 冲突 | 解决方案 |
|:-----|:---------|
| 请求跳舞，但正在思考 | **排队等待**: 思考完成后执行舞蹈 |
| 请求歪头思考，但正在跳舞 | **打断舞蹈**: 思考优先，舞蹈停止 |
| 请求飞行，但正在说话 | **并行**: 边飞边说 |
| 请求飞行，但正在跳舞 | **打断舞蹈**: 飞行优先 |
| 请求冻结，但任何状态 | **立即执行**: FREEZE 最高优先级 |

### 3.2 优先级链 (从高到低)

```
FREEZE (1) > FLY_TO/PERCH (2) > SPEAKING (3) > THINKING_ANIMATION (4) > DANCING (5) > IDLE (9)
```

### 3.3 Unity 侧冲突处理逻辑

```
收到新动画指令:
  1. 检查当前身体状态
  2. 查兼容矩阵
  3. 如果兼容 → 直接执行
  4. 如果不兼容:
     a. 新指令优先级 > 当前 → 中断当前，执行新指令
     b. 新指令优先级 ≤ 当前 → 排队等待，当前完成后执行
     c. FROZEN 状态 → 只接受 UNFREEZE
```

---

## 4. 思考状态的特殊处理

### 4.1 Tool 调用时的行为

Gemini 调用 tool 时 = THINKING 状态

| 事件 | 鹦鹉反应 |
|:-----|:---------|
| Tool 调用开始 | Gemini 自然说"让我看看~"/"hmm~" (LLM 自行决定) |
| Tool 执行中 (< 200ms) | 无可见反应 (太快了) |
| Tool 执行中 (> 500ms) | 歪头 `HEAD_TILT` (如果身体状态兼容) |
| Tool 执行完成 | 恢复 `HEAD_FORWARD`，Gemini 继续说话 |

### 4.2 不能同时发生的事

- ❌ 思考(歪头) + 说话 — 歪头是"还没想好"，说话是"想好了"
- ❌ 思考(歪头) + 跳舞 — 不合逻辑
- ✅ 思考(歪头) + 站在手上 — 可以在手上思考
- ✅ 思考(继续飞行) + 不歪头 — 飞行中可以思考但不表现出来

### 4.3 GOSLO 自身行为工具注册表

| Tool | 调度层 | 意识层 | 是否阻塞本轮对话 | 结果闭环 | 失败反馈 |
|:-----|:------|:------|:-----------------|:---------|:---------|
| `fly_to` | Intent / 自身身体行为 | 层②；失败升层③ | 是 | await Unity `flyTo` RPC | 同步 tool 结果 + `tick/last_rpc_ack` |
| `animate` | Intent / 自身身体行为 | 层②；失败升层③ | 是 | await Unity `animate` RPC | 同步 tool 结果 + `tick/last_rpc_ack` |
| `set_video_tier` | Intent / 自身感知配置行为 | 层②；失败升层③ | **是** | await Unity `setVideoTier` applied/rejected | 同步 tool 结果 + `tick/last_rpc_ack` |
| `identify_object` | Intent / 按需感知行为 | 层②；不确定或多次失败升层③ | **是** | 抓帧/比对/搜索后返回 | 同步 tool 结果；若委派 Nanobot 必须明示 Task |
| `dispatch_task` | Task / 异步委派 | 层①记录；结果到达再层③通报 | 否 | Scheduler/Nanobot 后续回流 | 立即返回 task id，不能说已完成 |

`set_video_tier` 的特殊规则：

- 它切换的是同一条 `ar-camera` 主视频轨的质量 Tier，不是另开一条视频流。
- 用户或 Gemini 主动调用时，它是 GOSLO 的自身行为，进入 THINKING 并等待 Unity 返回真实 `applied / rejected / timeout`。
- 后台 `PerceptionSupervisor` 因视觉降级或 A10 状态自动调节时，可作为层②自主 Intent 静默处理；失败通过 `last_rpc_ack` 升层③。
- Blackboard 的 `session/video_tier` 不应早于 Unity applied 被写成“已生效”，否则 GOSLO 世界线会和手机 HUD 分叉。

`identify_object` 的特殊规则：

- 它是 GOSLO 的按需感知行为，默认阻塞本轮对话；GOSLO 必须拿到图像/搜索结果后再说“这是 XX”。
- 若内部调用 Nanobot 且不等待结果，则这条路径已经降格为 `dispatch_task`，话术必须是“我派出去查了，稍后告诉你”。
- `audit_identify_object_no_screenshot_20260420.md` 是该工具的升级设计来源；实现时必须保持“同步/异步体感一致”。

---

## 5. 手部交互状态规则

### 5.1 PerchOnHand 状态转换

```
IDLE → (open_palm) → FLYING_TO_HAND → (arrived) → PERCHED_ON_HAND
                                                        ↓
                                            (hand lost / fist) → FLYING(返回) → IDLE
```

### 5.2 手上状态的特殊规则

| 情况 | 行为 |
|:-----|:-----|
| 站在手上 + 用户说话 | 听，可以点头 |
| 站在手上 + Gemini 说话 | 说话，可以配合头部动画 |
| 站在手上 + 用户走动 | 跟着手移动 (纯本地渲染) |
| 站在手上 + 用户收手 | 飞回默认位置 |
| 站在手上 + fly_to 指令 | 先离开手 → 飞向目标 |
| 站在手上 + 跳舞指令 | 在手上跳舞 (如果动画支持，否则先离开手) |

---

## 6. 动画清单与状态映射

### 6.1 当前动画 (P2.5)

| 动画名 | 身体状态 | 头部层 | 备注 |
|:-------|:---------|:-------|:-----|
| `idle` | IDLE | HEAD_FORWARD | 默认 |
| `fly` | FLYING | HEAD_FORWARD/LOOK_AT | 飞行中可看目标 |
| `perch` | PERCHING → IDLE | HEAD_FORWARD | 着陆过渡 |
| `dance` | DANCING | 独立头部动画 | 不接受头部覆盖 |
| `head_bob` | IDLE | HEAD_NOD | 点头 |
| `wing_flap` | IDLE | 不影响 | 拍翅膀 |
| `sleep` | IDLE (特殊) | HEAD_FORWARD | 不接受头部指令 |
| `sit` | IDLE | HEAD_FORWARD | 坐姿 |

### 6.2 需要新增的动画 (用户制作)

| 动画名 | 用途 | 优先级 |
|:-------|:-----|:-------|
| `thinking` | Tool 调用时歪头 | P2.5 高 |
| `fly_fast` | 快速飞行 (紧急) | P3 |
| `land` | 着陆过渡 | P3 |
| `look_around` | 空闲时四处看 | P3 |
| `nuzzle` | 亲昵蹭蹭 | P3 |
| `scared` | 受惊 (突然事件) | P4 |

---

## 7. 后端→前端 指令协议扩展

### 7.1 指令类型

```json
// 身体指令 (互斥通道)
{"type": "body_cmd", "cmd": "fly_to", "target": [x,y,z], "speed": "normal"}
{"type": "body_cmd", "cmd": "perch_on", "anchor": "hand_right"}
{"type": "body_cmd", "cmd": "freeze"}
{"type": "body_cmd", "cmd": "idle"}

// 头部指令 (独立通道，可与身体并行)
{"type": "head_cmd", "cmd": "look_at", "target": [x,y,z]}
{"type": "head_cmd", "cmd": "tilt", "angle": 15}
{"type": "head_cmd", "cmd": "forward"}

// 动画指令 (经过状态机过滤)
{"type": "anim_cmd", "animation": "dance", "priority": 5}
{"type": "anim_cmd", "animation": "thinking", "priority": 4}
```

### 7.2 前端响应

```json
// 指令确认
{"type": "anim_ack", "animation": "dance", "status": "playing"}
{"type": "anim_ack", "animation": "dance", "status": "queued", "reason": "body_busy"}
{"type": "anim_ack", "animation": "thinking", "status": "rejected", "reason": "frozen"}

// 状态上报
{"type": "state_report", "body": "FLYING", "head": "LOOK_AT", "cognitive": "SPEAKING"}
```

---

## 8. 设计原则

1. **身体和大脑分离**: 身体状态(Unity)和认知状态(Python)独立运行，通过 DataChannel 协调
2. **优先级不等于覆盖**: 高优先级可以打断低优先级，但低优先级的"意图"保留在队列中
3. **并行是常态**: 大多数情况下鹦鹉可以同时做多件事 (飞+说+看)
4. **冻结是绝对的**: FREEZE 覆盖一切，只有 UNFREEZE 能解除
5. **自然过渡**: 状态切换不能"跳帧"，必须有过渡动画 (如飞行→着陆→站立)
6. **头部独立**: 头部动画层独立于身体，可以在飞行中注视物体
7. **前端可预测**: 手势检测到后立刻播放预测动画，不等后端确认

---

*本文件由用户和 AI 共同维护。用户负责动画设计和视觉规则，AI 负责代码实现和状态机逻辑。*
