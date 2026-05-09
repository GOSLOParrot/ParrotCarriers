---
status: active
category: frontend-audit
date: 2026-05-10
owner: Codex / App V1
scope: startup flow, dialogue gate, capability modes, menu modes, tool UX, real-device smoke prep
code:
  - unity/ArSpike/Assets/Scripts/ParrotApp/UI/AppV1MetaUiController.cs
  - src/scripts/prepare_app_v1_device_smoke.py
tests:
  - tests/test_unity/test_app_v1_meta_ui_static.py
---

# App V1 Frontend Flow / Modes Audit

## 0. 本轮审计目标

目标是从用户真实使用路径审计 App V1，而不是只检查接口是否存在：

- 对话 gate：连接成功、SceneReady、GOSLO placed、能力模式切换时，GOSLO 何时能说话。
- 使用功能：工具柜、Settings、Camera、Magnifier、BBox、Workdesk、Notes、XRHand。
- 使用体验：是否遮挡 AR 画面，是否误切启动页，是否有模式状态反馈。
- 多模式覆盖：Startup / Transition / Main UI / Settings / Camera clean / Camera pro / Tool overlays / Workdesk。
- 真机准备：避免 localhost、权限、AR tracking、LiveKit/token/photo upload 端口缺失。

## 1. 本轮发现并修复的问题

| 问题 | 影响 | 修复 |
|:--|:--|:--|
| Settings 入口只有纸条反馈 | 真机测试时看不到能力模式、对话 gate、Awareness | 新增 `AppV1SettingsDialoguePanel` |
| 主界面内切能力模式可能回启动页 | 用户在 AR 主界面切 Silent/Voice/Full AR 会丢上下文 | `ApplyCapability` 现在在 Main UI 内只发纸条并刷新状态，不调用 `ShowStartup` |
| HUD 只写 “Greeting waits” | 多模式测试时无法看当前 session policy | HUD 增加 Mode / Dialogue / Camera / Focus+BBox / Notes |
| SceneReady 与 GOSLO placed 的体感边界不明显 | 连接成功后是否该问候容易漂移 | Settings 面板提供 `SceneReady` 与 `Placed` 两个显式按钮，并写明 SceneReady 不问候 |
| 相机 zoom/EV rail 子对象无 Graphic | 真机触摸可能打不到 slider 区域 | Slider 直接挂在 rail 面板上，贴边区域本身可接收输入 |
| 真机测试容易误用 `localhost` | 手机无法访问桌面 Brain/LiveKit/photo upload | 新增 `prepare_app_v1_device_smoke.py` 输出 LAN-facing URLs 和 checklist |

## 2. 当前前端模式矩阵

| 模式 | 入口 | 可见 UI | 允许动作 | 不允许 / 审计边界 |
|:--|:--|:--|:--|:--|
| Startup | App 打开 | Start AR / Local Preview / Silent / Voice / Full AR | 选择能力模式、进入真实启动或本地预览 | 不主动问候，不假装 Brain 已连接 |
| Transition | Start AR 后 | CONNECTING + progress + local skip | 权限、TokenGate、LiveKit connect | 失败必须回 Startup |
| Main UI | 启动成功或 Local Preview | HUD + ToolCabinet + Notes | 打开工具、报告 GOSLO placed | 连接成功但未 Placed 不问候 |
| Settings | ToolCabinet -> Settings | `AppV1SettingsDialoguePanel` | Quiet/Voice/Full AR、SceneReady、Placed、Aware、本地 Workdesk/Notes | 不直接写 L2-B / Graphiti；Awareness 真实写入仍走 facade |
| Camera clean | ToolCabinet -> Camera | 透明 HUD + 薄边 + zoom/EV + capture | WYSIWYG capture，轻量参数 | 默认不画取景框、不挡中心画面 |
| Camera pro | Camera gear | Pro panel + filter/ready/preview/hide UI + stamp slot | 专业参数槽、隐藏 panel | 第一版不处理真实滤镜和设备 exposure |
| Magnifier | ToolCabinet -> Magnifier | 白边可拖 overlay + gear + x | focus anchor/release、倍率 UI | 不新造 attention 数学，不新建 topic |
| BoundaryBox | ToolCabinet -> BoundaryBox | 白边框 + resize handle + x | bbox place/remove/resize | Unity 不做 L2-B 注意力权重 |
| Workdesk | ToolCabinet / Note click | `AppV1_2DWorkdesk` | Accept/Dismiss/Archive 本地纸条 | 不拥有 IntentWorkspace payload |
| Nanobot Notes | ToolCabinet -> Notes | Paper note stack | 生成/展开纸条 | 不直接写长期记忆 |
| XRHand | ToolCabinet -> XRHand | 纸条反馈 | debug branch gesture -> PerchOnHand | 不切 Scene，不绕过对话策略 |

## 3. 对话流程审计

### 3.1 正向流程

1. Startup `Start AR`。
2. Transition 完成权限、token、LiveKit。
3. Main UI ready，HUD 显示 `Dialogue: wait place`。
4. Settings `SceneReady` 可报告 scene ready，但仍是 `scene_ready_silent`。
5. HUD `Placed` 或 Settings `Placed` 后，`ReportGosloPlaced()` 发送，HUD 显示 `Dialogue: ready`。
6. 之后 GOSLO 可以按 Brain 策略问候。

### 3.2 静默 / 语音 / 全 AR

- `Quiet`：进入 `SessionOnlySilent`，HUD 显示 `Mode: Silent` / `Dialogue: quiet`，房间保持但不发布麦克风。
- `Voice`：进入 `VoiceOnlyNoVideo`，允许语音但不发 camera video。
- `Full AR`：进入 `FullARCompanion`，允许完整 AR companion 能力。

审计结论：这些切换现在不会把主界面打回启动页，用户可以在测试场景里连续切模式。

## 4. 工具使用场景覆盖

### 4.1 Camera

- Clean 模式打开后不遮挡中心画面。
- Zoom / EV 贴边 rail 可拖。
- Capture 只调用 `PhotoController.CapturePhoto()`。
- Pro 面板只在 gear 后出现。
- Close 隐藏 clean/pro/transition slot。

### 4.2 Magnifier

- 打开即 anchor focus。
- 拖动结束重新 anchor。
- Gear 调倍率。
- x release focus。

### 4.3 BoundaryBox

- 打开即 place bbox。
- 拖动/resize 后 remove + place，保持显式生命周期。
- x remove bbox。

### 4.4 Workdesk / Notes

- Notes 生成纸条。
- 点击纸条或 Workdesk 打开桌面。
- Accept/Dismiss/Archive 都产生本地纸条记录。
- 真实 Nanobot / Calendar ref 由 Web/facade/IntentWorkspace 验证。

## 5. 素材与 UI 打磨

已完成：

- Settings 变成可见 session panel，不再只是临时纸条。
- HUD 变成模式摘要，方便真机拍屏验收。
- 相机 Pro 工具箱保留 pixel BBox / stamp slot。
- `unity/ArSpike/Assets/UI/ParrotApp/README.md` 补充 Settings / Pro toolbox / Nanobot animation / real-device badge 视觉槽。

仍是 slot：

- 现代相机图标裁切。
- Nanobot 递纸条动画。
- 转场动画。
- BBox 像素控制点最终美术。
- Settings panel 9-slice 边界。

## 6. 真机测试准备

新增脚本：

```text
uv run python src/scripts/prepare_app_v1_device_smoke.py --print
```

可选写入：

```text
uv run python src/scripts/prepare_app_v1_device_smoke.py --lan-host <LAN_IP> --write tmp/app_v1_device_smoke.json
```

脚本输出：

- `livekit_url`: `ws://<LAN_IP>:7880`
- `token_mint_endpoint`: `http://<LAN_IP>:7888/mint`
- `photo_upload_host`: `<LAN_IP>`
- `photo_upload_port`: `7889`
- `web_console_url`: `http://<LAN_IP>:7892/`
- phone preflight checklist
- tool smoke order

未能自动完成的真机项：

- Unity Inspector 里的 `PhotoController.brainHost` 仍需配置为 LAN IP / Castle 域名，不能用 `127.0.0.1`。
- `LiveKitTokenMintClient.MintEndpoint` 需配置为手机可访问 endpoint。
- `RoomManager.serverUrl` 真机需使用可访问 `ws://` 或 `wss://`。
- Android/iOS player settings 和权限需要 build 前复核。
- 真 XRHand 要安装并验证 `com.unity.xr.hands`。

## 7. 结论

App V1 前端现在已经具备“可连续验收”的模式可见性：

- 主界面能看当前对话 gate 和能力模式。
- Settings 能切模式、报告 SceneReady、报告 Placed、切 Awareness UI 状态。
- 各工具仍复用既有 controller / facade / live-state，不重复造后端轮子。
- 真机测试最容易卡住的 LAN URL 和端口已固化为脚本输出。

## 8. 验证记录

已通过：

- `uv run ruff check src/scripts/prepare_app_v1_device_smoke.py tests/test_unity/test_app_v1_meta_ui_static.py`
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`：3 passed。
- `uv run pytest tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_app_v1_monitor.py tests/test_unity/test_app_v1_meta_ui_static.py -q`：15 passed。
- `uv run python src/scripts/run_app_v1_self_check.py --obsidian-vault D:\GOSLOParrot\GOSLObsidian\GOSLOParrot`：`passed=true`。
- `uv run python src/scripts/prepare_app_v1_device_smoke.py --lan-host 192.168.1.23 --print`：输出 phone-facing LiveKit / token mint / photo upload / Web console URLs。
- Unity MCP `refresh_unity(scope=scripts, compile=request)`：ready。
- Unity MCP Console：0 error / 0 warning。
- Unity MCP `ParrotSmokeScene` validate：0 issues / 0 missing scripts / 0 broken prefabs。
- Unity MCP EditMode / PlayMode：Passed，当前 Unity test tree total=0。
