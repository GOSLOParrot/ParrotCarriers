# Unity AR App 设计区

> 主目标：先设计并落定 App 的第一版使用路径，再决定代码目录和前端 TODO。

## 第一版页面 / 组件

| 层 | 组件 | 当前设计状态 |
|:--|:--|:--|
| 启动 | 启动页菜单 | 需要草图：开始 AR、房间、Brain 管线、人设 / 场景、权限 / 连接测试。 |
| 启动 | 像素加载 / 转场 | 先占位，不阻塞功能。 |
| 主界面 | 摄像头 AR 画面 | 第一屏核心；中心尽量干净。 |
| 主界面 | HUD | 角落，可横 / 竖展开，显示连接、时间、天气、音频、视频、Brain、视觉状态。 |
| 主界面 | 工具柜 | HUD 对角，可横 / 竖展开，放设置、相机模式、拍照、放大镜、注意力框、任务按钮、2D 工作区入口。 |
| 交互 | 放大镜 / 海盗望远镜 | 放大手机画面包括 UI，倍率可调。 |
| 交互 | 注意力框 / Bounding Box | 拖动圈出区域；业务上要对齐 Intent / Task / ECP / DSG。 |
| 反馈 | 纸条 / 猫爪 / 报告 | Nanobot / Brain 结果变成可展开纸条。 |
| 高级 | 菜单画布 | 4-block：model / persona / mode / scene，保存 preset；先设计，不急实现。 |

## 近期先做的草图

1. 启动页菜单布局。
2. 进入后的摄像头主界面。
3. HUD 组件展开 / 收纳。
4. 工具柜组件展开 / 收纳。
5. 纸条反馈的最小交互。

## 和后端的关键对齐

| App 元素 | 后端 / 协议锚点 |
|:--|:--|
| LiveKit 连接 | `bus_v4.md`、Unity `ParrotApp/LiveKit/`、token mint。 |
| HUD 连接状态 | ECP heartbeat、connection health、BB session state。 |
| 菜单 4-block | `backend_interface_refinement_20260507.md` 的 MenuRegistry / PresetLoader / BB 4 keys。 |
| 注意力框 | ECP / DSG SightingEvent / IntentWorkspace，待业务接口设计。 |
| 拍照 / PhotoNode | PhotoController、PHOTO_PATH RefBinding、Phase 4 L7 锁。 |
| 纸条报告 | Scheduler / Nanobot result → Brain / App report payload。 |

## 代码落点以后再定

等第一版草图和 Figma 对齐后，再补：

- Unity UI 目录结构。
- 前端路由 / scene / prefab TODO。
- ActiveContext 和任务分解。

现阶段只做设计，不急着写前端代码。

## 2026-05-09 设计草稿

- `startup_menu_design_v0_20260509.md`：横屏启动页、Room Setting、START/Mode 切换、启动动画留白。
- `main_hud_landscape_v0_20260509.md`：横屏 AR 主页面、左上 HUD、左下工具栏、展开方向。
- `menu_canvas_mvp_2dworkspace_20260509.md`：菜单画布核心五块与 2DWorkspace 边界。
- `menu_canvas_external_modules_20260509.md`：Google / Obsidian / GOSLO Module / Nanobot / Photo 外部模块 dock 设计。
- `app_v1_whitebox_shell_20260510.md`：第一版 App 白膜，说明模块布局、状态、Pixel Asset 皮肤方向。
