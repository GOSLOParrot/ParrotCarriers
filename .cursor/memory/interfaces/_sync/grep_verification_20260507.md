---
status: stage-4-completion
category: grep-verification
chat_4_stage: "Stage 4"
status_note: "Stage 4 grep 验证报告 — 25 接口文件 vs 实际代码 grep 对账。发现 4 处漂移 / 9 处 doc 不全（命名 / 命中漏 / Phase 5+ defer）；全部进 upgrade_roadmap。"
last_reviewed: 2026-05-07
parent_doc: "../INDEX.md"
ai_priority: high
ai_audience: both
---

# Stage 4 Grep 验证报告（2026-05-07）

> per `interface_extraction_plan §7.5.2` grep 兜底脚本；扫描完毕 → 与 25 接口文件 inventory 对账。

---

## §0 TL;DR

| 维度 | 数 |
|:--|:--|
| grep 命令跑数 | 12 |
| ✅ 验证通过的接口面 | 21 / 25 |
| ⚠️ 漂移（doc 与 code 不一致）| 4 处 |
| 🆕 doc 不全（应列入 doc 但漏）| 9 处 |
| 🛑 Stage 4 阻塞性问题 | 0（全部进 upgrade_roadmap）|

---

## §1 attach_* helpers — **doc 不全 8 处**

**doc 列了 5**：attach_event_ingest / attach_ecp_state_ingest / attach_telemetry_receiver / attach_attention_config_handler / attach_transcript_listener_to_session

**grep 实际 13**：

| # | helper | doc 状态 | 处置 |
|:--|:--|:--|:--|
| 1 | `attach_ecp_state_ingest` | ✅ in doc | — |
| 2 | `attach_state_header` | ✅ 在 selection_c_state_context.md | — |
| 3 | `attach_cognitive_state_tracker` | ⚠️ 标"隐式" — 实际是显式 attach | upgrade_roadmap：attach_helpers.md §1 改进列表 |
| 4 | `attach_ecp_event_publisher` | ❌ 漏 | 同上 |
| 5 | `attach_ecp_event_ingest` | ✅ in doc | — |
| 6 | `attach_mode_watcher` | ❌ 漏 | 同上 |
| 7 | `attach_context_injector` | ❌ 漏 — B12 | 同上 |
| 8 | `attach_perception_supervisor` | ❌ 漏 | 同上 |
| 9 | `attach_video_state_rpc` | ❌ 漏 | 同上 |
| 10 | `attach_mode_controller` (DSG) | ❌ 漏 | 同上 |
| 11 | `attach_telemetry_receiver` | ✅ in doc | — |
| 12 | `attach_conversation_writer` | ❌ 漏 | 同上 |
| 13 | `attach_video_state_rpc` (重复) | — | — |

**根因分析**：driver-first 方法论从 needs / capabilities 反推接口，但 Phase 1-3 落地的 attach helper 数量超出 needs 显式列表（B 系列只列 14 brain modules，attach 函数是 Phase 4 W2 收口加入的实施细节）。**这是方法论本身的 trade-off**：driver-first 抓主要需求，但漏 incremental 实施细节；grep 兜底正好捕捉。

**修复方向**：upgrade_roadmap 标 13 attach helper 全列；attach_helpers.md §1 修订（不在本 chat 修，留 4-A 实施轨末段）。

---

## §2 register_* / Strategy / Backend — **命名漂移 1 处**

### §2.1 register_* 实际 6 处

| register fn | doc 中状态 |
|:--|:--|
| `register_admission_policy` | ✅ 隐含（pool_admission_policy.md §1）|
| `register_source_meta_factory` | ✅ 显式（ingest_runner.md §2.2）|
| `register_attention_decay_policy` | ⚠️ 命名漂（doc 用 "AttentionDecayStrategy"） |
| `register_attention_mechanism` | ✅ 显式（attention_strategy.md §1.3）|
| `register_phase4_observers` | ⚠️ 漏（observer_event_bus.md 仅描述 .subscribe 模式） |
| `register_intent_workspace_backend` | ✅ 显式（intent_workspace_backend.md §3）|

### §2.2 命名漂移：AttentionDecayStrategy vs AttentionDecayPolicy

**实际代码**：

```
src/parrot/dsg/l2b/intent_event_boundary.py:109: class AttentionDecayStrategy(Protocol)  # 一处
src/parrot/dsg/l2b/attention/decay.py:24: class AttentionDecayPolicy(Protocol)            # 另一处
```

**doc**（`attention_strategy.md §1.2`）：用 "AttentionDecayStrategy"。

**漂移类型**：代码里有 **两个** Protocol 都叫"衰减策略"——一个用 Strategy，一个用 Policy。doc 用的是其中一个。

**处置**：upgrade_roadmap 标"DSG attention decay 命名一致化"——非 Chat 4 主场（推 P3 仿生升级 chat / DSG 协议升级 chat 决定保留哪个）。

---

## §3 Strategy / Activation 类 — **验证齐**

| 实际类 | doc 状态 |
|:--|:--|
| `FoldStrategy(Protocol)` + `NoOpFoldStrategy` | ✅（attention_strategy.md §2）|
| `AttentionDecayStrategy(Protocol)` + `NoOpDecayStrategy` + `SimpleDecayStrategy` | ✅（部分；含 §2.2 命名漂）|
| `AttentionDecayPolicy(Protocol)` + `NoOpAttentionDecayPolicy` + `SimpleAttentionDecayPolicy` | ⚠️（命名漂）|
| `AttentionMechanism(Protocol)` + `NoOpActivation` + `BoundedBfsActivation` + `SpreadingActivationPlaceholder` | ✅（attention_strategy.md §1.3）|
| `PoolAdmissionPolicy(Protocol)` + `DesktopPolicy` | ✅（pool_admission_policy.md §1）|
| `IntentWorkspaceBackend(Protocol)` + `InMemoryBackend` + `DiskBackend` | ✅（intent_workspace_backend.md §1-§3）|

---

## §4 Topic 常量 — **验证齐 + 已知 inline 边界**

```
TOPIC_ECP_EVENT     = "parrot.ecp.event"      ✅ in topic_matrix.md
TOPIC_ECP_STATE     = "parrot.ecp.state"      ✅ in topic_matrix.md
TOPIC_ECP_TICK      = "parrot.ecp.tick"       ✅ in topic_matrix.md
parrot.ecp.health    (inline envelope)         ✅ in topic_matrix.md (标 inline 不迁移)
parrot.ecp.intent_disconnect (inline envelope) ✅ in topic_matrix.md (同上)
```

**5 topic 全 doc 化 ✅**。Health 与 intent_disconnect 是 inline envelope（不在 ecp_event.py 常量），doc 已正确说明（topic_matrix.md §1.1）。

---

## §5 RPC_METHOD_ 常量 — **doc 不全：可能漂移**

```
rg "^RPC_METHOD_" → 0 命中
rg "RegisterMethodAsync\|PerformRpc" Unity → 4 文件有命中
```

**当前**：RPC method name（"flyTo" / "animate" / etc.）实际**用字符串**而不是 Python / C# 常量。

**doc**（livekit_rpc_v1.md §1）：列 7 method 名表，但**没要求 freeze test 守护**。

**处置**：upgrade_roadmap 推 4-C freeze test 扩展候选 #6：RPC method name 常量化 + cs_parity 守。

---

## §6 NodeKind / EdgeKind / RefKind / Backend — **验证齐 ✅**

```
class NodeKind(...)   → enum 6 项 (test_node_kind_enum_six_values 守)
class EdgeKind(...)   → enum 8 项 (test_edge_kind_enum_eight_values 守)
class RefKind(...)    → enum 4 项
class RefTargetKind(...) → enum 4 项
```

✅ 全部对应 doc。

---

## §7 4-A 实施轨待落地接口（NEED-* 标签）

以下是当前是 skeleton / 缺写者的接口，**Chat 4 4-A 实施轨**完成后再补 producer / consumer 实证：

| NEED 标签 | 接口 doc | 4-A 任务 |
|:--|:--|:--|
| NEED-P2.5-PLAN-INTEGRATION（4 个 plan-* TODO）| `redis_stream.md` + `intent_workspace_backend.md` + `dsg_trigger_outcome_v2.md` plan_request 通道 | A 轨 #1 |
| NEED-P2.5-NANOBOT-HEARTBEAT | `redis_hash.md` parrot:nanobot_heartbeat | A 轨 #3 |
| NEED-P2.5-ARCHIVE-LLM | `graphiti_v1.md` archive_to_graphiti | A 轨 #2 |
| TODO(Chat4-disk-recover) | `intent_workspace_backend.md` DiskBackend.recover() | A 轨 #4 |
| NEED-P3-CAPABILITY-GATING（**user §10 Q1 待答**）| 当前未在 25 接口文件主表中显式 — proposed-new；§10 Q1 sign off 后决定加入 wire/ 还是 capability/ | A 轨 #5 (可选) |

---

## §8 Stage 4 验证结论

| 维度 | 验证 |
|:--|:--|
| **wire 层（9 文件）** | ✅ Phase 4 §8 13 锁全 doc 化；cs_parity 4/4 通过；topic 5 + RPC 7 + RefBinding / NodeKind / EdgeKind 全有实证 |
| **cross-process 层（6 文件）** | ✅ HTTP / Redis 4 类 / Graphiti / Mecha placeholder 全 doc 化；4-A 实施轨 3 项 skeleton 标注清晰 |
| **in-process 层（10 文件）** | ⚠️ attach_helpers.md 漏 8 个；attention 命名漂 1 处；其余 9 文件齐 |
| **capability 层（7 cards）** | ✅ 全 doc 化；与 wire / cross / in 接口 cross-link 齐 |

---

## §9 给 upgrade_roadmap 的输入

详 [`../upgrade_roadmap.md`](../upgrade_roadmap.md)（Stage 4 同步落地）。本节列入 5 项：

1. attach_helpers.md §1 列表扩展到 13 attach helper（next 4-B-in 改进 / 4-A 末段）
2. attention_strategy.md 命名一致化（AttentionDecayStrategy vs AttentionDecayPolicy）— 推 P3 / DSG 协议升级 chat
3. observer_event_bus.md 加 register_phase4_observers 显式描述
4. 4-C freeze test 推扩展 #6：RPC method name 常量化 + cs_parity
5. 4-A 实施轨完成后填 5 接口（plan / nanobot heartbeat / archive_to_graphiti / disk_recover / capability_gating）的 producer / consumer 实证

---

## §10 cross-link

- 父规划稿 §7.5.2 grep 脚本：[`../../architecture/interface_extraction_plan_20260507.md`](../../architecture/interface_extraction_plan_20260507.md)
- 25 接口文件：[`../wire/`](../wire/) + [`../cross_process/`](../cross_process/) + [`../in_process/`](../in_process/)
- 配套 upgrade_roadmap：[`../upgrade_roadmap.md`](../upgrade_roadmap.md)
- 配套 sync reports：[`4-B-req_completion.md`](4-B-req_completion.md) + [`4-B-cap_completion.md`](4-B-cap_completion.md) + [`4-B-wire_completion.md`](4-B-wire_completion.md)
