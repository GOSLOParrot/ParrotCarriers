# App V1 ECP / Disconnect-Path Audit (Round 3)

Date: 2026-05-11
Audit by: Cursor (Opus parent agent), continuation of
`app_v1_session_context_pack_audit_20260511.md` and
`app_v1_core_interface_audit_round2_20260511.md`.

> **Methodology change for this round**: per user request, every claimed
> bug must be **empirically verified before fixing** — not just inferred
> from code reading. Both bugs in this report were repro'd against the
> live code before the fix landed.

## TL;DR

两个**已证实**的 bug，都在 `ecp_state_ingest.py` ↔ `agent.py` 的 disconnect
契约上。

| Bug | 严重度 | 类型 | 验证方式 |
|:---|:---|:---|:---|
| E | HIGH | 死代码：documented-but-unwired cleanup | AST 扫描 agent.py，0 个 `clear_bb_ecp_state` 调用点 |
| F | MEDIUM | 跨 session module-state carry-over | 直接 import 模块跑 5+5 次 packet，看 `duplicate_skipped` 计数器 |

修复都集中在 `ecp_state_ingest.py` + `agent.py::_on_room_disconnected`，
新增 1 个公开 API `reset_ecp_state_ingest_on_session_end()` + 2 个回归测试。
346 个 ECP/brain/unity/shared 测试 + 全仓 546 测试全部 PASS。

## Audit Scope

| 层 | 文件 | 审计深度 |
|:---|:---|:---|
| ECP 上行 ingest | `event_ingest.py`, `ecp_state_ingest.py`, `attention_config_handler.py` | 行级阅读 + 模块级 mutable state 列表 |
| ECP 下行 publisher | `event_publisher.py` | 行级 |
| HTTP server | `photo_upload_server.py` | 行级 + 路径遍历检查（`is_safe_photo_id` / FastAPI 路径段语义） |
| Observer 模块 | `observer/photo.py`, `observer/sighting.py`, `observer/bbox.py`, `observer/focus.py` | 行级 |
| Cognitive 状态 | `cognitive_state_tracker.py` | 行级 |
| Workspace | `workspace_registry.py` | 行级 |
| Session policy | `session_policy.py` | 行级 |
| RPC payload helpers | `agent.py::_payload_*` | 边界值（None / 0 / "" / bool） |
| Disconnect 清理 | `agent.py::_on_room_disconnected` | 与每个有模块级状态的模块对照 |

---

## Bug E — `clear_bb_ecp_state()` 是 dead code（HIGH）

### 验证

```python
# AST 扫描确认 zero callers in agent.py
$ python -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('src/parrot/brain/agent.py').read_text(encoding='utf-8'))
calls = [n.func.attr for n in ast.walk(tree)
         if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
print('clear_bb_ecp_state calls:', sum(1 for c in calls if 'ecp_state' in c.lower()))
"
clear_bb_ecp_state calls: 0
```

`grep` 全仓也只在 `ecp_state_ingest.py` 自身（定义点 + `__all__` 导出）找到。

### 现象

`ecp_state_ingest.clear_bb_ecp_state()` 的 docstring 明确写着：

> **Called from** `brain.agent._on_room_disconnected` (BUG-P4 fix) so that
> `_state_context.get_state_snapshot()` cannot serve stale EcpState data
> from the previous session during the reconnect gap.

但 `agent.py::_on_room_disconnected` 的清理列表里**没有这一行**。当前会执行：

- `_set_goslo_mode("chat")`
- `TriggerRunner.stop()`
- `PerceptionSupervisor.stop()`
- `reset_refs_for_session()`
- `reset_lineb_audio_guard_on_session_end()`（上一轮新增）

但 EcpState 那一项缺失。等同于 BUG-P4 的修复"被设计但从未生效"。

### 后果

`session/ecp_state` BB key 在 disconnect 后保留旧 session 的 dict（含
`active_locks` / `active_command_id` / `body_state` 等字段）。下一次 Brain
进入 `brain_entrypoint`：

- `_state_context.get_state_snapshot()` 仍然能读到旧值；
- `selection-C` tool wrappers（`fly_to` / `animate` / `set_video_tier`）
  会向 LLM 报告"前一个 session 还在执行 `cmd_xxx`"；
- 直到第一个新 EcpState packet 落 BB（1 Hz publishing 下平均 ~500 ms）才
  自我修正。

时间窗口很短（500 ms）但**永远存在**。如果用户在窗口内触发 tool call，
LLM 会基于错误状态生成回复。

### 修复

新增 `reset_ecp_state_ingest_on_session_end()`，内部调用
`clear_bb_ecp_state()` + 清 `_last_seq`（见 Bug F）。在
`agent.py::_on_room_disconnected` 里和其他 reset 并列调用。
保留 `clear_bb_ecp_state()` 作为更窄的 BB-only 原语供测试 / 调试用，
docstring 更新指明它本身不是完整的 session-end cleanup。

---

## Bug F — `_last_seq` per-identity 序列去重跨 session 残留（MEDIUM）

### 验证

```python
$ python -c "
import json
from parrot.brain import ecp_state_ingest as eis
eis.reset_metrics_for_tests()

# Session 1 — identity 'unity_x' 发 seq=1..5
for s in range(1, 6):
    eis._on_ecp_state_packet(json.dumps({
        'schema_version':'ecp.v2.alpha','unity_identity':'unity_x','sequence_id':s
    }).encode('utf-8'))
print('Session 1:', eis.get_metrics_snapshot())
print('  _last_seq:', eis._last_seq)

# Session 2 — Unity restart, seq 又从 1..5
for s in range(1, 6):
    eis._on_ecp_state_packet(json.dumps({
        'schema_version':'ecp.v2.alpha','unity_identity':'unity_x','sequence_id':s
    }).encode('utf-8'))
print('Session 2 (no reset between):', eis.get_metrics_snapshot())
"

Session 1: {'received_count': 5, 'dispatched_count': 5, 'duplicate_skipped': 0, ...}
  _last_seq: {'unity_x': 5}
Session 2 (no reset between): {'received_count': 10, 'dispatched_count': 5, 'duplicate_skipped': 5, ...}
```

**实测：5 个合法的 session-2 packet 全部被静默丢弃。**

### 根因

`ecp_state_ingest.py` 里的 sequence dedup：

```python
_last_seq: dict[str, int] = {}
_DEDUP_WINDOW = 10

if unity_identity and seq:
    last = _last_seq.get(unity_identity, -1)
    if 0 <= last - seq < _DEDUP_WINDOW:
        # 视作 duplicate，drop
        return
    _last_seq[unity_identity] = seq
```

代码作者已经意识到 boot/restart 的不可分辨性（注释里有 `BUG-U2 (boot_id field)`
TODO），所以用 `last - seq < _DEDUP_WINDOW` 的窗口启发式：

- `seq` 远小于 `last`（差 ≥ 10）→ 当作 Publisher restart，接受并 reset
- `seq` 略小于 / 等于 `last`（差 0..9）→ 当作真 duplicate，drop

但 Publisher 真正 restart 时 seq 通常**从 1 开始**，新 session 的前
`_DEDUP_WINDOW`（=10）个 packet（seq=1..10 vs last=5..10）会落入"略小于
last"的判定区间被全部丢弃。

### 后果

- EcpState 1 Hz publishing：disconnect→reconnect 后**前 10 秒** ECP 状态
  在 BB 上没有更新；
- selection-C tool wrappers 看到的 `active_locks` / `active_command_id` 来自
  上一个 session 的快照（叠加 Bug E 之后效果更糟，因为旧值还没被清）；
- 可观测信号：`metrics["duplicate_skipped"]` 计数器不正常上涨；但生产
  上没人盯这个值。

### 修复

`reset_ecp_state_ingest_on_session_end()` 里调用 `_last_seq.clear()`，
每次断开都清空 per-identity 跟踪。

> 备注：清空整个 dict 在当前 Brain 单 room 模型下是安全的 —
> `room.on("disconnected")` fires 时整个 room 已经在拆，所有 participant 都
> 即将断。如果未来支持 multi-participant 室内独立 lifecycle（一个
> participant 走另一个留），需要细化为 per-identity 的清理。

---

## 已确认正确（无需改动）

### `event_ingest.py::_is_duplicate` 时间窗 + 容量双兜底

`OrderedDict` + `popitem(last=False)` 的窗口 + 容量双 eviction，配合
`time.time()` 单调递增假设。理论上系统时钟回拨会破坏顺序，但生产环境
极罕见。**保持现状。**

### `event_ingest.py` 8KB payload cap 只检查 payload 字段而非整 envelope

策略上 OK — spec 写的是 "8KB payload cap"。一个攻击性 envelope 可以塞大
`unity_identity`/`room_id` 字段，但这些是受控参与者标识，不是无约束输入。

### `photo_upload_server.is_safe_photo_id`

- FastAPI `{photo_id}` 路径段默认不接受 `/`（除非 `:path` 转换）
- `_FORBIDDEN_PATH_CHARS` 子串扫描覆盖 `..`、`\`、`\0`、空白字符
- `len > 128` 截断
- `..` 单独存在 → 拒
- 单点前缀（`.foo`）允许，但只构造 `data/photos/{day}/.foo.jpg`，不是 traversal
- Unicode 同形字（如 `∕` U+2215）允许但不会被 OS 当成 `/`

**OK，没有可达的 path traversal。**

### `event_publisher.publish_nowait` 在无 loop 时的处理

显式 catch `RuntimeError` + `failed_count` 计数 + 不 spawn 线程。设计上
正确：希望调用方修自己的调用上下文，而不是 publisher 偷偷开新线程。

### `cognitive_state_tracker` / `attention_config_handler` 模块级状态

只有 `_metrics: dict[str, int]` 计数器和 `_bb` cached client。计数器跨
session 累计是预期（"自 Brain 启动以来"），不是 bug。BB client cache 是
长生命周期对象，安全。

### `agent.py::_payload_bool` / `_payload_float` 边界值

- `None` / 缺失 key → default ✓
- 显式 JSON `null` → default ✓
- `0` / `""` → 显式 falsy 处理 ✓
- bool 直接返回 ✓
- string `"1"` / `"true"` / `"yes"` 等被识别 ✓

**Defensive enough，没有可滥用的边界。**

---

## 发现但本轮不动的事项

### A. `event_ingest.py` 里 `_is_duplicate` 的时钟回拨敏感性

`time.time()` 不是单调时钟。如果系统时钟回拨大于 `DEDUP_WINDOW_SECONDS`
（60s），eviction 会停在第一个"未过期"条目上但其后可能有更早 ts 的条目。
影响：少量过期条目延迟 eviction，最终被容量 cap 强制清。**不影响正确性，
只是内存效率。** 改成 `time.monotonic()` 是低优 todo。

### B. `event_publisher` 没有在 disconnect 时显式释放 `_publisher_singleton`

旧 Room 的死引用残留到下次 `attach_ecp_event_publisher(new_room)` 替换。
窗口期内 `publish_nowait` 会 fail-and-count。不是正确性 bug，是日志噪音。

### C. `_state_context.get_state_snapshot()` 的 BB 读取没有时间戳验证

如果 `session/ecp_state` 里有 30 分钟前的 timestamp 字段，consumer 不会
意识到。本轮 Bug E + F 修了"清不干净"那一面，但 consumer 主动忽略陈旧
状态是另一道防线。**留给 consumer 模块的下一轮审计。**

### D. `photo_upload_server` 没有 size cap

注释里明确说 "Phase 5+ may add a 10 MB hard cap; for now we trust the
Unity client"。预期内的 spike-scope 取舍。

### E. `event_publisher.publish_nowait` 创建的 task 没有 set_name

`asyncio.create_task` 没有 `name=` 参数，意味着 debugging 时看不出是哪个
publish 任务。低优 todo。

---

## 文件改动清单（本轮）

| 文件 | 改动 |
|:---|:---|
| `src/parrot/brain/ecp_state_ingest.py` | 新 `reset_ecp_state_ingest_on_session_end()`；`clear_bb_ecp_state` docstring 更新指明它本身不完整 |
| `src/parrot/brain/agent.py` | `_on_room_disconnected` 调用 `reset_ecp_state_ingest_on_session_end()` |
| `tests/test_ecp_event/test_ecp_state_ingest.py` | 新增 `TestSessionEndResetClearsBBAndDedup`（2 个用例覆盖 Bug E + F） |
| `.cursor/memory/architecture/Interface/app_v1_ecp_disconnect_audit_round3_20260511.md` | 本报告（NEW） |

无 Unity 端改动。无新依赖。无 schema/protocol 变更（cs_parity 不动）。

---

## 测试

```
.\.venv\Scripts\python.exe -m pytest tests/test_ecp_event/test_ecp_state_ingest.py -v
→ 12 passed (含新增的 2 个 session-end 回归)

.\.venv\Scripts\python.exe -m pytest tests/test_ecp_event tests/test_brain tests/test_unity tests/test_shared -q
→ 346 passed

.\.venv\Scripts\python.exe -m pytest tests -q
→ 546 passed, 4 skipped (4 个 skipped 是 optional integration deps；与本次无关)
```

无新增 / 失败。无 lint 错误。

---

## 给 Codex 的同步要点

1. **Bug E 是"docstring 写了但代码忘做"的典型经验**：以后任何
   `reset_*_on_disconnect` / `clear_*_on_session_end` 类的辅助函数定义
   出来时，**必须同 PR 里完成 wire-up**，不能留作 follow-up。这一类函数
   一旦不被调用就成纯 dead code，下次审计才能发现。本仓库 LineB
   audio guard 也曾踩过同型坑（上一轮 Bug B）。

2. **Bug F 的根因是"in-process 模块状态没有 session boundary 概念"**：
   `_recent_segments`（LineB）、`_last_seq`（EcpState）、`_refs`（RefBinding）
   都是同型问题。本仓库 `_refs` 已经在 `reset_refs_for_session()` 模式
   下处理；`_recent_segments` 在 Round 2 修了；`_last_seq` 这次修。
   建议加一条 cursor rule：
   > **任何在 `parrot/brain/**` 里声明的 module-level mutable
   > state（`_dict` / `_list` / `_set`）必须有显式的 session-end reset
   > 函数，并在 `brain.agent._on_room_disconnected` 里 wire-up。**

3. **Bug F 的 BUG-U2（`boot_id` field in EcpStateDto）仍然 TODO**：
   清空 `_last_seq` 是 cheap workaround；最终方案是 Unity 端在每次
   Publisher 启动时 mint 一个新 `boot_id` 并打进 EcpStateDto，Brain 端
   按 `(unity_identity, boot_id)` 复合键去重。涉及 cs_parity 协议 schema
   变更，留给下一次协议 chat。

4. **真机回归建议**：
   - 启动 Brain → 让 Unity 跑一段（产生 ≥ 5 个 EcpState packets）
   - kill Unity 进程，立刻重启
   - 看 Brain 日志：disconnect 时应出现
     `[ecp_state_ingest] cleared N per-identity sequence dedup entries`
     和 `[ecp_state_ingest] BB session/ecp_state cleared on disconnect (BUG-P4)`
   - 重连后第一个 EcpState packet（≤ 1 s 内）就应该 dispatch 成功，
     `metrics["duplicate_skipped"]` 不增加

---

## 与前两轮的关系

| 轮次 | 焦点 | 修了几个 bug |
|:---|:---|:---|
| Round 1 | `update_instructions` 错位 + env vs BB 优先级 + prompt_target typo + L1.5 bootstrap 时序 | 4（A-D） |
| Round 2 | RoomProfile draft BB JSON + LineB cross-session reset + cosine dim guard + applyRoomProfile fallback warning | 4（A-D） |
| Round 3 (this) | EcpState clear-on-disconnect 死代码 + `_last_seq` 跨 session 残留 | 2（E-F） |

合计 10 个 bug，全部基于代码阅读 + （本轮起）实测验证 → 修复 → 回归测试 →
文档同步。

下一轮如果继续审计，建议入口：
- **DSG triggers / L1.5 admit path** — Phase 4 之后的 L2-B 写入闭环
- **menu RPC 端到端 fuzzing** — 用 hypothesis 喂奇怪 payload，看
  `agent.py::_payload_*` helper 是否都健壮
- **`_state_context.get_state_snapshot` 的 staleness 检测** — 本轮 §C
  里提到的另一道防线
- **`workspace_registry` 的 fallback 链 + IntentWorkspace eviction**
