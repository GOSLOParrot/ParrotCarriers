---
status: active
category: business-interface
date: 2026-05-10
owner: Codex / App V1
scope: camera, magnifier focus, boundary box, XRHand, workdesk, nanobot notes, Web console
---

# App V1 工具与指令数据流接口

## 0. 分层原则

Unity App 只负责可见交互和本地 reflex。Backend facade 负责 App 业务状态和测试控制台。
DSG/L2-B/Graphiti 负责记忆与图谱，不被 App UI 直接写入。

## 1. 相机工具

启动前调研：

- `photo_memory_awareness_true_connection_guide_20260509.md`
- `protocol_snapshot_p4.md` § photo events
- `PhotoController.cs`

数据流：

1. 用户在工具柜点 `Camera`：UI 展示 camera mode 说明。
2. 用户点 `Capture`：Unity 调用 `PhotoController.CapturePhoto()`。
3. Unity 发 `photo.taken_preview` EcpEvent，preview ≤ 8KB。
4. Unity HTTP POST 原图到 `/upload/photo/{photo_id}`。
5. Brain observer 写 PhotoNode / transient photo event。
6. Awareness policy 决定是否 stage 短期 preview ref。

Web 测试流：

- `/api/app/camera/mode`
- `/api/app/camera/capture-request`
- `/api/app/test/photo-preview`

审计结论：

- Python 不抓设备帧，不伪造原图。
- `session/photo_capture_request` 已加入 BB schema，由 `brain.app_first_version` 单写。

## 2. 放大镜 Focus

启动前调研：

- `protocol_snapshot_p4.md` § `focus.anchored` / `focus.released`
- `FocusController.cs`
- `ar_app_flow_ui_design.md` 放大镜倍率需求

Unity 状态：

- `MagnifierFocusOverlay_Draggable`
- 白边 `Outline` 表示选中。
- 右上 `x`：调用 `FocusController.ReleaseFocus(active_focus_id)`。
- 右上 `gear`：打开倍率 slider，更新本地 UI scale 和 label。
- 拖动结束：释放旧 Focus，再调用 `FocusController.AnchorFocus(...)` 创建新的显式 Focus。

后端流：

`focus.anchored` → Brain observer/focus → RefBinding FOCUS → attention threshold 可消费。

审计结论：

- 第一版不做真正屏幕像素放大 shader；保留倍率控制和明确 UI slot。
- 不新增 DataChannel topic。

## 3. BoundaryBox 注意力框

启动前调研：

- `protocol_snapshot_p4.md` § `bbox.placed` / `bbox.removed`
- `BBoxController.cs`
- `dsg.attention.threshold` 边界

Unity 状态：

- `BoundaryBoxOverlay_DraggableResizable`
- 白边 `Outline` 表示选中。
- 右上 `x`：调用 `BBoxController.RemoveBBox(active_bbox_id)`。
- 右上 `gear`：显示操作说明。
- 右下白色 resize handle：拖动改变 size。
- move/resize 结束：移除旧 BBox，再 `PlaceBBox(...)`，保持显式用户意图。

后端流：

`bbox.placed` → Brain observer/bbox → RefBinding BBOX → attention threshold 可消费。

审计结论：

- Unity 不计算 attention 权重。
- BBox 生命周期由用户显式打开/调整/关闭，不自动长期持久化。

## 4. XRHand 与指令系统

三类指令边界：

| 层 | 示例 | 中断对话吗 | 数据面 |
|:--|:--|:--|:--|
| Local reflex | 食指树枝 → `PerchOnHand` | 否 | Unity 本地 |
| Unity 上行事件 | focus/bbox/photo/gesture | 否，除非 Brain 后续策略决定 | EcpEvent / DataChannel |
| Brain 下行命令 | fly/animate/app menu RPC | 由 Brain 策略决定 | LiveKit RPC / EcpCommand / EcpAck |

当前实现：

- `HandGestureSource.DebugFireBranchGesture()` 可在未启用 XRHands 包时测试。
- `PerchOnHand` 使用食指中段作为目标。
- UI 的 `XRHand` 按钮只触发本地 debug reflex，不切 Scene。

## 5. 2D 工作桌与 Nanobot 纸条

启动前调研：

- `ideas.md`
- `app_2d_workspace/workspace_mansion_reference_20260509.md`
- IntentWorkspace roles：`nanobot_report` / `calendar_draft`

Unity 状态：

- `NanobotNoteStack`：显示最近纸条。
- 点击纸条或工具柜 `Workdesk`：打开 `AppV1_2DWorkdesk`。
- Workdesk 支持 `Accept` / `Dismiss` / `Archive`。

后端流：

- Nanobot report → `/api/app/nanobot/report` → IntentWorkspace `RICH_REPORT`。
- Calendar draft → `/api/app/calendar/draft` → IntentWorkspace `DOC`。
- 2DWorkspace 只展示 refs，不拥有 payload。

## 6. Web 控制台与 Graphiti

Web 端职责：

- 复现 App 后端流程。
- 展示 canvas snapshot、tool cabinet、asset manifest。
- 展示 L2-B bounded JSON。
- Graphiti 提供 status/search/draft/dry-run write，默认不真写。

审计结论：

- Graphiti OSS 没有现成完整 dashboard；本轮做轻量管理壳。
- L2-B 在控制台里 read-only，避免测试页变成新写入口。

