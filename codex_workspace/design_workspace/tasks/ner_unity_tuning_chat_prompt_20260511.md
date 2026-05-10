# Ner Unity Tuning Chat Prompt

> Date: 2026-05-11
> Use from repo root: `D:\GOSLOParrot\ParrotCarriers`
> Scope: Unity/Ner prefab and device-feel tuning only.

## Prompt

你现在接手 ParrotCarriers 的 Ner Unity 微调场景。请先从
`D:\GOSLOParrot\ParrotCarriers` 作为项目根目录开始，不要从
`D:\GOSLOParrot` 根级旧 workspace 开始。

先阅读这些文件，按顺序建立上下文：

1. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
2. `codex_workspace/design_workspace/tasks/lineb_ner_gameplay_longline_todo_20260511.md`
3. `.cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md`
4. `unity/ArSpike/Assets/Resources/parrot_models/ner_skin2.json`
5. `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerSpineController.cs`
6. `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerCheekPinchInteractor.cs`
7. `unity/ArSpike/Assets/Scripts/ParrotApp/Parrot/NerPickupPlaceInteractor.cs`
8. `tests/test_unity/test_app_v1_meta_ui_static.py`

目标不是重写架构，而是完成 Ner production prefab / 微调验证：

- 创建或验证一个 Ner prefab，包含 Spine skeleton component、
  `ModelDriver(modelId=ner_skin2)`、`NerSpineController`、
  `NerCheekPinchInteractor`、`NerPickupPlaceInteractor`、cheek/body hit
  regions，以及 camera-safe scale。
- 调 cheek collider、body pickup collider、`pickupLiftMeters`、
  `dragPixelsForFullStrength`、长按阈值、释放手感。
- 验证以下 capability 都能从 manifest 到 controller 正常工作：
  `spine_idle`, `spine_walk`, face 系列表情, `touch_idle`, `pat_idle`,
  `tickle_idle`, `cheek_pinch_*`, `body_pickup_start`,
  `body_held_in_air`, `body_dragging_in_air`, `body_place_release`,
  `lineb_speaking`, `lineb_listening`, `lineb_echo_suppressed`。
- LineB 说话或 echo-suppressed 时，新的强交互开始应该被抑制；
  release/cancel/recover 必须允许执行，不能让脸或身体悬空卡死。
- 如果 pickup 被取消、触摸丢失、组件禁用、或 LineB 抑制中断拖拽，
  Ner 必须落回最后 resolved ground point，不能悬在 `pickupLiftMeters`
  的高度。
- prefab 允许 interactor transform 和 `targetRoot` 不同；body hit 和
  placement raycast 都要把这两个 transform 的子 collider 当作同一模型
  处理。
- 不要给 Ner 声称 `fly` / `perch`，也不要把 GOSLO/parrot reserved
  `animate` 词表扩给 Ner。Ner 自定义动作走 `play_capability` /
  strict capability route。
- 不要扩展 manifest capability `kind` 枚举；现有可用值是
  `pose` / `animation` / `procedural`。body pickup/place 当前使用
  `procedural`。

验证要求：

- 用 Unity MCP 检查 Editor console，必要时 `validate_script` 新/改的 C#
  脚本。
- 跑：
  `.\.venv\Scripts\python.exe -m pytest tests\test_unity\test_app_v1_meta_ui_static.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py -q`
- 如果改动影响 LineB/RoomSetting/manifest/facade，再跑当前宽回归：
  `.\.venv\Scripts\python.exe -m pytest tests\test_brain\test_app_first_version_facade.py tests\test_brain\test_app_v1_monitor.py tests\test_brain\test_menu_workspace.py tests\test_brain\test_lineb_model_reaction.py tests\test_brain\test_tools_model_id.py tests\test_shared\test_model_manifest.py tests\test_ecp_event\test_w8_observer_photo.py tests\test_unity\test_app_v1_meta_ui_static.py -q`

当前已知边界：

- Backend/config 层已经能选择 `ner_lineb_room`、`lineb_ner_ja_test`、
  `ner_companion`、`ner_skin2`。
- Unity Editor 已验证 Ner Spine 动画名和 controller 脚本无错误。
- 仍未完成：production prefab 真实挂接、Build Settings App 正式入口、
  启动页 RoomSetting UI、真机 ASR/TTS/echo/voiceprint 验证、UI 页面正式设计。
- `ParrotSmokeScene`、Web monitor、smoke/self-check 报告只能作为测试证据，
  不能作为 App 完成证据。

完成输出：

- 简短列出改了哪些 prefab/script/manifest/test/doc。
- 明确区分 `完成`、`partial`、`未验证`。
- 如果有手感参数，记录推荐值和为什么。
