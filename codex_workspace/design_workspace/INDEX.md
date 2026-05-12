# 设计协作工作区 Index

> 创建：2026-05-09
> 用途：给用户和 Codex 一起做 App / Web / 2D 工作区设计、原话存档、草图记录、素材收集、Figma / Unity 预览对齐。

这个目录不是 `.cursor/memory` 的替代品。`.cursor/memory/**` 仍然是后端事实源、协议源和架构追溯；这里是“设计桌面”：放用户原话、草图入口、页面 / 组件想法、素材清单、业务流程草案、今天的任务顺序。

## 读法

1. `00_original_words/README.md`：用户原话镜像和本轮需求摘录。
2. `backend_interface_map/README.md`：设计时怎么看后端设计、代码、核心接口、协议。
3. `tasks/ACTIVE_CONTEXT.md`：当前设计阶段和下一步。
4. 按设计方向进入：
   - `unity_ar_app/INDEX.md`
   - `app_2d_workspace/INDEX.md`
   - `web_console/INDEX.md`
   - `asset_pipeline/INDEX.md`

## 目录角色

| 目录 | 角色 |
|:--|:--|
| `00_original_words/` | 用户原话镜像、今天需求摘录、后续可直接复制进 Figma / 设计说明的文本。 |
| `unity_ar_app/` | Unity AR App 第一屏、启动、摄像头主界面、HUD、工具柜、菜单画布、纸条反馈。 |
| `app_2d_workspace/` | App 内 2D 工作区：Nanobot 报告、Google 日程批改、Ref / 照片 / 纸条处理。 |
| `web_console/` | Web 控制台设计。当前原则：先理解 App 流程，再设计监控 / 管理视图；read-only 优先。 |
| `asset_pipeline/` | Figma、Unity UI 素材、像素风资源、插件和导出路径。 |
| `backend_interface_map/` | 设计用后端索引：模块怎么协作、业务接口怎么写、哪些协议不能乱动。 |
| `tasks/` | Codex 风格进度记录：ActiveContext、任务顺序、技能 / 蒸馏资料索引。 |
| `sketches/` | 可在 Codex 内置浏览器直接打开的 HTML 草图，用于快速预览布局。 |

## 当前设计判断

- 先做 Unity AR App 的启动菜单、摄像头主界面、HUD、工具柜、纸条反馈与基础 App 2D 工作区。
- Web 控制台先不抢跑完整设计，等 App 流程清楚后反推需要监控哪些后端状态。
- Obsidian / Google / PhotoNode 是外挂或外部源：先搞清楚“怎么连上、数据怎么进 L1.5 / L2-B、App 里怎么让用户感觉到”，再做漂亮页面。
- Figma 是设计源，Unity 是运行预览源；设计区只放索引、草图说明、资产清单，不把大资源塞进 memory。

## 2026-05-10 路由清理后阻塞任务

正式 App 前端尚未完成。下一轮 App 前端工作必须从 `tasks/ACTIVE_CONTEXT.md` 开始，并先做调研，再从启动页进入长线实现。

1. **Room Setting**：启动页 `SCENE` 入口进入 App preset/config 页面，管理 LineA/LineB、Model、setting file、Scene、skin、Persona/Mode 和保存的 Room preset。这里的 Room 是 App 菜单预设，不是 LiveKit Room。
2. **LineB 菜单升级**：菜单必须显示 ASR/TTS readiness、Google ADC 状态、声纹/说话人状态、回音风险、处理模式、近期 TTS 与麦克风判定证据。
3. **Ner 第二模型**：Ner 目前只是 raw asset，必须升级成可选择的生产模型路径；启动页要能选择 Brain 管线、模型、设定、场景和皮肤。

## 硬规则

- 不改 `.cursor/memory/lore/ideas.md`；这里只放镜像副本和设计草稿。
- 业务接口文档只写“业务如何跑通”，不复制半个代码仓库。
- 改核心协议 / DTO / enum / topic / BB key 时，必须回到 `.cursor/memory/architecture/protocol_snapshot_p4.md` 和 `Interface/INDEX.md`。
- 新增 `.cursor/memory/architecture/**` 才需要登记 `.cursor/memory/INDEX.md`；本设计区新增文件默认不需要。

## 2026-05-11 LineB + Ner Longline Route

- Current longline TODO: `tasks/lineb_ner_gameplay_longline_todo_20260511.md`.
- This is the route for LineB configurable profiles, Ner model/gameplay upgrade, GOSLO joystick/gameplay upgrade, and unified prop/object interactions.
- Start from `tasks/ACTIVE_CONTEXT.md`, then read the longline TODO before editing ECP, model manifest, Brain tools, RoomSetting, or Unity model controllers.
- Current architecture decision: keep the existing ECP wire route and build profile, manifest, capability resolver, and `play_capability` layers on top.

## 2026-05-13 App/Web 并行工作流

- Workflow: `../app_web_parallel_workflow_20260513.md`
- Shared board: `tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md`
- App business interfaces: `backend_interface_map/app/`
- Web business interfaces: `backend_interface_map/web_console/`
- Core candidate queue: `backend_interface_map/core_interface_candidate_queue_20260513.md`

`ACTIVE_CONTEXT.md` 只保留当前事实和路由，不承载完整 TODOList。

## 2026-05-09 新增设计入口

- `00_original_words/chat_original_20260509_startup_menu_assets.md`：本轮关于启动页、启动动画、2D 工作区、主页面 HUD 的原话摘录。
- `unity_ar_app/startup_menu_design_v0_20260509.md`：横屏启动页与启动菜单 v0。
- `unity_ar_app/main_hud_landscape_v0_20260509.md`：横屏 AR 主页面 HUD / 工具栏 v0。
- `app_2d_workspace/workspace_mansion_reference_20260509.md`：2D 宅邸工作区和工作桌交互参考。
- `asset_pipeline/reference_assets_20260509.md`：本轮 7 张参考图的资产板和待收集素材类别。
- `sketches/startup_menu_landscape_v0.html`：可直接预览的横屏启动页 HTML 草图。
- `workflows/web_vs_figma_design_workflow_20260509.md`：当前采用网页草图优先、Figma 后置精修的设计工作流判断。
- `unity_ar_app/menu_canvas_mvp_2dworkspace_20260509.md`：新增 `2DWorkspace` 作为第五个菜单块的 MVP 设计。
- `unity_ar_app/menu_canvas_external_modules_20260509.md`：Google / Obsidian / GOSLO Module / Nanobot / Photo 外部模块 dock 设计。
- `unity_ar_app/app_v1_whitebox_shell_20260510.md`：第一版 App 白膜，连接菜单画布、外部模块 Dock、Pixel Asset 方向。
- `backend_interface_map/menu_canvas_external_modules_business_flow.md`：菜单画布外部模块业务接口流，按 A-D 纪律记录缺口和完成判据。
- `backend_interface_map/app_v1_core_business_interface_coverage_20260510.md`：第一版 App 核心接口与业务接口覆盖，对齐 `AppFirstVersionFacade`。
- `asset_pipeline/pixel_asset_audit_20260510.md`：Pixel Asset 候选素材审计与第一版使用建议。
- `asset_pipeline/pixel_asset_selection_20260510.md`：已解压 Pixel Asset 的精选分组、素材定位和白膜使用策略。
- `tasks/app_v1_design_handoff_index_20260510.md`：第一版 App 设计交接索引、自检标准、漂移检查和素材使用目标。
- `web_console/monitoring_demo_scope_20260509.md`：只读 Web 监控小 demo 范围，用于 App 第一版连接层验证。
- `sketches/menu_canvas_mvp_v0.html`：菜单画布 MVP HTML 草图。
- `.cursor/memory/architecture/Interface/app_v1_current_status_and_test_report_20260510.md`：清理后的唯一 App V1 状态/测试报告；明确正式 App 前端尚未完成。
