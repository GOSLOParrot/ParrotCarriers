---
status: active
category: frontend-audit
date: 2026-05-10
owner: Codex / App V1
scope: Unity AR frontend, camera mode, tool UX, dialogue flow, real-device readiness
code:
  - unity/ArSpike/Assets/Scripts/ParrotApp/UI/AppV1MetaUiController.cs
tests:
  - tests/test_unity/test_app_v1_meta_ui_static.py
---

# App V1 Frontend Camera UX And Real-Device Audit

## 0. 本轮目标

本轮目标不是新增后端接口，而是继续完善 App 前端第一版的使用体感：

- 相机模式从“现代取景框面板”改成“透明 WYSIWYG 拍照 HUD”。
- 默认拍照界面保持干净，只保留关闭、设置、快门、手滑 zoom、手滑 exposure。
- 专业相机参数在齿轮展开后出现：filter、ready/preview、hide UI、像素 BBox / 印花素材 slot。
- 继续审计启动页、对话、工具柜、相机、放大镜、BBox、工作桌、Nanobot 纸条、XRHand 的多场景流程。
- 补充真机测试准备清单，明确哪些已经具备，哪些还需要手机/网络/权限实测。

## 1. 启动前调研

### 1.1 Cursor / 项目内文档

本轮修改前对照：

- `.cursor/memory/architecture/ar_app_flow_ui_design.md`: App Flow 基线要求 AR 摄像头画面所见即所得，Meta UI 只做低遮挡 2D overlay。
- `.cursor/memory/lore/ideas.md`: 复杂管理功能归 Web，移动端保持轻量、有趣、像素纸条和道具交互。
- `.cursor/memory/architecture/Interface/app_v1_tool_dataflow_interface_20260510.md`: Unity 只负责可见交互，Photo / Focus / BBox 继续复用现有 controller。
- `.cursor/memory/architecture/Interface/photo_memory_awareness_true_connection_guide_20260509.md`: Camera mode 与 Awareness 分离；拍照不默认打断对话。
- `.cursor/memory/architecture/Interface/app_v1_web_live_state_audit_20260510.md`: Web 控制台已经能看 BB / IW / RefBinding / L2-B 的工具流程落点。

### 1.2 外部相机 / Photo Mode 调研

参考链接：

- Apple HIG Camera Control: https://developer.apple.com/design/human-interface-guidelines/camera-control
- Apple iPhone Camera basics: https://support.apple.com/en-sg/guide/iphone/iph263472f78/ios
- Google Pixel Camera settings: https://support.google.com/pixelcamera/answer/2838995
- Google Pixel high-quality photo controls: https://support.google.com/pixelcamera/answer/14106982
- Dovetail Games Photo Mode support: https://support.dovetailgames.com/hc/en-us/articles/29236139667858-How-do-I-use-Photo-Mode

关键发现：

- 系统相机类 UI 倾向把 zoom / exposure 做成贴边、轻量、可滑动的 overlay，不在画面中心造大面板。
- 游戏 Photo Mode 常见专业项包括 exposure、filter、grid、hide overlay、camera movement、reset 等，但这些通常在 secondary panel 或 hotbar 中，不应污染默认取景。
- 对 AR App，本项目的主摄像头画面就是用户视野；默认画面应该近似透明，避免让用户误以为 Unity 另有一个“伪取景器”。

## 2. 已实现修改

Unity `AppV1MetaUiController` 已更新：

- 删除默认相机取景框和 rule-of-thirds grid。
- 新增 `CameraModeOverlay_TransparentWysiwyg`：透明全屏 HUD。
- 新增 `CameraModeTinyTopEdge` / `CameraModeTinyBottomEdge`：仅保留很薄的黑边安全区。
- 新增 `CameraGestureRail_Zoom`：左侧手滑 zoom rail，默认 1.0x。
- 新增 `CameraExposureRail`：右侧手滑 exposure rail，默认 0.0 EV。
- 新增 `CameraModeTransitionSlot`：相机模式启动时的转场动画插槽。
- 新增 `CameraProSettingsPanel`：齿轮展开后才显示专业相机工具。
- 新增 `CameraToolbox_PixelBBoxStamp`：拍照工具箱的像素 BBox / 印花素材占位。
- `CameraModeShutterButton` 仍然只调用 `PhotoController.CapturePhoto()`。

边界不变：

- Unity UI 不拥有相机像素。
- Python / Web 不抓设备帧，不伪造照片原图。
- 照片 preview / HTTP asset / Awareness / IntentWorkspace / L2-B 继续走既有 PhotoController + Brain observer 链路。

## 3. 前端流程审计

### 3.1 启动页与对话

场景覆盖：

- Start AR：权限、Token Mint、LiveKit、AR readiness 进入转场；失败退回启动页。
- Local Preview：绕过连接，用于 UI smoke 和前端验收。
- Silent Session / Voice Only / Full AR：只设置 capability，不切 Scene。
- Main UI ready 但未放置 GOSLO：不主动问候。
- `HUD_ReportGosloPlaced` 后：才打开 greeting gate。

审计结论：

- 符合需求：启动页不是纯 debug 面板，已经承载 capability 和连接入口。
- 架构能力：`AppStartupFlowController` 仍是启动真源，UI 只调用公开入口。
- 协作机制：GOSLO 对话由 placement gate 控制，避免连接成功后突然问候。
- 体验风险：当前转场仍是静态 loading，后续可替换像素专场动画。

### 3.2 相机模式

场景覆盖：

- 工具柜 `Camera`：打开透明相机 HUD，状态 `preview`。
- 默认 HUD：仅显示关闭、齿轮、快门、zoom rail、exposure rail、薄边。
- 手滑 zoom / exposure：只更新本地 UI 状态，作为第一版参数槽；真机参数应用待接入摄像头能力。
- 齿轮：展开 `CameraProSettingsPanel`，显示 filter、ready、preview、hide UI、像素 BBox stamp slot。
- `Capture`：状态 `capture_locked`，调用 `PhotoController.CapturePhoto()`。
- 关闭：状态 `off`，隐藏 Pro 面板和转场 slot。

审计结论：

- 符合用户最新反馈：默认层无取景框，接近所见即所得。
- 架构能力：未复制拍照管线，仍复用 `PhotoController`。
- 模块划分：Pro panel 是 UI 参数槽，不直接写 Blackboard / L2-B。
- 使用体验：默认干净，专业设置按需展开。
- 未完成项：zoom / exposure 第一版只是 UI 状态，真机要绑定 AR camera / platform camera capability。

### 3.3 放大镜 Focus

场景覆盖：

- 工具柜打开：出现可拖动 overlay，白边表示选中。
- 拖动结束：释放旧 Focus，再 `FocusController.AnchorFocus(...)`。
- 齿轮：打开倍率 slider，更新 UI scale 和 label。
- x：`FocusController.ReleaseFocus(active_focus_id)`。

审计结论：

- 符合需求：白边、x、齿轮、倍率 slider 已有。
- 架构能力：不新造 DataChannel topic，复用 `focus.anchored/released`。
- 体验风险：第一版没有真实 shader 局部放大，后续需决定是否放大 AR camera texture 或只作为注意力工具。

### 3.4 BoundaryBox

场景覆盖：

- 工具柜打开：出现白边 BBox。
- 拖动结束：移除旧 BBox 后重新 `BBoxController.PlaceBBox(...)`。
- 右下白色 handle：resize 后重新 placed。
- x：`BBoxController.RemoveBBox(active_bbox_id)`。

审计结论：

- 符合需求：可关闭、可拖动、可拉大拉小、选中提示明确。
- 架构能力：Unity 不做注意力数学，Brain / RefBinding 负责解释。
- 使用体验：resize handle 可用但仍偏工程占位，后续可换像素控制点素材。

### 3.5 2D 工作桌与 Nanobot 纸条

场景覆盖：

- Nanobot note：进入纸条栈。
- 点击纸条或 `Workdesk`：打开 `AppV1_2DWorkdesk`。
- Accept / Dismiss / Archive：处理当前本地纸条。
- Web 端 Nanobot / Calendar：进入 IntentWorkspace staged ref，不直接写长期记忆。

审计结论：

- 符合项目理念：移动端轻量纸条，复杂管理归 Web。
- 未完成项：纸条动画、拖入桌面、垃圾桶、音效仍是 slot。

### 3.6 XRHand / 指令系统

场景覆盖：

- `XRHand` 按钮：触发 `HandGestureSource.DebugFireBranchGesture()`。
- 食指中段停靠：属于 `PerchOnHand` local reflex。
- focus / bbox / photo：属于 Unity 上行事件。
- Brain command：仍使用既有 RPC / EcpCommand 语义。

审计结论：

- 符合模块划分：手势不切 Scene、不绕过对话策略。
- 真机风险：`com.unity.xr.hands` 当前未在 manifest；真实手势需要单独加包并做设备验证。

## 4. Web 控制台联动审计

当前 Web 控制台已能验证：

- Camera capture request：Blackboard 可见 `session/camera_mode` / `session/photo_capture_request`。
- Photo preview + awareness：IntentWorkspace 可见 PHOTO ref，L2-B 可见 PhotoNode。
- Focus / BBox：RefBinding registry 可见 active ref。
- Nanobot / Calendar：IntentWorkspace 可见 staged ref。
- L2-B：read-only graph 可视化，不作为写入口。

审计结论：

- Web 控制台适合验证后端流程和 live-state。
- Unity App 前端负责用户体感；Web 不替代移动端 UI。
- Graphiti 管理仍应默认 dry-run，不把测试控制台变成记忆写入口。

## 5. 真机测试准备

已具备：

- `unity/ArSpike/Packages/manifest.json` 已包含 AR Foundation、ARCore、ARKit、XR Interaction Toolkit、Input System、LiveKit Unity SDK。
- `ParrotSmokeSceneBuilder` 会挂载 App V1 Meta UI、Photo、Focus、BBox、Hand source。
- Web 控制台能观察 Blackboard / IntentWorkspace / RefBinding / L2-B。
- Python self-check 与 Unity static tests 可作为桌面前置验收。

真机前还需要确认：

- Android / iOS build target、player settings、bundle id、camera/mic/network permissions。
- 手机与 Brain / LiveKit / Web 控制台在同一网络，或配置可访问的 host。
- LiveKit server `:7880`、Brain monitor `:7892`、photo upload endpoint 可从手机访问。
- Unity `PhotoController` 的 Brain host 不应写死 `localhost`，真机要用局域网 IP 或配置文件。
- ARSession 在目标设备上能进入 tracking；ARCore / ARKit 运行时已安装。
- 真实 zoom / exposure 是否可通过 AR camera 或 platform camera 参数控制，需要设备 API 验证。
- Bluetooth / mic route 切换不触发 LiveKit room 重连。
- `com.unity.xr.hands` 未安装；若本轮验收必须真实手势，需要先加入包并验证兼容。

建议真机 smoke 顺序：

1. 桌面先跑 Python + Unity static + Unity MCP console。
2. 生成本机可访问配置：Brain host、LiveKit URL、room、identity、token mint endpoint。
3. 手机启动 App：Start AR -> 权限 -> 连接 -> Main UI。
4. 未放置 GOSLO 前确认不主动问候。
5. 放置 GOSLO 后打开 greeting gate。
6. 工具柜依次测 Camera / Capture / Magnifier / BBox / Workdesk / Notes / XRHand。
7. 同时打开 Web Live State，确认每个工具的 BB / IW / REF / L2-B 落点。
8. 切后台 / 回前台 / 网络波动 / 蓝牙切换做生命周期 smoke。

## 6. 本轮未解决问题

- 相机 zoom / exposure 目前是 UI 状态槽，未真正下发到设备 camera capability。
- Pro settings 的 filter / DOF / lens / grid 仍是前端 slot，未连接图像处理。
- 真实相机素材缺现代图标时仍标 placeholder。
- 转场动画只有 slot，未做最终像素动画。
- 真实 XRHand 需要安装并验证 `com.unity.xr.hands`。

## 7. 验证记录

已通过：

- `uv run ruff check tests/test_unity/test_app_v1_meta_ui_static.py`
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`：3 passed。
- `uv run pytest tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_app_v1_monitor.py tests/test_unity/test_app_v1_meta_ui_static.py -q`：15 passed。
- `uv run python src/scripts/run_app_v1_self_check.py --obsidian-vault D:\GOSLOParrot\GOSLObsidian\GOSLOParrot`：`passed=true`。
- Unity MCP `refresh_unity(scope=scripts, compile=request)`：ready。
- Unity MCP Console：0 error / 0 warning。
- Unity MCP `ParrotSmokeScene` validate：0 issues / 0 missing scripts / 0 broken prefabs。
- Unity MCP EditMode / PlayMode：Passed，当前 Unity test tree total=0。

未作为本轮阻塞：

- 全仓 `uv run ruff check` 仍有既有 unrelated lint（老脚本、integration tests、未用 import 等），本轮只记录，不顺手重写无关文件。
