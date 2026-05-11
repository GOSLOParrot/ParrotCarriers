# App V1 Core / Business Interface Audit (Round 2)

Date: 2026-05-11
Audit by: Cursor (Opus parent agent), continuation of
`app_v1_session_context_pack_audit_20260511.md`.

## Version Snapshot

| 维度 | 值 |
|:---|:---|
| `pyproject.toml` version | `0.1.0` |
| Python | `>=3.11` (实测 3.11.14) |
| livekit-agents | `1.5.5` |
| FalkorDB / Graphiti | `graphiti-core[falkordb,google-genai]>=0.28,<0.29` |
| LineB plugin group | `livekit-plugins-silero>=1.5,<2.0` (`pip install -e ".[line_b]"`) |
| Voiceprint group | `speechbrain>=1.0,<2.0`, `torch>=2.1`, `torchaudio>=2.1`, `numpy>=1.26,<3.0` |
| Sprint stage | **P2.5 — App V1 build phase** (Sprint 4 Phase 4 已收口；DSG Chat 2 / GOSLO 模块化 / 接口提炼 pre 全部完成；当前在 RoomSetting + LineB + Ner 真机集成路径上) |
| 最近的 git 提交 | `c491535 App 0`, `c22bd5f Ner Update`, `55fdb48 docs: record ECS app v1 smoke` |

## Audit Scope

| 层 | 文件 |
|:---|:---|
| **Brain Core**（启动期注入 + Room/Line 状态机） | `preset_loader.py`, `session_context_pack.py`, `line_profile.py`, `room_setting.py`, `soul.py`, `bb_schema.py` |
| **Business RPC**（Unity → Brain 入口） | `agent.py::_attach_menu_rpc`, `app_first_version.AppFirstVersionFacade` |
| **LineB 业务子系统** | `lineb_audio_guard.py`, `lineb_voiceprint.py`, `lineb_model_reaction.py` |
| **菜单 / 工作区** | `menu_registry.py`, `workspace_registry.py`, `session_policy.py` |

## 发现的 4 类 Bug（全部已修）

### Bug A（HIGH）— Unsaved RoomProfile 草稿 `apply` 后 `setting_file_refs` 丢失

#### 现象

Unity 用户流程：

1. `newRoomProfile` → backend 生成新 id（如 `room_a1b2c3d4`），仅在内存
2. 用户编辑 `setting_file_refs`（添加新 Obsidian roleplay 笔记）
3. `applyRoomProfile` 直接传 full draft dict，**没有先 `saveRoomProfile`**
4. Backend `preset_loader.apply_room_profile(profile)` 写 BB：
   ```
   global/active_room_profile_id = "room_a1b2c3d4"
   global/active_persona_id = ...
   global/active_line_profile_id = ...
   ```
   但**只写 id，没有写完整 RoomProfile JSON**
5. 转一圈后 `session_context_pack._load_room_profile()`：
   - 读 BB → 拿到 `room_a1b2c3d4`
   - `get_preset_loader().load_room_profile("room_a1b2c3d4")` → 在 disk 找
     `data/presets/room_a1b2c3d4.json` → **不存在** → fall back to default
6. **Brain 实际加载的是 `default` Room 的 setting refs，不是 draft 的！**
7. LLM system prompt 包含的是 `default` 的 world/scene context；Unity 以为
   它配的是 draft 的 → 双方状态错位

对比 `line_profile.LineProfileLoader.apply` 的早就有的双写：

```python
"global/active_line_profile_id": resolved.line_profile_id,
"global/active_line_profile":    resolved.as_json(),  # ← 全量 JSON
```

`bb_schema.py` 早就给 LineProfile 配了 `global/active_line_profile`
key 并注释 "Resolved active LineProfile payload for **unsaved RoomSetting
drafts**" — 但同样的对偶 key **从来没有给 RoomProfile 配过**。

#### 影响范围

- 任何"先 new → 改 → apply（未 save）"的 Unity flow
- 真机/模拟器的菜单 UX 几乎一定会踩到（用户改了一下就 apply 是常见操作）
- 现有测试 `test_apply_room_profile_enforces_valid_profile_and_writes_keys`
  只断言 BB id 写入，**没有覆盖 setting refs 是否生效**

#### 修复

1. `bb_schema.py` 新增 `global/active_room_profile`（dict）key
2. `preset_loader.apply_room_profile` 同时写 id + 全量 `as_json()`
3. `session_context_pack._load_room_profile` 优先用 BB JSON（id 匹配时），
   失败再回 disk
4. 新增回归测试
   `test_unsaved_room_profile_draft_apply_preserves_setting_refs`：
   保证空 preset 目录下，apply 一份 draft 后 bundle 里能看到 draft 的
   setting 文件、`prompt_target == "llm+l1_5"`、`llm_prompt_block` 包含
   draft setting 的标题

```python
# 验证片段
draft = RoomProfile(
    room_profile_id="unsaved_draft_room",
    setting_file_refs=(str(note),),   # disk 上 NO file
    ...
)
loader.apply_room_profile(draft)
bundle = load_active_session_context_bundle()
assert any(source.ref == str(note) for source in bundle.sources)
assert "Draft Setting Source" in bundle.llm_prompt_block
```

---

### Bug B（MEDIUM）— LineB `_recent_segments` 跨 session 残留

#### 现象

`lineb_audio_guard._recent_segments: deque[TtsSegment]` 是**模块级** mutable
state，agent.py 的 `disconnected` 回调里没有清理（只清了
`reset_refs_for_session`）。

时序：

1. Session 1：Ner 用 LineB 说了一句话（5s TTS） → 注册 `TtsSegment(started_at=T,
   expected_end_at=T+5)`
2. 用户在 T+3s 断开（杀 LiveKit Room）
3. T+4s 用户重连，在 T+5s 第一次开口
4. `_matching_segment` 时间窗：`window_end = T+5 + 1.25 = T+6.25`，覆盖 T+5
5. → 命中老 session 的 segment → `_score()` 返回 ≥0.5 → 进 `time_overlap_but_low_similarity` → `turn_decision = "uncertain"`
6. agent.py 看到 `decision.turn_decision != "user_turn"` → **抛弃用户第一句**

对 Ner LineB 而言这就是"重连后第一句话被吃掉"。

#### 修复

1. `lineb_audio_guard.py` 新增 `reset_lineb_audio_guard_on_session_end()`
   （和 `reset_lineb_audio_guard_for_test` 区分命名，方便 grep 运行时不变量）
2. `agent.py` 的 `_on_room_disconnected` 调用它，与 `reset_refs_for_session`
   并列

```python
# agent.py 新增
try:
    from parrot.brain.lineb_audio_guard import reset_lineb_audio_guard_on_session_end
    reset_lineb_audio_guard_on_session_end()
except Exception:
    logger.exception("LineB audio guard reset failed on disconnect")
```

#### 备注

`_score()` 里 `match is not None` 时会无条件 append 0.5 的 baseline，这是
"在 TTS 窗口内时不要轻易判 noise" 的设计选择，本次审计**不动**该决策；
但用户在 TTS 结束后有 ~1.25s 的"uncertain blackout"是已知 trade-off，
没有 voiceprint 时尤其明显，建议在前端 UX 上提示 "Ner 还在说话" 或在
`active_lineb_voice_activity` 上加 `cooldown_until` 字段供 UI 灰一下
mic 按钮。**这是设计 todo 不是 bug。**

---

### Bug C（MEDIUM）— `_cosine_similarity` 默默截断不同维向量

#### 现象

LineB voiceprint 验证里：

```python
def _cosine_similarity(left, right):
    size = min(len(left), len(right))   # ← 取较短维度
    ...
```

如果用户 enrollment 用 `speechbrain_ecapa`（192 维），但运行时 provider
环境切到 `resemblyzer_fast`（256 维），或者某次 SpeechBrain 版本升级换了
embedding 维度，**两个维度不一致的向量被静默截断到较短维**，余弦相似度变成
有意义但完全无关于"说话人"的数。

后果：

- Owner centroid 192 dim vs new embedding 256 dim → 比对前 192 维
- 数值落在 [0, 1] 任何位置
- 可能：误判 owner 为 other_speaker（合法用户被拒），或反之（impostor 被接受）

#### 修复

`verify_embedding` 在调用 `_cosine_similarity` 前显式比对维度：

```python
if len(embedding_vector) == 0 or len(embedding_vector) != len(centroid):
    return _verification_error(
        status, "embedding_dim_mismatch",
        f"embedding dim {len(embedding_vector)} does not match owner "
        f"centroid dim {len(centroid)}; verifier provider may have "
        f"changed since enrollment.",
        observed,
    )
```

返回的 decision 是 `"embedding_dim_mismatch"`，前端可以提示用户重新
enrollment。

`_cosine_similarity` 函数本身保留 `min(len)` 兜底（内部 helper），但
docstring 明确"callers screen for equal length first"。

---

### Bug D（LOW）— `applyRoomProfile` RPC 静默回退到 default

#### 现象

```python
draft_or_id = payload.get("room_profile") or payload.get("room_profile_id") or payload
applied = AppFirstVersionFacade().apply_room_profile(draft_or_id, ...)
```

如果 Unity payload 拼写错（如 `roomProfileId` camelCase / `room_profile_ID`
大写），`payload.get` 全部返回 None / 空，最后 `draft_or_id = payload` 这个
完整 dict 进 `apply_room_profile`。

`apply_room_profile` 把 dict 当 RoomProfile.from_json 解析 → 如果没有
`room_profile_id` 字段 → fall back 到 `DEFAULT_PRESET_ID = "default"`。

**结果**：用户期望切到 ner_lineb_room，实际 backend 静默把 BB 改回了
default。前端 UI 可能因 BB watcher 反应正确，但 Brain 加载的是 default Room。

#### 修复

显式判定并 `logger.warning` 列出实际收到的 payload key 集合：

```python
if room_profile is None and not room_profile_id:
    logger.warning(
        "applyRoomProfile: payload missing both 'room_profile' and "
        "'room_profile_id'; falling back to default. payload_keys=%s",
        sorted(payload.keys()),
    )
```

不强行 raise（避免破坏现有自动化脚本），但日志够明显。

---

## 已确认正确（无需改动）

### 1. LineB / LineA pipeline 注入回路（上一轮已修）

`session.current_agent.update_instructions` + `await` 的修复在 LineA 和
LineB 上一致工作；本轮在新 BB 路径下复测了 4 个 session_context_pack
测试 + 113 个 brain 测试 + 35 个 unity / shared 测试，全 PASS。

### 2. `MenuRegistry.apply_selection` 的单写者契约

`apply_selection` 只通过 `PresetLoader.apply` 写 BB，没有绕路；
`menu.workspace` watcher 在 menu RPC 里也只读不写。OK。

### 3. `RoomSettingService.compatibility` 的能力解析

模型 / 场景 / 工作区 / line / line_profile / experience_mode 五维都有
`enabled / degraded / blocked` 的 CapabilityDecision；`apply` 正确在
`state == "blocked"` 时不写 BB 直接返回。OK。

### 4. LineB `apply_audio_route_policy` 的 risk / handling 默认

`_risk_for_route` + `_default_handling` 对未知 route 给出合理 fallback
（unknown → low if voiceprint else medium），与 `evaluate_line_profile` 的
`_echo_risk` 保持一致。OK。

### 5. `voiceprint manifest` schema 弹性

`runtime_status` / `_load_centroid` 对缺字段的 manifest（无 thresholds /
无 enrollment / 无 centroid path）都有 typed degraded state，前端可分别
展示 `disabled` / `not_configured` / `pending_enrollment` / `degraded`，
不会崩。OK。

---

## 发现但本轮不动的事项

### A. `_score()` 在 match 时无条件 +0.5 baseline

会让 TTS 窗口内任意 mic 输入至少拿到 0.5 score，配合 0.82 阈值不会被错判
为 echo，但会进 `time_overlap_but_low_similarity` → `uncertain` →
agent.py 抛弃。**这是 voiceprint 未启用时的保守策略**，需要前端配合给
"还在说话" 的可视提示，或在 `session/lineb_voice_activity` 加 cooldown
字段。涉及 Unity wire，留给前端 chat 处理。

### B. `_recent_segments` deque(maxlen=32) 内存累积

旧 segment 即使时间窗已过仍占 deque 槽。32 条无所谓，但应当在
`_matching_segment` 内主动 prune 已过期的（while front.expired_end_at +
window < now: popleft()）。**纯优化，不影响正确性。**

### C. `note_to_ingest_payload` 对 `kind: setting_source` 这类未知 NodeKind 无 warning

`UserTagFilter._normalize_node_kind("setting_source")` 静默 fall back
到 `OBJECT`，只 `logger.debug`。可以升 warning，但目前 ingest 逻辑不依
赖 kind 做关键分支，**不阻塞业务**。

### D. `AppFirstVersionFacade.apply_room_profile` 返回里没有 `room_profile_id` 字段

返回 dict 里有 `applied_keys` 包含 `global/active_room_profile_id`，但
应用方需要从中 grep。建议加显式 `room_profile_id` 字段。**API 完善，
不是 bug。**

### E. `RoomSettingService.snapshot` 用 `RoomProfile.as_json()` 序列化 → 没有 `compatibility` per-room

`rooms` 列表只是裸 RoomProfile JSON，没有跑 compatibility，前端要逐个
preview 才能知道某 Room 是否 blocked。**性能优化路径，本版可接受。**

### F. `setting_file_refs` 路径解析允许任意绝对路径 + `..`

`session_context_pack._resolve_ref` 当前完全信任 RoomProfile 来源。
未来若支持用户上传 RoomProfile（云端同步 / 第三方插件），需要白名单
sanitization。**当前 trust boundary 是受信本地，OK。**

### G. `_cosine_similarity` 在 `verify_audio_file` → 真实 embedding 路径下，
   ECAPA 默认 192 维，但用户 enrollment 时若用了 fast provider（256 维）
   的 manifest，下次切回 ECAPA verify 会立即触发 Bug C 的新错误返回。
   建议 `enroll_from_audio_files` 把 `embedding_dim` 写进 manifest，
   下次 verify 在更早层面给出 mismatch 提示。**待实施。**

---

## 文件改动清单（本轮）

| 文件 | 改动 |
|:---|:---|
| `src/parrot/shared/bb_schema.py` | 新增 `global/active_room_profile`（dict）key |
| `src/parrot/brain/preset_loader.py` | `apply_room_profile` 同时写 id + 全量 JSON |
| `src/parrot/brain/session_context_pack.py` | `_load_room_profile` 优先 BB JSON；新 helper `_bb_room_profile_payload` |
| `src/parrot/brain/lineb_audio_guard.py` | 新 `reset_lineb_audio_guard_on_session_end`；`__all__` 更新 |
| `src/parrot/brain/agent.py` | disconnect 回调里调 `reset_lineb_audio_guard_on_session_end`；`applyRoomProfile` RPC 加 fallback warning |
| `src/parrot/brain/lineb_voiceprint.py` | `verify_embedding` 在 cosine 前比对维度并返回 `embedding_dim_mismatch` |
| `tests/test_brain/test_session_context_pack.py` | 新增 `test_unsaved_room_profile_draft_apply_preserves_setting_refs` 回归 |
| `.cursor/memory/architecture/Interface/app_v1_core_interface_audit_round2_20260511.md` | 本报告（NEW） |

无 Unity 端改动。无 `data/presets/*.json` / 真机配置改动。无新增 Python 依赖。

---

## 测试

```
.\.venv\Scripts\python.exe -m pytest tests/test_brain/test_session_context_pack.py -v
→ 4 passed (含新增的 draft apply 回归)

.\.venv\Scripts\python.exe -m pytest tests/test_brain tests/test_unity tests/test_shared -q
→ 148 passed
```

无新增 / 失败用例。无 lint 错误。

---

## 给 Codex 的同步要点

1. **Bug A 修复后 RoomProfile 序列化字段必须保持稳定**：`apply_room_profile`
   会把全量 RoomProfile JSON 落 BB，下游会 `RoomProfile.from_json` 反序列化。
   未来给 RoomProfile 加新字段时记得：
   - 加入 `as_json` 序列化
   - `from_json` 提供安全默认（已有的 `_clean_text` / `_tuple_from_raw` 模式）
   - 加 `schema_version` bump 检查（如果引入不兼容字段）

2. **Bug A 也帮忙修复了之前一个隐性 UX 痛点**：以前用户必须 `save → apply`
   两步，现在可以 `new → 改 → apply` 直接生效（disk 还是 stale，但 BB 是
   source of truth）。前端如果想保留"未保存的 draft"提示，需要单独追踪
   draft state（不能依赖 disk 是否存在做判断）。

3. **Bug B 修复让 LineB 重连第一秒能拿到 user_turn**：之前在 ECS smoke 上
   如果观察到"重连后 Ner 听不到 hello"，多半就是这个原因。后续真机回归
   建议加一条：断开 → 立刻重连 → 用户立刻说"你好" → 看日志是否
   `turn_decision="user_turn"`。

4. **Bug C 修复增加了一个新的 verification decision**：`embedding_dim_mismatch`。
   前端 voiceprint UI 需要识别这个 decision 并提示用户：
   "声纹模型已变更，请重新注册"。具体文案由 UX chat 定。

5. **Bug D 的 warning 在 ECS 日志会出现频次**：取决于 Unity 端实际拼写。
   如果观察到该 warning 反复出现，说明 Unity 端有拼写错误，需要顺着
   `payload_keys=[...]` 的日志反向修 Unity 调用代码。

6. **本轮没有触动协议 / DTO / cs_parity 守护**。BB schema 加了一个
   key，但 BB 是 Brain 内部状态，不跨语言。

---

## 与上一轮报告的关系

上一轮 [`app_v1_session_context_pack_audit_20260511.md`](app_v1_session_context_pack_audit_20260511.md)
专注于 `update_instructions` 调用错位 + env vs BB 优先级 + prompt_target
typo 静默 + L1.5 bootstrap 时序竞态（4 项）。

本轮专注于 RoomProfile draft 双写 + LineB 跨 session 状态 + 维度校验 +
RPC 拼写防御（4 项）。两轮合在一起把 RoomSetting + LineB +
session_context_pack 三个相关业务面的入口路径全部走了一遍。

下一轮如果继续审计，建议入口选：
- **DSG triggers / L1.5 admit path**（Phase 4 之后的 L2-B 写入闭环）
- **photo_upload_server + EcpEvent 上行**（Phase 4 W8 的 HTTP + EcpEvent
  双通道，目前只有 manual smoke 验证）
- **menu RPC 端到端 fuzzing**（用 hypothesis 喂奇怪 payload，看
  agent.py 的 `_payload_*` helper 是否都健壮）
