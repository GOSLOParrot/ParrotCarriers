---
status: active
category: implementation-plan
date: 2026-05-10
owner: Codex / App V1 longline
scope: App V1 AR frontend, backend facade, Web console, Unity smoke tests, asset mapping
---

# App V1 长线扩展执行计划

## 0. 最终目标

本轮完成目标不是“接口能测”，而是 App V1 第一版体验闭环可验收：

启动页 → 权限/连接/转场 → AR 主界面 → 木质工具柜 → 相机模式 → 放大镜 Focus →
BoundaryBox → 2D 工作桌 → Nanobot 纸条 → GOSLO Awareness → Web 测试控制台 →
L2-B/Graphiti 调试视图 → 自检报告和提交记录。

## 1. 每项任务的启动/结束纪律

每个 task 开始前做局部调研，而不是一次性调研完：

| Task | 启动前查什么 | 结束时审计什么 |
|:--|:--|:--|
| 启动页/转场 | `ar_app_flow_ui_design.md`、`startup_menu_design_v0`、`AppStartupFlowController` | 连接成功不提前问候；权限失败回菜单；local preview 不假装联机 |
| 工具柜 | `ideas.md`、HUD/工具柜设计、Wood/Paper curated 素材 | 默认低遮挡；木质拉出柜；不复制 Photo/Focus/BBox 逻辑 |
| 相机 | `photo_memory_awareness_true_connection_guide`、`PhotoController`、BB schema | Python 只记录 request/Awareness；Unity 仍拥有像素 |
| 放大镜 Focus | `protocol_snapshot_p4` 的 `focus.anchored/released`、`FocusController` | 可拖；白边选中；`x` 释放 Focus；齿轮可调倍率 |
| BoundaryBox | `bbox.placed/removed`、RefBinding、attention threshold、`BBoxController` | 可拖/resize/关闭；不在 Unity 做 attention 数学 |
| XRHand/指令 | `HandGestureSource`、`PerchOnHand`、EcpCommand/EcpAck | local reflex / RPC command / EcpEvent 上行边界分明 |
| 2D 工作桌/纸条 | `ideas.md`、Papers Please 参考、IntentWorkspace roles | accept/dismiss/archive 是本地确认流；不直接写长期记忆 |
| Web 控制台 | Graphiti docs、rustworkx/L2-B、`web_console` skill | 控制台用于测试和 dry-run；L2-B read-only；Graphiti 默认不真写 |
| 素材 | curated selection、reference manifest、license/readme | 只导入精选子集；缺失槽明确 placeholder |
| 自检/commit | ruff/pytest/self-check/Unity static | 失败必须修复或记录阻塞；按阶段提交 |

## 2. 当前实现基线

- Backend facade 已扩展 `tool_cabinet`、`asset_manifest`、`request_camera_capture`。
- Web 控制台已有 App actions、test harness、L2-B snapshot、Graphiti status/search/draft/dry-run。
- Unity `AppV1MetaUiController` 已补启动页、转场、HUD、工具柜、放大镜/BBox overlay、工作桌、纸条、XRHand debug reflex。
- Smoke scene builder 已挂载 Meta UI 并把 Photo/Focus/BBox/Hand source 传给 UI。
- Unity curated 素材已进入 `Assets/UI/ParrotApp`，并有 manifest/README。

## 3. 关键验收场景

1. 打开 smoke scene，选择 `LOCAL PREVIEW`，进入 AR 主 UI。
2. HUD 点击 `Tools`，木质工具柜低遮挡拉出。
3. `Magnifier` 创建可拖放大镜，右上 `x` 释放 Focus，`gear` 调倍率。
4. `BoundaryBox` 创建可拖可 resize 的注意力框，关闭时移除 BBox。
5. `Capture` 调用现有 `PhotoController`。
6. `Workdesk` 打开 2D 工作桌，纸条可 accept/dismiss/archive。
7. `XRHand` 触发 `DebugFireBranchGesture()`，验证食指树枝本地 reflex 路径。
8. Web 控制台能复现 camera/focus/bbox/photo/nanobot/calendar/self-check 后端路径。

## 4. 本轮不解决但必须保留插槽

- 真正的屏幕级放大镜 shader / render texture 放大，包括 UI 的视觉采样。
- 现代相机图标裁切。
- IPoAC 转场动画精修。
- 真机 `com.unity.xr.hands` 包启用和手势检测编译验证。
- Graphiti 完整可视化 dashboard。

