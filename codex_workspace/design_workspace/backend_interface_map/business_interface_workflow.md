# 业务接口写法

> 继承 `.cursor/memory/architecture/Interface/INDEX.md` 的 A-D 纪律，但这里只为 App / Web / 2D 工作区写业务切片，不复制核心签名大全。

每个业务接口文件只回答四件事：

## A. 模块职责回读

列最多 3 个真源，例如：

- `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md §4.3`
- `.cursor/memory/architecture/backend_interface_refinement_20260507.md §3`
- `.cursor/memory/architecture/dsg/workspace_index.md`

## B. 现有核心接口能否组合实现？

写 `yes` 或 `no`。

- `yes`：进入 D，写完成判据。
- `no`：进入 C，列需要补的核心接口或协议，但不在业务设计里直接改协议。

## C. 缺什么核心表面？

仅在 B = no 时填写：

| 字段 | 写什么 |
|:--|:--|
| 候选命名 | 函数 / 事件 / adapter / DTO 的候选名。 |
| 落点模块 | Brain / Bus / DSG / Memory / Scheduler / Unity / Nanobot。 |
| 是否进协议 SSOT | wire 字段、topic、BB key 必须进。纯 Python 内部 API 不一定。 |
| 是否需要 Unity DTO 镜像 | Unity 要直接消费时需要。 |

## D. 完成判据

写“什么输入产生什么可观察结果”：

- 正向：用户做什么，App / Web / 后端能看到什么。
- 失败：依赖没连上时，用户看到什么错误或空状态。

## 即将需要的业务接口切片

| 切片 | 文件建议 | 当前状态 |
|:--|:--|:--|
| Obsidian L1.5 设定 Node 真连接 | `obsidian_l1_5_setting_node_flow.md` | 待设计 |
| Google Calendar raw event → Node → 写回 | `google_calendar_node_flow.md` | 待设计 |
| PhotoNode 保存 / RefBinding / aware 流程 | `photo_node_camera_flow.md` | 待设计 |
| Nanobot result → App 纸条 / 2D 工作区报告 | `nanobot_report_note_flow.md` | 待设计 |
| Menu canvas 4-block → preset → BB keys | `menu_canvas_business_flow.md` | 后端核心已落，前端流程待设计 |
| Menu canvas 外部模块 dock | `menu_canvas_external_modules_business_flow.md` | 已出第一版草案 |
| 第一版 App 统一业务 facade | `app_v1_core_business_interface_coverage_20260510.md` | 已实现并有单测 |
