---
status: draft / launch-prompt
category: chat-launch-prompt
status_note: "Sub-Chat A 入场 prompt — App Flow / 需求接口 chat（用户视角）。从总 chat（app_completion_master_audit_20260507.md）派发。只产 1 份 doc，不写代码、不动 wire、不重叠 Sub-Chat B 范围。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "新启动的 App Flow / 需求接口 chat（用户视角）"
parent_doc: "app_completion_master_audit_20260507.md"
related:
  - "ar_app_flow_ui_design.md (UI 基线)"
  - "../requirements.md §四 C 段 (Unity 12 项功能)"
  - "backend_interface_refinement_chat_launch_prompt_20260507.md (Sub-Chat B 互不重叠)"
---

# Sub-Chat A — App Flow / 需求接口 chat 启动 Prompt

## §0 Mission

把总 chat §1 8 场景对账表的"用户操作 → UI 反馈 → Unity 端点 → 期望结果"写成**1 份 doc**，覆盖 happy path + 失败路径 + 资产/wire 未到位时的占位策略。**视角 = 用户视角**；**不做后端模块拆解**（那是 Sub-Chat B 范围）。

## §1 入场必读（按顺序，≤ 6 份）

1. ⭐ [`app_completion_master_audit_20260507.md`](app_completion_master_audit_20260507.md) — 总 chat 主 doc（§1 8 场景 + §2 5 finding + §6 像素画资产清单）
2. ⭐ [`ar_app_flow_ui_design.md`](ar_app_flow_ui_design.md) — App Flow / UI 基线（启动页 / HUD / 工具柜 / 占位道具）
3. [`../parrot_behavior_rules.md §3.7 + §4.3`](../parrot_behavior_rules.md) — Tool 体感红线 + 同步 / 异步语义
4. [`../requirements.md §四 C 段`](../requirements.md) — Unity 客户端 12 项功能（C1-C12）
5. [`sprint4_phase4_entry_20260430.md §8`](sprint4_phase4_entry_20260430.md) — Phase 4 §8 13 锁（**避免越界**；不动 wire）
6. [`../protocol_snapshot_p4.md §3`](../protocol_snapshot_p4.md)（仅 §3 EcpEventType 13 项 + §7 RPC 7 method 用作"Unity 端点表"清单）

> **冷读完 6 份应 ≤ 60 分钟**。每份一句话总结写在 cog 里，不输出。

## §2 Scope（in / out）

### §2.1 In scope

**1 份 doc**：`architecture/app_flow_requirements_interface_<date>.md`

结构：
```
§0 TL;DR
§1 启动页流程（菜单选项 + 权限连接 + 加载过场）
§2 HUD + 工具柜布局（展开 / 收纳 / 对角设计原理）
§3 8 场景的用户视角拆解（每场景 1 子章节）
  §3.1 场景 1 GOSLO AR 陪伴对话 — 用户操作 → UI 反馈 → Unity 端点 → 期望结果 + 失败路径 + 占位
  ...（场景 2-8 同结构）
§4 占位策略（资产 / wire / 后端缺口未到位时的 stub）
§5 与 Sub-Chat B 的接口（用户事件 → Brain 端点的 mapping）
§6 引用源
§7 变更日志
```

**每场景子章节必须给出**：
- ① 用户操作步骤（"用户点 / 拖 / 说 ..."）
- ② 期望 UI 反馈（HUD 显示 / 工具柜动效 / GOSLO 表情）
- ③ 调用的 Unity 端点（RPC method / EcpEvent type / DataChannel topic — 仅引用，不发明）
- ④ 失败路径（GOSLO 怎么"说出口"= parrot_behavior_rules §0.3 体感红线）
- ⑤ 占位策略（资产未到位 / wire 未到位 / 后端缺口未到位）

### §2.2 Out of scope（**严禁触动**）

| 项 | 推到哪 |
|:--|:--|
| 后端模块内部接口 / 跨模块 binding | Sub-Chat B |
| 改 wire / 改 enum / 改 BB key | 永不（Phase 4 §8 锁）|
| 设计 ADR / 协议升级 | P3 wire ADR chat / DSG 协议升级 chat |
| 写代码 / 测试 | Chat 4 4-A 实施轨 |
| 设计具体 UI 控件像素细节 | AR 工作区独立 chat（菜单 UI）|
| 发明新 NEED-* 标签 | cross_chat_pending_registry §3/§4 是真源 |
| 写超过 1 份新 doc | 强制硬上限 |

## §3 硬约束

1. **不重写 SSOT** — 总 chat / ar_app_flow_ui_design / protocol_snapshot_p4 只引用
2. **8 场景必须全覆盖** — 不允许"这个场景留 P3"（P3 化由总 chat 派发清单已锁）
3. **失败路径必填** — 每场景的失败路径都要有 GOSLO 体感话术（"我没飞过去，超时了"等），不允许 fire-and-forget 假装成功
4. **占位策略必填** — 每场景必须给出资产 / wire / 后端缺口未到位时的 stub UI 方案
5. **不超 1 份 doc**

## §4 输出物

`architecture/app_flow_requirements_interface_<date>.md` ≤ 1 份，建议 ≤ 600 行。

## §5 启动开局 prompt（直接复制到新 chat）

```
你是 ParrotCarriers App Flow / 需求接口 chat（Sub-Chat A，用户视角）。

任务来源：总 chat 主 doc app_completion_master_audit_20260507.md §3.1 派发清单。
任务定义文件：
@architecture/app_flow_requirements_interface_chat_launch_prompt_20260507.md

行动顺序：
1. 读完 §1 入场必读 6 项（每项一句话总结写 cog 里，不输出）
2. 按 §2.1 doc 结构 § 0-§7 逐节写
3. 每场景子章节按 5 元素填齐（用户操作 / UI 反馈 / Unity 端点 / 失败路径 / 占位）
4. user sign-off 后即可独立交付

硬约束（违反即停）：
- 不动 wire / 不动 enum / 不动 BB key
- 不发明新 NEED-* 标签（cross_chat_pending_registry §3/§4 是真源）
- 不重写 SSOT（总 chat / ar_app_flow_ui_design / protocol_snapshot_p4 只引用）
- 不写代码 / 不写测试 / 不设计 UI 控件像素细节
- 不超 1 份 doc
- 8 场景必须全覆盖（不允许 P3 化）

成功判据：
- 8 场景每个有 5 元素（用户操作 / UI 反馈 / Unity 端点 / 失败路径 / 占位）
- 与 Sub-Chat B 互不重叠（A=用户视角 / B=后端模块视角）
- ≤ 600 行 markdown
- 引用 ≥ 6 个 SSOT 章节锚点

如果发现某场景必须改 wire / 发明新模块 → 在 doc 中标 BLOCKED-BY-NEW-ADR 并引
用对应 NEED-P3-A / TODO(P3-Wire-PlanUI) 等已有标签；不当场设计 ADR。

开始读 §1 入场必读项 1（app_completion_master_audit_20260507.md）。
```

## §6 提问纪律

✅ **应该问 user**：
- 启动页菜单 9 项是否第一版全部必交付（还是先做 5 项 baseline）
- Plan UI wire 未到位时（场景 5），占位是"列表 + approve 按钮"还是"完全跳过让 Brain 直接 approve()"
- 工具柜道具中 P1 优先级（行程单 / 贴图箱 / 任务按钮）哪 1-2 项第一版必含
- 失败路径的 GOSLO 体感话术是否需要 user 钦定（还是 Sub-Chat A 按 §0.3 自决）

❌ **不应该问 user**：
- Unity 端点细节（去 protocol_snapshot_p4 §3 / §7 查）
- 已交付能力的内部接口（去 3 完成报告查）
- UI 控件像素细节（留 AR 工作区 chat）
- 后端模块边界（Sub-Chat B 范围）

## §7.5 入场必读补充（2026-05-07 Interface 工作区建立后更新）

> **新增文件**：读完 §1 原 6 份后，**额外读**以下 3 份（已含 v0 补丁 + 概念词典 + 菜单设计 SSOT）：

| 文件 | 读什么 |
|:--|:--|
| ⭐ `architecture/Interface/interface_design_and_how_todo_v0_20260507.md` | §5.0 S0 启动页（6 项菜单） + §5.9 S9 HUD/工具柜 + §5.3 S3 拍照 + §7 Phase A-C 执行顺序 |
| `architecture/Interface/interface_design_supplement_20260507.md` | §1 v0 新发现（4 级视觉自我感知 / 2 Scene baseline / 三合一意识 / 海盗换肤） + §3 Sub-Chat A 额外子任务 T-A1-T-A4 |
| ⭐ `architecture/Interface/menu_design_complete_20260507.md` | **全文必读** — 三层菜单架构 + 4 类块定义 + 启动页 6 项 + 工具柜道具列表 + 像素画素材清单 + 海盗换肤 + 与 8 场景关联表 |

### §2.1.1 增补子任务（来自 interface_design_supplement §3）

- **T-A1** 启动页第 6 项加"场景 baseline"（DESKTOP_WEBCAM / AR_HANDHELD）的用户选择 UI
- **T-A2** 4 级视觉自我感知的用户 UI 反馈（active 时不显示 / blocked 时浮现"被挡住了"提示）
- **T-A3** 海盗主题切换的用户视角流程（启动页"人设/场景"→ ScriptableObject swap）
- **T-A4** 多设备 input 选择 UI（P3.5 标记，不阻塞主流程）
- **T-A5（新 P2.5）** 2D 独立工作区入口流程（工具柜入口 → Paper Please 风工作区 → 文件批改 + 模块连接设计）：
  - 普通 HUD 工具柜入口：简单按钮（确认/删除/完成）+ 消息提醒 + nanobot 汇报文件
  - 2D 工作区（场景 9 子任务）：文件批改 + 工作区模块连接（类菜单画布所见即所得）
  - Google 日程批改流程：前端修改 → nanobot tasks 同步 → **若开 Google 桶** = Google Node 加入 IntentWorkspace；**若未开** = nanobot 本地处理

## §8 变更日志

- **2026-05-07**：本文创建。Sub-Chat A 入场 prompt（用户视角 App Flow）。
- **2026-05-07（Interface 工作区建立）**：追加 §7.5 新增必读 3 份文件 + §2.1.1 增补子任务 T-A1-T-A5（含新 P2.5 需求：2D 独立工作区 + Google 日程批改流程）。