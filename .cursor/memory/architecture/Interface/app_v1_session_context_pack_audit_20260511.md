# App V1 Session Context Pack — Audit & Fix Report

Date: 2026-05-11
Audit by: Cursor (Opus parent agent), in response to Codex frontend upgrade
`app_v1_session_context_pack_upgrade_20260511.md`.

## TL;DR

Codex 的升级方向正确（RoomProfile.setting_file_refs → LLM 提示 + L1.5 ingest），
但**注入回路的"动态刷新"分支在 livekit-agents 1.5.x 上是失效的**：
`AgentSession` 没有 `update_instructions` 方法，必须经由 `session.current_agent`
拿到 `Agent` 实例并 **`await`** 该协程。Codex 的新代码、以及一直以来的
`mode_watcher` / `context_injector` 都踩了同一个坑。

本次 Cursor 端修复了 4 处：

1. `agent.py::_attach_session_context_watchers` —— 新代码（升级带入）
2. `mode_watcher.py::attach_mode_watcher` —— pre-existing 同型 bug
3. `context_injector.py::_try_update_instructions` —— pre-existing 同型 bug
4. `session_context_pack.py::_active_room_profile_id` —— env vs BB 优先级与
   line_profile 的修复保持一致（RemoteSSH 显式 env 应该胜过陈旧 BB）

另外加了两条小修：

- `_prompt_target` 对未知 frontmatter 值不再"静默吃掉"，统一降级为
  `reference_only` 并打 warning。
- `bootstrap_active_session_context_to_l15` 在 TriggerRunner 还没注册
  trigger 时不再消耗 dedupe set，避免 watcher 路径在 boot 早期的竞态。

68 个相关测试 + 113 个 brain 测试全部 PASS。

---

## 1. 关键 Bug：`update_instructions` 调用错位（severity = high）

### 现象

升级后的 `agent.py::_attach_session_context_watchers` 写法：

```python
updater = getattr(session, "update_instructions", None)
if not callable(updater):
    logger.warning(
        "session_context: AgentSession.update_instructions unavailable (%s)", reason,
    )
    return
updater(get_instructions(_read_mode()))
```

实际运行 livekit-agents `1.5.5`：

```python
>>> from livekit.agents import AgentSession, Agent
>>> hasattr(AgentSession, "update_instructions")
False
>>> hasattr(Agent, "update_instructions")
True
>>> import inspect; inspect.iscoroutinefunction(Agent.update_instructions)
True
```

源码（livekit-agents 1.5.x，简化）：

```python
class Agent:
    async def update_instructions(self, instructions: str) -> None:
        if self._activity is None:
            self._instructions = instructions
            return
        await self._activity.update_instructions(instructions)
```

`AgentSession` 暴露的入口是 `current_agent` (property)，未启动时 raises
`RuntimeError("VoiceAgent isn't running")`。

### 影响范围

| 模块 | 触发路径 | 升级前的实际行为 |
|:---|:---|:---|
| `agent.py::_refresh_instructions`（NEW） | RoomProfile/persona/mode/scene BB 切换 | 静默 `logger.warning` + 零刷新；用户切换 Room 后 LLM 仍在用旧 prompt |
| `mode_watcher._try_update_instructions`（pre-existing） | `set_behavior_mode()` / Pub/Sub 切换 BehaviorMode | 同上；mode 切换不真正落到 LLM |
| `context_injector._try_update_instructions`（pre-existing） | inject_memory / inject_scene / VIDEO_OFF boundary | C2 全量 rebuild 不执行；记忆和 scene 上下文从未热更 |

LineA（Gemini Live RealtimeModel）和 LineB（STT-LLM-TTS）共享这条注入路径，
两边都受影响：

- **LineA**：`Agent.update_instructions` 在 realtime 模式下会同步更新 Gemini
  Live 的 system_instructions（同时 `await activity.update_instructions`），
  没走该路径就意味着 Realtime session 永远只看到 boot 时刻的 prompt。
- **LineB**：`google.LLM` 在每次 LLM 调用时使用 `Agent._instructions` 拼系统
  消息，`Agent._instructions` 不更新就一直是旧的。

### 修复

统一改成：

```python
try:
    agent = session.current_agent
except RuntimeError:
    logger.debug("session not running yet, skipping refresh (%s)", reason)
    return
updater = getattr(agent, "update_instructions", None)
if updater is None:
    logger.warning("Agent.update_instructions unavailable (%s)", reason)
    return
await updater(new_text)
```

`agent.py::_refresh_instructions` 多了一层 sync→async 桥（watcher 是 BB 同步
回调），用 `asyncio.create_task` 异步驱动，不阻塞 BB writer。

`mode_watcher` 把 `_try_update_instructions` 改为 `async def` 直接 `await`。

`context_injector._try_update_instructions` 已经是 `async def`，把
`updater(rebuilt)` 改成 `await updater(rebuilt)` 即可。

### 验证

代码层面已通过 livekit-agents 源码确认：

- `Agent.update_instructions` 是 `async`；
- `AgentSession.current_agent` 是 property，未启动 raises。

测试层面，68 个 session_context_pack / menu / lineb / facade / unity meta UI
测试 + 113 个 brain 测试全部 PASS。运行时回归需要在真机/真房间内验证一次
"切换 RoomProfile → 看 LLM 输出是否变化"。

---

## 2. env vs BB 优先级一致性（severity = medium）

### 现象

升级文档里这一条：

> Bug fixed: `PARROT_ACTIVE_LINE_PROFILE_ID` now overrides stale Blackboard state.

只在 `line_profile.py::active_profile_id` 上落地，**没有同步给同一升级里新增
的 `session_context_pack._active_room_profile_id`**。

修复前：

```python
def _active_room_profile_id() -> str:
    # BB 先 → env 后 → DEFAULT
```

修复后（与 `line_profile.active_profile_id` 一致）：

```python
def _active_room_profile_id() -> str:
    # env 先（PARROT_ACTIVE_ROOM_PROFILE_ID / PARROT_ACTIVE_ROOM_PROFILE）
    # BB 次（global/active_room_profile_id）
    # DEFAULT 兜底
```

### 为什么要改

RemoteSSH 工程化：开发者临时跑 LineB + Ner Room，会同时设置：

```bash
PARROT_LLM_PIPELINE=line_b
PARROT_ACTIVE_LINE_PROFILE_ID=lineb_ner_ja_test
PARROT_ACTIVE_ROOM_PROFILE_ID=ner_lineb_room
```

如果 BB 里残留上一会话的 `default`，原来的 BB-first 就会让 Brain 启动后
继续加载 default RoomProfile 的 setting refs（既不是 ner_companion，也不是
ner_mochi_scene），但 line_profile 已切到 ner_ja_test。两侧错位 → "声音是 Ner
但人格是 GOSLO 默认"。

修复后，env 永远胜出，与 line_profile 同步。

> 说明：`soul.py::_resolve_active_persona_id`（persona）和现在的 room profile
> 不再一致——persona 还是 BB-first / env-fallback。这是有意保留的：persona
> 是会被频繁通过菜单 RPC 切换的"动态"维度，BB 是当前会话状态；line/room 是
> "启动期一次性挂载"维度，env 直觉上应当压过 BB。如果未来 persona 也要
> RemoteSSH 强制覆盖，再统一即可。

---

## 3. 未知 `prompt_target` frontmatter 静默吃掉（severity = low）

### 现象

```python
explicit = meta.get("prompt_target") ...
if explicit:
    return aliases.get(explicit, explicit)   # ← typo 直接透传
```

笔记里写了 `prompt_target: lll_5`（typo）会变成 `prompt_target="lll_5"`，
`"llm" in source.prompt_target` False、`"l1_5" in source.prompt_target` False、
两路都不进，前端也看不到任何告警。

### 修复

未知值统一降级为 `reference_only` 并 `logger.warning(...)` 把可接受的别名
列在日志里。debug 仍然能看到这份笔记被识别，但不会"消失"。

```python
canonical = _PROMPT_TARGET_ALIASES.get(explicit)
if canonical is None:
    logger.warning(
        "session_context_pack: unknown prompt_target=%r in %s; "
        "treating as reference_only (accepted: %s)",
        explicit, path, sorted(_PROMPT_TARGET_ALIASES),
    )
    return "reference_only"
```

---

## 4. L1.5 bootstrap 时序保护（severity = low）

### 现象

`bootstrap_active_session_context_to_l15` 在 watcher 路径下可能在
`_boot_l2b_and_triggers` 完成之前被触发（用户在启动后立刻切 RoomProfile）。
此时 `get_trigger_runner()` 在生产代码里会立即 `register_all_defaults()`，
所以一般有 trigger；但**测试注入的自定义 runner** 可能初始空。

旧代码会在空 runner 上 `fire_event` → `ObsidianIngestTrigger` 没注册 → 事件
被吃掉，**但 dedupe set 已经被加了**。下一次合法调用就再也不会重发同一份
payload。

### 修复

在 fire 前检查 `runner._triggers`，为空时直接 return 0（不污染 dedupe set），
这样下一次（boot 完成后）的 bootstrap 还能正常发出。

---

## 5. 已确认正确的部分（无需改动）

### 5.1 Obsidian "三种 profile + 第三种 UUID-free" 的语义

确认与升级一致：

| profile | 是否需 UUID | 进 LLM prompt | 进 L1.5 |
|:---|:---|:---|:---|
| `ref` | **必须** | 否（normal Obsidian sync 走的另一路径） | 是（绑定既有节点） |
| `daily` | 可省 | 是 | 是 |
| `roleplay` | 可省（**第三种 UUID-free**） | 是 | 是 |

`session_context_pack._prompt_target` 对 `profile in {"roleplay", "daily"}`
返回 `"llm+l1_5"`，UUID-free。`UserTagFilter.process_tag` 也只在
`profile == "ref"` 时强制 UUID。OK。

`note_to_ingest_payload` 里：

```python
if profile == "ref" and not uuid:
    return None
```

这里把"ref 但缺 UUID"的笔记当无效，daily/roleplay 永远不会被 None。
所以 RoomProfile 引用一份 `profile: roleplay` 的 Obsidian 笔记**不需要**
事先在 vault 里注册 UUID，符合升级原意。

### 5.2 LineA / LineB 注入回路（在 update_instructions 修复后）

| 维度 | LineA (Gemini Live) | LineB (STT-LLM-TTS) |
|:---|:---|:---|
| Boot 注入 | `ParrotAssistant(instructions=get_instructions())` → RealtimeModel system_instructions | `ParrotAssistant(...)` → google.LLM 系统消息 |
| 动态刷新 | `await session.current_agent.update_instructions(...)` 内部会 `await activity.update_instructions(...)` 同步给 Realtime session | 同上；`Agent._instructions` 改后下一轮 google.LLM 调用立即生效 |
| Room context 来源 | `soul.get_instructions()` 内部 append `session_context_pack` 的 `llm_prompt_block` | 同左 |
| L1.5 来源 | `bootstrap_active_session_context_to_l15` → `ObsidianIngestTrigger.on_event` | 同左（pipeline-agnostic） |

修复 `update_instructions` 之后，两条 Line 的注入与刷新回路都通了。

### 5.3 RoomProfile.setting_file_refs 的"四类"分流

`_prompt_target` 用 frontmatter + 路径线索做四分类，已覆盖：

- `personas/` 下或带 `persona_id` → `persona_loader_only`（不走 prompt，不走 L1.5）
- `.cursor/` 下 → `reference_only`（仅审计/报告，不进 prompt 不进 L1.5）
- `profile=daily|roleplay` → `llm+l1_5`
- 其余 `.md` → `llm`
- `prompt_target` frontmatter 显式覆盖（修复后未知值降级为 `reference_only`）

`ner_lineb_room.json` 当前 4 条 setting_file_refs：

| ref | 分类 | 实际行为 |
|:---|:---|:---|
| `src/parrot/brain/personas/ner_companion.md` | persona_loader_only | 由 PersonaLoader 单独走 |
| `codex_workspace/.../ner_roleplay_setting_obsidian_v0_20260511.md` | llm+l1_5 | 进 system prompt + ObsidianIngestTrigger |
| `codex_workspace/.../ner_mochi_scene_v0_20260511.md` | llm | 仅进 system prompt |
| `.cursor/.../app_v1_lineb_ner_realdevice_config_report_20260511.md` | reference_only | 不污染 prompt（避免角色变成"在背状态报告"） |

OK，符合升级文档预期。

---

## 6. 仍然存在但本次不动的事项（建议 Codex 后续处理）

### 6.1 SystemInstructions 长度（性能 / token 上限）

Persona 文本通常几 KB，加上 `max_chars=9000` 的 Room context block，再加上
`context_injector` 的 memory + scene block，整体可能逼近 Gemini Live 的
system_instructions 软上限。建议：

- Persona + Room context 在 `_build_llm_prompt` 里分别测算长度，超阈值打 warning；
- 或者把 `max_chars` 提为 RoomProfile metadata 的可配字段，留给前端。

### 6.2 watcher 时序

- `_attach_session_context_watchers` 当前在 `_attach_menu_rpc` 之后挂载。
  理论上存在"用户在两者之间发起 applyRoomProfile RPC"的极小窗口。
  实际生产链路里 Unity 不会这么快，但建议把所有 BB watcher 在 RPC 注册
  **之前**统一挂载，彻底排除竞态。
- `bootstrap_active_session_context_to_l15` 现在加了 trigger 列表为空时
  defer 的保护，但更彻底的方案是把 `_attach_session_context_watchers` 的
  L1.5 schedule 推迟到 `_boot_l2b_and_triggers` 完成（用 `asyncio.Event`）。

### 6.3 `update_instructions` 全仓回归

本次只修了 `agent.py / mode_watcher.py / context_injector.py` 三处。日后任何
调用 `session.update_instructions` / `session.update_chat_ctx` 的新代码都应当
直接走 `session.current_agent.<method>`。建议在 `architecture/Interface/` 加一
条短规则：

> "LiveKit Agents 1.5+ 中 `update_instructions` 与 `update_chat_ctx` 都在
> `Agent` 上，`AgentSession` 上不存在。永远使用
> `session.current_agent.<method>` 并 `await`。"

### 6.4 setting_file_refs 安全

`_resolve_ref` 接受任何路径（绝对路径、`..`）。RoomProfile JSON 当前是受信
来源，OK；但若未来支持用户上传 RoomProfile，需要加路径白名单。

---

## 7. 文件改动清单

| 文件 | 改动 |
|:---|:---|
| `src/parrot/brain/agent.py` | `_attach_session_context_watchers._refresh_instructions` 改为 `current_agent.update_instructions` + `await` + sync→async 桥 |
| `src/parrot/brain/mode_watcher.py` | `_try_update_instructions` 改 async + `current_agent` 路径；docstring 同步 |
| `src/parrot/brain/context_injector.py` | `_try_update_instructions` 改用 `current_agent.update_instructions` + `await` |
| `src/parrot/brain/session_context_pack.py` | `_active_room_profile_id` env→BB；`_prompt_target` 未知值告警 + `reference_only`；`bootstrap_active_session_context_to_l15` 加 0-trigger defer |
| `.cursor/memory/architecture/Interface/app_v1_session_context_pack_audit_20260511.md` | 本报告（NEW） |

无 Unity 端改动。无 `data/presets/*.json` 改动。无新增 Python 依赖。

---

## 8. 测试

```
.\.venv\Scripts\python.exe -m pytest tests/test_brain/test_session_context_pack.py
  tests/test_brain/test_menu_workspace.py
  tests/test_brain/test_app_first_version_facade.py
  tests/test_brain/test_lineb_voiceprint.py
  tests/test_brain/test_lineb_model_reaction.py
  tests/test_unity/test_app_v1_meta_ui_static.py -q
→ 68 passed

.\.venv\Scripts\python.exe -m pytest tests/test_brain -q
→ 113 passed
```

无新增/失败用例。建议下次 LineB 真机 smoke 时主动验证：

1. 先以 `default` Room 启动，看 console；
2. 通过菜单切到 `ner_lineb_room`；
3. 观察日志出现 `session_context: refreshed instructions (global/active_room_profile_id)`
   而不是 `... unavailable`；
4. 让 Ner 回复一句包含 setting_source 内特征词（"World Tree" / "高司祭" / "もちもちほっぺ"）
   的话——若包含则证明动态刷新到了 LLM。

---

## 9. 与升级文档的关系

升级文档（`app_v1_session_context_pack_upgrade_20260511.md`）里的
"Audit / Bugfix Pass" 三条仍然准确：

- L1.5 bootstrap dedupe 加 file_mtime ✅
- `.cursor` reference_only ✅
- `PARROT_ACTIVE_LINE_PROFILE_ID` 覆盖 BB ✅

**本报告补充第四类 bug（`update_instructions` 错位）和第五类一致性
（room env 覆盖 BB）。** 建议升级文档下一次修订时把"Audit / Bugfix Pass"
扩为 5 条，并在末尾标注这份审计的存在。
