---
status: tentative / chat-launch-prompt
category: chat-launch
status_note: "待开 chat 启动 prompt — Figma 设计稿 → unity/ArSpike/Assets/UI/ + Cursor 工作区设计参考目录。本任务主要是资产入仓 + Scene wiring，由 Codex+Unity MCP 工作区主导（参考 frontend_workspace_boundary.md）。"
last_reviewed: 2026-05-09
ai_priority: low
ai_audience: "Codex+Unity MCP 工作区启动者；Cursor 仅协同（规范同步 / 像素画清单对账）"
parent_doc: "../INDEX.md"
related:
  - "../frontend_workspace_boundary.md (Cursor vs Codex+Unity MCP 边界)"
  - "../Interface/menu_design_complete_20260507.md (菜单设计 SSOT，含像素画素材清单)"
  - "../app_completion_master_audit_20260507.md §6 (像素画 UI 资产清单 9 类 30+ 项)"
  - "../../lore/ideas.md (海盗主题 / 望远镜 / 镜片滤镜 / Paper Please 风格灵感)"
  - "../Interface/goslo_app_game_overview_asset_brief_20260507.md (App 总览 + 美术 brief)"
---

# Chat Launch — Figma UI 资产入工作区

## §1 Scope

把 user 在 Figma / 像素画工具内自管的 UI 资产入到仓库内可被 Unity 与 Cursor 同时引用的位置，建立**资产摆放规范**与**Scene wiring 规范**：

- **入仓位置**：`unity/ArSpike/Assets/UI/`（Codex+Unity MCP 工作区主导）
- **Cursor 端设计参考**：`docs/design_assets/`（新建）放 Figma 导出的低分辨率参考图 / 设计批注，给 Cursor 工作区在协议 / 接口设计时对照视觉
- **规范同步**：在 `Interface/menu_design_complete_20260507.md` 内追加"资产文件名约定 + 路径约定"小节

**本 chat 不涉及**业务接口字段 A-D 填表（属于纯资产入仓，非接口设计）。

## §2 输入（必读，≤ 3 份）

1. [`../frontend_workspace_boundary.md`](../frontend_workspace_boundary.md) — Cursor vs Codex+Unity MCP 边界（关键：本 chat 主要在 Codex 工作区做）
2. [`../Interface/menu_design_complete_20260507.md`](../Interface/menu_design_complete_20260507.md) — 菜单 SSOT + 像素画素材清单（决定哪些资产对应哪些菜单块）
3. [`../app_completion_master_audit_20260507.md`](../app_completion_master_audit_20260507.md) §6 — 9 类 30+ 项像素画 UI 资产清单（user 自管美术依据）

可选回读：
- [`../../lore/ideas.md`](../../lore/ideas.md) — 海盗主题（眼罩 skin / 望远镜 / 镜片滤镜 / 半边遮挡 / Paper Please 风格 / 猫爪伸出）
- [`../Interface/goslo_app_game_overview_asset_brief_20260507.md`](../Interface/goslo_app_game_overview_asset_brief_20260507.md) — App 总览 + 美术 brief
- [`../ar_app_flow_ui_design.md`](../ar_app_flow_ui_design.md) — UI 入口当前基线（HUD、工具柜、放大镜、注意力框、纸条）

## §3 锁（不可动）

- 资产摆放属于 Codex+Unity MCP 工作区职责（详见 `frontend_workspace_boundary.md` §2.2 + §2.4）
- **不动**协议字段（资产入仓不涉及 wire；菜单 RPC 在 `backend_interface_refinement_20260507` 已 ratified）
- 像素画资产清单的 9 大类 + 30+ 子项以 `app_completion_master_audit §6` 为准；新增类别**先在 user 确认下追加到该清单**再入仓

## §4 不做（显式 defer）

- 美术资产生成（user 自管）
- Unity 内 RuntimeUI 框架重构（用现有 UGUI / UI Toolkit 不切换）
- 声音 / 动画资产（独立 chat 处理）
- 多语言文案 / i18n（user 中文为主，先单语种）

## §5 输出物

- [ ] `unity/ArSpike/Assets/UI/` 子目录树（按菜单 SSOT 4 类块 + HUD + 工具柜 + 海盗主题 skin 分子目录）
- [ ] `docs/design_assets/` Cursor 端设计参考（Figma 导出 PNG / 设计批注 / 海盗主题 mood board）
- [ ] `unity/ArSpike/Assets/UI/README.md` — 资产文件名约定（命名 / 分辨率 / Atlas / Sprite slicing）+ Scene wiring 范式
- [ ] `Interface/menu_design_complete_20260507.md` 追加"资产路径约定"小节
- [ ] Scene wiring：把第一批已就绪的资产摆到 ArSpike 主 Scene + Inspector 接到 menu_registry RPC 端
- [ ] 1 份完成报告（资产入仓清单 + 待补资产清单 + 与 user 确认的命名/路径约定）

## §6 启动指令

启动该 chat 时（**在 Codex+Unity MCP 工作区**）复制以下到首条消息：

```
请按 .cursor/memory/architecture/chat_launches/figma_ui_assets_landing_launch_20260509.md
执行 Figma UI 资产入仓 + Scene wiring 任务（Codex+Unity MCP 工作区主导）。

入场顺序：
1. 读本 launch prompt 全文 + §2 三份输入（特别注意 frontend_workspace_boundary.md §2.2 §2.4 边界条款）
2. 列已就绪资产 + 待补资产清单，与 user 确认
3. 在 unity/ArSpike/Assets/UI/ 创建子目录树
4. 写 README + 追加菜单 SSOT 资产路径约定
5. 把第一批资产摆进 Scene + Inspector wire
6. 全程不动 protocol_snapshot_p4 / Brain Core 接口；如发现 RPC 缺失，在 cross_chat_pending_registry 写 NEED 后切 Cursor 工作区处理
```

## §7 与 Cursor 工作区的协同

按 [`../frontend_workspace_boundary.md`](../frontend_workspace_boundary.md) §3.1 流程：

- Codex 摆资产 + Scene wiring → 完成后在 `cross_chat_pending_registry` 加一行 `[Codex → Cursor] Interface/menu_design_complete §资产路径约定 已追加，请审核`
- Cursor 审核 + 同步到 `Interface/menu_design_complete_20260507.md`
- Cursor 在 INDEX.md §六 Design 列内出现新资产路径条目（如有需要）
