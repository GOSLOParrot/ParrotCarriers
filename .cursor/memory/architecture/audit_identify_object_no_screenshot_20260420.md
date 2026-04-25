---
status: ratified
status_note: "审计结论基于 2026-04-20 code review, 问题 (缺截图 + 异步破坏同步体感) 已被真实代码验证。修复方案 (三段 L0/L1/L2) 是设计 ratified, 实现在 Sprint 4 (S4.A-B) 完成后整体再做一次代码对齐。"
last_reviewed: 2026-04-22
---

# 审计报告: `identify_object` 按需发现路径 — 缺视觉 + 体感闭环断裂

> 日期: 2026-04-20
> 审计人: Agent (Composer)
> 触发: 用户确认 P2.5-DISCOVER 首测前 code review
> 状态: **设计与实现不一致**(双重偏离: 缺截图识图 + tool 火即忘破坏同步体感), 需随视频流采样设计一并升级
> 核心原则: **tool 的同步/异步行为, 必须和 GOSLO 说出口的话一致** (见 §1.2)
> 回引: 视频采样升级专项 / `active_context.md` 下一步 §5 按需发现首测 / `milestone_p2.md` D-P2.5-DISCOVER

---

## 0. TL;DR

当前 `identify_object` 偏离设计**两层**:

1. **缺视觉**: 三档 tool 全用纯文本描述, 没有截图 / 没有参考图 / 没有图比对
2. **体感闭环断裂**: `deep_search` 火即忘派 Nanobot + tool 立刻返回一句承诺话术, 结果走另一条异步通道回插, 本轮对话拿不到结果 → GOSLO "拿到结果才继续说话" 的同步体感闭环**断了**

一句话: 正确的路径是 "GOSLO 抓帧 → 调 tool → 等到结果(不管 tool 内部用 LLM / 本地程序 / Nanobot) → 拿到结果再说话"。tool 是火即忘还是同步等, 决定了 GOSLO 该说什么话, 二者必须一致。

**2026-04-26 联调补充**: 回路已证明能跑，但该 tool 未升级前不应进入默认语音/连接稳定性测试。第三轮日志中 Gemini 围绕白色鼠标连续触发 `save_new`，并伴随 `server cancelled tool calls`；这不是 Graphiti/Nanobot 常驻潜意识，而是未完成的按需识别 tool 被模型当成可用能力调用。当前代码已将 `identify_object` 从默认 `ALL_TOOLS` 移出，仅当 `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1` 时注册，直到本报告的 captureSnapshot + 同步体感闭环落地。

---

## 1. 路径边界 (最重要的一节, 先分清三条互不干扰的通路)

项目里关于"识别物体"其实有**三条完全独立的路径**, 过去报告把它们混成了两条, 这是一切后续设计错位的源头。重新划清:

### 1.1 三条路径对照表

| 路径 | 层 | 触发方 | GOSLO 话术 | 阻塞对话 | 速度预算 | 所在阶段 |
|---|---|---|---|---|---|---|
| **① A10 潜意识自动发现** | L1.5 视觉管线 | 视频流连续帧 | 不直接说话, 通过 Context Injector 注入 | **否** (潜意识) | 管线吞吐 10-30fps | P3+ (A10 到位后) |
| **② GOSLO 按需识别 tool** | Brain Tool | Gemini Live 主动调 | "让我看看...(停顿)...是 XX" 或 "我没见过, 要我查吗?" | **是** (tool 同步等, 等到再说话) | ≤1s → ≤2s → ≤4s 三段递进 | P2.5 (**本报告核心**) |
| **③ Nanobot 长任务** | Scheduler dispatch | GOSLO 调 `dispatch_task` | "我派女仆去 XX 了, 稍后告诉你" + 结果到达时 Context Injector 回插 | **否** (火即忘) | 无预算, 长任务 | 已有, 保持 |

### 1.2 体感决定一切 —— 路径 ② 的真正红线

**校正上一轮口径**: 报告早先说"路径 ② 必须 GOSLO 自己做, 不能派 Nanobot" —— 这个红线画错了, 真正的红线是**体感**:

> **tool 的同步/异步行为, 必须和 GOSLO 说出口的话一致。**

tool 内部调了什么 (LLM / 本地程序 / Nanobot / 远程服务) **完全不是问题**, 那些都是幕后。只要从 GOSLO 的视角看, **"调 tool → 等结果 → 继续说话"** 这个同步闭环成立、且它说出口的话和实际做的事一致, 就是对的。

**举组合看**:

| tool 实现 | tool 返回方式 | GOSLO 话术 | 体感 |
|---|---|---|---|
| 派 Nanobot + 同步等 3-5s 拿结果 | 同步 | "我查了下, 这是 XX" | ✅ 对 (女仆是幕后黑工) |
| 派 Nanobot + 火即忘立刻返回 | 异步 | "我派女仆去查了, 待会儿告诉你" | ✅ 对 (明示转交) |
| 派 Nanobot + 火即忘立刻返回 | 异步 | "这是 XX" | ❌ 错 (GOSLO 在编, 没拿到结果) |
| GOSLO 自己调 web_search | 同步 | "我查了下, 这是 XX" | ✅ 对 |
| tool 只搜内存, 未命中返回 `{status: unknown}` | 同步 | 由 GOSLO 自己决定下一步 (再调网搜 / 问用户 / 派 Nanobot) | ✅ 对 (tool 职责收敛, 决策权交还) |

### 1.3 当前代码错在哪 (真正的诊断)

现在 `_deep_search` 的问题**不是**"用了 Nanobot", 而是**第三种组合**:

- tool 火即忘派 Nanobot (异步) → 立刻返回承诺话术 `"I've sent... I'll let you know when I find out more"` 
- **Nanobot 结果到达时走另一条通道** (`SSOTEnrichmentTrigger` + Context Injector) **插回下一轮对话**
- 本轮对话里 GOSLO 拿不到结果, "拿到结果才继续说话" 的同步闭环**从根上就没成立**
- 话术倒是自洽的 ("我派去了" 不算编), 但**这条路径就失去了路径 ② 的意义** —— 它已经退化成了路径 ③

换句话说: 现在这条 `deep_search` **本质上不是路径 ② 的深度识别**, 是路径 ③ 的"让女仆查"的别名。要么把它**还原成路径 ② 的同步实现** (tool 内部同步拿结果, 返回给 GOSLO), 要么**把它显式降格到路径 ③** (重命名为 `delegate_research`, 从 identify_object 里拆出去)。

### 1.4 路径 ② 内部的三段递进 (核心体感设计)

路径 ② 这条 tool 里, 按速度预算分三段, 全部**同步等待**, 全部让 GOSLO "拿到结果再说话":

```
Gemini Live 听到/看到 "这是什么?"
  │
  ▼
[L0] 快速比对 (内存/工作记忆)         ≤ 1s
  ├ 抓当前帧
  ├ 在 L2-B / 预加载物体列表 里找候选 (小范围)
  ├ 拿各候选对应的参考图, 和当前帧快速比
  └ 命中 → 返回 GOSLO → "啊这不就是你上周买的马克杯嘛~"

  未命中 ▼

[L1] 深度搜索 (Graphiti + 物体图库)    ≤ 2s
  ├ 扩大搜索: Graphiti scene/user/objects 分区 + 本地图库
  ├ 把候选参考图和当前帧做多图比对
  └ 命中 → 返回 GOSLO → "哦这是...(翻记忆)...去年展会买的那个手办对吧"

  还是未命中 ▼

[L2] 确认是新物体                      处理方式可选, 只要体感一致:

  选项 α: tool 只返回 `{status: unknown, snapshot_id: xxx}` —— 决策权交还 GOSLO
    GOSLO 自己决定下一步:
      (a) 再调一个 web_search / reverse_image_search tool (同步, 体感: "我查了下")
      (b) 调 dispatch_task 派 Nanobot (异步, 体感: "我让女仆去查, 稍后告诉你")
      (c) 直接问用户 ("我没见过, 是什么呀?")
      (d) 靠自己的常识直接描述 ("好像是个手办?")

  选项 β: tool 内部自己进到网搜 (同步等结果, ≤ 4s) —— 决策权在 tool 内
    tool 返回 {status: new, web_info: "...", snapshot_id: xxx}
    GOSLO → "嗯...我查了下, 这可能是 XX 牌的 YY"

  选项 γ: tool 派 Nanobot 同步等 (≤ 10s) —— tool 内黑盒调度
    GOSLO → "我看了看, 是 XX" (体感和 β 一样, 实现不同)
```

**三段都是同步返回**, GOSLO 拿到结果再说话, 这是体感红线。

**L2 具体选哪种 (α / β / γ)**, 在本报告**不强制拍板**, 只定原则 (§1.2 的组合表)。实现阶段再按测试体感决定 —— 比如如果 web_search tool 调得顺畅, 选项 β 最省事; 如果 GOSLO 的人格设定需要显式的"自主判断是否查询", 选项 α 更自然。

---

## 2. 设计意图原文 (四处硬记录, 证明本次纠错不是事后发明)

### 2.1 `.cursor/memory/milestone_p2.md` — D-P2.5-DISCOVER

> | 维度 | Tool 按需发现 (P2.5) | A10 全发现 (P3+) |
> | 对话阻塞 | **有感知停顿 (Gemini 说"让我看看")** | 不阻塞 — 潜意识运行 |
> | 精度 | **高 (Gemini Flash 看截图)** | 中 (YOLO-World + DINOv2) |

这张表同时钉死了两件事: **(a)** Tool 通路**必须**带感知停顿 → 所以它是 GOSLO 的身体行动, 不是派 Nanobot; **(b)** Tool 通路**必须**看截图 → 所以缺图就是设计缺失。

### 2.2 `docs/InfoCollections/Opus/19_anomaly_ghost_expectation_vision.md` — ADR-028

> **ADR-028: 细粒度识别 = 给 Gemini 看裁切图, 不引入新模型**
> - 决策: **裁切物体区域图发给 Gemini 做详细描述**, 不引入 OCR/商品识别等专用模型
> - 按需触发: 用户问/鹦鹉好奇/新物体出现时才做, 95%时间不需要
> - 结果存入 ObjectNode.fine_description, 属于 gemini_described 权威级别

印证 L1/L2 阶段"给 Gemini 看图"的正式决策。权威链 ADR-026: `user > gemini > reid > yolo_voted > yolo_single` —— gemini 的权威建立在"**看图**", 缺图则权威链废掉。

### 2.3 `docs/InfoCollections/Opus/11_L1_vision_design.md` — On-Demand Tier

> | **On-Demand** | Gemini Tool Call `focus_on(uuid)` | **立即对指定目标执行 DINOv2 特征提取**(无论当前 Tier) | 按需 |

L1 视觉层明文预留 On-Demand 通路, 对应本报告路径 ② 的 L1 阶段。

### 2.4 `docs/InfoCollections/Opus/17_dsg_node_and_trigger_design.md` — `preload_object_semantics` (L579)

预加载逻辑已经预设"物体记忆里带图片参考", L2-B 初始化就应该有 `reference_image_path` 字段。

---

## 3. 当前实现的真实事实

### 3.1 `src/parrot/brain/tools/identify_object.py` 签名就不对

```python
@function_tool()
async def identify_object(
    context: RunContext,
    description: str,
    category: str = "",
    action: str = "match",
) -> str:
```

只有两个字符串入参, 没有 `snapshot_uuid` / 任何视觉输入。Gemini 能调的唯一方式是口述, 走了**路径 ② 但没做路径 ② 该做的事**。

### 3.2 `_match_known()` (L123-140) 没截图

```python
query = f"object: {description}"
if category:
    query += f" category: {category}"
results = await g.search(
    query=query,
    group_ids=[PARTITIONS.SCENE, PARTITIONS.USER],
    num_results=5,
)
```

Graphiti search = 文本 embedding + BM25, **不看图**。无论 L0 还是 L1 都退化成纯文本匹配。

### 3.3 `_save_new_object()` (L187-229) 不存图

```python
text_parts = [f"New object discovered (uuid={obj_uuid}): {description}"]
text_parts.append(f"  discovered_at: {time.strftime('%Y-%m-%d %H:%M')}")
text_parts.append("  status: newly_discovered, pending_enrichment")
```

没 `snapshot_path` / `reference_image_uri`, 未来 L0/L1 再遇到同一个物体也没有"参考图可比"。

### 3.4 `_deep_search()` (L236-283) 体感闭环断裂

```python
task_id = await do_dispatch_task(
    task_type="research",
    params=params,
    priority="normal",
)
return (f"I've sent '{description}' to my research assistant (task: {task_id}). "
        "I'll let you know when I find out more! ...")
```

这里不是"用了 Nanobot"不对 (用 Nanobot 也可以, 见 §1.2 组合表), 而是**火即忘 + 同步 tool 返回**的组合让体感闭环断了:

- tool **立刻返回承诺话术** → GOSLO 这轮说 "I've sent to my assistant..."
- Nanobot 真正结果到达时走 `SSOTEnrichmentTrigger` → Context Injector, 插进**下一轮**对话
- **本轮对话里 GOSLO 根本拿不到结果** → 路径 ② 的 "等结果再说话" 同步闭环从根上没成立
- 这个 `deep_search` 现在**本质上不是**路径 ② 的深度识别, 是路径 ③ 的"扔女仆"的别名

**修正方向** (按 §1.2 选一个):
- **路径 A**: 改成同步等 Nanobot 结果 (tool 内 await Redis 结果, 超时 ≤ 5s), GOSLO 拿到结果再说 "我查了下, 这是 XX" —— 体感正确
- **路径 B**: 把 `_deep_search` 从 `identify_object` 里拆出去, 重命名为 `delegate_research`, 明示是路径 ③ 的长任务派发; `identify_object` 的 L2 段用别的实现 (GOSLO 自调 web_search / tool 自包办等, 见 §1.4)

### 3.5 视频流只"直播", 没"留存"

- Unity `ARVideoPublisher.cs`: AR/Webcam → `RenderTexture` → LiveKit `LocalVideoTrack`, 发走即完, 本地不落盘。
- Python 侧 `src/parrot/bus/processor_hook.py` 的 `BaseProcessor.on_video_frame` 还是占位符, 无订阅、无抓帧 API。
- Gemini Live 是**唯一**看到视频的实体, 它的视觉记忆是云端黑盒, 我们无法取、无法留、无法复用。

### 3.6 数据结构没预留图片字段

- `src/parrot/dsg/l2b_types.py::SemanticNode` grep `image|jpeg|photo|thumbnail|snapshot` → 0 匹配。
- `src/parrot/memory/conversation_writer.py` 纯文本写 Graphiti。

---

## 4. 为什么当前实现"看起来能跑"却"不符合设计"

能跑是因为 Gemini Live 拿到视频流 → 它自己看 → 把描述当 tool arg 回传。整条链路**像是**在工作:

```
Gemini 云端看视频 ──→ 吐描述字符串 ──→ identify_object ──→ 文本搜 Graphiti ──→ 不行就扔 Nanobot
```

但违反了设计的**四个关键假设**:

1. **视觉权威链死字段** (ADR-026): gemini 的识别权威建立在"看图", 现在只有"自述描述", 未来复核/回放"它当时看到的到底是什么"做不到, `class_votes` / 权威链回溯机制全废。
2. **跨会话一致性崩溃**: 今天 Gemini 说 "blue ceramic mug uuid=abc", 明天同一个杯子它说 "陶瓷杯". 纯文本 embedding 难以判定同一实例, 必须靠"参考图 + 视觉比对"兜底。
3. **L2 路径性质错位** (本次新增发现): `deep_search` 派 Nanobot 破坏了 GOSLO 的自主性和体感, 它应该是 GOSLO 的身体行动 (自己上网查), 不是派人。
4. **无图 Nanobot 也白搭**: 即使**真需要**派 Nanobot (比如路径 ③ 的重研究), 现在传给它的也只有文本, 它即使挂了 Gemini Vision / Google Lens MCP 也用不上。

---

## 5. 升级口子 (按三段递进重组)

分四组, 前两组是基建, 后三组对应 L0 / L1 / L2 三段。**不做路径 ① (A10) 也不做路径 ③ 改造**, 那俩不在本报告范围。

### 5.1 基建组 — 视觉 IO 层 (所有路径都要用)

| # | 口子 | 位置 | 依赖 |
|---|---|---|---|
| B1 | **Unity RPC `captureSnapshot`**: `AsyncGPUReadback` 读 `_rt` → EncodeToJPG → base64 回传 (≤120KB) | `ARVideoPublisher.cs` 或新 `SnapshotService.cs` + Brain `_rpc_bridge.py` | 无 |
| B2 | **Brain `capture_current_frame() -> bytes`**: 封装 RPC + 超时 (<2s) + 错误回退 | 新增 `src/parrot/brain/vision/snapshot.py` | B1 |
| B3 | **落盘约定** `data/snapshots/objects/{uuid}/reference.jpg` + `sightings/{ts}.jpg` | `.gitignore` + Castle docker volume | B2 |
| B4 | **`SemanticNode` 扩展** `reference_image_path: str = ""` + `last_sighting_path: str = ""` | `src/parrot/dsg/l2b_types.py` | 无 |

### 5.2 L0 组 — 快速比对内存/工作记忆 (目标 ≤ 1s)

| # | 口子 | 位置 |
|---|---|---|
| L0-1 | 拆 `_match_known` → `_match_quick`: 只搜 L2-B + 最近物体列表 (不触碰 Graphiti 全库), 候选数 ≤ 3 | `identify_object.py` |
| L0-2 | 对 L0-1 的候选, 调 **轻量 VLM** 做"当前帧 vs 参考图"一次性多图比对, 给 `{match_uuid, confidence}` | 新 `src/parrot/brain/vision/visual_match.py` |
| L0-3 | 若文本 embedding 相似度 < 阈值 → 跳过 L0 图比对, 直接 L1 (省配额) | `identify_object.py` |

### 5.3 L1 组 — 深度搜索 Graphiti + 图库 (目标 ≤ 2s)

| # | 口子 | 位置 |
|---|---|---|
| L1-1 | 新 tool arg `action="match_deep"` 或自动从 L0 未命中 fallback | `identify_object.py` |
| L1-2 | 扩大 Graphiti 搜索范围 (scene + user + objects 分区, num_results ≤ 10) | `identify_object.py` |
| L1-3 | 候选参考图批量预热到内存, 一次 VLM 调用多图比对 (Gemini Flash 支持单次多图) | `visual_match.py` |
| L1-4 | 命中: 按权威链更新 L2-B `class_label`, `evidence_score` 显著跃升 | `l2b_graph.py` / `identify_object.py` |

### 5.4 L2 组 — 新物体处理 (目标 ≤ 4s 同步, 实现方式三选一)

按 §1.4 的选项 α/β/γ, L2 段具体落地**留到实现时再拍**, 但需要先把三种方案都能接上的前置件准备好:

#### 通用前置 (三方案共用)

| # | 口子 | 位置 |
|---|---|---|
| L2-1 | **Gemini Flash 视觉描述工具** (给张图 → 细节描述: 品牌/型号/状态) | `src/parrot/brain/vision/visual_match.py::describe_image` |
| L2-2 | `identify_object(action="confirm_new")`: 抓帧落盘 + 自描述 + 写 Graphiti + L2-B (无论 L2 走哪个选项, 新物体入库这步必做) | `identify_object.py` |

#### 选项 α (tool 返回 unknown, 决策交还 GOSLO) 所需口子

| # | 口子 | 位置 |
|---|---|---|
| L2-α1 | 新 Brain tool `web_search` (Google Search API / SerpAPI / Gemini grounding) | `src/parrot/brain/tools/web_search.py` |
| L2-α2 | 新 Brain tool `reverse_image_search` (可选, 用 snapshot_id 反查) | `src/parrot/brain/tools/web_search.py` |
| L2-α3 | Soul prompt 加指引: "识别未知物体时, tool 会返回 unknown, 你可以自己决定调 web_search / reverse_image_search / 派 dispatch_task / 直接问用户 / 直接描述" | `src/parrot/brain/soul.py` |

#### 选项 β (tool 内自包办网搜) 所需口子

| # | 口子 | 位置 |
|---|---|---|
| L2-β1 | `identify_object` 内部 L2 段直接调 `web_search` API + visual describe, 同步等结果 (≤ 4s), 拼 JSON 返回 | `identify_object.py` |
| L2-β2 | 超时保护: 任一 API 超 3s 则降级为"未知, snapshot 已存" | `identify_object.py` |

#### 选项 γ (tool 派 Nanobot 同步等) 所需口子

| # | 口子 | 位置 |
|---|---|---|
| L2-γ1 | 修 `_deep_search`: 改火即忘 → 同步 await Redis Pub/Sub 结果, 超时 ≤ 10s | `identify_object.py` + `dispatch_task.py` |
| L2-γ2 | Scheduler 侧保证 `identify_result` 通道的结果精确回到 identify_object 的调用方 (目前用 `SSOTEnrichmentTrigger` 回插, 需要给 tool 同步调用加一条直通路径) | `parrot/scheduler/*` |

#### 决策原则

实现阶段按以下顺序试:
1. **优先 α**: GOSLO 主导感最强, 符合"它自己有判断"的人格设定; 代价是 prompt 要写好
2. **退 β**: α 下 Gemini 判断不稳(总是跳过或总是查)时, 用 tool 自包办保证每次都做网搜
3. **备 γ**: 只在需要 Nanobot 能力 (如 MCP 的反向图搜 / 本地知识检索) 时才选, 且**必须同步 await**

**任何情况下**: 不允许回到"火即忘 + tool 立刻返回承诺话术"的组合 (§3.4 的当前错误)。如果真要火即忘, 那就**从 `identify_object` 拆出去变成显式的 `delegate_research`**, 让 GOSLO 自己决定什么时候派。

### 5.5 被回避的陷阱

- **不要**走 LiveKit `DataChannel` 传图, 120KB 是 DataChannel 安全上限边缘。用 `PerformRpc` 的 response payload。
- **不要**在 Python 侧自己订阅 VideoTrack 再抓帧, Unity 侧 RT 已 ARGB32, 用 `AsyncGPUReadback` + `EncodeToJPG` 简洁靠谱。
- **不要**改 Graphiti schema 加二进制字段, 图走独立存储 + URI 引用。
- **不要**让 `identify_object` 成为"火即忘 + 承诺话术"的 tool (§3.4 当前错误) —— 要么同步等, 要么拆成独立的 `delegate_research` 让 GOSLO 显式调, 不能让它在 tool 内偷偷把决策权转移给 Nanobot。

---

## 6. 升级后预期调用链 (三个 use case, 作为验收基准)

### Use Case A — L0 命中 (家里常见物品)

```
用户: "桌上这是什么?"
Gemini Live → identify_object(action="match", description="blue ceramic mug")
Brain (全程 GOSLO 自己, 约 800ms):
  1. capture_current_frame()                          [~200ms]
  2. L2-B 找候选 (≤3) + 取各自参考图                    [~100ms]
  3. visual_match.compare(current, candidates)          [~500ms]
     → {match_uuid: abc123, confidence: 0.82}
  4. L2-B evidence_score 0.5 → 0.75, 存 sighting
Gemini Live: "是你上周买的那个马克杯~"
```

### Use Case B — L0 未命中, L1 命中 (不常见但记过)

```
用户: "这个呢?"
Gemini Live → identify_object(action="match", description="小手办")
Brain (约 1.8s):
  1. 先跑 L0, 未命中
  2. 回 Gemini "让我仔细看看..." (可选桥接话)
  3. capture + 扩大 Graphiti 搜索 (num_results=10)    [~400ms]
  4. 批量 VLM 多图比对                                 [~1200ms]
     → 命中 uuid=xyz789 "去年展会的初音手办"
  5. 更新 L2-B, 存 sighting
Gemini Live: "哦, 是去年展会那个初音对吧~"
```

### Use Case C — L0/L1 未命中, L2 处理 (三种选项都给一遍)

#### C.α — tool 返 unknown, GOSLO 自主决策

```
用户: "这是啥?"
Gemini Live → identify_object(action="match", ...)
Brain: L0/L1 全部未命中, 返回 {status: "unknown", snapshot_id: xxx}
Gemini Live (自主判断, 可能说一句桥接话 "唔...没见过"):
  → 直接调 web_search(query="白色发光方形装置 handheld")    [~1500ms]
  → (可选) describe_image(snapshot_id=xxx)                 [~800ms]
Gemini Live: "嗯...我查了下, 这可能是 Nintendo Alarmo 闹钟, 今年新款哦~"
Brain 后台: identify_object(action="confirm_new") → 写 Graphiti + L2-B + 存 reference.jpg
```

**体感**: GOSLO 自己想、自己查、自己说, 主导感最强。总时长 3-4s。

#### C.β — tool 内自包办

```
用户: "这是啥?"
Gemini Live → identify_object(action="match", ...)
Brain 内部 (约 3-4s):
  L0 未命中 → L1 未命中 → 进入 L2
  → web_search + describe_image 并行调用
  → 汇总返回 {status: "new_investigated", info: "Nintendo Alarmo 闹钟..."}
  → confirm_new 自动完成
Gemini Live: "哦, 我看了看查了下, 这是 Nintendo Alarmo 闹钟~"
```

**体感**: GOSLO "思考停顿更长" 一点, 一句话交付答案。调用逻辑内聚在 tool 内。

#### C.γ — tool 派 Nanobot 同步等

```
用户: "这是啥?"
Gemini Live → identify_object(action="match", ...)
Brain 内部 (≤10s):
  L0/L1 未命中 → _deep_search 修正版
  → dispatch_task + 同步 await Redis 结果
  → Nanobot 用 Google Lens MCP / Search MCP 做反向图搜
  → 结果回来 → confirm_new
Gemini Live: "我看了看, 这是 Nintendo Alarmo 闹钟"
```

**体感**: 从 GOSLO 视角看和 β 一样 ("调了 tool 等到结果再说话"), 用户感知不到 Nanobot 存在。实现上女仆是幕后黑工。

---

**三个选项对用户的体感是相同的**: 都是 "GOSLO 看了想了说了"。差别只在实现成本、延迟、和 Soul prompt 要不要指导自主判断。按 §5.4 决策原则选。

---

## 7. 回流动作

1. 本报告存档路径: `.cursor/memory/architecture/audit_identify_object_no_screenshot_20260420.md`
2. `active_context.md` "下一步 §5 按需发现链路首测" 条目加注 `⚠ 设计未落地 (缺截图+错派Nanobot), 见 audit_identify_object_no_screenshot_20260420.md`
3. `milestone_p2.md` D-P2.5-DISCOVER 决策表下加注 `实现延后: 当前 identify_object 未含截图+错派 Nanobot, 待视频采样升级统一修正, 见 audit_identify_object_no_screenshot_20260420.md`
4. `.cursor/memory/INDEX.md` 在 architecture 段新增一行指向本报告
5. 视频采样升级专项开工前, 把本报告 §5 的 "B1-B4 + L0-* + L1-* + L2-*" 当成需求清单, **§6 三个 use case 当成验收基准**

---

## 8. 风险与权衡 (给未来自己看)

### 8.1 存储

每天 ~50 次新发现 (reference) + ~200 次复核 (sighting), 每张 80KB → **年化约 7GB**。2C8G + 40GB ECS 有压力。
- 策略: sighting 保留最近 7 天 + 每月抽样 10% 长期归档; reference 永久; 老会话归档可打 tar.zst 压缩归 OSS。

### 8.2 隐私

AR 全帧落盘 = 用户家里环境都在磁盘上。
- 策略: 只在 identify_object 的 L0-L2 **被调用那一瞬**抓帧, 不做常驻录像; `goslo-chat /forget_snapshots [since|uuid]` 命令一键清理; 报告里显式记录 "每次抓帧会被保存" 给用户知情。

### 8.3 VLM 调用配额

L0 如果每次都图比对会烧配额。
- 策略: 文本 embedding 相似度先过滤 (阈值 ≥0.7 才触发图比对); L0 用 Flash-Lite, L1/L2 才用 Flash; 单次调用尽量多图 (一次 API 带 N 张候选, 不要 N 次串行)。

### 8.4 Unity 主线程

`Texture2D.ReadPixels` 同步读 RT 会卡 Unity 主线程 50-200ms → 必须用 `AsyncGPUReadback.Request()`, 回调里 `EncodeToJPG`, 主线程只多花 5ms。

### 8.5 L2 的 GOSLO 自主判断 (选项 α) 会不会变成"遇到啥都要上网"

可能。
- 策略: Soul prompt 里写明 "如果物体看起来是常见家用品 (杯子/笔/纸/书等), 即使不认识也先描述一下, 不强制上网"; 给 `web_search` tool 限频 (每 5min ≤ 3 次, 超限则只能描述)。
- 若选项 α 下 Gemini 总是跳过或总是查, 按 §5.4 决策原则切到 β 或 γ, 由 tool 内部强制每次都做调查。

---

## 附: 相关文件索引

**实现侧**:
- `src/parrot/brain/tools/identify_object.py` — 三档 tool (本次审计对象)
- `src/parrot/brain/tools/dispatch_task.py` — Nanobot 派发入口 (路径 ③, 不该被 L2 调)
- `unity/ParrotDev/Assets/Scripts/LiveKit/ARVideoPublisher.cs` — 视频发布
- `src/parrot/bus/processor_hook.py` — L1 视觉处理器占位 (路径 ①)
- `src/parrot/dsg/l2b_types.py` — `SemanticNode` (缺图片字段)
- `src/parrot/brain/soul.py` — Gemini Live 人格 prompt

**设计侧**:
- `.cursor/memory/milestone_p2.md` §九 D-P2.5-DISCOVER (路径 ② 定性)
- `docs/InfoCollections/Opus/19_anomaly_ghost_expectation_vision.md` ADR-028 (Gemini 看图决策) / ADR-026 (权威链)
- `docs/InfoCollections/Opus/11_L1_vision_design.md` §2.3 On-Demand Tier (路径 ① 预留给 ② 的接口)
- `docs/InfoCollections/Opus/17_dsg_node_and_trigger_design.md` L579 `preload_object_semantics` (带图预加载契约)
