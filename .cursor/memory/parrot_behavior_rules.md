---
status: ratified
category: reference
status_note: "GOSLO 行为状态机 + 兼容矩阵 + 冲突规则, 当前代码已遵循。Sprint 1 可能扩展 body/head/cognitive 子状态, 扩展时追加而不翻案。"
last_reviewed: 2026-04-22
---

# GOSLO 鹦鹉行为状态规则

> 维护者: 用户 + AI
> 创建: 2026-04-13
> 用途: 定义鹦鹉的行为状态机、动作兼容矩阵、冲突解决规则
> 对应代码: Unity 前端状态机 + Python 后端调度器
> 参考: Opus 14 (调度器+状态机), Opus 17 (DSG触发器), 包容架构

---

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
