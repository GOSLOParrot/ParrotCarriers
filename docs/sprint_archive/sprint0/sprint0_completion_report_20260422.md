---
status: ratified
status_note: "Sprint 0 的事实记录, 代码已落地 + smoke 过。记录本身只描述既成事实, 不含未验证设计。"
last_reviewed: 2026-04-22
---

# Sprint 0 完成报告 — Schema 层 V1 锁定

> 日期: 2026-04-22
> 作者: Agent (Composer) + 用户决策
> 定位: **事实记录**, 不是计划, 不是设计; 只记"Sprint 0 实际交付了什么"
> 关联文档:
> - `sprint0_preflight.md` (立项 + 裁剪过程, §7.2 任务单, §11 执行记录)
> - `ar_feature_vision.md` (架构愿景, 本次 Schema 要落的锚点)
> - `audit_identify_object_no_screenshot_20260420.md` (识物审计, 本次顺带前置 audit §5.1 B4)

---

## 0. TL;DR (三行说完)

Sprint 0 **只做了一件事**: 把 Sprint 1-4 所有跨进程协议 / 类型 / 枚举的 **V1 定义**一次性锁死。

- **8 个新 schema 文件** (L0 Event + Snapshot + Tiers + VisualState + Blackboard Manifest + L1.5 Protocol + Ingest Filter 协议) + SemanticNode 加 4 个 additive 字段
- **3 次 commit** (S0.A → 过度工程 → 裁剪回 Schema V1) 最终落位
- 测试 / 流程 / ADR / workspace 合约 / Castle 依赖审计 / kickoff 模板 **全部交还用户自管**

---

## 1. 范围演化 — 为什么最终只有 Schema

用户在 Sprint 0 中段 (2026-04-22) 发生两次关键校正, 本报告如实记录:

| 阶段 | 时间 | Scope | 触发原因 |
|:-----|:----|:------|:--------|
| **初始** | 2026-04-22 早 | `preflight §7` 全表 (S0.A-O, 15 项 + 原 7 项 = 22 项) | 担心"没验证就开工会踩坑", 想先把流程/闸门/ADR 都搭好 |
| **过度工程 (commit `36818c4`)** | 2026-04-22 中 | 一次性完成 B/C/D/E/F/G/H/I/K/L/M/N/7 共 13 项 (schema + ADR 目录 + 三闸门规则 + kickoff 模板 + Castle 依赖审计脚本 + workspace 工作合约 + drift 条款) | Agent 按扩大计划开工 |
| **用户裁剪** | 2026-04-22 晚 | **只保留 Schema 层 V1**; 删掉 ADR/ / timeline_api.md / test_gate_rules.md / sprint_kickoff_template.md / audit_deps.ps1, workspace.mdc 恢复到精简版 | 用户原话: "在 test 上花了太多规则了有点本末倒置, 我更希望你能专注于代码和功能的实现... 验收代码部分我自己来设计" |
| **Schema V1 收口 (commit `3a07ca8`)** | 2026-04-22 晚 | 纯 Schema 文件一次性落地, 测试/流程规则全部不碰 | 按裁剪后范围执行 |

**结论**: Sprint 0 的"两态机" (`§6 tentative vs ratified`) 在自己身上跑了一遍 — 过度设计被实证打回, 流程规则降级为 tentative 由用户自选。

---

## 2. 交付物清单 (按文件)

### 2.1 新增 Schema 文件 (8 个)

| 文件 | 行数 | 核心类型 | 下游消费 (Sprint 1+) |
|:-----|:-----|:--------|:-------------------|
| `src/parrot/shared/event_log.py` | 118 | `EventEnvelope` (Pydantic v2 frozen), `EventLayer` (REFLEX/INTENT/TASK) | Sprint 1 L0 Stream dispatcher |
| `src/parrot/shared/snapshot.py` | 142 | `SnapshotEnvelope`, `BBox`, `CameraPose`, `SnapshotSource`, `SnapshotPayloadKind` | identify_object L0-L2, Sprint 4 PhotoEvent, capture_current_frame |
| `src/parrot/shared/tiers.py` | 108 | `VideoTier`, `DsgMode`, `ALLOWED_COMBOS` (5 合法), `validate_combo`, `IllegalCombinationError` | PerceptionSupervisor (Sprint 1 S1.C), set_video_tier tool |
| `src/parrot/shared/vision_state.py` | 64 | `VisualState` 四级, `Scene` (DESKTOP + AR_HANDHELD), `VisualStateReason` 12 词 | Sprint 1 S1.C Injector, Soul get_instructions |
| `src/parrot/shared/bb_schema.py` | 199 | `BB_KEYS` 19 键 × 4 作用域 (Global/Session/Tick/Transient), `get_key`, `keys_in_scope` | Sprint 1 S1.A py-trees Blackboard 扩域 |
| `src/parrot/dsg/l1_5_protocol.py` | 163 | `SensorFrame`, `Detection`, `DetectionAuthority` (ADR-026 六级), `FrameSource` 7 种 | A10/Sentinel/Gemini vision-proxy 上游, Sprint 2 S2.B filters |
| `src/parrot/dsg/ingest/__init__.py` | 30 | 子包出口 | — |
| `src/parrot/dsg/ingest/base.py` | 156 | `IngestFilter` ABC, `Observation`, `ObservationSource`, `IngestOutcome` | Sprint 2 S2.B 5 个 filter 直接继承 |

### 2.2 扩展现有文件 (2 个, 全 additive)

| 文件 | 改动 | 向后兼容 |
|:-----|:-----|:--------|
| `src/parrot/dsg/l2b_types.py` | `SemanticNode` 加 `provenance_stream_id` / `time_span` / `reference_image_path` / `last_sighting_path` 四字段, 全部带默认值 | ✅ 4 现有调用方 (l2b_graph / message_trigger / calendar_trigger / identify_object) 零改动, smoke import OK |
| `src/parrot/shared/constants.py` | 加 `STREAM_EVENT_LOG = "parrot.events.log"` | ✅ 新常量 |
| `pyproject.toml` | 显式声明 `pydantic>=2.5,<3.0` (之前 transitive via graphiti-core) | ✅ 仅提升依赖可见性 |

### 2.3 文档更新 (5 个)

| 文件 | 改动 |
|:-----|:-----|
| `sprint0_preflight.md` | §7.2 任务表重排为 "Agent 落地 / 用户自管 / 延后" 三组; §10.1 登记 S0.P (SemanticNode → Pydantic) 为 deferred; §11 新增执行记录 |
| `.cursor/rules/workspace.mdc` | 补 `status: ratified` frontmatter (保持用户手动剔出的精简版) |
| `.cursor/rules/ar-foundation.mdc` | 同上 |
| `.cursor/rules/livekit-unity-sdk.mdc` | 同上 |
| `.cursor/skills/livekit-unity-video-publish/SKILL.md` | 同上 |

---

## 3. Schema ↔ 架构设计锚点对照

确认每个 Schema 都有明确的"上游设计文档"和"下游消费场景", 不是凭空发明:

| Schema | 架构锚点 | 下游 Sprint |
|:-------|:--------|:-----------|
| `EventEnvelope` + `EventLayer` | `sprint0_preflight.md §1.3-1.4` (四层时间轴) + `ar_feature_vision.md §3.5` (三层意识分发) | Sprint 1 S1.A dispatcher / router |
| `SnapshotEnvelope` + `BBox` | `audit §5.1 B1-B2` (`captureSnapshot` RPC + `capture_current_frame`) | identify_object 升级 + Sprint 4 S4.A PhotoEvent |
| `VideoTier` × `DsgMode` + `ALLOWED_COMBOS` | `ar_feature_vision.md §3.6` (两轴正交 C1-C5) — 用户 2026-04-21 M1 定稿 | Sprint 1 S1.C `PerceptionSupervisor` |
| `VisualState` 四级 + `Scene` + `VisualStateReason` | `ar_feature_vision.md §3.3` V1 定稿 (四级颗粒度) + §3.4 S1 定稿 (Scene 两个) | Sprint 1 S1.C Injector + Soul 分支 |
| `bb_schema.BB_KEYS` (4 作用域 × 19 键) | `ar_feature_vision.md §3.5` (GOSLO Blackboard 四作用域) | Sprint 1 S1.A py-trees 扩域 + Redis mirror |
| `SensorFrame` + `Detection` + `DetectionAuthority` | `module_map_p2.md §10.1` (L1.5 视觉皮层位置) + `ADR-026` (权威链) | A10 / Sentinel / Gemini vision-proxy 落位时直接生产 |
| `IngestFilter` + `Observation` | `ar_feature_vision.md §3.6` (Ingest 过滤器层 4+1 种) — 用户 M2 定稿 | Sprint 2 S2.B text/tool/user_tag/cv_track filter 继承 |
| `SemanticNode.reference_image_path` 等 4 字段 | `audit §5.1 B4` + `vision G1/G2` | Sprint 4 S4.A5 一次性路径填充 (原计划的 `SemanticNode` 扩字段工作已被 Sprint 0 吸收) |

---

## 4. 验证事实

### 4.1 Agent 内 smoke (9 类全通)

```
[OK] EventEnvelope.to_xadd_fields round-trip + frozen + extra=forbid
[OK] SnapshotEnvelope frozen + size_hint_bytes 估算
[OK] BBox ge/le 0-1 校验拒绝越界
[OK] tiers ALLOWED_COMBOS 5 条 / validate_combo 非法抛错
[OK] bb_schema 19 keys, session scope 8, get_key 未知抛 KeyError
[OK] SensorFrame.top_detection 按 (authority.priority(), confidence) 排序
[OK] IngestFilter ABC 子类化 + process_text 默认 no-op
[OK] Observation 字段约束 + ConfirmationStatus 桥接 l2b_types
[OK] SemanticNode 4 新字段默认值 + 4 现有调用方 import 无回归
```

### 4.2 静态检查

`ReadLints` 对 8 个新文件 + 2 个改动文件: 无 linter 错误。

### 4.3 回归调用方

`dsg.l2b_graph` / `dsg.triggers.message_trigger` / `dsg.triggers.calendar_trigger` / `brain.tools.identify_object` 共 4 个 `SemanticNode(...)` 调用点, import 全通 (rustworkx 缺失警告是环境问题, 非回归)。

### 4.4 用户负责的验收 (不在本报告覆盖)

按用户意图, 本 Sprint 不写测试文件、不定三闸门细则、不写 regression baseline。验收 gate 由用户自行设计后挂到 Sprint 1 开工前。

---

## 5. 显式不做清单 (防误解)

以下事项 **Sprint 0 没做** 且 **不是遗漏**, 属于用户已裁剪或延后:

| 项 | 原归属 | 现状态 |
|:--|:------|:------|
| 测试文件 (`Test/sprint0/*.py`) | 用户原话"test 从简交给我" | **用户自管** |
| 三闸门验收规则 (`test_gate_rules.md`) | S0.H | **用户自管** (commit 36818c4 曾写过, 已被用户删除) |
| ADR 目录 + 3 个追溯 ADR | S0.F/G | **用户自管** (已删除) |
| Sprint 开工模板 (`sprint_kickoff_template.md`) | S0.E | **用户自管** (已删除) |
| Castle 依赖审计脚本 (`infra/audit_deps.ps1`) | S0.K | **用户自管** (已删除) |
| `workspace.mdc` Cursor 工作合约 + 两态机正文 | S0.D/M | **用户已手动剔出**, 保留精简版 |
| `commit_guidelines.md` drift 条款 | S0.N | **用户自管** |
| `timeline_api.md` 独立文档 | S0.C | **合并进 schema docstring** (event_log / bb_schema 已写完整) |
| AR Foundation 5.1 配置修复 | S0.O | **挪到 AR 项目升级专项** |
| `SemanticNode` 迁移 Pydantic v2 | S0.P | **deferred**, 挂在 `preflight §10.1` 等 archive filter ratify 后再做 |
| Castle docker up / FalkorDB health | S0.4/5 | **用户手动, 不走 agent** |
| 业务逻辑 (dispatcher / filter 实现 / Blackboard sync / identify_object 重写) | Sprint 1-4 | **本 Sprint 明确只做 Schema, 不写 logic** |

---

## 6. 遗留与观察

### 6.1 working tree 的未追踪文件 (非本 Sprint 产物)

- `src/parrot/brain/vision/snapshot.py` — `capture_current_frame()` 草稿, 已用新 `SnapshotEnvelope` 接口, 但**未被本 Sprint commit**
- `src/parrot/brain/vision/visual_match.py` — VLM compare / describe_image 草稿, 同上

这两个文件是前序 agent 会话留下的 Sprint 4 草稿, Schema 接口对齐 ✅, 但业务逻辑未测。**Sprint 1 识物升级开工时**需要重新审视 + 补测。

### 6.2 git working tree 的待清理状态

`git status` 显示 6 个 `D` (用户删掉的过度工程产物) 和 20+ 个 `M` (其他 memory 文件). 本 Sprint commit **刻意没有**清理这些, 以避免把用户手动决策塞进自动 commit。建议用户在下一次 commit 前做一次人工 review 再批量处理。

### 6.3 pydantic 迁移的再次表态

`SemanticNode` 保留 dataclass 是刻意选择, 见 `preflight §10.1`:
- 运行时热路径 (`touch()` / `attention +=` 每 tick)
- archive filter 设计未 ratify → 锁 schema 会触发 `§6` 提前锁定陷阱
- 最早重拾点在 Sprint 4 S4.A5, 和 "`reference_image_path` 已前置完" 合并处理

---

## 7. 交到下一步

用户已表明下一步的两条主线 (原话 2026-04-22):

1. **数据流获取升级 + 物体发现第一条** — 对应 `audit §5` B1-B4 + L0/L1/L2 三段
   - **Schema 已就位**: `SnapshotEnvelope` (B1-B2) / `SemanticNode.reference_image_path` (B4) / `SensorFrame + Observation` (L0-L2 都能用)
   - **阻塞点仅在业务逻辑**: Unity `SnapshotService.cs` / Brain `capture_current_frame` / identify_object 三段重写

2. **AR 项目升级** — 对应 `ar_feature_vision §3.4` Scene 拓展 + `§3.6` VideoTier 落地
   - **Schema 已就位**: `Scene` / `VisualState` / `VideoTier` / `bb_schema` Session 作用域 8 键
   - **阻塞点在 Unity 侧 + AR Foundation 5.1 对齐 (S0.O)**

---

## 8. 数据统计

| 指标 | 数值 |
|:-----|:----|
| Sprint 0 相关 commit | 3 (`b8bb0a9` S0.A → `36818c4` 过度工程 → `3a07ca8` Schema V1 收口) |
| 最终净产出 (从 `72981e5` P2 基线到 HEAD) | 16 文件 change, +1663 / -11 行 (其中 ADR/kickoff/audit_deps 等中间产物已被用户删除, 不计入净) |
| 纯 Schema V1 commit (`3a07ca8`) | 13 文件, +1041 / -198 |
| 新 Pydantic/dataclass 类型数 | 16 (Envelope/Enum/ABC 合计) |
| 新枚举成员数 | 45 (Scene/VisualState/VideoTier/DsgMode/... 合计) |
| Blackboard 声明键数 | 19 (跨 4 作用域) |
| 现有代码调用方回归 | 0 (4 个 SemanticNode 使用点零改动) |

---

## 9. 回引 / 交叉索引

- 两态机自身的应用: `preflight §6` → 本 Sprint 把"过度工程提前锁定"实证打回, §10.1 S0.P 就地登记 deferred
- L0 Event 写入契约: `event_log.py` docstring + `preflight §1.3-1.4` + `constants.STREAM_EVENT_LOG`
- 三层意识分发: `ar_feature_vision §3.5` → `EventLayer` 三值 + `bb_schema` 事件驱动标记
- 两轴工作模式: `ar_feature_vision §3.6` → `tiers.ALLOWED_COMBOS` 5 条
- 识物升级前置: `audit §5.1 B4` → `SemanticNode.reference_image_path/last_sighting_path`, `§5.2 B1-B2` → `SnapshotEnvelope`

---

## 10. 阶段遗留问题 (Sprint 1 开工前简单登记, 不展开)

> 用户 2026-04-22 要求"简单记录到专门段落, 下次测试前 (P2.5 那轮) 必须解决, 不要现在展开讨论"。
> 原则: **只记问题 + 归属 Sprint, 不提前设计方案**。具体方案等开工时对着现有代码决定。

### 10.1 视频流双通道语义需要在 Sprint 1 就分清楚

- **主通道** (已跑): `ARCameraBackground._rt → TextureVideoSource → "ar-camera" track`。纯摄像头画面, 无鹦鹉无 UI, Gemini Live 看的就是这路 — **所有识物 (identify_object L0/L1/L2) 都走这里**, 不抓二次帧, 便宜。
- **补充通道** (未建, Sprint 4 S4.C): `Unity 完整渲染帧 (相机 + 鹦鹉 + UI) → captureSnapshot RPC → Brain`。只在**用户触发相机模式 / 主动拍照**时按需拉一帧, 落 `data/photos/`, 写 Graphiti `PhotoEvent`, 做相册分流。
- **不要混**: 识物不要走补充通道 (多余抓帧 + 帧里会带鹦鹉干扰 Gemini 判断); 相册/回忆杀不要走主通道 (没有渲染合成, 只有原始摄像头)。
- **代码现状**: `ARVideoPublisher.cs` 只有主通道; `captureSnapshot` 的 Unity handler (`SnapshotService.cs`) 和 `ParrotRpcHandler` 注册都不存在; Python `brain/vision/snapshot.py` 的 RPC 调用现在会 timeout (但 schema 对齐, 逻辑正确, 保留入 git)。
- **归属**: Sprint 4 S4.C (相机模式), 但 Sprint 1/2 写 `identify_object` 升级时要**写注释明确走主通道**, 避免后续混淆。

### 10.2 Schema 命名分裂 (provenance_parent vs provenance_stream_id)

- `EventEnvelope.provenance_parent` + `SensorFrame.provenance_parent` = 因果父事件 id
- `Observation.provenance_stream_id` + `SemanticNode.provenance_stream_id` = 创建本节点的 L0 stream entry id
- 两个名字语义不同是对的, 但 Sprint 2 写 Ingest runner 时**必须显式赋值**: `Observation.provenance_stream_id = SensorFrame.provenance_parent`。一行代码, 不要静默漏掉。
- **归属**: Sprint 2 S2.B 开工第一件事。

### 10.3 SnapshotEnvelope / BBox 缺一致性校验

- 可以构造 `payload_kind=INLINE_JPEG_B64` 但 `payload_inline_b64=""` 的假 envelope, `has_payload()` 返 True, 下游会静默 base64 解码空串。
- `BBox` 没有 `x2 >= x1` / `y2 >= y1` 强约束。
- 不紧急, 但 Sprint 4 `confirm_new` 写入时必然踩到。
- **归属**: Sprint 4 S4.A, 加 `model_validator` 两行搞定。

### 10.4 bb_schema.py 的 writer 名字是占位

- `brain.vision.state`, `brain.perception_supervisor`, `brain.gesture_source` 这几个模块都**还不存在**, Schema 里的 writer 字段是预占。
- Sprint 1 S1.A 真正接 py-trees 时要**一次性对齐**: 要么模块按这个名建, 要么改 Schema, 不要两边都留着不对齐。
- **归属**: Sprint 1 S1.A。

### 10.5 constants.py 旧 BB_* 前缀 和 bb_schema.py 并存

- `constants.BB_PARROT_STATE = "parrot_state"` 等旧字符串仍在, 但目前没有实际消费者。
- 新代码一律走 `bb_schema.get_key()`, **不要碰** `constants.BB_*`。
- 等 Sprint 2 全部走通后再决定删不删 (现在删可能打破未知的遗留测试)。
- **归属**: Sprint 2 结束后 review, 非硬任务。

### 10.6 brain/vision/ 草稿文件未入 git

- `brain/vision/snapshot.py` (capture_current_frame) + `brain/vision/visual_match.py` (compare / describe) 已存在且 schema 对齐, 但未 git add, 目录也没 `__init__.py`。
- **归属**: Sprint 1 开工第一个 commit 顺手收进来 (加 `__init__.py` + git add), 不要到 Sprint 4 才补。
