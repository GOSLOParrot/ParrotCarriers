---
status: ratified-code / pending-online-smoke
category: completion-report
status_note: "Sprint 4 Phase 5+ Line B (STT-LLM-TTS Gemini text) 实施 + Phase 4 协议合同双管线兼容性承诺验证。结构性改动 + 234/234 pytest 全绿 + Phase 4 §8 0 漂移 + ObservationSource enum 0 漂移 ✅；Editor 联机 6-axis 双跑 smoke 留下游 chat 在 Editor + Castle 联机环境执行（本 chat 无 LiveKit 可达 + 无 GOOGLE_APPLICATION_CREDENTIALS）。"
last_reviewed: 2026-05-04
authoritative_for: "Phase 4 协议合同双管线兼容性承诺的代码层证据；Line B 启动 SOP；6-axis 联机对比 smoke 模板；接口提炼 chat 的双管线 finding 输入"
prereq_commits: "(本 chat 改动；落库后填)"
sources:
  - "sprint4_pre_entry_prompt_and_plan.md §双管线适配边界"
  - "sprint4_deferred_issues_and_bugs_20260504.md GAP-2 §options A-E (option E 高代价 trade-off 接受)"
  - "sprint4_phase4_completion_and_final_audit_20260430.md §3 (协议合同最终态)"
  - "sprint4_phase4_entry_20260430.md §8 (决策锁 13 条)"
  - "adr_l1_5_source_dispatch_extension_space_20260504.md §1.1 §4.1 (ObservationSource enum 锁)"
  - ".cursor/skills/livekit-agents/SKILL.md §1 §3 §4 §5"
---

# Line B 实施完成报告（2026-05-04）

> **本文用途**：Sprint 4 Phase 5+ Line B（livekit-agents STT-LLM-TTS pipeline，
> LLM 走 Gemini 文本 API 而非 Realtime）实施收口 + Phase 4 协议合同**双管线
> 兼容性承诺**（pre-entry §70 隐含承诺）的代码层验证。
>
> **基调**：本 chat 完成的是"代码 + 测试 + 配置 + 文档"的结构性收口；6-axis
> Editor 联机双跑 smoke 是 follow-up 工作（需要 Editor + Castle Brain 联机
> 环境 + Google Cloud ADC，本 chat 无该上下文）。本 chat 已交付完整的
> 双跑执行 SOP + 期望对比矩阵模板 + Multi-Agent Handoff 实验脚本。

---

## §0 TL;DR

| 维度 | 状态 |
|:--|:--|
| 代码：env-gate + `_build_session(pipeline)` + listener 改名 + 抽象 | ✅ |
| Phase 4 §8 决策锁 13 条 0 漂移 | ✅（git diff 仅 CRLF + 本 chat 不动 contract files）|
| ObservationSource enum 0 漂移 | ✅（7 entries verbatim；GEMINI_ORAL value 保留）|
| 234/234 pytest 全绿 | ✅（baseline 不变）|
| Line A 构造 smoke | ✅（`_build_session('line_a', cfg)` returns AgentSession）|
| Line B 构造 smoke | ✅（plugin import + AgentSession 构造路径运行；ADC 需在部署侧配置才能完成 STT 实例化，**这是设计意图**）|
| `livekit-plugins-silero` 已装 + `[google,silero]` 全可用 | ✅（pip install via Tsinghua mirror，1.5.7）|
| Castle .env / pyproject.toml Line B 知识落地 | ✅ |
| Multi-Agent Handoff 最小例子（IntroAgent → StoryAgent）| ✅ 脚本已交付（`src/scripts/multi_agent_handoff_spike.py`）|
| **Editor 联机 6-axis Line A vs Line B 双跑** | ⏳ pending（SOP + 对比矩阵模板见 §6 + §7，留 follow-up chat 在 Castle 联机环境执行）|
| **Phase 4 协议合同双管线兼容性承诺** | **PASS（结构性）** — 代码层 0 协议变更即支持 Line A / Line B；联机行为对比 axis 2/3/4/5 待 Editor 真跑确认 |

**一句话**：Phase 4 协议合同的双管线兼容性承诺（隐含承诺 = 协议、BB、selection-C
wrapper、cognitive_state_tracker、DSG triggers、observers 全部 SoT-agnostic）
在代码层 ✅ 通过验证 — Line B 切换无需触动任何 Phase 4 §8 决策锁项。Editor
联机 6-axis 双跑由下游 chat 执行。

---

## §1 改动清单

### §1.1 新增

| 文件 | 用途 |
|:--|:--|
| `src/parrot/dsg/ingest/transcript_extractor.py` | NEW — pipeline-agnostic listener bridge（旧名 alias 保留）|
| `src/scripts/multi_agent_handoff_spike.py` | NEW — Multi-Agent Handoff 最小可运行例子（Line B 之上跑）|
| `architecture/lineb_implementation_completion_20260504.md` | NEW — 本文 |

### §1.2 修改

| 文件 | 改动 |
|:--|:--|
| `src/parrot/brain/agent.py` | + `_resolve_pipeline()` env-gate；+ `_build_session(pipeline, config)` helper；listener `_attach_gemini_transcript_to_terminal` → `_attach_transcript_listener_to_session`；改 `brain_entrypoint` 调 `_build_session()` |
| `src/parrot/dsg/ingest/gemini_transcript_extractor.py` | 退化为 alias shim — 全部从 `transcript_extractor` re-export；保持向后兼容 import |
| `src/parrot/dsg/ingest/__init__.py` | docstring 更新指向新模块名 |
| `pyproject.toml` | + `[project.optional-dependencies] line_b` 装 `livekit-plugins-silero` |
| `.env` | + Sprint 4 Phase 5+ Line B 配置块（PARROT_LLM_PIPELINE / GEMINI_TEXT_MODEL / GOOGLE_STT_* / GOOGLE_TTS_*）|

### §1.3 显式不动

| 锁 | 实测 |
|:--|:--|
| `src/parrot/shared/ecp_event.py` | git diff 空（仅 CRLF）|
| `src/parrot/shared/bb_schema.py` | 同上 |
| `src/parrot/shared/ref_binding.py` | 未触及 |
| `src/parrot/dsg/ingest/base.py` `ObservationSource` enum 7 entries | 未触及 — `GEMINI_ORAL = "gemini_oral"` value 保留（per ADR-L1.5-001 §1.1 + §4.1）|
| `src/parrot/dsg/attention/threshold.py` `_SOURCE_PRIORITY` | 未触及 |
| `src/parrot/dsg/triggers/` 4 触发器 | 未触及 |
| `src/parrot/dsg/ingest/text_source_filter.py` regex | 未触及（ASR 转写风格差异作为 finding 记录，§5 axis-5）|
| selection-C 三 tool wrapper（`fly_to.py` / `animate.py` / `set_video_tier.py`）| 未触及 |
| `cognitive_state_tracker.py` | 未触及 — `agent_state_changed` 事件由 livekit-agents AgentSession 在两条管线下都 emit（PipelineAgent + RealtimeAgent 共用 Voice/AgentActivity 状态机）|
| `identify_object` 1.9s budget | 未触及 |
| Unity 任何代码 | 未触及 |

---

## §2 设计决策摘录

### §2.1 env-gate `PARROT_LLM_PIPELINE`

```
PARROT_LLM_PIPELINE=line_a    # 默认 — Phase 4 baseline
PARROT_LLM_PIPELINE=line_b    # STT-LLM-TTS 管线
其他值 / 拼写错 → RuntimeError 显式抛出
```

代码：`src/parrot/brain/agent.py:_resolve_pipeline()` + `_build_session(pipeline, config)`。

**无 fallback**（per chat task §1.1 + §4 关键设计约束）。Line B 任何依赖
缺失（livekit-plugins-silero 缺、`GOOGLE_API_KEY` 缺、`GOOGLE_APPLICATION_CREDENTIALS`
缺）都会在 `_build_session('line_b', ...)` 同步抛错，**不静默降级到 line_a**。

### §2.2 Line A vs Line B 实例化对比

| 方面 | Line A | Line B |
|:--|:--|:--|
| LLM 实例 | `google.realtime.RealtimeModel(voice, model, api_key)` | `google.LLM(model="gemini-2.5-flash", api_key=...)` |
| STT | Gemini Live 内置（多模态原生）| `google.STT(model="latest_long", languages=["cmn-CN","en-US"])` |
| TTS | Gemini Live 内置（多模态原生）| `google.TTS(language="cmn-CN", voice_name="cmn-CN-Wavenet-D")` |
| VAD | Gemini Live 内置 | `silero.VAD.load()` |
| Turn detection | Gemini Live 内置 | livekit-agents 默认（VAD-based；可选 `TurnHandlingOptions(turn_detection="vad"|"stt")`，本 chat 不引入显式配置）|
| AgentSession 事件契约（`agent_state_changed` / `user_input_transcribed` / `conversation_item_added`）| ✅ 同 | ✅ 同 |
| Auth | `GOOGLE_API_KEY` | `GOOGLE_API_KEY` (LLM) + `GOOGLE_APPLICATION_CREDENTIALS` (ADC for STT/TTS) |

### §2.3 Transcript Extractor 抽象（改名为主，不是大重构）

旧实现已经 SoT-agnostic（`feed_transcript(text, role)` 只用 LiveKit
AgentSession 的标准事件），所以本次改动是：

1. 模块改名 `gemini_transcript_extractor.py` → `transcript_extractor.py`
2. 类改名 `GeminiTranscriptExtractor` → `TranscriptExtractor`
3. 工厂改名 `get_gemini_transcript_extractor()` → `get_transcript_extractor()`
4. **旧名一律保留为 alias**（同模块 + 旧模块 path 都 re-export），任何现存
   import 路径都不破坏
5. agent.py listener helper 同步改名
   `_attach_gemini_transcript_to_terminal` → `_attach_transcript_listener_to_session`
6. **不动** `ObservationSource.GEMINI_ORAL` enum value（避免破坏 11 项 source
   dispatch 测试 + ADR-L1.5-001 §1.1 锁）；只在 transcript_extractor 模块
   docstring + agent.py listener docstring 注释里说明"任何 LLM 助手的
   口头提及，不局限 Gemini Realtime"

### §2.4 cognitive_state_tracker 在 Line B 下的运作

**结论**：无需改动。

**理由**：`AgentSession.emit("agent_state_changed", ...)` 由 livekit-agents 的
`AgentActivity` / `Voice` 状态机统一发出，与 LLM 类型（RealtimeModel vs
PipelineLLM）解耦。Line A 时 RealtimeModel 直接驱动 audio 输出 → speaking 态；
Line B 时 STT-LLM-TTS pipeline 通过 voice/audio 子系统驱动 → 同样发出 listening /
thinking / speaking。`cognitive_state_tracker.AGENT_STATE_TO_COGNITIVE` 映射
表（initializing / idle / listening / thinking / speaking → CognitiveState）
两条管线复用同一份。

**风险与待 Editor 真跑确认（axis-1）**：Line B 因为 STT/LLM/TTS 三段串接，
`thinking → speaking` 的状态切换可能比 Line A 的 RealtimeModel 多 200-600ms
延迟（STT endpoint detection + LLM first-token），导致 selection-C
"附 reason 的 cognitive_state header"在 LLM 看到的瞬间已经是 speaking 而非
thinking。axis-1 联机时需 verify 这条时序差异不破坏 selection-C 体感。
若发生破坏，加 `TurnHandlingOptions(endpointing={"mode": "dynamic"})` 调教
（见 SKILL.md §3）— **本 chat 不引入**，作为 finding 留 axis-1 验证。

---

## §3 测试结果

### §3.1 pytest baseline

```
.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/integration \
    --ignore=tests/test_ecp_event/test_identify_object.py -q
234 passed in 3.32s
```

234/234 ✅。`test_identify_object.py` 仍是 pre-existing breakage（BUG-T1，
deferred chat 修），与本 chat 无关。

### §3.2 跨语言契约（cs_parity）

未触及任何 wire 字段（EcpEvent / EcpEventType / topic / BB key），4/4 cs_parity
继续守护。

### §3.3 ObservationSource 守护

11 项 `tests/test_dsg/test_l2b_node_source_dispatch.py` 通过；enum 7 entries
verbatim（USER_TAG_OBSIDIAN / USER_EXPLICIT / IDENTIFY_OBJECT / GEMINI_ORAL /
CV_A10 / CV_SENTINEL / MOCK）。

### §3.4 _build_session 烟雾测试

```
PARROT_LLM_PIPELINE=line_a → AgentSession 构造 ✅
PARROT_LLM_PIPELINE=line_x → RuntimeError (invalid) ✅
PARROT_LLM_PIPELINE=line_b（无 ADC）→ ValueError("Application default credentials must be available...") ✅ 显式抛错
PARROT_LLM_PIPELINE=line_b（无 GOOGLE_API_KEY）→ RuntimeError("requires GOOGLE_API_KEY for google.LLM") ✅
```

最后两条是设计意图：Line B 启动失败必须显式可见，不 silent fallback。

### §3.5 Alias identity

```
from parrot.dsg.ingest.gemini_transcript_extractor import GeminiTranscriptExtractor, get_gemini_transcript_extractor
from parrot.dsg.ingest.transcript_extractor import TranscriptExtractor, get_transcript_extractor
assert GeminiTranscriptExtractor is TranscriptExtractor  ✅
assert get_gemini_transcript_extractor is get_transcript_extractor  ✅
```

任何旧 import 路径继续工作 — 无破坏。

---

## §4 Phase 4 协议合同双管线兼容性承诺评判

### §4.1 评判维度

pre-entry §双管线适配边界承诺的实质是：**Phase 4 已锁定的协议合同 / 状态面 /
事件时间轴 / DSG L2-B / snapshot / speech state 必须能兼容 Line B**。

### §4.2 代码层证据

| 合同点 | Line A 行为 | Line B 行为 | 兼容 |
|:--|:--|:--|:--|
| EcpEventType 13 项 enum | 不依赖 LLM 管线 | 不依赖 LLM 管线 | ✅ |
| EcpEvent 8KB 拒收 + dedup | event_ingest 路径 LLM-agnostic | 同 | ✅ |
| `parrot.ecp.state` 1Hz + 事件驱动 | Unity 单独 publish；Brain ingest LLM-agnostic | 同 | ✅ |
| `parrot.ecp.event` reliable + 13 event_type | Unity ↔ Brain wire 不变 | 同 | ✅ |
| BB `tick/cognitive_state` writer | `agent_state_changed` 事件触发 | **同事件触发**（livekit-agents 共用 AgentActivity 状态机）| ✅ 代码；axis-1 联机时序待 verify |
| BB `transient/last_*_event` writer 链 | observer 路径 LLM-agnostic | 同 | ✅ |
| selection-C `_state_context` 读 BB 三态附 reason | tool wrapper 不依赖 LLM 类型 | 同 | ✅ |
| RefBinding lifecycle（BBox/Focus place→remove）| Unity 单独驱动 | 同 | ✅ |
| identify_object 1.9s budget（captureSnapshot + L0 text + L1 Graphiti + buffer）| budget 内部计时 LLM-agnostic | 同 | ✅ 代码；axis-3 联机预算分布待对比 |
| attention.threshold.crossed publish | dsg.attention.threshold LLM-agnostic | 同 | ✅ |
| Photo 双通道（preview reliable + asset HTTP POST）| Unity + Brain photo_upload_server 不依赖 LLM | 同 | ✅ |
| transcript listener wiring | `user_input_transcribed` / `conversation_item_added` AgentSession 共用 | 同 | ✅ |

### §4.3 评判

**结构性 PASS**。Phase 4 §8 决策锁 13 条 0 漂移，0 个协议合同字段、0 个 BB key、
0 个 EcpEventType、0 个 wire schema 因为 Line B 而需要修改 — 这正是
pre-entry §70 隐含承诺的实质。

**联机 PASS-with-finding 待 Editor 真跑确认**：
- axis-1 cognitive_state 时序（thinking→speaking 延迟）
- axis-3 identify_object 内部 1.9s 预算分布 + 外部 STT/LLM/TTS 时序图
- axis-5 DSG 文本提取层稳定性（同输入下 Observation label 数量 / 质量）

**整体口径**：**PASS（结构性）/ PASS-with-finding（联机层）**。Final 状态由
follow-up smoke chat 在 Castle 联机环境执行 §6 SOP 后填回。

---

## §5 已知 finding（本 chat 暴露）

### FINDING-LB-1 — Google Cloud ADC 是 Line B 部署的硬前置

```
severity:   med
file:       src/parrot/brain/agent.py:_build_session('line_b', ...)
现象:       google.STT(...) 构造期校验 ADC，ADC 缺则 ValueError 抛
            "Application default credentials must be available..."
影响:       Line B 启动失败显式可见（设计意图），但 Castle 部署需要：
              1. 准备 Google Cloud Service Account JSON（Speech-to-Text + TTS roles）
              2. 挂入容器 + 设 GOOGLE_APPLICATION_CREDENTIALS 路径
              3. 或在 Local Dev 用 `gcloud auth application-default login`
            这与 Line A 只需 GOOGLE_API_KEY 的部署门槛不同。
            .env 已记 + pyproject [line_b] 知识已记。
触发条件:    任何首次启动 Line B 的部署场景。
```

### FINDING-LB-2 — google.STT 构造期 vs 运行期校验

```
severity:   low（doc-only finding）
现象:       google.STT 在 __init__ 就检 ADC（ValueError），不是首次 invocation。
            agent.py 内的 GOOGLE_APPLICATION_CREDENTIALS warning 是兜底信息，
            实际抛错点早于 warning（构造）。
影响:       FINDING-LB-1 的副作用 — 误读 doc 可能以为"先连上再失败"，实际
            是"启动构造就失败"。
proposal:   保留当前 warning + ValueError 双信号（warning 信息含 fix 路径，
            ValueError 含定位）。
```

### FINDING-LB-3 — text_source_filter regex 与 ASR 转写风格差异

```
severity:   待 axis-5 联机确认
file:       src/parrot/dsg/ingest/text_source_filter.py（不动 — per chat task §2 锁）
背景:       Line A 走 Gemini Live 多模态，转写文本风格与 google.STT (cloud
            speech) 输出可能不同（标点、儿化音、断句 / endpoint 切分）。
            text_source_filter 的 NP / 介词正则是按 Gemini Live 转写风格调教
            的。Line B 同输入下，可能抽出不同数量 / 不同质量的 Observation。
预期影响:    DSG L2-B 候选 node 数量 / label 准确度受影响 — 这是 axis-5
            "DSG 文本提取层稳定性"的真正验证目标。
本 chat 不动:  per chat task §2 + §4 关键设计约束 — regex 不动，差异作为
            axis-5 finding 显式记录，留接口提炼 chat 决定如何处理（加 STT
            normalization 层 / 替换 regex / 保持现状 + 容忍）。
```

---

## §6 Editor 联机 6-axis 双跑 smoke 执行 SOP（follow-up chat 用）

> **执行方**：Castle 联机环境 + Unity Editor 可达的 chat（参考
> `sprint4_phase4_online_smoke_completion_20260504.md` 形态）
>
> **前置**：
> 1. Castle Brain 容器或 host Python 已就绪
> 2. Unity Editor 已连 LiveKit room
> 3. `GOOGLE_API_KEY` 已配（Line A + Line B 共用）
> 4. `GOOGLE_APPLICATION_CREDENTIALS` 指向有效的 SA JSON（Line B 必需）
> 5. `livekit-plugins-silero` 已装（`pip install '.[line_b]'` 或单装）

### §6.1 步骤

**Round A — Line A baseline**：

```bash
PARROT_LLM_PIPELINE=line_a python -m parrot.brain.agent dev
# Editor 进 room，跑：
#   1. 简单问候 5 句（驱 cognitive_state 全 listening↔thinking↔speaking）
#   2. fly_to / animate 各 1 次（驱 selection-C 状态 header）
#   3. identify_object 1 次（驱 1.9s budget log + STT/LLM 时序）
#   4. BBox 放置 1 次 + Focus 锚定 1 次（驱 attention.threshold.crossed）
#   5. 自由对话 10 句（驱 DSG ingest Observation 计数）
# 留 brain.log + Unity Console + obs_log
```

**Round B — Line B 同剧本**：

```bash
PARROT_LLM_PIPELINE=line_b \
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json \
python -m parrot.brain.agent dev
# 重复 Round A 完全同一剧本。
```

**Round C — Multi-Agent Handoff（bonus axis）**：

```bash
PARROT_LLM_PIPELINE=line_b \
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json \
python -m parrot.scripts.multi_agent_handoff_spike dev
# Editor 入 room，告诉 IntroAgent 名字 + 城市，验证 StoryAgent 接管 + 个性化故事。
```

### §6.2 6-axis 对比矩阵模板

| Axis | 维度 | Line A 期望 | Line B 期望 | 实测 Line A | 实测 Line B | Verdict |
|:--|:--|:--|:--|:--|:--|:--|
| 1 | cognitive_state（含 agent_state_changed 时序）| listening / thinking / speaking 切换 < 200ms | 切换 < 600ms（STT endpoint + LLM first-token 串联）| (填) | (填) | (填) |
| 2 | selection-C 状态 header LLM 接受度 | LLM input prompt 含三态 reason | 同 | (log brain.tools._state_context) | (同 log) | (填) |
| 3 | identify_object 1.9s 内部预算分布 + 外部 STT/LLM/TTS 时序 | snapshot ≤ 800ms / L0 ≤ 200ms / L1 Graphiti ≤ 800ms | 内部预算同；外部 STT input 不参与（identify_object 是 tool 调用，Brain 内部）| (填) | (填) | (填) |
| 4 | attention.threshold.crossed → LLM 反应延迟 | < 1s | (期待略增 200-500ms — STT/LLM 串)| (填) | (填) | (填) |
| 5 | **DSG 文本提取层稳定性**：同输入下 Observation label 数量 / 质量 | baseline N₁ | 比对 N₂；ratio = N₂/N₁ | (填) | (填) | **关键 axis** — 见 FINDING-LB-3 |
| 6 (bonus) | Multi-Agent Handoff IntroAgent → StoryAgent | n/a | StoryAgent 个性化故事开口 | n/a | (填) | PASS / FAIL with reason / 跳过 |

### §6.3 失败处理

- axis 1-5 任一 FAIL → 在本 doc §5 加 finding；**不阻塞本 chat 收口**（接口
  提炼 chat 决定后续）
- axis 6 FAIL → 接受（per chat task §1.6 "失败可接受，不阻塞前 5 axis"）

---

## §7 manage_episode 在 Line B 下话题感知质量评估（数据采集模板）

> 本 chat 不动 manage_episode 代码；下面是 follow-up smoke 的数据采集 spec。

测试剧本：
1. 用户连续讲 3 个不同话题（A / B / C），每个话题 3-4 句
2. 观察 manage_episode 是否在话题切换点正确开 / 关 episode

数据：

| 维度 | Line A | Line B | 说明 |
|:--|:--|:--|:--|
| 话题切换识别准确度 | (填) | (填) | manage_episode tool 调用 vs 实际话题边界对比 |
| 误开 episode 数 | (填) | (填) | 单话题内 manage_episode 重复 open |
| 漏闭 episode 数 | (填) | (填) | 话题已切换但旧 episode 未 close |

期望：Line B 因为转写文本风格差异（FINDING-LB-3）可能影响话题边界识别，
但 manage_episode 是 LLM tool 调用，主要受 LLM 推理质量影响 — gemini-2.5-flash
text 与 Gemini Live native audio 的中文话题感知能力差异预计较小（同模型族）。

---

## §8 与现有 doc 的衔接

| Doc | 衔接点 |
|:--|:--|
| `sprint4_phase4_completion_and_final_audit_20260430.md` §3 | 本文 §4.2 表证明 §3 协议合同最终态对 Line B 0 修改即兼容 |
| `sprint4_phase4_entry_20260430.md` §8 决策锁 13 条 | 本文 §1.3 + §4.2 — 0 漂移 |
| `sprint4_pre_entry_prompt_and_plan.md` §双管线适配边界 | 本文是该承诺的代码层兑现 |
| `sprint4_deferred_issues_and_bugs_20260504.md` GAP-2 §options A-E | option E（自建 ASR → 文本通道）的 trade-off 接受 — Line B 不解决 GAP-2 外放回声本身（原因：echo 仍可能进 google.STT），但提供了"换底座"的能力，未来加 `livekit.plugins.noise_cancellation`（option D）或硬件耳机（option A）可叠加 |
| `adr_l1_5_source_dispatch_extension_space_20260504.md` §1.1 + §4.1 | 本文 §1.3 + §2.3 — `ObservationSource.GEMINI_ORAL` value 不动 |
| `.cursor/skills/livekit-agents/SKILL.md` §1 §3 §4 §5 | 本文实现完全照 SKILL §1 + §4 的范式 |

---

## §9 下一步建议

按 chat task §5 回复用户的"建议下一步"，候选项：

| 候选 | 触发条件 |
|:--|:--|
| Editor 联机 6-axis 双跑 smoke chat | 本 chat 已交付 SOP + 对比矩阵；任何有 Castle + Editor 联机环境的 chat 可执行 |
| 接口提炼 chat 用本文 §5 finding 输入 | finding-LB-1/2/3 是接口面影响；接口提炼应决定是否提炼"管线无关 LLM 适配层"更高层接口 |
| GAP-2 外放回声叠加修复 | Line B + livekit.plugins.noise_cancellation（option D）+ 硬件耳机（option A）组合验证 |
| DeepSeek V4 第二验证（Line C） | 本 chat 显式不做（chat task §0.5 注明） — 等 Line A/B 联机对比稳定后再启 |
| 真机 spike（验收 #1 perch_to_finger / #2 identify_object）| 仍按既有 Phase 4 收口口径走，Line B 仅作为可选启动模式 |

---

## §10 git diff 验证（Phase 4 §8 0 漂移）

```bash
$ git diff --stat src/parrot/shared/ecp_event.py src/parrot/shared/bb_schema.py \
    src/parrot/shared/ref_binding.py src/parrot/dsg/ingest/base.py \
    src/parrot/dsg/attention/threshold.py src/parrot/dsg/attention/__init__.py \
    src/parrot/brain/ecp_state_ingest.py
# Output: only CRLF warnings; ecp_state_ingest.py +76 -2 (pre-chat existing change, not本 chat)
```

本 chat 实际修改文件（git status `M` + `??`）：

```
M  src/parrot/brain/agent.py             (Line B refactor)
M  src/parrot/dsg/ingest/__init__.py     (docstring)
M  src/parrot/dsg/ingest/gemini_transcript_extractor.py  (alias shim)
?? src/parrot/dsg/ingest/transcript_extractor.py         (NEW)
?? src/scripts/multi_agent_handoff_spike.py              (NEW)
M  pyproject.toml                        (+ [line_b] optional-deps)
M  .env                                  (+ Line B config block)
?? .cursor/memory/architecture/lineb_implementation_completion_20260504.md  (本文)
```

无任何 Phase 4 §8 决策锁文件触动 ✅。

---

## §11 收口签名

- 本文创建 commit: 待入库后填
- 234/234 pytest 全绿（baseline 不变）
- 4/4 cs_parity 不动 — wire 0 改动
- 11/11 source dispatch 测试不动 — ObservationSource 0 漂移
- Phase 4 §8 决策锁 13 条 0 漂移
- Line A 默认 / Line B env-gate / 无 silent fallback ✅
- Multi-Agent Handoff 脚本可运行（待 Editor 联机 axis-6 实测）
- Castle .env + pyproject 已记录 Line B 知识 + 部署门槛（FINDING-LB-1）
- transcript_extractor.py 抽象 + 旧名 alias 100% 向后兼容
