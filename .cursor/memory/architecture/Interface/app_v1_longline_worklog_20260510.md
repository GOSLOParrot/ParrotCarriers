---
status: active
category: worklog
date: 2026-05-10
owner: Codex / App V1
---

# App V1 长线实现 Worklog

## 04:00-04:20 计划与事实源审计

- 已读 `ideas.md`、`ar_app_flow_ui_design.md`、`Interface/INDEX.md`、`concept_dictionary`。
- 结论：`ar_app_plan.md` 是历史追溯；当前 App Flow 以 `ar_app_flow_ui_design.md` 和设计工作区为准。
- 发现已有代码雏形：backend facade、Web monitor、Graphiti console、Unity Meta UI 初稿。

## 04:20-04:35 Backend facade / Web 初始测试

- `ruff` 首轮通过。
- `pytest` 首轮发现 `session/photo_capture_request` 未入 BB schema。
- 修复：新增 `session/photo_capture_request`，writer = `brain.app_first_version`。
- 复测：`tests/test_brain/test_app_first_version_facade.py` 和 `test_app_v1_monitor.py` 全部通过。

## 04:35-05:05 Unity Meta UI 扩展

- `AppV1MetaUiController` 从工具按钮白膜扩展为：
  - `StartupSurface`
  - `StartupTransitionSurface`
  - HUD
  - wood `ToolCabinet_WoodDrawer`
  - `MagnifierFocusOverlay_Draggable`
  - `BoundaryBoxOverlay_DraggableResizable`
  - `AppV1_2DWorkdesk`
  - `NanobotNoteStack`
  - XRHand debug reflex button
- Smoke scene builder 已添加 `AppV1MetaUiController` 并 wire Photo/Focus/BBox/Hand source。

## 05:05-05:20 素材入库

- 复制 curated 子集到 `unity/ArSpike/Assets/UI/ParrotApp`。
- 新增 Unity 侧 `README.md` 和 `app_v1_asset_manifest.json`。
- 新增设计工作区素材对照表 `app_v1_asset_mapping_20260510.md`。

## 05:20 静态 Unity 测试

- 新增 `tests/test_unity/test_app_v1_meta_ui_static.py`。
- 覆盖：
  - Meta UI 保留启动页、转场、工具柜、工作桌、Nanobot、Magnifier、BBox、XRHand。
  - Meta UI 调用现有 `PhotoController` / `FocusController` / `BBoxController`。
  - Smoke scene builder 挂载并 wire Meta UI。
  - Unity 素材 manifest 中 slot 文件存在。
- 复测：3 passed。

## 05:35 Unity MCP 验证与素材导入设置

- Unity MCP active instance：`ArSpike@a0c0295f7bd40ecc`。
- Refresh/compile：ready。
- Console：0 error / 0 warning。
- Scene validate：`ParrotSmokeScene` 0 issues / 0 missing scripts / 0 broken prefabs。
- EditMode / PlayMode test jobs：Passed（当前 Unity test tree total=0）。
- 7 个 App V1 PNG 素材已通过 Unity MCP 设为 Sprite、Point filter、no mipmaps、alpha transparency。

## 当前关键决策

1. 放大镜第一版实现为可拖 Focus overlay + 倍率 UI，不做真实屏幕采样 shader。
2. BBox move/resize 通过 remove+place 重建显式注意力框，避免新增 wire schema。
3. XRHand 在未启用 `com.unity.xr.hands` 前保留 debug/manual flow，不阻塞 App V1。
4. Graphiti 控制台默认 dry-run，避免测试页成为长期记忆写入口。
5. 素材只导入 curated 子集，现代相机图标和转场动画保留 slot。

## 待复测

- 全量相关 ruff：passed。
- Python facade/Web/self-check：15 pytest passed；self-check `passed=true`。
- Unity static tests：3 passed。
- Web 控制台浏览器 smoke：`http://127.0.0.1:7892/` 打开成功；tabs 可切换；页面按钮触发 self-check 返回 `passed=true`。
- Unity MCP：refresh/compile ready；Console 0 error / 0 warning；`ParrotSmokeScene` validate 0 issues；EditMode / PlayMode jobs Passed（当前 Unity test tree total=0）。

## 当前剩余风险

- `AppV1MetaUiController` 是 runtime-built UGUI 白膜，未做真实设备视觉验收。
- 放大镜倍率目前是 overlay scale + Focus 数据流，不是真实屏幕采样 shader。
- PNG 导入设置已由 Unity MCP 设置并生成 `.png.meta`；仍未做最终 9-slice 边界。
- Smoke scene builder 新增 UI 挂载逻辑已编译通过，但没有自动执行菜单重建 scene，以免触发保存对话框。

## 05:55-06:15 Camera UX 修正与真机准备审计

- 外部调研对照 Apple Camera Control、iPhone Camera、Pixel Camera、Dovetail Photo Mode：默认拍照层应轻量贴边，专业参数放二级面板。
- 用户反馈确认：相机模式需要所见即所得，不应默认画取景框。
- Unity 已把 `CameraModeOverlay_Modern` 替换为 `CameraModeOverlay_TransparentWysiwyg`。
- 默认相机层只保留薄黑边、关闭、齿轮、快门、zoom rail、exposure rail。
- 齿轮展开 `CameraProSettingsPanel`，包含 filter / preview / ready / hide UI / pixel BBox stamp slot。
- 新增 `app_v1_frontend_camera_ux_realdevice_audit_20260510.md`，记录多场景前端流程审计和真机测试准备。
- 静态测试已改为防止重新引入 `CameraPreviewFrame`。

## 06:20-06:45 Frontend Flow / Dialogue / Real-Device Prep

- 审计发现 Settings 只有纸条反馈，真机测试时无法连续看到能力模式、对话 gate、Awareness。
- 新增 `AppV1SettingsDialoguePanel`：Quiet / Voice / Full AR、SceneReady、Placed、Aware、Workdesk、Notes。
- 修复主界面内切能力模式可能回到 Startup 的 UX bug；Main UI 内现在只发纸条和刷新 HUD。
- HUD 增加 Mode / Dialogue / Camera / Focus+BBox / Notes 摘要，方便拍屏验收。
- 相机 zoom/EV rail 改为 Slider 直接挂在 rail 面板上，避免触摸 hit area 过小。
- 新增 `src/scripts/prepare_app_v1_device_smoke.py`，输出手机可访问 LiveKit / token mint / photo upload / Web console URL 与 smoke 顺序。
- 新增 `app_v1_frontend_flow_modes_audit_20260510.md`，固化多模式/多菜单/对话流程审计。
