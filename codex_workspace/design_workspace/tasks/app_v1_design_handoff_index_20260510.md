# App V1 设计交接索引与自检标准

> 建立日期：2026-05-10  
> 用途：给后续长线 Chat / Codex 任务直接接手第一版 App 设计、Unity 白膜、素材落位和自检。  
> 原则：先完成 App 体验闭环，再反推 Web 控制台；先用白膜素材占住真实插槽，再替换最终美术。

## 0. 任务目标

第一版 App 不是“漂亮首页”，而是跑通一条可以验证架构理解的使用链路：

1. 用户在横屏启动页选配置。
2. App 请求必要权限。
3. 进入 IPoAC 风格转场/进度条页面，同时启动 LiveKit 连接。
4. LiveKit 连接成功后不主动打招呼。
5. 进入 AR 主界面，识别平面。
6. 用户点击放置 2D 像素鹦鹉或占位模型。
7. 鹦鹉做疑问/醒来动作，然后打招呼。
8. HUD、工具抽屉、菜单画布可以打开；展开前不挡视野，展开后允许遮挡。
9. 用户可以切到 2D 工作区，LiveKit session 不销毁。
10. Model / Persona / Mode / Scene / 2DWorkspace 五类菜单块能表达当前设置和连接状态。

## 1. 必读文档索引

### 设计工作区入口

| 文档 | 用途 |
|:--|:--|
| `codex_workspace/design_workspace/INDEX.md` | 设计工作区总入口。 |
| `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md` | 当前设计阶段和下一步。 |
| `codex_workspace/design_workspace/00_original_words/chat_original_20260509_startup_menu_assets.md` | 用户关于启动页、HUD、2D 工作区、像素风格的原话。 |
| `codex_workspace/design_workspace/00_original_words/today_request_digest_20260509.md` | 本轮需求摘要。 |

### App UI / 交互

| 文档 | 用途 |
|:--|:--|
| `codex_workspace/design_workspace/unity_ar_app/app_v1_whitebox_shell_20260510.md` | 第一版 App 白膜总壳：页面、菜单画布、外部模块 Dock。 |
| `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md` | 横屏启动页设计。 |
| `codex_workspace/design_workspace/unity_ar_app/main_hud_landscape_v0_20260509.md` | AR 主界面 HUD / 工具抽屉布局。 |
| `codex_workspace/design_workspace/unity_ar_app/menu_canvas_mvp_2dworkspace_20260509.md` | 菜单画布 MVP，新增 2DWorkspace 块。 |
| `codex_workspace/design_workspace/unity_ar_app/menu_canvas_external_modules_20260509.md` | Google / Obsidian / GOSLO / Nanobot / Photo 外部模块 Dock 思路。 |
| `codex_workspace/design_workspace/app_2d_workspace/workspace_mansion_reference_20260509.md` | 2D 宅邸、工作桌、报告/审批交互参考。 |

### 可预览草图

| 文档/页面 | 用途 |
|:--|:--|
| `codex_workspace/design_workspace/sketches/INDEX.md` | HTML 草图入口。 |
| `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html` | 启动页布局预览。 |
| `codex_workspace/design_workspace/sketches/startup_transition_ipoac_v0.html` | IPoAC 转场/进度条预览。 |
| `codex_workspace/design_workspace/sketches/main_hud_landscape_v0.html` | AR 主界面 HUD / 工具抽屉预览。 |
| `codex_workspace/design_workspace/sketches/menu_canvas_mvp_v0.html` | 菜单画布 MVP 预览。 |

### 素材与参考

| 文档 | 用途 |
|:--|:--|
| `codex_workspace/design_workspace/asset_pipeline/reference_assets_20260509.md` | 用户给的参考图归档和理解。 |
| `codex_workspace/design_workspace/asset_pipeline/pixel_asset_selection_20260510.md` | 当前 Pixel Asset 整理结果。 |
| `codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace/README.md` | Pixel Asset 原始包、解压区、精选区说明。 |
| `codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace/curated/README.md` | 第一版白膜具体从哪些素材文件夹取。 |
| `codex_workspace/design_workspace/asset_pipeline/pixel_asset_workspace/curated/00_previews/` | 素材预览图。 |
| `codex_workspace/design_workspace/asset_pipeline/reference_images/manifest_20260509.md` | 6 张关键参考图清单。 |

### 后端理解与接口边界

| 文档 | 用途 |
|:--|:--|
| `codex_workspace/design_workspace/backend_interface_map/module_collaboration_brief.md` | 后端模块如何协作的设计用摘要。 |
| `codex_workspace/design_workspace/backend_interface_map/app_v1_core_business_interface_coverage_20260510.md` | App V1 需要覆盖的核心/业务接口。 |
| `codex_workspace/design_workspace/backend_interface_map/menu_canvas_external_modules_business_flow.md` | 菜单画布外部模块业务流。 |
| `codex_workspace/design_workspace/tasks/chatA_livekit_flow_prompt_20260509.md` | LiveKit / 启动流程 / 连接稳定性 ChatA 提示词。 |

### 后端 SSOT 入口

这些是事实源，不要用设计文档替代：

| 文档 | 用途 |
|:--|:--|
| `.cursor/memory/INDEX.md` | 后端真源路由总入口。 |
| `.cursor/memory/architecture/module_map_p2.md` | 模块职责、数据流、成熟度矩阵。 |
| `.cursor/memory/architecture/module_map_p4_snapshot.md` | P4 阶段模块快照。 |
| `.cursor/memory/architecture/protocol_snapshot_p4.md` | 当前协议真源。 |
| `.cursor/memory/architecture/Interface/INDEX.md` | 接口分类规则和业务接口模板。 |
| `.cursor/memory/architecture/backend_interface_refinement_20260507.md` | 后端核心接口归纳第一版。 |
| `.cursor/memory/architecture/Interface/menu_design_complete_20260507.md` | 4-block 菜单设计真源。App V1 已提出增加 2DWorkspace 块，需要写明 reason。 |

## 2. App V1 通过标准

### 功能闭环

- 启动页能表达 `Scene` 入口、`Room Setting` 展开菜单、`Start`、模式切换、退出/设置入口。
- 启动页只做配置与进入，不把 IPoAC 进度条塞在首页；转场动画是独立页面。
- LiveKit 连接流程和 UI 流程能对齐：开始连接、连接中、已连接但静默、AR ready、placed 后才问候。
- AR 主界面有清晰的摄像头背景层、左上 HUD 折叠块、右下工具抽屉折叠块。
- HUD 和工具抽屉折叠态足够小，不遮挡视野；展开态可以遮挡，但可关闭、可回到低遮挡状态。
- 菜单画布至少有 `Model / Persona / Mode / Scene / 2DWorkspace` 五类块，能表达连接、未连接、禁用、只保持 session 等状态。
- 2D 工作区入口存在，切换时 LiveKit session 不销毁。
- Obsidian / Google / Photo / Nanobot / GOSLO 外部模块可以先作为 Dock 或灰态节点出现，但不能假装已经完成真实连接。

### 视觉与布局

- 横屏优先，按手机横屏设计；UI 使用可缩放锚点，不依赖固定 iQOO Neo9 绝对像素。
- 像素字体统一，按钮和面板文本不溢出。
- 所有核心 UI 有素材插槽：标题牌、2D 模型形象、Scene 面板、Start 按钮、Mode 拉杆、进度条、HUD、工具抽屉、菜单节点、2D 房间、工作桌纸张。
- 当前素材主风格使用 `Magic + Book/Paper/Wood + ModernInteriors`，不要混成过多不相干 UI 包。
- 2D 工作区应像“宅邸里的功能房间”，不是普通后台 dashboard。
- 工作桌交互参考 Papers Please：纸张、印章、批准/驳回、归档、丢弃、报告反馈，而不是表单堆叠。

### 连接状态表达

- 用户能看懂四档能力模式：
  - 保持 session，不说话。
  - 保持对话，不视频。
  - 保持对话和视频，不监控动作。
  - 全开。
- 断连、重连、权限缺失、设备切换都要有 UI 状态位。
- 蓝牙设备、扬声器、麦克风切换需要设计成“可失败但不崩溃”的流程，至少有状态反馈。
- 平面未识别、已识别但未放置、已放置、角色 ready 四种 AR 状态要区分。

### 素材落位

- Unity 白膜不得直接导入 `extracted/moderninteriors-win` 全量。
- 第一版优先导入 `pixel_asset_workspace/curated/` 子集。
- UI 图片导入建议：`Sprite (2D and UI)`、`Filter Mode = Point (no filter)`、需要拉伸的面板后续做 9-slice。
- Tilesheet 当前优先 16x16：`moderninteriors` room builder 和 theme sheets。
- 鹦鹉主角色、IPoAC 飞行动画角色、GOSLO logo 仍是待定插槽，不要被当前通用素材锁死。

### 文档固化

- 每次完成一个页面/流程，要更新对应设计文档，而不是只改 Unity 场景或 HTML。
- 如果新增核心接口、协议字段、菜单块，必须在设计文档写 `reason:`，并对照 `.cursor/memory/architecture/Interface/INDEX.md`。
- 如果新增正式后端 SSOT 文档，才需要登记 `.cursor/memory/INDEX.md`；设计工作区内部文档不需要污染 memory。
- 自检报告要记录：完成项、未完成项、偏离原设计的地方、为什么偏离、下一轮需要用户审查的问题。

## 3. 漂移检查

长线任务每轮结束时至少检查这些问题：

1. 是否仍然是“App first”，而不是提前转成 Web 控制台设计？
2. 是否仍然是“横屏 AR 主体验 + 2D 工作区”，而不是普通移动 App 首页？
3. 是否仍然保留用户原话中的像素风、鹦鹉、IPoAC 转场、宅邸工作区、Papers Please 式工作桌？
4. 是否把 Obsidian / Google 当作外部软件和外挂模块，而不是在 App 里重新做文件管理/日历管理？
5. 是否把 LiveKit session 保持和能力开关分离，而不是每次切模式就销毁 session？
6. 是否只在真实连接完成后标记模块 ready，没有用假 UI 掩盖状态？
7. 是否把 `2DWorkspace` 作为菜单画布里的新增块处理，并写清楚它为什么需要超出原 4-block？
8. 是否避免把素材包全量导入工程，导致 Unity 项目膨胀？

## 4. AR 素材使用背景

当前 AR App 里的“2D 像素风”不是临时贴图风格，而是产品语言：

- AR 层负责现实摄像头、平面识别、放置、角色在现实中的存在感。
- Meta UI 层负责菜单、HUD、工具抽屉、状态反馈。
- 2D 工作区层负责把复杂任务变成可操作的“宅邸房间”和“工作桌物件”。
- 像素素材的作用是降低复杂系统的压迫感，让 GOSLO / Nanobot / Google / Obsidian 这些模块变成可被看见、可被拖动、可被连接、可被批准或驳回的对象。

素材使用建议：

- `MagicalUI`：给系统级 UI，一眼看起来像 GOSLO 的魔法书/任务书。
- `Wood UI`：给启动按钮、抽屉、工具栏，负责触感和操作感。
- `Paper UI`：给报告、审批、日志、Obsidian/Google 反馈。
- `Book UI / Fantasy Book UI`：给菜单画布节点、模块详情页、设定页。
- `AdventureUI`：只做小面积图标和强调，不当主风格。
- `ModernInteriors`：只做 2D 宅邸、工作房间、书桌环境，不混进 AR HUD 主 UI。

## 5. 页面达成目标

### 启动页

- 画面结构简单，像游戏标题页。
- 标题是 `GOSLO Parrot`，后续可替换正式 Logo。
- 只露出 `SCENE` 入口；点击后才进入 Room Setting。
- `START` 旁有 Mode 切换或像素拉杆。
- 2D 模型形象插槽与 Room Setting 里的模型选择绑定。

### 启动转场

- 单独页面，不挤在启动页。
- IPoAC 风格：低保真进度条、飞行动画、慢吞吞状态文案、最后瞬间 100%。
- 连接 LiveKit 时不要求视觉完全真实，但状态顺序要真实。

### AR 主界面

- 默认视野干净，只保留左上 HUD 小块和右下工具抽屉小块。
- HUD 展开后显示 session、room、mode、connection、plane/placement、audio/video 状态。
- 工具抽屉展开后显示相机、PhotoNode、菜单画布、2D 工作区、设备/权限等入口。
- 两个展开栏可以重叠，但重叠区域不放关键信息。

### 菜单画布

- 第一版只需跑通 Model / Persona / Mode / Scene / 2DWorkspace。
- 外部模块先作为 dock：Obsidian、Google、Photo、Nanobot、GOSLO Module。
- 连接线要表达“能力接入”和“状态流”，不要只是装饰线。
- 未连接模块必须有灰态/锁定/待配置状态。

### 2D 工作区

- 是宅邸主大厅 + 工作房间，不是 Web 控制台。
- 用户可以进入不同工作桌处理纸条、报告、日程、照片、设定 Node。
- 角色可以作为副驾驶/模块拟人存在，但第一版只需要占位。

## 6. 推荐长线任务输出

长线任务跑完后建议输出：

1. `App V1 完成报告`：页面完成度、素材落位、交互闭环、已知缺口。
2. `自检报告`：按本文第 2-3 节逐项标记 pass / partial / fail。
3. `漂移报告`：哪些地方偏离用户原话，偏离理由是什么。
4. `Unity 导入清单`：哪些 curated 素材进入 Unity，路径是什么，导入设置是什么。
5. `下一轮用户审查清单`：只列需要用户判断的视觉和体验问题。
