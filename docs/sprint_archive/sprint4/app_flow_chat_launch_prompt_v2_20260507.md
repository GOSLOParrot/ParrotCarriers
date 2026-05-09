---
status: draft / launch-prompt-v2.2-app-build
category: chat-launch-prompt
status_note: "Sub-Chat A v2.2 启动 prompt — 从 doc-only 调研升级为 AR App 白模实施 chat。新增：① 直接开始 unity/ArSpike App 白模制作 ② 使用 backend_interface_refinement_20260507 后端菜单接口 ③ 完整实现已设计/已测试的 LiveKit 生命周期 ④ 允许小后端补充接口（必须标 frontend-supplement，不动 DSG/Plan/wire 锁）。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sub-Chat A AR App 白模实施 chat + Unity 前端菜单 / 生命周期实施"
parent_doc: "app_completion_master_audit_20260507.md"
supersedes: "app_flow_requirements_interface_chat_launch_prompt_20260507.md"
---

# Sub-Chat A v2.2 — AR App 白模实施 + 前端菜单 / 生命周期 chat

## §0 Mission（一段话）

代码先行 → 把 `unity/ArSpike/Assets/Scripts/ParrotApp/` + LiveKit 生命周期 skill + 菜单设计 + `architecture/backend_interface_refinement_20260507.md` 读进来 → **直接开始做 AR App 白模**：完整接入已设计/已测试的 LiveKit 连接生命周期，完成启动页 / HUD / 工具柜 / 简单 2D 工作区白模，消费后端菜单接口（list / apply / preset），并在必要时补少量 frontend-supplement 后端薄接口。**不动 wire / 不重写 SSOT / 不进 DSG 核心与 Plan/Scheduler**。

---

## §1 工作区域（硬边界）

| 范围 | 路径 | 角色 |
|:--|:--|:--|
| **可读 + 可改代码** | `unity/ArSpike/Assets/Scripts/ParrotApp/` | AR App 白模主场（Lifecycle / LiveKit / Ecp / HUD / Toolbar / Menu / Photo / Attention / Parrot / RPC） |
| **可读** | `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md` | 迁移台账 + 不允许误读 |
| **可读** | `unity/ArSpike/README.md` | ArSpike 双角色说明 |
| **可读 + 可改 doc** | `architecture/ar_*.md` | AR 工作区文档（修 drift OK；不重写 SSOT）|
| **可读 + 可改 doc** | `architecture/Interface/*.md` | Interface 工作区文档（同上）|
| **可读 + 可改入口** | `architecture/ar_workspace_index.md` | 登记 backend interface doc + App 白模进度 |
| **只读 + 必用接口** | `architecture/backend_interface_refinement_20260507.md` | 后端菜单 / BB / IntentWorkspace / L2-B baseline 接口真源；前端直接消费 |
| **只读 引用** | `architecture/sprint4_phase4_entry_20260430.md §8` | Phase 4 §8 13 锁（不动）|
| **只读 引用** | `architecture/protocol_snapshot_p4.md` | 协议 SSOT（不重写）|
| **只读 引用** | `architecture/dsg/*.md` | DSG 工作区（Sub-Chat B 主场；本 chat 仅引用交集 — EcpEvent / PhotoNode / RefBinding） |
| **⚠ 可读 + 小补丁** | `src/parrot/brain/{menu_registry.py,preset_loader.py,persona_loader.py,bb_watchers.py}` + `src/parrot/brain/tools/` 薄 RPC/HTTP adapter | 仅当前端接入缺少薄端点时可补；必须注释 `frontend-supplement` + 更新接口 doc |
| **❌ 不读 / 不动** | `src/parrot/dsg/` / `src/parrot/brain/plan/` / `src/parrot/scheduler/` / `src/parrot/shared/ecp*.py` | DSG / Plan / Scheduler / wire 主场；不得为前端方便改核心协议 |
| **❌ 不读 / 不动** | `unity/ParrotDev/` | Sprint 1-3 测试床（冻结）|

---

## §2 入场必读（≤ 8 份；按顺序读完再做事）

1. **本文件**（任务定义）
2. ⭐ `architecture/backend_interface_refinement_20260507.md` — **后端菜单接口已交付**（MenuRegistry / PresetLoader / 4 active BB / IntentWorkspace / L2-B baseline）
3. ⭐ `architecture/Interface/menu_design_complete_20260507.md` — 完整菜单设计（启动页 / HUD / 工具柜 / 4 类块 / 节点画布 / 2D 工作区入口）
4. ⭐ `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` §5（12 场景 + 4 横切关注点）+ `interface_design_supplement_20260507.md` §1（7 项新发现）
5. ⭐ `architecture/ar_workspace_index.md` + `architecture/ar_app_flow_ui_design.md` — AR 工作区入口 + App Flow / UI 基线
6. ⭐ `.cursor/skills/livekit-unity-lifecycle/SKILL.md` + `IMPL_REF.md §1-§6` — 11 态 FSM / 重连 / 切后台 / ARCore 黑帧 / audio route / setVideoTier 副作用
7. ⭐ `.cursor/skills/client-sdk-unity/SKILL.md` + `.cursor/skills/livekit-unity-video-publish/SKILL.md` — LiveKit RPC/DataChannel + 一流多采样 / Photo 双通道
8. **代码扫一遍**（实现前建索引）：
   - `unity/ArSpike/Assets/Scripts/ParrotApp/{Lifecycle,Ecp,Photo,Attention,Parrot,RPC,LiveKit}/` 各文件名 + 一句话职责
   - `unity/ArSpike/Assets/Scripts/ParrotApp/MIGRATION.md`

> **冷读完**应 ≤ 90 分钟；每份一句话总结写在 cog 里，不输出。先读 skill，再动 LiveKit 生命周期代码。

---

## §3 6 个任务（按权重 + 推进顺序）

### Task 1 — 代码现状审查（先读代码再实现；权重 10%）

目标：搞清楚 `unity/ArSpike/` 现在真实有什么、缺什么。不要用 Interface 文档当真源；代码是真源。

做法：
- 列 `ParrotApp/` 各子目录文件清单 + 类清单
- 对照 `Interface/menu_design §1-§5`（启动页 / HUD / 工具柜 / 4 类块 / 节点画布 / 默认 fallback）判断已有 / 缺口 / 可复用
- 对照 `backend_interface_refinement_20260507.md §5` 判断前端需要消费哪些后端接口

输出锚点：写到实现日志 / PR summary；不要先写长 doc 阻塞实现。

### Task 2 — LiveKit 连接生命周期完整实现（权重 25%）

目标：把已设计/已测试的生命周期能力真正落入 ArSpike App 白模启动链。

必须覆盖：
- 11 态 FSM：Unbooted → Booting → Booted → ConnectingLiveKit → AwaitingPermissions → SessionWarming → SessionReady → SessionLive → SessionPaused → SessionRecovering → SessionShuttingDown
- Token Mint → Room connect → permissions → AR session start → onSceneReady 单问候去重
- OnApplicationPause 短/长后台策略、30s ICE 残留 / identity 抢占防御、ARCore 黑帧 / pause-resume 缓解
- connection health 聚合（audio + video + brain_presence + ar_tracking）并驱动 HUD icon
- setVideoTier cool-down / hold_seconds 路径；Photo 双通道仍按 Phase 4 W8

技能入口：`livekit-unity-lifecycle/IMPL_REF.md §1-§6` + `client-sdk-unity/SKILL.md`。

### Task 3 — 2D 工具区 + 菜单白模实现（权重 25%）

目标：完成能跑的前端白模，不等美术：启动页 6 项、HUD、工具柜、2D 工作区入口、菜单 4 类块 fallback。

白模范围：
- 启动页 6 项：开始 AR / room / pipeline / persona-preset / scene baseline / 权限连接测试
- HUD：连接、音频、视频档位、brain presence、visual_state、时间 / 天气占位
- 工具柜 P0：设置 / 相机模式 / 拍照 / 放大镜 / 注意力框 / 常用任务按钮
- 简单 2D 工作区白模：报告/消息/提醒卡片列表 + accept / reject / open detail 占位
- 菜单 fallback：调用后端 `listMenuBlocks` / `applyMenuSelection` / `applyPreset` / `saveAsPreset`，不直接写 BB

后端接口真源：`backend_interface_refinement_20260507.md §1 / §5`。

### Task 4 — 前端补充后端薄接口（权重 15%）

目标：前端实现过程中如发现缺少薄端点 / adapter，可以就地补，但不得变成后端架构大改。

允许补：
- Brain RPC / HTTP thin adapter：`listMenuBlocks` / `applyMenuSelection` / `applyPreset` / `saveAsPreset`
- 只为前端白模服务的小 DTO / JSON wrapper / error mapping
- Unity C# DTO mirror 与 Python JSON shape 对齐（不新增 EcpEventType）

必须标注：
- 代码注释含 `frontend-supplement` + 说明调用方
- 文档同步到 `backend_interface_refinement_20260507.md` 或本 prompt 变更日志
- 如触动 `.py`，只限 `src/parrot/brain/{menu_registry,preset_loader,persona_loader,bb_watchers}` 或极薄 RPC adapter；不动 DSG/Plan/Scheduler

禁止：
- 新增 wire / enum / EcpEventType
- 改 `src/parrot/dsg/` 核心、`brain/plan/`、`scheduler/`
- 为 Plan UI 创建新 wire；仍用占位 stub

### Task 5 — AR 工作区文档 drift 修复（权重 10%）

修哪些 doc（按重要度）：

| Doc | 修什么 | 不动 |
|:--|:--|:--|
| `ar_workspace_index.md` | 登记 `backend_interface_refinement_20260507.md` + App 白模进度 + GOSLO 4 报告（如缺）+ broken link 修 | 不重写 §1-§8 |
| `ar_app_flow_ui_design.md` | 如实现与启动页 / HUD / 工具柜 baseline 有 drift，仅追加 1-5 行实现注脚 | 不动用户原话 §2 / §3 |
| `ar_feature_vision.md` | 如需引用 4-scope BB / 三合一意识 / 4 级视觉自我感知，只追加一行交叉引用 | 不动 §1-§9 |
| `Interface/menu_design_complete_20260507.md` | 如前端白模接口名与菜单设计不一致，追加实现注脚 | 不重写 |

原则：修 drift 不是大改；引用而非复制；旧文本不变。

### Task 6 — 整体白模验收 + 自定义动画接入 smoke（权重 15%）

目标：完成整个项目白模闭环，并用标准 GOSLO 动画 + 一个自定义动画/模型（Ner）做 smoke。

验收链路：
- App 启动 → Token Mint → LiveKit connect → AR session ready → GOSLO 问候
- 菜单 fallback 读取后端 blocks → apply preset → HUD 状态同步
- 工具柜拍照按钮 → PhotoController.CapturePhoto → preview/event/asset path 不破
- 相机模式按钮 → setVideoTier → HUD video icon 变化
- 注意力框 / 放大镜白模 → bbox/focus event path 保持 Phase 4 W6-7
- GOSLO 标准动画：idle / fly / dance / wing_flap / head_bob / perch / sit / sleep 任一 smoke
- 自定义动画/模型 Ner 接入 smoke：走 `ModelManifest` / `ModelDriver` / `ParrotRegistry` fallback，不改 ParrotAnimation 8 项 enum

输出：实现日志 + 测试记录 + 如有 bug，写 frontend-supplement TODO；不再产长篇 App Flow doc 作为主产物。

---

## §3b 可选短文档（只在需要时写）

若实现过程中必须补用户视角说明，可写 `architecture/app_flow_requirements_interface_<date>.md`，但它不再是阻塞产物。建议结构：

```markdown
§0 TL;DR + Task 1 代码现状摘要表
§1 启动页流程（#1-#6 baseline + 调试折叠）
§2 HUD + 工具柜布局（占位策略 + 持久化）
§3 8 场景 × 5 元素子章节
§4 与 Sub-Chat B 接口（用户事件 → Brain 端点 mapping）
§5 4 级视觉自我感知 + Soul 8 条强制话术 UI 反馈
§6 海盗主题换肤（NEED-P3-PIRATE-SKIN）切换流程
§7 引用源
§8 变更日志
```

长度上限：≤ 400 行。

---

## §4 输出物清单（代码为主）

| # | 文件 | 类型 | 长度 |
|:--|:--|:--|:--|
| 1 | `unity/ArSpike/Assets/Scripts/ParrotApp/` | 主产物：App 白模代码（Lifecycle / LiveKit / Menu / HUD / Toolbar / Workspace / RPC adapters） | 按实现需要 |
| 2 | `architecture/ar_workspace_index.md` | patch：登记 backend interface doc + App 白模进度 | ≤ 30 行新增 |
| 3 | `architecture/ar_app_flow_ui_design.md` | patch：如实现与 UI 基线有 drift，最小更新 | ≤ 15 行新增 |
| 4 | `architecture/app_flow_requirements_interface_<date>.md` | 可选短文档：只在实现需要时写 | ≤ 400 行 |
| 5 | `src/parrot/brain/*` 薄 adapter | 可选 frontend-supplement 后端小接口 | 必须注释 + 测试 |

---

## §5 硬约束（违反即停）

1. **代码先行** — Task 1 没读完代码不允许动生命周期 / 菜单代码
2. **允许写 Unity C#** — 主场是 `unity/ArSpike/Assets/Scripts/ParrotApp/`
3. **小后端补充必须薄** — 仅 frontend-supplement RPC/HTTP adapter；必须写注释和文档；不得改 DSG/Plan/Scheduler
4. **不动 wire / enum / BB key** — Phase 4 §8 13 锁 + cs_parity 4/4；4 active BB 已由后端接口 doc ratified，前端只消费
5. **不重写 SSOT**（Interface/ 4 文件 / protocol_snapshot_p4 / module_map_p4_snapshot / 3 完成报告 / cross_chat_pending_registry）
6. **不发明新 NEED-* 标签** — `cross_chat_pending_registry §3 / §4` 是真源；bug 用 `frontend-supplement-*` 注释而非新 NEED
7. **App 白模闭环必须能跑** — 启动 / 连接 / 菜单 / HUD / 工具柜 / 2D 工作区入口 / GOSLO 动画 smoke
8. **失败路径必填** — UI 状态、toast/纸条、GOSLO 体感话术必须有
9. **不动 user 原话** — `ar_app_flow_ui_design.md §2 / §3` 用户原话区不动
10. **不进 DSG 工作区** — `architecture/dsg/` / `src/parrot/dsg/` 是 Sub-Chat B 主场；只读 `backend_interface_refinement_20260507.md`

---

## §6 启动开局 prompt（直接复制到新 chat）

```markdown
你是 ParrotCarriers Sub-Chat A v2.2（AR App 白模实施 + 前端菜单 / 生命周期 chat）。

任务定义：
@architecture/Interface/app_flow_chat_launch_prompt_v2_20260507.md

工作区域硬边界：
- 可读 + 可改代码: unity/ArSpike/Assets/Scripts/ParrotApp/
- 可读 + 可改 doc: architecture/ar_*.md + architecture/Interface/*.md + ar_workspace_index.md
- 必读后端接口: architecture/backend_interface_refinement_20260507.md
- 技能必读: livekit-unity-lifecycle + client-sdk-unity + livekit-unity-video-publish
- ⚠ 可小补后端: src/parrot/brain/{menu_registry,preset_loader,persona_loader,bb_watchers} 或薄 RPC/HTTP adapter，必须标 frontend-supplement
- ❌ 不读/不动: src/parrot/dsg/ / brain/plan/ / scheduler/ / unity/ParrotDev/
- ❌ 不动: wire / enum / EcpEventType / cs_parity 锁

行动顺序（6 任务）：
1. 读 §2 入场必读 8 份 + 扫 unity/ArSpike 代码
2. 完整实现 LiveKit 连接生命周期（11 态 FSM / token mint / permissions / reconnect / pause-resume）
3. 完成 2D 工具区 + 菜单白模（启动页 / HUD / 工具柜 / 2D 工作区入口 / 4 类块 fallback）
4. 必要时补 frontend-supplement 后端薄接口（listMenuBlocks / applyMenuSelection / applyPreset / saveAsPreset adapter）
5. 最小 doc drift 修复（登记 backend_interface_refinement_20260507.md + 实现差异）
6. 整体白模验收 + GOSLO 标准动画 + Ner 自定义动画/模型 smoke

硬约束（10 条，§5）：
- 代码先行 / 可写 Unity / 小后端补充必须薄 / 不动 wire
- 不发明新 NEED-* / 不重写 SSOT
- App 白模闭环能跑 / 失败路径必填 / 不动 user 原话 / 不进 DSG 核心

提问纪律（§7）：
- 应该问 user：2D 工具区白模布局 / 启动页视觉优先级 / Ner 动画资源路径
- 不应该问：LiveKit 生命周期设计（读 skill）/ 后端菜单接口字段（读 backend_interface_refinement）/ wire 字段（读 protocol_snapshot_p4）

成功判据：
- App 可从启动页进入 AR 主场景并完成 LiveKit connect / reconnect / pause-resume smoke
- 菜单白模可读取后端 blocks 并 apply preset / selection
- HUD/工具柜/2D 工作区入口可交互，状态反馈完整
- Photo / setVideoTier / BBox/Focus 既有路径不破
- GOSLO 标准动画 smoke + Ner 自定义动画/模型 smoke 通过

如发现某场景必须改 wire / 发明新模块 → 在 doc 标 BLOCKED-BY-NEW-ADR + 引用对应 NEED 标签；不当场设计 ADR。

开始读 §2 入场必读项 1（本文件）。
```

---

## §7 提问纪律

✅ **应该问 user**：
- 2D 工具区白模具体布局（卡片列表 / 抽屉 / 纸条样式）
- 启动页 6 项是否第一版全交付（默认全交付；如资源不足才折叠）
- Ner 自定义动画/模型资源路径、manifest 名称、期望 smoke 动画名
- 如果 frontend-supplement 后端薄接口需要新增 HTTP/RPC endpoint，确认 endpoint 命名是否沿用 `listMenuBlocks` / `applyMenuSelection` / `applyPreset` / `saveAsPreset`

❌ **不应该问 user**：
- Unity 代码细节（去读源文件）
- 协议字段（去 `protocol_snapshot_p4 §3 / §7`）
- 已交付能力（去 3 完成报告）
- 后端菜单接口字段（去 `backend_interface_refinement_20260507.md`）
- LiveKit 生命周期策略（去 `livekit-unity-lifecycle/IMPL_REF.md`）
- DSG 后端（Sub-Chat B 范围）

---

## §8 变更日志

- **2026-05-07 v2**：本文创建。replace v1（保留作历史）。新增：工作区域硬边界 / 代码先行 / AR 工作区文档 drift 修复 / 工作区完整性 audit；输出从 1 份扩到 3 份（1 主 + 2 patch）。
- **2026-05-07 v2.1（backend ready 注脚）**：后端菜单接口、4 active BB 写入路径、IntentWorkspace、L2-B baseline 真算法已交付（见 `architecture/backend_interface_refinement_20260507.md`）。前端可直接消费 RPC：`listMenuBlocks` / `applyMenuSelection` / `applyPreset` / `saveAsPreset`，无须等接口提炼 doc。Persona / Preset 块第一版可继续用占位 stub UI，但后端真功能已 ready，切真 dropdown 不再阻塞。
- **2026-05-07 v2.2（App build mode）**：任务从“用户视角 App Flow doc”升级为“直接开始 AR App 白模实施”。新增：完整 LiveKit 生命周期实现、启动页/HUD/工具柜/2D 工作区白模、后端菜单接口消费、frontend-supplement 薄后端接口规则、GOSLO 标准动画 + Ner 自定义动画/模型 smoke。输出改为代码为主，doc 只做 drift / 实现日志。
