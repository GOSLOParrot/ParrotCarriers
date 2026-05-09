---
status: superseded
category: interface-design-historical
superseded_by: "INDEX.md（2026-05-09 路由整理：v0 + 本补丁的"穷举接口签名"路线已被核心/业务二分骨架取代；7 项新发现仍是有效背景，业务 chat 内可引用）"
status_note: "v0 补丁包 — v0 之外 7 项新发现（Obsidian 3 子类 / 4 级视觉自我感知 / 2 Scene baseline / 三合一意识 / 三阶段归档 / 海盗换肤 / 多设备）+ 完整性确认 + 文档索引段落。原路线已 superseded（见 INDEX.md §0 失败教训）。"
last_reviewed: 2026-05-07
superseded_at: 2026-05-09
ai_priority: low
ai_audience: "业务 chat 内引用 7 项新发现作为设计输入"
parent_doc: "INDEX.md"
related:
  - "INDEX.md (本目录核心/业务二分骨架，2026-05-09 新建)"
  - "interface_design_and_how_todo_v0_20260507.md (parent，同样 superseded)"
  - "concept_dictionary_20260507.md"
  - "legacy_issues_split_20260507.md"
  - "menu_design_complete_20260507.md"
---

---
status: draft / interface-design-supplement
category: interface-design
status_note: "v0 (interface_design_and_how_todo_v0_20260507.md) 的补充审查 + 完整性确认 + 文档索引段落。最后一轮覆盖了 v0 没抓到的：Obsidian 3 子类语义 / 4 级视觉自我感知 / 三合一意识统一视图 / 4-scope Blackboard / 工作记忆延迟归档三阶段 / 2 Scene baseline / 海盗主题换肤 / DSG 工作区 vs AR 工作区交集。本文不重写 v0；只做新发现 + 完整性确认 + 索引补丁。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sonnet 4.6 + Opus 4.7 ×2 调研 + 用户最终整合"
parent_doc: "interface_design_and_how_todo_v0_20260507.md"
related:
  - "../app_completion_master_audit_20260507.md"
  - "../app_flow_requirements_interface_chat_launch_prompt_20260507.md"
  - "../backend_interface_refinement_chat_launch_prompt_20260507.md"
  - "concept_dictionary_20260507.md"
  - "legacy_issues_split_20260507.md"
  - "menu_design_complete_20260507.md"
sources_re_audited:
  - "ar_feature_vision.md (§3.5 三合一意识 / §3.6 4-scope Blackboard / §3.4 2 Scene baseline / §3.3 4 级视觉自我感知)"
  - "dsg/dsg_decisions_master.md (§3.2 Obsidian 3 子类 / §5 工作记忆延迟归档)"
  - "dsg/dsg_current_state_distilled.md (§11 防爆炸 3 层门控 / §12 三阶段归档)"
  - "dsg/workspace_index.md (DSG vs AR 工作区交集)"
  - "ar_workspace_index.md (AR 工作区入口)"
  - "lore/ideas.md (海盗主题 / 猫爪 / 望远镜 / 羊皮纸 / Paper Please 灵感 / P3.5 多设备 / iOS ARWorldMap)"
  - "dsg/dsg_protocol_scene_snapshot_v1_20260506.md (SceneType vs LocationTag vs IntentEvent 三概念区分)"
---

# 接口/能力提炼 — 补充审查 + 完整性确认 + 索引段落

> **本文用途**：v0（[`interface_design_and_how_todo_v0_20260507.md`](interface_design_and_how_todo_v0_20260507.md)）写完后再读 7 份关键文件后产出的补丁包。**不重写 v0**；用 §1-§5 增量、§6 完整性确认、§7 文档索引段落补全。
>
> **规则**：v0 + 本文一起喂 Sonnet 4.6；Opus 4.7 ×2 在两个 Sub-Chat 内调研后再做最终整合。

---

## §0 v0 之外读到的 7 份关键文件 + 各自一句话发现

| # | 文件 | 一句话新发现（v0 没覆盖）|
|:--|:--|:--|
| 1 | `ar_feature_vision.md §3.5 / §3.6` | **三合一统一视图** — `Reflex/Intent/Task 三层调度` ≡ `三层意识分发(Subconscious/Autonomous/Report)` ≡ `CTHA Temporal Hierarchy + GR00T System1/System2`，是同一架构的三个侧面；§3.6 4-scope Blackboard 是真源 |
| 2 | `ar_feature_vision.md §3.3` | **4 级视觉自我感知**（active / degraded / paused / blocked）+ Soul 8 条强制话术；不是 LLM 自由发挥 |
| 3 | `ar_feature_vision.md §3.4` | **P2 上线 = 2 Scene baseline**：DESKTOP_WEBCAM + AR_HANDHELD（不是只 DESKTOP）；当前 `SceneType` enum 仅 DESKTOP 是 deferred-to-design |
| 4 | `dsg/dsg_decisions_master.md §3.2` | **Obsidian 3 子类**（重大）：Ref-加强 / 设定-日常 / 设定-Roleplay 语义不同；roleplay 是临时 Persona+Mode+Scene 子集；不是 3 个 Bucket 而是 3 类 Observation |
| 5 | `dsg/dsg_current_state_distilled.md §11 / §12` | **3 层防爆炸门控**（A10 / L1.5 / L2-B 各一道）+ **三阶段工作记忆归档**（hot 内存 → cold 硬盘 → nanobot 闲时归档）|
| 6 | `dsg/workspace_index.md §5 / ar_workspace_index.md §8` | **DSG vs AR 工作区交集 = EcpEvent / PhotoNode / RefBinding**；交集以 Phase 4 §8 为准；新增内容先登记到对应工作区再决定是否进 INDEX |
| 7 | `lore/ideas.md`（user 手写）| **海盗主题换肤** = 眼罩 skin / 望远镜替放大镜 / 镜片滤镜 / 半边黑色遮挡 / 大副 + 水手；纸条递交可猫爪伸出；UI 风格学 Paper Please / Last Report；P3.5 多摄像头/麦克风指定（DroidCam / OBS / 副摄）；P3+ iOS ARWorldMap |

---

## §1 v0 没抓到的关键能力（增补 8 项 + 1 主题换肤）

> 每条 = ① 来源 ② 影响哪些场景 / 子任务 ③ 接口签名草稿 ④ How TODO ⑤ TODO 注释草稿。

### §1.1 ⚠ Obsidian 3 子类的 Ingest 路径（v0 §5.2 GOSLO 主动好奇 + 场景 6 4 类块都受影响）

**来源**：`dsg/dsg_decisions_master.md §3.2`（ratified）+ user 原话"上轮 source_x_lifecycle_status §2.1 把 USER_TAG_OBSIDIAN 当一类处理；现在拆 3 子类"。

**冲突点**：v0 §2.2 把 OBSIDIAN_REFERENCE_REINFORCE / OBSIDIAN_SETTING_DAILY / OBSIDIAN_SETTING_ROLEPLAY 列作 3 个 BucketKind；语义层面这是 3 类 Observation 的下游分桶，但**当前 ObservationSource enum 只有 USER_TAG_OBSIDIAN 一项**。

| Obsidian 子类 | 用途 | UUID 绑定 | 永久权威 | 进 L1.5 池 | 进 L2-B 节点 | Bucket | Graphiti 分区 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| **Obsidian-Ref-加强** | 加强既有节点的 Ref（不是节点本身）| 是 | — | ❌ 不进 | 作为其他节点 `meta.obsidian_uuid` 引用 | — | 生活区 |
| **Obsidian-设定-日常** | 介绍家具 / 公用场景 / 可作其他节点引用 | 是（节点）| 是 | ✅ 进 | ✅ 是节点本身（OBJECT/SURFACE/PERSON）| OBSIDIAN_SETTING_DAILY | 生活区 |
| **Obsidian-设定-Roleplay** | Roleplay 模式自定义；中世纪 / XXX 物品 | 是 | 是 | ✅ 进（roleplay 模式时） | ✅ 是节点本身 | OBSIDIAN_SETTING_ROLEPLAY | **roleplay 自定义区** |

**接口签名草稿**：
```python
# src/parrot/dsg/ingest/user_tag_filter.py (existing; 改造)
class UserTagObsidianFilter(IngestFilter):
    def filter(self, evt: ObsidianSyncEvent) -> Observation | None:
        # 当前: 不分子类 → 走同一 Observation
        # ✅ 升级: 按 obsidian path / front-matter 子类标记区分
        subclass = self._infer_subclass(evt)  # ref / daily / roleplay
        meta = {
            "obsidian_path": evt.path,
            "obsidian_uuid": evt.uuid,
            "double_link_count": evt.link_count,
            "profile": subclass,  # ref / daily / roleplay
        }
        if subclass == "ref":
            return None  # 不建节点；走 SsotEnrichmentTrigger 加 meta 到既有节点
        # daily / roleplay 走正常 Observation → IngestRunner → L1.5 → L2-B
        return Observation(source=ObservationSource.USER_TAG_OBSIDIAN, ..., meta=meta)
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| 子类区分 | obsidian path 前缀 / front-matter `profile:` 字段 | dsg_decisions_master §3.2 |
| 是否新增 ObservationSource | **否** — 走 USER_TAG_OBSIDIAN + meta.profile（不动 enum；ADR-L1.5-001 §4.1 未触发）| 同上 |
| Roleplay 模式开关 | BB key `global/active_mode` 含 "ROLEPLAY" flag → IngestRunner 检查 → roleplay 子类才入池 | ratified（设计原则）|
| 一键删除 roleplay 节点 | RustworkX `remove_nodes_from(roleplay_subgraph)` | dsg_decisions_master §3.2（deferred-to-design）|

**TODO 注释草稿**：
```python
# TODO(NEED-P2.5-OBSIDIAN-3SUB): Obsidian 3 子类 Ingest 路径
#   - 来源: dsg_decisions_master §3.2 (ratified)
#   - 子类: ref-加强 / 设定-日常 / 设定-roleplay
#   - 不动 enum: 用 USER_TAG_OBSIDIAN + meta.profile 区分（ADR-L1.5-001 §4.1 未触发）
#   - Bucket: BucketKind.OBSIDIAN_SETTING_DAILY / OBSIDIAN_SETTING_ROLEPLAY (已存在)
#   - Graphiti: roleplay 走"roleplay 自定义区"分区 (P3 实施 group_id 隔离)
#   - Skill: graphiti/SKILL.md (group_id 分区)
#   - 名词: 概念词典 §3 "Obsidian-Ref vs 设定-日常 vs 设定-Roleplay"
```

---

### §1.2 ⚠ 4 级视觉自我感知 + Soul 8 条强制话术（场景 1 baseline / S10 视频档位 / NEED-P2.5-A 配套）

**来源**：`ar_feature_vision.md §3.3`（V1/V2/V3 待用户确认；当前是 tentative，但风格基线已锁）。

**4 级 + 话术示例**：
| visual_state | 语义 | Gemini 反应 | 允许话术 | 禁止话术 |
|:--|:--|:--|:--|:--|
| `active` | 看得清，在动 | 正常描述 | "你桌上的杯子是蓝色的" | — |
| `degraded` | 看到但糊/暗/抖 | 不做断言；用"好像 / 似乎" | "好像有什么东西，看不太清" | "杯子是蓝色的" |
| `paused` | 主动暂停（App 后台 / 用户请求）| 不提画面，转语音/记忆 | "虽然我现在看不见，但上次你跟我聊过..." | "我看到..." |
| `blocked` | 被挡（手 / 物体） | 主动抱怨 + 不编造 | "我被挡住了！你把手拿开呀~" | 描述任何画面内容 |

**接口签名草稿（Brain Soul）**：
```python
# src/parrot/brain/soul.py (existing; 增 visual_state 段)
def get_instructions(mode: BehaviorMode, visual_state: str) -> str:
    base = CORE_INSTRUCTIONS  # NEED-P2.5-A 后改为加载 personas/<id>.md
    visual_directive = _VISUAL_STATE_DIRECTIVES.get(visual_state, "")
    return f"{base}\n\n{mode_directive}\n\n{visual_directive}"

_VISUAL_STATE_DIRECTIVES = {
    "active": "",   # default
    "degraded": "Visual degraded. Use '好像/似乎' tone. No definitive claims.",
    "paused": "Visual paused. Switch to audio/memory. Do NOT mention current scene.",
    "blocked": "Visual blocked. Complain first, then redirect. Don't fabricate.",
}
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| visual_state 由谁判定 | 三层门控（Unity 产地 / LiveKit 传输 / Python 消费端）汇总；BB key `session/visual_state` | ar_feature_vision §3.1 |
| Soul 是否硬编码 | **是**（受用户原话约束；不允许 LLM 自由发挥） | ar_feature_vision §3.3 V2 |
| 失去视觉撑对话 | 拉 Graphiti 最近记忆 + 鹦鹉絮叨人设 | ar_feature_vision §3.3 V3 |

**TODO 注释草稿**：
```python
# TODO(NEED-P2.5-VISUAL-SELF-AWARE): 4 级视觉自我感知 + Soul 8 条强制话术
#   - 来源: ar_feature_vision §3.3 (V1/V2/V3 tentative; 已锁风格)
#   - 4 级: active/degraded/paused/blocked
#   - BB key: session/visual_state (writer = VideoStateManager 三层汇总)
#   - 配套 NEED: NEED-P2.5-A persona 外置（与 4 级强制话术合并到 personas/<id>.md）
#   - 名词: 概念词典 §3 "Proprioception 4 级"
#   - Skill: livekit-unity-lifecycle/IMPL_REF.md §5 (ARCore 黑帧反馈)
```

---

### §1.3 ⚠ 三合一统一视图（Reflex/Intent/Task ≡ 三层意识 ≡ System1/System2/反思层）

**来源**：`ar_feature_vision.md §3.5 / §3.6`（关键洞察）+ `parrot_behavior_rules.md §0.1`。

**三视图对应关系**：
```
Reflex  ≡ Subconscious      ≡ System 1 (反射)        ms-s
Intent  ≡ Autonomous Action ≡ System 1 + 部分 System 2 s-min
Task    ≡ Conscious Report  ≡ System 2 + 反思层      min+
```

**Blackboard 4 scope**（`ar_feature_vision §3.6`，受 LimboAI scope chain + Unreal Blackboard 启发）：
| Scope | 持久度 | 例子（含 writer）|
|:--|:--|:--|
| **Global** | 跨 session（Graphiti / config）| user_profile / behavior_mode / persistent_prefs / **active_persona_id**（NEED-P2.5-A）/ **active_model_id**（GOSLO mod）/ **active_scene_id** / **attention_thresholds**（Echo 写）|
| **Session** | 本次 LiveKit room 期间 | room_id / unity_identity / connected_since / **scene** / **visual_state**（§1.2）/ ecp_state / connection_health / audio_route_policy |
| **Tick** | 每次 telemetry / RPC ack | body_state / head_state / cognitive_state / ar_tracking_state / last_rpc_ack |
| **Transient** | 秒级 consume-then-expire | just_captured_photo / hand_gesture_detected / current_attention_hint / last_sighting_event / last_photo_event |

**v0 §6.1 跨场景 binding 表的补丁**：v0 把所有 BB 写入混在一起，本文 §1.3 表是更准确的 4-scope 划分。

**接口签名草稿**（已有；本节仅做语义补丁）：
```python
# src/parrot/scheduler/blackboard.py (existing; 增 scope 标注 namespace)
# BB key 命名约定: <scope>/<key>
# global/active_persona_id ; global/active_model_id ; global/active_scene_id
# session/visual_state ; session/scene
# tick/body_state ; tick/cognitive_state
# transient/current_attention_hint ; transient/last_sighting_event
```

**How TODO**：
| 决策点 | 推荐 | 依据 |
|:--|:--|:--|
| 是否做 4 scope 物理隔离 | **否**（baseline；继续用 single Redis hash + key 前缀） | ar_feature_vision §3.6 |
| Injector 注入策略 | **事件驱动 + turn 起始快照** 双路并行（Voyager 模式） | ar_feature_vision §3.6 三条原则 |
| cognitive_state 注入 | **不送**（LLM 自己就是这个状态，送了是噪音） | ar_feature_vision §3.6 矩阵 |
| last_rpc_ack 注入 | **仅失败送**（成功不汇报；BrainBody-LLM 核心洞察） | 同上 |

**TODO 注释草稿**：
```python
# TODO(CC-4-bb-namespace-audit): 4-scope BB key namespace audit
#   - 当前: bb_schema 已用 global/ session/ tick/ transient/ 前缀（部分 keys 0 漂移）
#   - 增量: 给 4 active 块 (model/persona/mode/scene) 全部入 global/ scope；session/visual_state 加；
#   - 来源: ar_feature_vision §3.6 (4-scope Blackboard)
#   - 名词: 概念词典 §3 "Blackboard 4 scope"
#   - 决策: ar_feature_vision §3.6 注入策略矩阵 7 行
```

---

### §1.4 ⚠ 2 Scene baseline（DESKTOP_WEBCAM + AR_HANDHELD）非仅 DESKTOP

**来源**：`ar_feature_vision.md §3.4`（用户已确认 P2 = 2 个 Scene）。

**冲突点**：当前 `SceneType` enum 含 6 项（DESKTOP / HOME_INDOOR / OUTDOOR / LIBRARY / KITCHEN / OTHER），但 `dsg/l1_5/scene_snapshot.py:SceneRegistry` 只注册了 DESKTOP_PROFILE。**P2 baseline 应注册 2 个 Profile**：
- `DESKTOP_WEBCAM` (Editor / 无 AR 设备 / 2D 背景 / Webcam ARVideoPublisher 路径)
- `AR_HANDHELD` (Android 真机 AR / ARCore 平面 + anchor / AR ARVideoPublisher 路径)

**接口签名草稿**：
```python
# src/parrot/dsg/l1_5/scene_snapshot.py (existing; 改 enum + 注册第 2 个 profile)
class SceneType(str, Enum):
    DESKTOP_WEBCAM = "desktop_webcam"   # P2 baseline
    AR_HANDHELD    = "ar_handheld"       # P2 baseline
    # P3+ 占位
    HOME_INDOOR = "home_indoor"
    OUTDOOR     = "outdoor"
    LIBRARY     = "library"
    KITCHEN     = "kitchen"
    OTHER       = "other"

# 注册 2 baseline profile
DESKTOP_WEBCAM_PROFILE = SceneProfile(scene_type=SceneType.DESKTOP_WEBCAM, ...)
AR_HANDHELD_PROFILE = SceneProfile(scene_type=SceneType.AR_HANDHELD, ...)
```

**注意**：这触动 `protocol_snapshot_p4 §18 BucketKind` 注释，但 SceneType enum 不在 cs_parity 守护范围（仅 Python 内部）→ **不破 wire 锁**。

**TODO 注释草稿**：
```python
# TODO(S0-scene-baseline-2): P2 baseline = 2 Scene (DESKTOP_WEBCAM + AR_HANDHELD)
#   - 当前: SceneRegistry 仅注册 DESKTOP_PROFILE
#   - 升级: 加 AR_HANDHELD_PROFILE; SceneType enum 加新值 DESKTOP_WEBCAM (替换 DESKTOP)
#   - 触发位置: Unity 启动时读 config 决定 → RPC setScene → Brain L1.5 SceneRegistry.switch
#   - 名词: 概念词典 §2 "SceneType vs LocationTag vs IntentEvent"
#   - 决策: ar_feature_vision §3.4 S1/S2 (Unity 决定 Scene; 不让 Gemini 决定)
#   - 不破 wire: SceneType 不在 cs_parity (Python 内部 enum)
```

---

### §1.5 ⚠ 工作记忆延迟归档 三阶段（NEED-P2.5-ARCHIVE-LLM 配套约束）

**来源**：`dsg/dsg_current_state_distilled.md §12` + `dsg/dsg_decisions_master.md §5`（user 原话钦定）。

**v0 §5.4 NEED-P2.5-ARCHIVE-LLM 仅说"真 LLM 蒸馏"，没强调"延迟归档"约束**。完整三阶段：

```
对话期间（Hot）:
  L2-B 工作记忆图 + 内存快照 + Ref 表 + 时间轴标注（运行时）
  → 不写 Graphiti
       ↓ 对话结束
对话结束（Cold Storage）:
  序列化到硬盘 data/conversations/{conv_id}/{snapshot,refs,timeline}.{json,jsonl}
       ↓ nanobot 闲时 / 夜间
归档（Archive Flow）:
  统一过滤器（含 MemoryValidity）+ LLM 蒸馏
  → 写 Graphiti (add_episode + group_id 分区)
```

**冲突点**：当前 `l2b_graph.py:start_episode()` 异步**立即** `archive_episode_to_graphiti(...)`；这违反延迟归档约束 → Chat 4 实施时**改为**：序列化 + 入 nanobot 闲时队列。

**TODO 注释草稿**（在 v0 §5.4 TODO(Chat4-archive-llm) 之上加）：
```python
# TODO(Chat4-archive-llm-defer): NEED-P2.5-ARCHIVE-LLM 三阶段延迟归档
#   - 关键约束: 对话期间不写 Graphiti（破坏当前 start_episode 立即归档行为）
#   - 三阶段: hot 内存 → cold 硬盘 (序列化 jsonl) → nanobot 闲时 (LLM 蒸馏 + add_episode)
#   - 配合: NEED-P2.5-NANOBOT-HEARTBEAT (闲时检测信号)
#   - 配合: TODO(P3-RefHealth) (MemoryValidity 过滤器)
#   - 来源: dsg_decisions_master §5 (ratified) + dsg_current_state_distilled §12
#   - 路径约定: data/conversations/{conv_id}/{snapshot,refs,timeline}.{json,jsonl}
#   - 名词: 概念词典 §2 "Episode" + "ConversationBoundary"
```

---

### §1.6 ⚠ 3 层防爆炸门控（A10 / L1.5 / L2-B 各一道）

**来源**：`dsg/dsg_current_state_distilled.md §11`（user 决策）。

**v0 §4 算法决策表里 §4.1 候选检索 + §4.2 AdmissionPolicy 没把"3 层门控"显式聚合**。完整图：

```
A10 端 CV Flow（Mecha；不在 DSG 模块）
  IoU + CLIP sim + persistence threshold + obj_min_detections=3
  → SensorFrame + Detection
       ↓
L1.5 入池门（Brain；Chat 2 设计）
  置信度 + 加权投票 + 注意力足够 + 与当前事件相关 + 跳数硬上界 4 跳
  → Observation → Pool.admit
       ↓
L2-B 入图门（IngestRunner._find_existing + _merge）
  UUID 对齐已记忆物体 + 大类背景 Node 合并 + 不可能事件报错 + 同类第二实例需用户确认
  → SemanticNode upsert
```

**触发关注**：v0 §5.2（场景 2 主动好奇）+ §5.8（场景 8 场景切换）+ §1.6（本节）= 3 层门控的具体阈值实施。

**TODO 注释草稿**（散到 IngestRunner 各处）：
```python
# TODO(S2-explosion-guard-l15): L1.5 入池门 - 防爆炸第二层
#   - 当前: 30s repeat-seen → CONFIRMED 升级；缺投票 / 注意力门 / 事件相关性 / 跳数硬上界
#   - 升级: AdmissionPolicy 加 weighted_vote + attention_threshold + event_relevance + max_hop=4
#   - 来源: dsg_current_state_distilled §11 + dsg-rustworkx-master §3.5 (4 跳硬上界 AGCN 实证)
#   - 名词: 概念词典 §2 "防爆炸门控 3 层"
#   - 跳数算法: dsg-attention-schema-papers §1.3 (over-globalization 防御)
```

---

### §1.7 ⚠ 海盗主题换肤（P3 — 像素画资产 P2 优先级要提前考虑）

**来源**：`lore/ideas.md` 2026-04-27 角色设定。

**v0 §6 像素画清单只列了"大小姐宅邸主题"+ "海盗主题 P3 换肤"作为类别注释**，没具体到资产元素的"两套互斥"。

**两套并存的资产清单**（master_audit §6 已部分覆盖；本节做补全）：

| 元素 | 大小姐宅邸（默认）| 海盗（P3 换肤）|
|:--|:--|:--|
| 启动页背景 | 维多利亚 / 蕾丝 / 暖色调 | 深蓝 / 木质 / 黄铜 / 海图 |
| HUD 板纹理 | 像素羊皮纸（白底 / 暖金边）| 老海图 / 卷边纸 / 黄铜钉 |
| 工具柜板 | 同上 | 同上海盗风 |
| 放大镜 | 圆形玻璃放大镜 | **海盗望远镜 skin**（lore §海盗主题）|
| AR 视野滤镜 | 无 | **半边模糊黑色遮挡**（眼罩 / lore 钦定）/ 脏兮兮镜片 |
| 角色 emoji 头像 | 大小姐（GOSLO）+ 女仆（猫娘）| 大副（GOSLO 戴眼罩 skin）+ 水手（Nanobot）|
| 纸条 | 现代邮件信封 | 卷起的羊皮纸 / 火漆封 |
| 字体 | 可读像素中文字体 baseline | 海盗风装饰字体（**字体可读性挑战**，lore 提及）|
| 工具按钮 | 像素彩色按钮 | 海盗木牌按钮 |

**TODO 注释草稿（资产清单注释；不在源码 — 仅 markdown）**：
```
# TODO(P3-pirate-skin): 海盗主题换肤 (P3 / 主题切换 = ScriptableObject swap)
#   - 来源: lore/ideas.md 2026-04-27 (user 钦定)
#   - 触发: 启动页"人设/场景"选择 → 切换 SO swap (不重启 app)
#   - 配合: 4 类块 Mode 块加 ROLEPLAY flag → 同 dsg_decisions_master §3.2 Obsidian-设定-Roleplay
#   - 资产: master_audit §6 + 本文 §1.7 表格
#   - 名词: 概念词典 §6 "Roleplay vs 主题换肤" 区分
#   - 字体可读性: lore §设计挑战; 推 P3 调研 (Last Report / Paper Please 风)
```

---

### §1.8 ⚠ 多设备 input 选择（P3.5 — 调试折叠 / 玩法扩展）

**来源**：`lore/ideas.md` P3.5 条目。

**需求**：在设置 / 调试菜单允许指定一个或多个摄像头 / 麦克风（含虚拟设备 DroidCam / OBS / 屏幕采集），便于联调 + "换一路画面"玩法（听房间声场 / 切副摄看屏幕）。

**接口签名草稿（Unity）**：
```csharp
// unity/ArSpike/Assets/Scripts/ParrotApp/Settings/DeviceSelector.cs (NEW; deferred to P3.5)
public class DeviceSelector : MonoBehaviour {
    public string[] AvailableCameras { get; }    // WebCamTexture.devices
    public string[] AvailableMicrophones { get; } // Microphone.devices
    public void SelectCamera(string deviceName);  // → ARVideoPublisher 切设备
    public void SelectMicrophone(string deviceName);  // → MicrophonePublisher 切
}
```

**TODO 注释草稿**：
```csharp
// TODO(P3.5-multi-device-input): 多摄像头 / 麦克风选择
//   - 来源: lore/ideas.md P3.5 (user 自托管的玩法 / 联调 / "换一路画面")
//   - Skill: livekit-unity-video-publish/SKILL.md (Webcam fallback 路径)
//   - 名词: 概念词典 §4 "VideoTier × DsgMode 2 轴"
//   - 推 P3.5 chat
```

---

### §1.9 ⚠ DSG 工作区 vs AR 工作区交集 = EcpEvent / PhotoNode / RefBinding

**来源**：`dsg/workspace_index.md §5.3` + `ar_workspace_index.md §8.2`。

**重要边界**：
- DSG 工作区 = `architecture/dsg/` + `src/parrot/dsg/`
- AR 工作区 = `architecture/ar_*` + `unity/ArSpike/`
- **交集 = EcpEvent / PhotoNode / RefBinding 三类**；交集以 Phase 4 §8 13 锁为准

**v0 没强调**：菜单设计（场景 6 / NEED-P3-B/C/D/E）属于**两个工作区都要登记**的内容（Sub-Chat A 用户视角 + Sub-Chat B 后端模块视角）；模块化菜单需求要**同时**进 AR 工作区 + DSG 工作区。

**Sonnet 任务**（见 §7）会处理这个跨工作区登记。

---

## §2 v0 完整性确认（8 场景 + 4 增补 + 4 横切关注点）

> 本节做一次 cross-check：v0 §1 列的 8 + 4 + 4 = 16 项是否全覆盖？发现的新 4 项（§1.1-§1.4）该归到哪里？

| v0 章节 | 范围 | 新发现是否覆盖 | 补丁 |
|:--|:--|:--|:--|
| v0 §5.0 S0 启动流程 | 启动页 5 项菜单 | ⚠ 未含 §1.4 2 Scene baseline | 加 "Scene 选择"作为启动页第 6 项 |
| v0 §5.1 S1 baseline | LLM + selection-C | ⚠ 未含 §1.2 4 级视觉自我感知 | 加 "Soul 8 条话术"作为 NEED-P2.5-A 配套子任务 |
| v0 §5.1b S1.5 perch_to_finger | 手势 + 自动接续 Intent | ✅ 已含 | 无 |
| v0 §5.2 S2 主动好奇 | DSG curiosity | ⚠ 未含 §1.6 3 层防爆炸门控 | 加 "L1.5 入池门"作为 §1.6 子任务 |
| v0 §5.3 S3 拍照 | W8 双通道 | ✅ 已含 | 无 |
| v0 §5.4 S4 Plan + nanobot | 4-A 主场 | ⚠ 未含 §1.5 三阶段延迟归档 | 加 TODO(Chat4-archive-llm-defer) |
| v0 §5.5 S5 Plan UI | BLOCKED-BY-NEW-ADR | ✅ 已含 | 无 |
| v0 §5.6 S6 4 类块 | 推 DSG 协议升级 chat | ⚠ 未含 §1.1 Obsidian 3 子类 / §1.7 海盗换肤 | 加 "Persona 块 = 4 级视觉自我感知 + Obsidian 3 子类" |
| v0 §5.7 S7 LineA/LineB | 已 PASS 结构性 | ✅ 已含 | 无 |
| v0 §5.8 S8 场景切换 | DSG Chat 2 已落 | ⚠ 未含 §1.4 2 Scene baseline | 加 SceneType enum 升 2 baseline |
| v0 §5.9 S9 HUD/工具柜 | 全新 UI | ⚠ 未含 §1.7 海盗换肤资产 | 加 ScriptableObject swap 接口 |
| v0 §5.10 S10 视频/音频 | set_video_tier | ⚠ 未含 §1.8 多设备 input | 加 P3.5 推延标记 |
| v0 §5.11 S11 Brain tool 全集 | capability gating | ✅ 已含 | 无 |
| v0 §5.12 S12 4 legacy triggers | 已实施 | ✅ 已含 | 无 |
| v0 §5.cc1 CC-1 Echo 全链路 | 已实施 | ✅ 已含 | 无 |
| v0 §5.cc2 CC-2 重连 | livekit-unity-lifecycle | ✅ 已含 | 无 |
| v0 §5.cc3 CC-3 8KB/dedup | 已实施 | ✅ 已含 | 无 |
| v0 §5.cc4 CC-4 三层调度 | py-trees BT | ⚠ 未含 §1.3 4-scope BB / 三合一统一视图 | 加 BB key namespace audit + Injector 注入策略矩阵 |

### §2.1 完整性结论

**v0 缺了 7 项重要补丁**（已在本文 §1 全部补全）；**v0 + 本文 = 100% 覆盖** 8 + 4 + 4 = 16 场景 / 关注点 + 5 用户钦定增补需求（菜单画布 / 动画素材 / GOSLO 模块化 / Obsidian 3 子类 / 海盗换肤）。

---

## §3 给两个 Sub-Chat 派发的额外子任务（Sonnet 4.6 / Opus 4.7 ×2 用）

| Sub-Chat | 新增子任务 | 引用本文锚点 |
|:--|:--|:--|
| **Sub-Chat A 用户视角** | T-A1 启动页第 6 项加"Scene 选择"（DESKTOP_WEBCAM / AR_HANDHELD）| §1.4 |
| **Sub-Chat A 用户视角** | T-A2 4 级视觉自我感知的用户 UI 反馈（active 时不显示 / blocked 时浮现"被挡住了"提示） | §1.2 |
| **Sub-Chat A 用户视角** | T-A3 海盗主题切换的用户视角流程（启动页"人设/场景"→ ScriptableObject swap）| §1.7 |
| **Sub-Chat A 用户视角** | T-A4 多设备 input 选择 UI（P3.5 标记，不阻塞）| §1.8 |
| **Sub-Chat B 后端模块** | T-B1 Obsidian 3 子类 IngestFilter 改造（不动 enum；用 meta.profile）| §1.1 |
| **Sub-Chat B 后端模块** | T-B2 Soul.py 4 级视觉自我感知段加载（与 NEED-P2.5-A persona 外置同 chat）| §1.2 |
| **Sub-Chat B 后端模块** | T-B3 BB key 4-scope namespace audit + Injector 注入策略矩阵（CC-4 增量）| §1.3 |
| **Sub-Chat B 后端模块** | T-B4 SceneType enum 升 2 baseline（DESKTOP_WEBCAM + AR_HANDHELD；不破 cs_parity）| §1.4 |
| **Sub-Chat B 后端模块** | T-B5 工作记忆三阶段延迟归档约束（与 Chat4-archive-llm 同 PR）| §1.5 |
| **Sub-Chat B 后端模块** | T-B6 3 层防爆炸门控数值实施（A10 端 deferred / L1.5 入池门 baseline / L2-B 入图门 baseline）| §1.6 |

---

## §4 文档索引补充段落（**这是 user 让 Sonnet 复制到 v0 / Sub-Chat A / B prompt 末尾的内容**）

> **使用方式**：把下面 §4.1 的 markdown 段落复制到：
> 1. `interface_design_and_how_todo_v0_20260507.md` §11 变更日志之前
> 2. `app_flow_requirements_interface_chat_launch_prompt_20260507.md` §1 入场必读末尾
> 3. `backend_interface_refinement_chat_launch_prompt_20260507.md` §1 入场必读末尾
> 4. `app_completion_master_audit_20260507.md` §5 引用源末尾
> 5. `ar_workspace_index.md` §2.2b 末尾
> 6. `dsg/workspace_index.md` §1.2 末尾

### §4.1 段落原文（直接复制）

```markdown
---

## §X Interface 工作区文档索引（2026-05-07 增补）

> **触发**：app 完成度审计后产出的"接口/能力提炼 + 概念词典 + 遗留问题 + 菜单设计"4 文件，分别给 Sonnet 4.6 + Opus 4.7 ×2 + 用户最终整合用。

| 文件 | 角色 | 入场谁 |
|:--|:--|:--|
| `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` | v0 接口设计 + How TODO（12 场景 + 4 横切）| Sonnet 4.6 主战场；Opus 4.7 ×2 调研基线 |
| `architecture/Interface/interface_design_supplement_20260507.md` | v0 补丁包（7 项新发现 + 完整性确认 + 索引段落） | 同上；Sonnet 把 v0 + 本文一起喂 |
| `architecture/Interface/concept_dictionary_20260507.md` | 词/字段概念全集（≈80 项）+ 设计文档路由指引 | Sonnet 4.6 写代码遇到不懂术语回查；Opus 4.7 ×2 命名一致性审计 |
| `architecture/Interface/legacy_issues_split_20260507.md` | 遗留问题二分（要解决 / P3 完成）| Sonnet 4.6 知道哪些不要碰；Opus 4.7 ×2 验证未漏标签 |
| `architecture/Interface/menu_design_complete_20260507.md` | 完整菜单设计（启动页 + HUD + 工具柜 + 4 类块 + 节点画布 + 海盗换肤） | Sub-Chat A 用户视角主输入；菜单 UI chat 主输入 |

**关系**：v0 + supplement = 接口设计；concept_dictionary = 命名 SSOT；legacy_issues = 不做清单；menu_design = UI 设计 SSOT。
```

---

## §5 与 v0 的关系明确

| 维度 | v0 | 本文（supplement）|
|:--|:--|:--|
| 范围 | 12 场景 + 4 横切关注点 + 接口签名 + How TODO | v0 之外的 7 项新发现 + v0 完整性确认 + 索引段落 |
| 是否重写 v0 | — | **不重写** — 只增量 |
| Sonnet 4.6 用法 | 主战场（每个场景按 ⑥ TODO → ④ 签名 → ⑤ How TODO 抄） | 配套查（v0 §5.X 引用 supplement §1.Y 时来这里）|
| Opus 4.7 ×2 用法 | 校准 v0 接口签名是否覆盖 | 校准 supplement 7 项新发现 + 完整性确认表 §2 |
| 用户最终整合 | 保留全部信息冗余 | 同上 |

---

## §6 变更日志

- **2026-05-07 v0.1**：本文创建。v0 (interface_design_and_how_todo_v0) 之外的 7 项新发现 + v0 完整性确认表 + 文档索引段落（用于 6 处复制）+ Sub-Chat A/B 额外子任务派发清单。
- **2026-05-07 backend build patch**：§1.4 SceneType 升 2 baseline (DESKTOP_WEBCAM + AR_HANDHELD) 已实施 (`src/parrot/dsg/l1_5/scene_snapshot.py`，DESKTOP 保留作 backward-compat alias)；§1.3 4-scope BB namespace 4 active keys 已落 (`shared/bb_schema.py:global/active_persona_id|active_model_id|active_scene_id|active_mode`，单写 = `brain.preset_loader`)；详见 `architecture/backend_interface_refinement_20260507.md`。