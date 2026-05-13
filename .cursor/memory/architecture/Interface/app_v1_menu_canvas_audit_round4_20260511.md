# App V1 Menu Canvas + Startup Audit (Round 4)

Date: 2026-05-11
Audit by: Cursor (Opus parent agent), continuation of Rounds 1-3.

> **Methodology**: 与 Round 3 一致——每个 bug 必须**实测验证**才能落地。
> 本轮 4 个 verified bug 全部有 repro 脚本输出，1 个 design gap 单独标记。

## TL;DR

围绕"画布菜单 + 启动页"路径深审：

1. 启动页期望 6 个 RPC（`getRoomSettingSnapshot` / `previewRoomProfile` /
   `newRoomProfile` / `saveRoomProfile` / `applyRoomProfile` /
   `setAppCapabilityMode`）— 全部存在
2. 菜单画布期望 5 核心块（Model / Persona / Mode / Scene / 2DWorkspace）+
   外部模块 dock 5 项（Google / Obsidian / GOSLO Module / Nanobot / Photo）
   — `MenuRegistry` + `AppFirstVersionFacade.list_module_statuses`(8 项，含 3
   个超集模块) 全部就位
3. **后端就绪，Unity 端尚未对接**：`AppStartupFlowController` 当前只调用
   `setAppCapabilityMode` + `applyWorkspace` 两个 RPC，剩下 14 个 RPC 还没
   wire。这是"frontend pending"，不算 bug

但审计在已经存在的 backend RPC 路径上**实测发现 4 个 verified bug + 1 个
design gap**，全部已修：

| ID | 严重度 | 类型 | 一句话 |
|:---|:---|:---|:---|
| G | HIGH | 数据破坏 | `saveRoomProfile` 可以覆盖 builtin `default` preset |
| H | LOW | 静默失败 | `previewRoomProfile`/`saveRoomProfile` 缺 Round 2 Bug D 同款 payload typo 警告 |
| I | MEDIUM | 状态错位 | `applyMenuSelection` 静默替换 invalid workspace_id，调用方拿到 `success=True` 但实际 workspace 不是请求的那个 |
| J | LOW | 静默失败 | `setAppCapabilityMode` 未知 mode 静默回退 FullARCompanion |
| K | LOW (gap) | 接口不对称 | `setPhotoAwareness`/`setCameraMode`/`setXrHandMode` 只有 HTTP 没有 LiveKit RPC，菜单画布的 GOSLO Module 抽屉没法走 in-band 通道 |

352 个测试全部通过（含 6 个 Round 4 新增回归）。0 lint 错误。

---

## 1. 启动页 + 菜单画布 现状盘点

### 1.1 启动页设计期望（codex_workspace `startup_menu_design_v0_20260509.md`）

| 区域 | 元素 | 后端 RPC | 实现状态 |
|:---|:---|:---|:---|
| 中央 | GOSLO Parrot 标题 + 2D model 形象位 | — | UI-only |
| 左下 | 小基础菜单 / settings | `setAppCapabilityMode`（部分 cover）| ✅ 后端有 |
| 左侧 | `SCENE` → 进入 RoomSetting | `getRoomSettingSnapshot` / `newRoomProfile` / `previewRoomProfile` / `saveRoomProfile` | ✅ 后端有 |
| 右侧 | `START` 主按钮 + Mode 拉杆 | `applyRoomProfile(experience_mode=...)` | ✅ 后端有 |
| 右上 | EXIT | — | UI-only |

**结论**：启动页所需的全部后端 RPC（6 个）都在 `agent.py::_attach_menu_rpc`
里挂载好了，只等 Unity 端 `AppStartupFlowController` 接入。

### 1.2 菜单画布期望（codex_workspace `menu_canvas_external_modules_20260509.md`）

| 模块 | 后端接口 | 实现状态 |
|:---|:---|:---|
| **5 核心块** | | |
| Model | `MenuRegistry.list_blocks().models` | ✅ |
| Persona | `MenuRegistry.list_blocks().personas` | ✅ |
| Mode | `MenuRegistry.list_blocks().modes`（BehaviorMode 6 项）| ✅ |
| Scene | `MenuRegistry.list_blocks().scenes`（SceneType enum）| ✅ |
| 2DWorkspace | `MenuRegistry.list_blocks().workspaces` | ✅ |
| Apply 选择 | `applyMenuSelection` LiveKit RPC | ✅ |
| **外部模块 Dock** | `AppFirstVersionFacade.list_module_statuses()` 8 项（design 5 + 3 超集）| |
| Google Calendar | `module_status(GOOGLE_CALENDAR)` | ✅ |
| Obsidian | `module_status(OBSIDIAN)` | ✅ |
| GOSLO Module | `module_status(GOSLO_MODULE)` + `set_photo_awareness` | ⚠️ HTTP 有 / RPC 缺（Gap K） |
| Nanobot | `module_status(NANOBOT)` + `stage_nanobot_report` | ✅（HTTP / Python facade）|
| Photo / Awareness | `module_status(PHOTO_CAMERA)` + `set_camera_mode` | ⚠️ HTTP 有 / RPC 缺（Gap K） |
| **超集** | VOICE_PIPELINE / XR_HAND / CANVAS_CONNECTION（design 没写，code 加了）| 设计扩展 |

**结论**：核心 5 块完整、Dock 5 项功能上完整，但 GOSLO Module 抽屉的核心
toggles（Photo Awareness / 相机模式 / XRHand 模式）只暴露了 HTTP，没有
LiveKit RPC，菜单画布走 in-band 通道时缺乏对称性 → **Gap K**。

### 1.3 Unity 端实际接入情况

`AppStartupFlowController.cs` 当前调用的 RPC：

```csharp
// 真实代码（unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Lifecycle/AppStartupFlowController.cs）
"setAppCapabilityMode" → ✅
"applyWorkspace"       → ✅
// 其余 14 个 menu/RoomSetting RPC 全部未接入
```

`onSceneReady` / `onGosloPlaced` / `setScene` 等是另一组 RPC（已接入）。

**结论**：后端 RPC 表面完整，Unity 启动页 + 菜单画布 UI 还是 placeholder
状态。这不是 bug，是 frontend pending。

---

## 2. Bug G — `saveRoomProfile` 可覆盖 builtin `default` preset（HIGH）

### 验证

```python
$ python -c "
from parrot.brain.preset_loader import PresetLoader, RoomProfile
import tempfile, pathlib, json
tmp = pathlib.Path(tempfile.mkdtemp())
seed = tmp / 'default.json'
seed.write_text(json.dumps({'preset_id':'default','active_model_id':'GOSLO_default','metadata':{'note':'real default'}}))
loader = PresetLoader(search_paths=[tmp])
print('Before:', json.loads(seed.read_text())['active_model_id'])
hijack = RoomProfile(room_profile_id='default', display_name='Hijacked', model_id='evil_model')
loader.save_room_profile(hijack)
print('After :', json.loads(seed.read_text())['model_id'])
"

Before: GOSLO_default
After : evil_model
VERIFIED: 系统 default preset 在没有任何 guard 的情况下被覆盖
```

### 后果

- 任何调用方（菜单 RPC / 直接 facade / 测试 fixture）传 `room_profile_id="default"`
  的 RoomProfile draft 都会重写 `data/presets/default.json`
- 同样的问题也针对 `ephemeral` / `workspace_only` 这两个 menu_registry /
  preset_loader 内部用的 sentinel id
- 真实场景：用户在 RoomSetting UI 里 "save as default room"，UI 把
  display_name="Default" 误用作 id → 覆盖系统默认

### 修复

`preset_loader.py` 新增 `RESERVED_ROOM_PROFILE_IDS = {"default", "ephemeral",
"workspace_only"}` + `ReservedRoomProfileIdError` typed exception。
`save_room_profile` 在写盘前检查，触发就 raise。

`room_setting.py::RoomSettingService.save` 翻译这个 exception 成结构化
error response（`status="error" / reason="reserved_room_profile_id" /
reserved_ids=[...]`）。

`agent.py::saveRoomProfile` RPC 把 facade 返回的 `status="error"` 镜像到
RPC 响应顶层，让 Unity 看到失败。

---

## 3. Bug H — `previewRoomProfile` / `saveRoomProfile` payload typo 静默问题（LOW）

### 现象

Round 2 Bug D 已经修了 `applyRoomProfile`，但同样的"`payload.get("room_profile") || payload`"模式还在 `previewRoomProfile` 和 `saveRoomProfile` 里：

```python
# applyRoomProfile（Round 2 已加 warning）
if room_profile is None and not room_profile_id:
    logger.warning("applyRoomProfile: payload missing both ...")

# previewRoomProfile / saveRoomProfile（Round 4 之前没 warning）
draft = payload.get("room_profile") if isinstance(...) else payload  # 静默 fallback
```

### 后果

Unity 拼写错（`roomProfile` camelCase / `room_profile_data` 等）会让 preview
看起来 plausible 但实际是 default-filled empty profile，掩盖前端 bug。同样
saveRoomProfile 会保存到非预期的 id。

### 修复

两个 RPC 加上 Round 2 Bug D 同款 `logger.warning(... payload_keys=...)`
诊断行。

---

## 4. Bug I — `applyMenuSelection` 静默替换 invalid workspace_id（MEDIUM）

### 验证

```python
$ python -c "
import py_trees
py_trees.blackboard.Blackboard.storage = {}
py_trees.blackboard.Blackboard.metadata = {}
from parrot.brain.menu_registry import MenuRegistry, MenuSelection

reg = MenuRegistry()
sel = MenuSelection(
    persona_id='goslo_parrot_default',
    mode_flags=('BASE',),
    scene_id='ar_handheld',
    model_id='GOSLO_default',
    workspace_id='nonexistent_xyz',  # ← 故意写错
)
result = reg.apply_selection(sel)
print('success      :', result.success)
print('errors       :', result.errors)

bb = py_trees.blackboard.Client(name='check', namespace='/')
bb.register_key('global/active_workspace_id', access=py_trees.common.Access.READ)
print('actual stored:', bb.get('global/active_workspace_id'))
"

success      : True
errors       : ()
actual stored: mansion_hub
VERIFIED: 请求 nonexistent_xyz, 静默替换为 mansion_hub, success=True 没有任何 warning
```

### 后果

菜单画布 UI 拿到 `success=True` 后会高亮显示用户原本请求的
"nonexistent_xyz"，但实际后端写到 BB 的是 `mansion_hub`。下一次 `listMenuBlocks`
返回 `active_workspace_id="mansion_hub"`，UI 状态和用户操作错位 → 用户体验
为"切了但没切"。

### 修复

- `PresetApplyResult` 新增 `warnings: tuple[str, ...] = ()` 字段（additive，
  向后兼容）
- `MenuRegistry.apply_selection` 在做 fallback 时把
  `"workspace_id='X' not registered; substituted to fallback 'mansion_hub'"`
  写进 warnings
- 调用方（Unity 菜单画布）可以读 `result.warnings` 显示 toast 或重新同步状态

---

## 5. Bug J — `setAppCapabilityMode` 未知 mode 静默回退（LOW）

### 验证

```python
$ python -c "
from parrot.brain.session_policy import apply_capability_mode
profile = apply_capability_mode('totally_bogus_mode')
print('mode resolved to:', profile.mode.value)
"

mode resolved to: FullARCompanion
VERIFIED: setAppCapabilityMode 任意未知字符串都静默成 FullARCompanion
```

### 后果

启动页 / 菜单画布如果误传 "voice_only" 而后端 enum 实际是 "VoiceOnlyNoVideo"
（写法漂移），后端就会静默用最 permissive 的 FullARCompanion，掩盖 UX
配置错误，可能误启用相机 / 麦克风。

### 修复

`session_policy.parse_capability_mode` 在 `text` 非空但匹配失败时打
`logger.warning(... accepted=...)`。空 / None 输入是合法的"无偏好"情况，
保持安静不污染日志。

---

## 6. Gap K — Photo Awareness / Camera Mode / XRHand Mode 缺 LiveKit RPC 镜像（LOW）

### 现象

设计文档（`menu_canvas_external_modules_20260509.md` §6 GOSLO Module）：

> Photo Awareness / Voice input / Camera mode / Greeting … 这些开关要通过
> backend-owned RPC 写入，不能让 Unity 直接写 Blackboard。

实际：

| 控制 | HTTP（`app_monitor_server.py`）| LiveKit RPC |
|:---|:---|:---|
| `setLineBAudioRoutePolicy` | ✅ | ✅ |
| `setAppCapabilityMode` | ✅ | ✅ |
| `set_photo_awareness` | ✅ `/api/app/awareness` | ❌ |
| `set_camera_mode` | ✅ `/api/app/camera/mode` | ❌ |
| `set_xrhand_mode` | ❌ | ❌ |

HTTP 是 Web 监控面，LiveKit RPC 是 Unity 在房间内的 in-band 通道。Unity
（按现有 `AppStartupFlowController.cs` 模式）只用 LiveKit RPC，HTTP 通道仅
token mint 用过。

### 修复（不是 bug 是补口）

`agent.py::_attach_menu_rpc` 新增 3 个 RPC handler：

```python
@room.local_participant.register_rpc_method("setPhotoAwareness")
@room.local_participant.register_rpc_method("setCameraMode")
@room.local_participant.register_rpc_method("setXrHandMode")
```

每个都：
- 校验必需字段（`policy` / `mode`），缺就返回 `status="error"`
- 调 `AppFirstVersionFacade` 对应 setter
- 捕获 `ValueError`（无效 enum）返回结构化错误
- 成功返回完整 BB write 结果

---

## 7. 已确认正确（无需改动）

### MenuRegistry 数据完整性
- `list_blocks()` 5 块都有真实数据源（PersonaLoader / ModelManifestRegistry /
  WorkspaceRegistry / SceneType / 静态 BehaviorMode 描述符）
- `MenuRegistry` 不直接写 BB，所有 apply 都路由到 `PresetLoader.apply` 维持
  单写者契约

### RoomSetting 五维 capability resolver
- 在 Round 2 已审过 `RoomSettingService.compatibility` 的 5 维（model /
  scene / workspace / line / line_profile / experience_mode）
- 都有 `enabled / degraded / blocked / disabled` 状态分级
- `apply` 在 `state == "blocked"` 时不写 BB 直接返回

### 启动页 6 个 RPC handler
- `getRoomSettingSnapshot` / `previewRoomProfile` / `newRoomProfile` /
  `saveRoomProfile` / `applyRoomProfile` / `setAppCapabilityMode` 完整
- 加上本轮 G/H/I/J/K 修复后，所有错误路径都有结构化响应

### `app_first_version.list_module_statuses` 8 项
- 5 项与设计 dock 对齐
- 3 项扩展（VOICE_PIPELINE / XR_HAND / CANVAS_CONNECTION）合理

### `applyPreset` 只写 5 axes（不写 line/skin/...）
- 这是 v2 legacy `Preset` 的设计意图（`apply_room_profile` 才是 v3 路径）
- 不是 bug

---

## 8. 改动清单

| 文件 | 改动 |
|:---|:---|
| `src/parrot/brain/preset_loader.py` | Bug G：`RESERVED_ROOM_PROFILE_IDS` + `ReservedRoomProfileIdError`；`save_room_profile` 加 guard。Bug I：`PresetApplyResult.warnings` 字段，`_apply_values` 接收 warnings |
| `src/parrot/brain/menu_registry.py` | Bug I：`apply_selection` 把 workspace fallback 写进 warnings |
| `src/parrot/brain/room_setting.py` | Bug G：`save` 翻译 `ReservedRoomProfileIdError` 成结构化 error response |
| `src/parrot/brain/session_policy.py` | Bug J：`parse_capability_mode` 在非空未知输入时 warning |
| `src/parrot/brain/agent.py` | Bug G：`saveRoomProfile` RPC 镜像 facade 的 status；Bug H：`previewRoomProfile`/`saveRoomProfile` 加 payload warning；Gap K：3 个新 RPC（`setPhotoAwareness` / `setCameraMode` / `setXrHandMode`） |
| `tests/test_brain/test_menu_workspace.py` | 6 个 Round 4 回归（`TestAuditRound4MenuCanvasGuards` 类） |
| `.cursor/memory/architecture/Interface/app_v1_menu_canvas_audit_round4_20260511.md` | 本报告（NEW） |

无 Unity 端改动。无新依赖。无 cs_parity 协议变更（PresetApplyResult 加字段
是 additive，不破坏向后兼容）。

---

## 9. 测试

```
.\.venv\Scripts\python.exe -m pytest tests/test_brain/test_menu_workspace.py -v -k AuditRound4
→ 6 passed (Round 4 新增的全部 6 个回归)

.\.venv\Scripts\python.exe -m pytest tests/test_brain tests/test_ecp_event tests/test_unity tests/test_shared -q
→ 352 passed (= Round 3 的 346 + 6 个新增)

.\.venv\Scripts\python.exe -m pytest tests -q
→ 551 passed, 1 failed, 4 skipped
```

无 lint 错误。

### 9.1 全仓 1 个 pre-existing failure（不是 Round 4 引入）

```
FAILED tests/test_brain/test_menu_workspace.py::test_repo_ner_line_profile_and_room_setting_are_selectable
  E   AssertionError: assert '' == 'ja-JP-Neural2-B'
```

**根因**：`data/line_profiles/lineb_ner_ja_test.json` 在 Round 4 之前（由
Codex 进行中的 Cartesia 语音迁移）从 `google.TTS` + `voice_name="ja-JP-Neural2-B"`
改成了 `cartesia.TTS` + `voice_name=""`，但相应的 test 没同步更新。

**验证**：`git stash`（移除我所有改动）→ 同一 test PASSES。所以与
Round 4 无关。

**处理**：本轮**不动**。这是 Codex Cartesia 工作的 in-flight 状态；
正确的修法应当由 Cartesia 迁移负责方完成（更新 JSON 或更新 test 断言）。
我不会改 Codex 的 voice_profile JSON 或 cartesia upload 脚本。

如果 Codex 想完成迁移：
- 选项 A：回滚 JSON 到 google.TTS baseline（保 test 兼容）
- 选项 B：更新 test 断言为 `provider == "cartesia.TTS"` 等 Cartesia 期望值
- 选项 C：改 test 用更松散的断言同时支持两套 provider

我倾向选项 B（test 跟踪 Codex 的实际意图）。

---

## 10. 给 Codex 的核心同步要点

1. **`saveRoomProfile` 现在会拒绝 `default` / `ephemeral` / `workspace_only`
   三个 reserved id**。RoomSetting UI 必须识别返回的
   `status="error" / reason="reserved_room_profile_id"` 并提示用户改名。
   常量 `RESERVED_ROOM_PROFILE_IDS` 已 export。

2. **`applyMenuSelection` 现在通过 `PresetApplyResult.warnings` 报告
   workspace 替换**。Unity 菜单画布读 `result.warnings`，非空就显示 toast
   或重新同步 active_workspace_id。

3. **`setAppCapabilityMode` 未知 mode 仍然静默 fallback 到 FullARCompanion**
   （为了向后兼容），但现在打 warning。Unity 应当只发送 enum 已知值；操作员
   `grep "unknown capability mode"` 可以反查 Unity 拼写错误。

4. **新增 3 个 LiveKit RPC**：`setPhotoAwareness` / `setCameraMode` /
   `setXrHandMode`。菜单画布 GOSLO Module 抽屉应当用这些，不要再调 HTTP
   `/api/app/awareness` 等。Web monitor 仍然用 HTTP（不改）。

5. **启动页 + 菜单画布的全部后端 RPC 已就绪**，Unity 端只需要把
   `AppStartupFlowController` / 未来的 `MenuCanvasController` 接到这 17 个
   RPC（11 个 Round 4 之前 + 3 个 Gap K + 3 个原有 LineB）即可。

---

## 11. 与前三轮的关系

| 轮次 | 焦点 | 修了几个 |
|:---|:---|:---|
| Round 1 | LLM 注入通道 + RoomProfile env/BB | 4 |
| Round 2 | RoomProfile draft + LineB session reset + voiceprint dim | 4 |
| Round 3 | ECP state ingest disconnect 死代码 + cross-session carry-over | 2 |
| **Round 4** | **菜单画布 + 启动页 RPC（reserved id / silent fallback / payload warning / RPC mirror）** | **4 + 1 gap** |
| **合计** | | **14 + 1** |

下一轮可继续：
- DSG triggers / L1.5 admit path（仍未审）
- `_state_context.get_state_snapshot` staleness 检测（Round 3 §C 提到）
- menu RPC payload fuzzing（hypothesis）
- 真机 smoke 验证 Round 4 修复在 Unity 侧的可见性

