---
status: ratified
status_note: "Phase 4 Brain 侧自审 (W3.A.1 + W4-5 + W6-7) — 双轮 audit 后收口；13 项 finding，0 项触动 Phase 4 锁定需求/功能/契约。proposed 项待用户 sign off 后由实现 chat 应用。"
last_reviewed: 2026-04-30
audit_rounds: 2
audit_scope: "commits d228626 → 7f20b18 (本 chat 全部 Brain 侧产出，9 个 commit)"
test_baseline_at_audit: "176/176 全绿；0 lints；git tree clean"
---

# Sprint4 Phase 4 — Brain 侧自审报告 (W3.A.1 + W4-5 + W6-7)

> **维护者**: AI 自审 (本 chat)
> **创建**: 2026-04-30
> **用途**: 在 Unity B chat 启动 / 端到端 smoke 之前，把本 chat 本身的 Phase 4 Brain 侧产出 cold-read 一遍，找隐藏 bug / 边界违反 / 设计 gap，但**绝不改动 Phase 4 锁定需求**。
> **审计方**: Cold-read by self (fresh-eye 模式)。
> **审计法**: 以 `sprint4_phase4_entry_20260430.md §8` (决策锁) + `audit_identify_object_no_screenshot_20260420.md §9` (W4-5 实施口径) + `parrot_behavior_rules.md §0.3 / §3.7` (体感 + Observer/Attention 边界) 为口径。
> **格式**: 参考本 chat 第 E.3 节 finding 模板。

---

## §0 TL;DR

| 严重度 | 计数 | 修复立场 |
|:--|:--|:--|
| 🔴 高 | 2 | 强烈建议修（边界 violation + 隐藏 attention 数学） |
| 🟡 中 | 4 | 建议修但可推后（bug / doc 漂移 / wire 缺口） |
| 🟢 低 | 7 | 按需修（doc / test / style） |

**总 13 项 finding**。其中：

- **0 项**修改会改动 Phase 4 锁定的需求 / 功能 / 契约（详见 §2 一致性核对表）
- **9 项** proposed 等用户 sign off 即可应用
- **3 项** 建议显式 reject (Phase 5+ 待办)
- **1 项** 建议二轮加强（threshold key 改 `{kind}:{id}`）

测试基线：176/176 全绿，0 lints，工作树 clean。

---

## §1 Audit 口径与锚点

| 锚点 | 用途 |
|:--|:--|
| `sprint4_phase4_entry_20260430.md §8` | Phase 4 决策锁；任意 finding 与 §8 冲突 = audit 越界，应 reject |
| `sprint4_phase4_entry_20260430.md §3.7` | Observer / Attention 边界硬约束 |
| `audit_identify_object_no_screenshot_20260420.md §9` | W4-5 实施口径 (用户 4/30 澄清) |
| `parrot_behavior_rules.md §0.3` | 体感红线 (tool 同步/异步 ↔ GOSLO 话术) |
| `bb_schema.py` | BB key producer 归属真源 |

---

## §2 需求一致性核对（红线检查）

每个 proposed 修改逐项验证**是否会改 Phase 4 锁定需求/功能/契约**。

| Finding | requirement_impact | 验证 |
|:--|:--|:--|
| F-01 (docstring 修正) | ❌ 不改 | 仅 align doc 与 §3.7 边界陈述 |
| F-02 (删除 observer.sighting +0.05) | ❌ 不改 | 删后单次 match net = +0.20，与 audit §1.4 / W4-5 设计意图（单一 Δ）一致；attention 仍上升，felt experience 不变 |
| F-03 (删 identify_object 死代码) | ❌ 不改 | 该 if 永不触发，删除等价 |
| F-04 (threshold docstring 同步) | ❌ 不改 | 仅 doc |
| F-05 (entry doc §8.1 L9 加注 Echo defer) | ❌ 不改 | 显式记录"未接通"，不动 §8 锁定值 |
| F-06 (disconnect 时 reset_refs_for_session) | ❌ 不改 | refs.py docstring 已声明契约，agent 端补实现 |
| F-07 (AttentionHint payload cross-link 注释) | ❌ 不改 | 仅 doc |
| F-08 (race test: cross 后 unbind) | ❌ 不改 | 仅加 test |
| F-09 (cross-kind 同 id test) | ❌ 不改 | 仅加 test |
| F-09-强化 (改 threshold key = `{kind}:{id}`) | ❌ 不改 | 当前测试 bbox/focus id 无碰撞 → 176 全绿不变；预防 Unity B 落地后的潜在合并；不动任何 EcpEvent payload 字段 |
| F-10 (拆 missing_*_id metric, 可不改) | ❌ 不改 | 仅 metric 拆分 |
| F-11 (L0 评分对称, 不改) | n/a | 不动 |
| F-12 (save_new 不发 sighting, 不改) | n/a | 不动 — audit §9.4 没承诺 |
| F-13 (hint_writer dispatch 现为 dead path 注释) | ❌ 不改 | 仅 doc |

**结论**: 13 项 finding 全部**不动** Phase 4 锁定的：
- EcpEvent `event_type` / `source` / topic / 8KB / schema_version 常量
- BB key 名字 / producer 字段
- Δ_focus / Δ_bbox / threshold 起步值
- L11 budget 数值（1.9s / 800/200/800/100ms）
- §3.7 Observer / Attention 边界
- §8.1 L13 dsg/attention/__init__ 硬约束
- §0.2 五条验收口径

---

## §3 Findings (full format)

### §3.1 🔴 高优先级（强烈建议修）

#### F-01 — observer/sighting.py docstring 与 §3.7 边界自相矛盾

```text
severity:    high
confidence:  high
category:    doc + design
file:        src/parrot/brain/observer/sighting.py:13-23
problem:     docstring 写 "Observer ... MAY ... bump L2-B attention"，但 entry doc §3.7 明确
             "Observer 不直接写 L2-B 节点"。这条 docstring 自己给自己授权违反协议。
proposal:    改 docstring：移除 "MAY bump L2-B attention" 行；明确写 "Observer 仅做事件→
             archiver 路由，绝不直接写 L2-B"。配合 F-02 一起改。
why:         §3.7 是 Phase 4 sign off 的硬约束。Phase 5+ 重构时如果有人引用这条 docstring 来
             扩展，会以为"Observer 写 L2-B 是合规的"，扩散到更多地方。
considered_intent:    yes — §E.6 第 1 条已认了 "L2-B +0.05 是 Phase 5+ refactor"，
                      但 docstring 没标 "暂时违反"，反而 normalize 了违规
requirement_impact:   ❌ 不改 — 仅 align doc 与 §3.7
status:               proposed (docstring fix 无副作用)
```

#### F-02 — observer/sighting.py 直写 L2-B `+0.05` 与 in-tool `+0.2` 复合产生 `+0.25`/match

```text
severity:    high
confidence:  high
category:    bug + design
file:        src/parrot/brain/observer/sighting.py:202-204
             src/parrot/brain/tools/identify_object.py:_upsert_to_l2b (existing.attention += 0.2)
problem:     identify_object L0/L1 命中 → _on_match → _upsert_to_l2b(+0.2) +
             publish sighting.matched → observer.sighting 接到 → +0.05 → 净 attention bump
             = +0.25 per match。**没有任何 doc / 注释说明此值 = 0.25**。代码注释只说
             "+0.05 是 second bump"，没意识到是 0.25 复合值。
proposal:    选 1 个：
             A. 移除 observer.sighting 的 +0.05 直写 (行 196-209) — 净 bump 变 0.20，
                与 in-tool 写者归并，遵守 §3.7 边界。**推荐**。
             B. 保留 +0.05 但 hint_writer 接管，从 in-tool 移除 +0.2 — 把所有 L2-B
                attention 数学集中在 dsg.attention。Phase 5+ 大重构。
             C. 显式承认 0.25 是设计值，加注释。**最差**。
why:         W4-5 / W6-7 都是 sign off 的设计稿。设计稿没有任何地方说 attention bump 是
             0.25 — entry doc §8.1 L9 + audit §1.4 都假设是单一 Δ。当前 0.25 是两次提交
             组合的偶然产物。
considered_intent:    yes — §E.6 第 1 条；意识到是 0.25 比意识到 "重复责任" 更严重
                      —— 因为没人 spec 过 0.25 这个值
requirement_impact:   ❌ 不改 — 删除 +0.05 后 attention 仍上升 (+0.20)，felt experience 不变
status:               proposed (选 A — 1 行删除 + 1 行注释 + 1 个测试更新)
```

### §3.2 🟡 中优先级（建议修但可推后）

#### F-03 — identify_object L0 `if node.evidence_score < 0.0` 永远 False（dead code）

```text
severity:    med
confidence:  high
category:    bug (dead code)
file:        src/parrot/brain/tools/identify_object.py:333-334
problem:     `if node.evidence_score < 0.0: continue` —— SemanticNode.evidence_score 默认 0.0，
             代码路径只见 += 而无 -=，永远 ≥ 0.0。这条 if 永远不触发。
proposal:    删除 (1 行)。Phase 5+ tune scoring 时再考虑加正向阈值。
why:         未触发的代码 = 假阳性的"已防御"。读者会以为"低 evidence 的 L2-B 节点会被跳过"，
             但实际不会。
considered_intent:    no — 我写的时候是模糊地想做什么但没想清楚就放下了
requirement_impact:   ❌ 不改 — 删除等价
status:               proposed (1 行删除)
```

#### F-04 — threshold.py docstring 说 "keyed by correlation_id" 但代码已切到 `bbox_id/focus_id`

```text
severity:    med
confidence:  high
category:    doc drift
file:        src/parrot/dsg/attention/threshold.py:16, 141-145
problem:     docstring 说 "Maintains a per-correlation_id ... weight tally"，但 W6-7 实质化时
             _add_weight 已经改成优先用 payload.bbox_id/focus_id 作为 key，correlation_id 只是
             fallback。docstring 没同步。
proposal:    更新两处 docstring：
             - "Maintains a per-target weight tally (keyed by Unity-side bbox_id /
               focus_id from event payload, falling back to correlation_id, then
               '_default')"
why:         docstring 漂移会让 Unity B chat 误以为 correlation_id 是主 key，写新代码时给
             EcpEvent 用 correlation_id 不填 payload key 就跑错路径。
considered_intent:    no — W6-7 升级时漏改 docstring
requirement_impact:   ❌ 不改 — 仅 doc
status:               proposed (纯 doc 修复)
```

#### F-05 — `global/attention_thresholds` BB key Echo 路径**未实现**

```text
severity:    med
confidence:  high
category:    design gap (跨 chat 协调)
file:        src/parrot/shared/bb_schema.py declares; threshold.py 不读
problem:     bb_schema.py 声明 `global/attention_thresholds` (# CANDIDATE，producer =
             brain._rpc_bridge，"Δ_focus / Δ_bbox / threshold / target_ttl_s (Unity
             ScriptableObject Echo)")。但：
             1. brain._rpc_bridge 没有写这个 key 的代码
             2. FocusBboxThreshold 构造时不读这个 key — 永远用硬编码 DEFAULTS
             3. Unity 端 ParrotAttentionConfig SO 在 Unity B chat 待做
             整条 Echo 链路只在 doc 里存在，code 完全没接通。
proposal:    Phase 4 W6-7 范围内**承认这是 Unity B 的 prerequisite gap**：
             - entry doc §8.1 L9 加注 "Echo 路径 Phase 4 W6-7 仅声明、未接通；Unity B
               chat 提供 SO + DataChannel publish 后，brain._rpc_bridge 补 BB write，
               FocusBboxThreshold 在 register() 前读 BB 注入构造参数"
             - bb_schema.py 注释明确 Phase 5+ 读取
why:         我在 commit message 写 "ParrotAttentionConfig SO ... 留 Unity chat" 但没在
             doc 标 Brain 侧的对应空缺。Unity B chat 拿到的 spec 只能告诉它"写这个 BB key"，
             不知道 Brain 这边谁读。
considered_intent:    partial — 知道 Unity 半边没做，但没意识到 Brain 半边读取也没做
requirement_impact:   ❌ 不改 — 显式记录"未接通"，不动 §8 锁定值
status:               proposed (推荐 entry doc + bb_schema 注释 ≥ 2 处)
```

#### F-06 — `refs.reset_refs_for_session` 未 wire 进 brain/agent.py 的 Room.Disconnected hook

```text
severity:    med
confidence:  high
category:    bug (lifecycle)
file:        src/parrot/brain/refs.py:34-40 (docstring 说 "ideally calls...")
             src/parrot/brain/agent.py 的 _on_room_disconnected 没调用
problem:     refs.py docstring 说 "Each LiveKit session ideally calls reset_refs_for_session
             on disconnect"。但 agent.py 的 _on_room_disconnected handler 实际没调。
             多 session（开发期 reload / 真机断重连）时 RefBindings 跨 session 残留。
proposal:    在 agent.py:_on_room_disconnected 加：
                 try:
                     from parrot.brain.refs import reset_refs_for_session
                     dropped = reset_refs_for_session()  # active_ids=None → drop all
                     logger.info("RefBinding registry cleared on disconnect (%d refs)", dropped)
                 except Exception:
                     pass
why:         docstring 写了的契约 code 没履行 = 隐式漂移。Phase 4 W6-7 单 session 不出 bug，
             但开发 reload 会让 test 间状态串联；真机断重连场景同样受影响。
considered_intent:    yes — refs.py docstring 自己说了 "agent boot does NOT install this
                      hook"。当时偷懒没接，现在审计认为应该接
requirement_impact:   ❌ 不改 — refs.py 文档承诺已存在，仅补实现
status:               proposed (5 行 wire-up + 1 测试)
```

### §3.3 🟢 低优先级（按需修）

#### F-07 — AttentionHint payload schema 重复定义无 cross-link

```text
severity:    low
confidence:  high
category:    doc
file:        src/parrot/dsg/attention/threshold.py:248-258 (生产)
             src/parrot/shared/bb_schema.py:current_attention_hint 注释 (文档)
problem:     transient/current_attention_hint 的 8 字段 schema 在两处独立维护：threshold.py 的
             hint_payload dict + bb_schema.py 注释。两者将来可能漂移。
proposal:    threshold.py docstring 顶部加 "schema: see bb_schema.py
             transient/current_attention_hint comment"
considered_intent:    no
requirement_impact:   ❌ 不改 — 仅 cross-link
status:               proposed (1 行 docstring)
```

#### F-08 — 测试空白：bbox 移除发生在 threshold cross 之后但在 hint_writer dispatch 之前

```text
severity:    low
confidence:  med
category:    test
file:        tests/test_ecp_event/test_threshold_emit.py
problem:     当前测试覆盖：bbox.placed → cross → publish + BB + hint_writer(no-op)。未测：
             bbox.placed → cross → bbox.removed (registry 清掉) → 之后某事件触发
             dispatch_to_hint_writer(ref_id=旧 ref) → ref 已不在 registry → silently return。
             这条路径 code 是写了的，但没验证。
proposal:    加一个 test：bind_bbox + manually call _emit_threshold_crossed + unbind_bbox
             + verify hint_writer no-op（ref None）。
considered_intent:    no — 边界条件测试漏掉
requirement_impact:   ❌ 不改 — 仅加测试
status:               proposed (1 个测试)
```

#### F-09 — 测试空白：focus_id 与 bbox_id 同号不同类的 threshold 行为 + **二轮加强**：建议改 key

```text
severity:    low → med (二轮加强后)
confidence:  high
category:    test + bug (potential)
file:        src/parrot/dsg/attention/threshold.py:200-207
             tests/test_ecp_event/test_threshold_emit.py
problem:     refs.py 的 test_brain_refs.py 测了 cross-kind isolation（同 id 不同 kind →
             不同 ref）。但 threshold.py 没测同样情况：bbox_id="001" 和 focus_id="001"
             两个 EcpEvent 来 — threshold._targets dict 用 subject_id ("001") 作 key，
             会**合并**到同一 _TargetState（subject_kind 取决于谁先到）。

             二轮加强 (审计第二轮): 当前测试 bbox/focus id 无碰撞 → 176 全绿，但 Unity B chat
             落地后约束 bbox_id/focus_id 命名空间是个潜在踩坑点。建议预防式修。

proposal:    A. 仅加测试暴露当前行为 + 加注释说明（保守）
             B. **改 key 为 `{subject_kind}:{subject_id}` + 加测试验证隔离 (推荐)**

             B 改动：
                 # threshold.py L200 附近：
                 target_key = f"{subject_kind}:{subject_id}"
                 state = self._targets.get(target_key)
                 if state is None:
                     state = _TargetState(...)
                     self._targets[target_key] = state
             payload 里继续保留原始 subject_kind/subject_id 不变。
why:         refs.py 已经做了同 id 不同 kind 隔离（test 已覆盖），threshold.py 不一致是隐藏 trap。
             改 key 不动任何 EcpEvent 字段、不动 BB schema、不动 publish payload；176 全绿不变。
considered_intent:    no — 一轮没意识到 refs vs threshold 一致性问题
requirement_impact:   ❌ 不改 — payload + EcpEvent + BB key 都不变；只动内部 _targets dict 索引
status:               proposed (推荐 B — 改 1 处 key 计算 + 加 1 测试)
```

#### F-10 — bbox.py / focus.py `missing_*_id` metric 不区分 placed vs removed

```text
severity:    low
confidence:  high
category:    style (observability)
file:        src/parrot/brain/observer/bbox.py:_metrics + focus.py 同
problem:     `missing_bbox_id` 是单一 counter，placed 和 removed 路径都用。debug HUD
             看到 "missing_bbox_id=3" 不知道是 3 个 placed 缺 id 还是 1 placed + 2 removed。
proposal:    拆为 `missing_bbox_id_placed` + `missing_bbox_id_removed`，或保留单一 counter
             但加注释说明语义。Phase 4 单 counter 够用，可不动。
considered_intent:    no
requirement_impact:   ❌ 不改 — 仅拆 counter
status:               proposed (style，可不修)
```

#### F-11 — identify_object L0 substring 评分方向对称

```text
severity:    low
confidence:  med
category:    style (heuristic tuning)
file:        src/parrot/brain/tools/identify_object.py:313-316
problem:     `desc in label` (短描述匹长 label) 和 `label in desc` (长描述匹短 label)
             都给 0.8。直觉上应该不对称。
proposal:    Phase 4 W4-5 不修（L0 是 starter heuristic）。Phase 5+ tune scoring 时再说。
considered_intent:    yes — audit §9.1 锁定 "L0 = text fast match" 不强制评分模型
requirement_impact:   n/a — 不动
status:               rejected_by_audit (Phase 5+ 待办)
```

#### F-12 — identify_object._save_new_object 未发 sighting EcpEvent

```text
severity:    low
confidence:  med
category:    design gap
file:        src/parrot/brain/tools/identify_object.py:_save_new_object
problem:     save_new 创建新 L2-B 节点 + 写 Graphiti，但没发任何 sighting.* EcpEvent。
             observer.sighting 看不到 save_new 路径，相关 archiver 路径 / 监控完全 bypass。
proposal:    要么加 `sighting.created` 新 event_type，要么 sighting.matched 也覆盖
             save_new 场景。Phase 4 W4-5 不强求 — audit §9.4 没承诺。
considered_intent:    no — 但 audit §9.4 没承诺要做，所以不算遗漏
requirement_impact:   n/a — 不动
status:               rejected_by_audit (Phase 5+ 待办，需新 event_type 走 sign off)
```

#### F-13 — threshold._dispatch_to_hint_writer 当前是 dead path（仅 metric）

```text
severity:    low
confidence:  high
category:    doc
file:        src/parrot/dsg/attention/threshold.py:330-346
problem:     hint_writer 只对 RESOLVED Ref 起效。当前 Phase 4 W6-7 没有任何路径会 resolve Ref
             (identify_object 的 sighting.matched 不联动 refs.resolve_ref)。所以 dispatch
             永远走 bumps_skipped_unresolved 分支。这条线是为 Phase 5+ "resolve flow" 预留。
proposal:    threshold.py docstring 顶部加注：
             "Phase 4 W6-7: hint_writer dispatch path is wired but always no-op until
             something resolves Refs (e.g. identify_object integration in Phase 5+).
             The path is pre-wired so Phase 5+ only adds the resolver."
considered_intent:    yes — code 注释说了 "no-op when ref is UNRESOLVED, which is the
                      common case at threshold time"。但没显式说"目前是 100% no-op"
requirement_impact:   ❌ 不改 — 仅 doc
status:               proposed (1 行 docstring)
```

---

## §4 推荐修复顺序与影响面

| 优先 | finding | 改动 | 测试影响 |
|:--|:--|:--|:--|
| 1 | F-02 (选 A) | 删除 observer.sighting 行 196-209 +0.05 块 + docstring 改 + 测试 `test_matched_event_triggers_archiver_and_l2b_bump` 把 attention=0.55 改成 0.5 + 移除 `l2b_attention_bumps` metric 或重定义 | 1-2 个 assertion 更新 |
| 2 | F-01 | 改 docstring（与 F-02 同时） | 无 |
| 3 | F-03 | 删除 1 行 dead code | 无 |
| 4 | F-04 | docstring 同步 (2 处) | 无 |
| 5 | F-09-B (二轮加强) | threshold._add_weight key 改 `{kind}:{id}` + 加 1 测试 | + 1 测试，176 不破 |
| 6 | F-06 | agent.py wire reset_refs_for_session + 1 测试 | + 1 测试 |
| 7 | F-13 | docstring 1 行 | 无 |
| 8 | F-07 | docstring 1 行 cross-link | 无 |
| 9 | F-05 | entry doc §8.1 L9 加注 + bb_schema 注释 | 无 (仅 doc) |
| 10 | F-08 | race test 1 个 | + 1 测试 |
| 11 | F-10 | metric 拆分（可推） | 无 |
| 12 | F-11 / F-12 | rejected — 不修 | 无 |

**总改动量**: 核心代码删 ~15 行，加 ~5 行，doc 修 ~10 处，测试 +3-4 个。预计 0.5-1 小时。

---

## §5 测试影响地图

修复后预期测试基线：

| 文件 | 当前 | 修后 | Δ |
|:--|:--|:--|:--|
| `test_observer_sighting_handlers.py` | 6 | 6 (1-2 项 assertion 改) | 0 |
| `test_threshold_emit.py` | 6 | 8 (+ F-08 + F-09-B) | +2 |
| `test_attention_threshold.py` | 13 | 13 | 0 |
| `test_brain_refs.py` | 12 | 12 | 0 |
| `test_observer_bbox_focus.py` | 10 | 10 | 0 |
| `test_event_ingest_*` / `test_ecp_event*` / `test_ref_binding` 等 | 不动 | 不动 | 0 |
| 新增 disconnect cleanup test | 0 | 1 | +1 |
| **总计** | **176** | **179** | **+3** |

修后预期：**179/179 全绿**。

---

## §6 用户 sign-off 需要的清单

修改全集分两组路由给用户决定：

### §6.1 直接 fix（无设计 implication，纯局部 + doc + test）

如果用户 sign off "F-01 + F-02(选A) + F-03 + F-04 + F-06 + F-07 + F-08 + F-09-B + F-13"，可由实现 chat 直接动手 + commit + push。

### §6.2 需要先讨论 / 推迟

| 项 | 路由 |
|:--|:--|
| F-05 | **请讨论** — 触及 Unity B chat 契约 + entry doc §8.1 L9 加注，建议在 Unity B chat 启动 prompt 时一并 spec |
| F-10 | **可补可不补** — 纯 metric 拆分，按用户偏好 |
| F-11 | **建议 reject** — Phase 5+ tune |
| F-12 | **建议 reject** — Phase 5+ 新 event_type 需 sign off |

### §6.3 硬约束（任何人不允许动）

复刻 §E.4 给 audit chat 的 10 条硬约束（防越界 checklist）：

1. 不修改 entry doc §8 任意条款（修改即漂移，必须 sign off）
2. 不修改 audit doc §9 任意条款（同上）
3. 不修改 dsg/attention/__init__.py 的 export 集合（§8.1 L13 硬约束）
4. 不修改 ecp_event.py 的 EcpEventType / EcpEventSource 枚举值（C# parity）
5. 不修改 ecp_event.py 的 8KB / topic / schema_version 常量
6. 不修改 bb_schema.py 任意 key 的 producer 字段（除非同步说明 doc）
7. defer 列表里的项 (audit §9.5 / entry §8.6) — 默认不补；如想补，先 propose
8. 修改后保持 pytest 全绿（修后预期 179）；新增测试只能加，不能换语义
9. Unity 端文件 (unity/) 完全不动
10. 给用户看 diff 之前先跑 pytest，不要把 broken 状态推过来

---

## §7 已知 trade-off（不计入 finding）

| 项 | 立场 |
|:--|:--|
| `_state_context.py "HEAD_FORWARD"` fallback | 保留 defensive，无 cost |
| `identify_object` capture 失败不发 snapshot.captured | 故意 — Unity captureSnapshot 还没 ECP-化 (def-1) |
| `observer/snapshot.py` + `photo.py` 仍是 stubs | 故意 — def-1 + W8 |
| RefBinding 一直 UNRESOLVED 是 Phase 4 W6-7 常态 | 故意 — resolve flow 是 Phase 5+ 动作 |

---

## §8 引用

- `architecture/sprint4_phase4_entry_20260430.md §8` — 决策锁
- `architecture/sprint4_phase4_entry_20260430.md §3.7` — Observer/Attention 边界
- `architecture/audit_identify_object_no_screenshot_20260420.md §9` — W4-5 实施口径
- `parrot_behavior_rules.md §0.3` — 体感红线
- `architecture/sprint4_phase4_w3_a2_a3_completion_20260430.md` — Unity W3.A.2/A.3 接合点
- `architecture/sprint4_ecp_minimal_audit_20260429.md` — 前序审计（Phase 1）格式参考
