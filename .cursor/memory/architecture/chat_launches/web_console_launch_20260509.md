---
status: tentative / chat-launch-prompt
category: chat-launch
status_note: "待开 chat 启动 prompt — Web 控制台 read-only 优先（DSG 可视化 + Ref 仓库 + 模块状态 + 菜单/画布管理）。read+write 在第二轮独立 chat。"
last_reviewed: 2026-05-09
ai_priority: low
ai_audience: "Web 控制台 chat 启动者（启动前读完本文 + Interface/INDEX.md + RustworkX skill 头部）"
parent_doc: "../INDEX.md"
related:
  - "../Interface/INDEX.md (核心/业务二分骨架 + 4 字段业务模板)"
  - "../module_map_p2.md (模块成熟度)"
  - "../bus_v4.md (Bus 拓扑)"
  - "../Interface/menu_design_complete_20260507.md (菜单设计 SSOT)"
  - "../backend_interface_refinement_20260507.md (Brain Core 公开接口)"
  - "../dsg/workspace_index.md (DSG 模块入口)"
---

# Chat Launch — Web 控制台（read-only 优先）

## §1 Scope

构建 Web 控制台（前后端薄壳）作为开发期可视化工具，覆盖 4 大场景的**只读**视图：

1. **DSG 可视化** — L1.5 池 / L2-A 语义节点 / L2-B 图（节点 / 边 / 注意力分数 / scope 激活）
2. **Ref 仓库管理** — Graphiti episode 时间线 + group_id 分区 + Obsidian 3 子类 ingest 状态
3. **模块状态** — Bus 注册表 / Blackboard V2 当前快照 / IntentWorkspace 当前 scope chain / BehaviorMode / VideoTier
4. **菜单/画布管理** — 4 类块（model / persona / mode / scene）当前选择 + 可用预设清单 + 画布节点对照

**read+write 在第二轮**：本 chat **不做**任何 Mutation API；所有写操作（应用预设 / 切换 mode / 调整 ECP 目标）defer 到独立 chat。

## §2 输入（必读，≤ 3 份）

1. [`../Interface/INDEX.md`](../Interface/INDEX.md) — §0 失败教训 + §1 5 模块核心接口指针 + §2 4 字段业务模板
2. [`../module_map_p2.md`](../module_map_p2.md) — 模块职责 + 数据流 + A10 依赖（决定哪些可视化数据来自哪个模块）
3. [`../backend_interface_refinement_20260507.md`](../backend_interface_refinement_20260507.md) — Brain Core 已 ratified 公开接口（menu_registry / preset_loader / intent_workspace / bb_schema 直接复用）

可选回读：
- [`../bus_v4.md`](../bus_v4.md) §通道分类（决定数据通过 RPC / Redis / DataChannel 哪条到 Web）
- [`../Interface/menu_design_complete_20260507.md`](../Interface/menu_design_complete_20260507.md) §三层架构 + §4 类块（Web 控制台菜单视图与 Unity 端一致）
- [`../dsg/workspace_index.md`](../dsg/workspace_index.md) §DSG 当前接口（L2-B graph 可视化数据源）
- `.cursor/skills/dsg-rustworkx-master/` SKILL.md 头部（节点 CRUD / 图查询 API 候选）
- `.cursor/skills/graphiti/` SKILL.md 头部（search / group_id 分区）

## §3 锁（不可动）

- **不动** `protocol_snapshot_p4` 已锁的 wire / topic / BB key（Web 控制台 BFF 走 read-only HTTP/SSE，不引入新 wire 字段）
- **不动** Phase 4 §8 13 决策锁
- **不动** menu_registry / preset_loader / intent_workspace 等已 ratified 接口签名（直接消费）
- 所有可视化数据**必须**走现有 Python API；如发现某场景没有现成 read API（例如"L2-B 全图 dump"），**字段 C 非空时进 protocol upgrade 子 chat**

## §4 不做（显式 defer）

- 任何 write / mutate 操作（应用预设 / 改 mode / 切 ECP）
- Web 鉴权（开发期默认局域网，user 自管）
- Obsidian Web 写回（user 原话"我们可以直接用 Obsidian"）
- 多用户 / 多 session（单 user 单 session）
- 移动端响应式（桌面浏览器优先）

## §5 输出物

- [ ] 4 张业务接口字段 A-D 表（按 [`../Interface/INDEX.md`](../Interface/INDEX.md) §2 模板，4 大场景各一张）
- [ ] BFF（前后端粘合层）位置选型：放 `src/parrot/web_console/`（新建）或独立薄包
- [ ] Frontend 实现位置：建议 `web/console/`（仓库根目录新建子目录）
- [ ] 1 份完成报告（4 场景跑通信号 + 漂移说明）
- [ ] 若发现某场景 read API 缺失（字段 C 非空）→ fork 子 chat 走 protocol upgrade

## §6 业务接口字段 A-D（chat 启动后填，4 张表）

### §6.1 DSG 可视化
- A：（待填）
- B：（待填）
- C：（待填）
- D：（待填）

### §6.2 Ref 仓库管理
- A：（待填）
- B：（待填）
- C：（待填）
- D：（待填）

### §6.3 模块状态
- A：（待填）
- B：（待填）
- C：（待填）
- D：（待填）

### §6.4 菜单/画布管理
- A：（待填）
- B：（待填）
- C：（待填）
- D：（待填）

## §7 启动指令

```
请按 .cursor/memory/architecture/chat_launches/web_console_launch_20260509.md
执行 Web 控制台 read-only 优先实现。

入场顺序：
1. 读本 launch prompt 全文 + §2 三份输入
2. 读 .cursor/memory/architecture/Interface/INDEX.md §0 §1 §2
3. 在本 launch prompt §6 填 4 大场景的字段 A-D（一次填一张表，user 确认后下一张）
4. 4 张表都确认 → 进入 BFF + Frontend 实现
5. 任何场景字段 C 非空，先停下来 fork 子 chat 走 protocol upgrade
```
