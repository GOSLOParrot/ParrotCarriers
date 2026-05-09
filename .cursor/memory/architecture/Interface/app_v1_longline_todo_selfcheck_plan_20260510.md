---
title: App V1 Longline TODO And Self-check Plan
date: 2026-05-10
started_at: 2026-05-10 04:00 +08:00
owner: Codex / App V1 longline
status: active
scope: App completion pass, Unity AR app interface scripts, test Web console, Graphiti management, asset mapping, audit records
---

# App V1 长线 TODO 与自检计划

## 0. 大目标

本轮目标不是最小可运行版本，而是把 App V1 推到可验收、可自测、可继续扩展的状态：

- Unity AR App 白模具备对角线 HUD + 木质拉出工具柜 + 相机模式 + 放大镜 Focus + BoundaryBox + 2D 工作桌 + Nanobot 纸条提醒入口。
- 后端 facade 明确暴露 App 工具状态、工具数据流、相机请求、Awareness、纸条、工作区和测试动作。
- 测试用 Web 控制台从只读 monitor 升级为可触发测试流的 developer console，可看 L2-B、测试工具流、管理 Graphiti memory core。
- 素材有可追踪映射表；已找到素材直接挂入插槽，缺失项用 placeholder 并标明替代来源。
- 每轮实现前后做架构审计：需求匹配、模块边界、协作机制、使用体验、Cursor 规则/记忆命中、是否重复造轮子。

## 1. 验收成果

| 验收项 | 必须结果 | 验证方式 |
|:--|:--|:--|
| 计划与自检 | 有 TODO、验收口径、审计清单、时间线记录 | 本文件 + worklog |
| Cursor 文档审计 | 查询本地 `.cursor` 记忆/规则，并核对官方 Cursor rules/memory 文档 | 记录关键发现和链接 |
| 不重复造轮子 | Graphiti 写入按 episode；L2-B 可视化吃 rustworkx/L2-B bounded JSON；Unity 只做 UI/事件，不重写 Brain 判断 | 接口文档和代码边界 |
| Unity App UI | `ArSpike` 新增正式 App UI 白模脚本；不往 `ParrotDev` 加新功能 | C# 文件位置 + smoke builder |
| 工具柜 | 工具柜包含 Settings、Camera、Workspace、Magnifier/Focus、BoundaryBox、Note Inbox；木质视觉插槽 | Unity UI 脚本 + asset manifest |
| 相机流程 | Toolbar 中进入 preview/photo_ready/capture request；拍照仍走 `PhotoController` 双通道；Awareness 不 interrupt | facade API + Web 操作 + self-check |
| Focus / BBox | UI 工具调用现有 `FocusController` / `BBoxController`，后端测试可模拟 EcpEvent | Unity API + Web test endpoint |
| 2D 工作桌 | 可打开/关闭，可显示 report/calendar/photo/note 文档插槽 | Unity UI + Web canvas snapshot |
| Nanobot 纸条 | 后端 report 可变成 paper note，Unity 有纸条提醒/展开入口 | facade + UI white model |
| Web 控制台 | 黑灰紫 Obsidian 风；包含 Overview、Tool Flow、L2-B、Graphiti、Assets、Self-check | FastAPI 页面 + tests |
| Graphiti 管理 | 提供 status/search/episode draft/write endpoint；无依赖或连接失败时清晰降级 | FastAPI tests + doc |
| 测试 | Python focused tests 通过；self-check 通过；Unity 编译若 MCP/Editor 不可用则做静态 C# 审计 | pytest/ruff/静态记录 |
| 提交 | 多阶段 git commit，不混入无关改动 | git log/status |

## 2. 详细 TODO

### A. 计划、文档、调研

- [ ] 写入长线 TODO、自检和验收计划。
- [ ] 查询本地 `.cursor/memory`、`.cursor/rules`、`.cursor/skills`，抽取本轮必须遵守的规则。
- [ ] 查询官方 Cursor rules/memories 文档，确认项目规则/记忆固化方式。
- [ ] 查询 Graphiti / rustworkx 文档，确认 Web 控制台和 Graphiti 管理不重复造轮子。
- [ ] 输出关键发现、决策、阻塞和疑问。

### B. 后端 App facade / 测试流

- [ ] 扩展 `AppFirstVersionFacade`：工具柜 read model、相机 capture request、工具状态、素材 manifest。
- [ ] 增加 Focus/BBox/Photo preview 测试 harness，优先复用 EcpEventIngest 和 observer，不绕过既有协议。
- [ ] 增加 Graphiti console adapter：status/search/episode draft/write，缺依赖时 graceful unavailable。
- [ ] 扩展 self-check 覆盖 camera request、tool cabinet、focus/bbox simulation、Graphiti graceful status。
- [ ] 增加/更新单元测试。

### C. 测试 Web 控制台

- [ ] 将现有 App monitor 扩展为 developer console。
- [ ] 页面包含：Overview、Tool Cabinet、Tool Flow Test、L2-B Topology、Graphiti Core、Asset Map、Self-check。
- [ ] UI 风格使用黑/灰/紫，接近 Obsidian 的安静操作台气质。
- [ ] 所有写入动作只经 POST 触发，刷新页面不写 Graphiti / Google / L2-B。
- [ ] 加 FastAPI endpoint tests。

### D. Unity AR App UI / 场景脚本

- [ ] 在 `unity/ArSpike/Assets/Scripts/ParrotApp/UI/` 新增 UI 白模脚本。
- [ ] 工具柜以木质抽屉/工具柜为视觉插槽；可拉出/收起。
- [ ] 工具按钮绑定：Camera -> `PhotoController` capture；Magnifier -> `FocusController`; BoundaryBox -> `BBoxController`; Workspace -> 工作桌 overlay；Note Inbox -> paper note。
- [ ] 2D 工作桌 overlay 具有 dim AR 背景、纸张列表、accept/dismiss/archive 本地状态。
- [ ] Nanobot 纸条提醒提供大小两种 paper note 样式；转场动画只留插槽。
- [ ] 更新 `ParrotSmokeSceneBuilder` 把 UI root 挂进 smoke scene。
- [ ] 记录 Unity 接口脚本测试步骤。

### E. 素材与映射

- [ ] 选择并复制小体量 UI 素材到 `unity/ArSpike/Assets/UI/ParrotApp/`。
- [ ] 记录 `ToolDrawer`、`PaperNote`、`WorkspaceDesk`、`CameraIcon`、`FocusTool`、`BBoxTool` 的素材路径。
- [ ] 对缺失项写 placeholder 策略，不阻塞 App 完成。

### F. 审计 / 测试 / 提交

- [ ] 第一轮审计：实现前模块边界与需求匹配。
- [ ] 第二轮审计：后端 API 与 tests。
- [ ] 第三轮审计：Unity UI 脚本和素材映射。
- [ ] 第四轮审计：Web 控制台体验和 Graphiti 边界。
- [ ] 跑 pytest focused + ruff。
- [ ] 若可用，使用 Unity MCP/Editor 验证 scene；不可用则记录静态审计。
- [ ] 6:00 后若核心目标完成，做最终 worklog 和 completion record；6:30 前只处理 bug/文档收口。

## 3. 自检清单

每轮完成后都按以下问题打勾：

| 自检问题 | 判定标准 |
|:--|:--|
| 是否符合需求 | 覆盖用户明确点：相机在工具栏、放大镜、BoundaryBox、木质工具柜、素材映射、2D 工作桌、Nanobot 纸条、Web 控制台、Graphiti 管理 |
| 是否符合架构能力 | 不改 ParrotDev；Unity 只产生 UI/事件；Brain facade 统一读写；IntentWorkspace 承载 draft/report/photo ref |
| 模块划分是否清晰 | UI、facade、test harness、Graphiti adapter、monitor server、docs 分离 |
| 协作机制是否合理 | Nanobot 通过 paper note；GOSLO Awareness 只通知不 interrupt；Graphiti 只在明确写入动作里 add_episode |
| 使用体验是否顺 | 工具都从工具柜进入；Web console 可一键跑测试；状态和降级原因可见 |
| 是否查 Cursor 文档 | 本地 `.cursor` + 官方 Cursor rules/memory 已引用 |
| 是否重复造轮子 | rustworkx/L2-B 使用现有 snapshot；Graphiti 使用 episode/search；Unity 复用 Focus/BBox/PhotoController |
| 是否记录关键决策 | 每个绕过/占位/阻塞写入 worklog |

## 4. 第一轮关键发现

- 现有 `app_v1_longline_self_check_completion_20260510.md` 已完成 facade、Awareness、只读 monitor 和基础 self-check，但明确留下：专业相机 UI、正式 Web 控制台、Graphiti memory core 管理、L2-B 图可视化和素材映射。
- `codex_workspace/skills/unity_ar_app.md` 明确新 App 代码必须进 `unity/ArSpike`，不要往 `unity/ParrotDev` 加新功能。
- `codex_workspace/skills/web_console.md` 建议 read-only first，但本轮用户明确要求测试控制台；因此写操作只做 POST 测试动作，并且每个动作标明是否会写外部系统。
- `Graphiti` 写入应以 episode 为 provenance 单位；Web 页面刷新绝不能写入 episode。
- `rustworkx` 已提供 PyDiGraph 查询、node/edge 计数和 visualization API；App V1 Web 控制台先用已有 L2-B bounded JSON，不新建后端图引擎。

## 5. 外部参考

- Cursor Rules: https://docs.cursor.com/context/rules
- Cursor Memories: https://docs.cursor.com/context/memories
- Graphiti README: https://github.com/getzep/graphiti
- Graphiti Adding Episodes: https://help.getzep.com/graphiti/core-concepts/adding-episodes
- rustworkx PyDiGraph: https://www.rustworkx.org/apiref/rustworkx.PyDiGraph.html
- rustworkx visualization: https://www.rustworkx.org/dev/visualization.html
