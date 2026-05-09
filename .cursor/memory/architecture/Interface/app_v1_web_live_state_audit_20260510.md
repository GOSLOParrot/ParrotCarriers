---
status: active
category: audit
date: 2026-05-10
owner: Codex / App V1
scope: Web console live visualization, Blackboard, IntentWorkspace, RefBinding, L2-B, tool-flow audit
code:
  - src/parrot/brain/app_live_state.py
  - src/parrot/brain/app_monitor_server.py
tests:
  - tests/test_brain/test_app_v1_monitor.py
---

# App V1 Web Live State 审计记录

## 0. 本轮目标

本轮目标不是只做接口 smoke，而是让测试 Web 控制台在工具流程中实时看到状态落点：

- Blackboard: 轻量状态和单写者 key。
- IntentWorkspace: 照片 preview、Nanobot 报告、Calendar draft 等 staged ref。
- RefBinding registry: Focus / BoundaryBox 会话级锚点。
- L2-B: PhotoNode 等语义图节点。

最终验收口径：用户点击 Web 控制台里的 Camera / Focus / BBox / Nanobot 测试动作后，Live State 页可以直观看到 BB / IW / REF / L2B 哪些表面发生变化，并显示每个工具的预期数据流和场景覆盖。

## 1. 启动前 Cursor 文档审计

本轮开始前查询了 `.cursor/memory`，重点对照：

- `.cursor/memory/lore/ideas.md`: 复杂管理功能归 Web 控制台，移动端 App 保持轻量。
- `.cursor/memory/architecture/ar_app_flow_ui_design.md`: AR 前端和工具交互体验。
- `.cursor/memory/architecture/protocol_snapshot_p4.md`: `photo.taken_preview`、`focus.anchored/released`、`bbox.placed/removed` 等协议名。
- `.cursor/memory/architecture/Interface/concept_dictionary_20260507.md`: Blackboard / IntentWorkspace / L2-B / 2DWorkspace 概念边界。
- `.cursor/memory/architecture/Interface/photo_memory_awareness_true_connection_guide_20260509.md`: PhotoNode、Awareness、IntentWorkspace staged ref 边界。
- `.cursor/memory/architecture/Interface/app_v1_facade_core_business_interface_20260510.md`: App facade、Web monitor、Graphiti dry-run、L2-B read-only 边界。
- `.cursor/memory/architecture/Interface/app_v1_tool_dataflow_interface_20260510.md`: Camera / Focus / BBox / XRHand / Workdesk / Nanobot 数据流。

审计结论：Web 控制台可以补 live visualization，但不能绕过 facade、EcpEvent observer、IntentWorkspace stage、L2-B snapshot 等现有边界直接写内部结构。

## 2. 实现结果

新增 `src/parrot/brain/app_live_state.py`：

- `build_app_live_state(l2b_limit=80)`: 聚合 Blackboard、IntentWorkspace、RefBinding registry、L2-B snapshot。
- Blackboard 输出 declared key、scope、writer、type_hint、event_driven、exists、value、summary。
- IntentWorkspace 输出 ref_id、kind、origin、role、workspace_id、photo_id、expires、pressure。
- RefBinding 输出 Focus / BBox 当前会话锚点和 resolved L2-B target。
- L2-B 输出 bounded nodes / edges、kind count、top attention。
- Tool Artifacts 输出每个工具在 `blackboard / intent_workspace / ref_registry / l2b` 的 present 状态。

新增 Web endpoint：

- `GET /api/app/live-state?limit=80`

Web 控制台新增 Live State 页：

- Live Poll: 自动轮询，显示 BB keys、Intent refs、RefBindings、L2-B nodes。
- Tool Artifacts: 每个工具显示 BB / IW / REF / L2B 四个状态标记。
- Blackboard Live: key、writer、present、summary、value，变更高亮。
- IntentWorkspace Live: staged refs、role、origin、workspace、node/photo、expires。
- L2-B Live Graph: 轻量 SVG 图视图，不引入新的图写入依赖。
- RefBinding Registry: Focus / BBox ref 生命周期可视化。
- Live JSON: 完整调试 payload。

## 3. Bug 审计与修复

浏览器实测发现一个真实 bug：

- 现象：Tool Flow 按钮点击后浏览器报 `TypeError: value is not a function`。
- 原因：内联 `onclick` 作用域中，函数名 `value(...)` 被按钮元素自身 `value` 属性遮蔽。
- 修复：改名为 `fieldValue(...)`，并在 `tests/test_brain/test_app_v1_monitor.py` 增加静态回归断言，避免重新引入 `value('cameraMode')` 这类调用。

## 4. 工具流程审计

| 工具 | Blackboard | IntentWorkspace | RefBinding | L2-B | 审计结论 |
|:--|:--|:--|:--|:--|:--|
| Camera / Photo Awareness | `session/camera_mode`、`session/photo_capture_request`、`transient/last_photo_event`、`transient/photo_awareness_notice` | Awareness enabled 时产生 `photo_preview_awareness` PHOTO ref | 不使用 | preview 创建 PHOTO node | 符合需求；Python 不假装拥有相机像素；复用 PhotoController / observer.photo / photo_awareness |
| Magnifier Focus | 可能更新 `transient/current_attention_hint` | 不使用 | `focus` ref | 仅 resolved ref 才影响 L2-B | 符合架构；Unity 负责拖动和选中态；Brain 只接 `focus.anchored/released` |
| BoundaryBox | 可能更新 `transient/current_attention_hint` | 不使用 | `bbox` ref | 仅 resolved ref 才影响 L2-B | 符合架构；Unity 负责框、resize、关闭；Brain 不做 UI 几何 |
| 2D Workdesk / Paper Notes | `global/active_workspace_id` | `nanobot_report`、`calendar_draft` | 不使用 | 默认不写 | 符合 2DWorkspace / IntentWorkspace 分层；纸条只拿 ref，不拥有 payload |
| XRHand / Perch | `session/xrhand_mode`、`transient/hand_gesture` | 不使用 | 不使用 | 不写 | 符合 local reflex / command / event 三分法；手势不切 Scene |
| Settings / Awareness | session policy keys | 不直接写 payload | 不使用 | 不写 | 符合 backend-owned policy key 规则 |

## 5. 场景覆盖

已覆盖的 Web 控制台场景：

- Camera capture request: `session/camera_mode=capture_locked`，`session/photo_capture_request` 出现。
- Photo preview: `transient/last_photo_event` 出现，L2-B 出现 `photo:ph_web_console` PHOTO node。
- Awareness silent: `transient/photo_awareness_notice` 出现，IntentWorkspace 出现 `photo_preview_awareness` ref，`allow_interrupt=false`。
- Focus anchor: RefBinding registry 出现 `focus_refs=1`。
- BBox place: RefBinding registry 出现 `bbox_refs=1`。
- Nanobot note: IntentWorkspace 出现 `nanobot_report` ref。

浏览器实测结果：

```text
BB: 8/40 present
IntentWorkspace refs: 2
RefBindings: total=2, bbox_refs=1, focus_refs=1
L2-B nodes: 1
camera.blackboard: true
camera.intent_workspace: true
camera.l2b: true
magnifier_focus.ref_registry: true
boundary_box.ref_registry: true
workdesk_notes.intent_workspace: true
```

## 6. 是否重复造轮子

没有新造业务管线：

- Blackboard 读取复用 `open_bb_client` 和 `BB_KEYS` manifest。
- IntentWorkspace 读取复用 `get_intent_workspace().list_active()` 和 pressure report。
- RefBinding 读取复用 `refs_registry.all_refs()` / `metrics_snapshot()`。
- L2-B 读取复用 `build_l2b_snapshot()`。
- 工具动作仍然走 `AppFirstVersionFacade` 或 `app_test_harness` 的 EcpEvent observer 路径。
- 图视图第一版只做轻量 SVG read model 渲染，没有引入新写入口或绕过 rustworkx / L2-B。

## 7. 验证

已运行：

```text
uv run ruff check src/parrot/brain/app_live_state.py src/parrot/brain/app_monitor_server.py tests/test_brain/test_app_v1_monitor.py
All checks passed

uv run pytest tests/test_brain/test_app_v1_monitor.py -q
4 passed
```

浏览器验证：

- 打开 `http://127.0.0.1:7892/`。
- 进入 Tool Flow。
- 点击 `Request Capture`、`Sim Preview`、`Anchor Focus`、`Place BBox`、`Nanobot Note`。
- 回到 Live State，确认 BB / IW / REF / L2-B 状态均可见。

## 8. 剩余问题

- Graphiti 管理仍保持 status/search/draft/dry-run write，真实写入必须显式 dry_run=false；本轮没有把 Graphiti 变成工具流程写入口。
- L2-B 图视图是轻量 SVG，可验收但不是最终图谱管理器。若未来要做完整图谱交互，应独立选择 Cytoscape / D3 / rustworkx export + layout 方案。
- Unity AR 前端仍需要下一轮继续完善视觉细节和真机交互手感，尤其是工具柜材质、Focus 倍率设置、BBox 控制点和 Nanobot 纸条动效。

## 9. App 前端补充审计

Web 控制台通过后，复查 Unity `AppV1MetaUiController`，发现相机工具虽然已经在工具柜中，但只有 `Camera` / `Capture` 按钮和纸条反馈，缺少进入相机模式后的明确可见状态。已补：

- `CameraModeOverlay_Modern`: 现代相机模式 overlay。
- `CameraPreviewFrame`: 深色取景框和 rule-of-thirds grid。
- `CameraModeLabel`: 显示当前 `off / preview / photo_ready / capture_locked` 和本地 shots 计数。
- `CameraModeShutterButton`: overlay 内 capture 按钮，仍然只调用 `PhotoController.CapturePhoto()`。

审计结论：相机前端现在能从工具柜进入 preview 面板，也能在 overlay 内触发 capture。UI 仍不拥有像素和后端状态；真实 capture 继续由 `PhotoController` 和 Brain observer 处理。
