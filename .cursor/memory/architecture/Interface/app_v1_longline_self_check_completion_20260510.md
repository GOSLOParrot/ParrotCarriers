---
title: App V1 Longline Self-check Completion Record
date: 2026-05-10
status: completed
owner: Chat B / App V1
scope: autonomous App V1 self-check target, Awareness v1, read-only Web monitor, Unity MCP smoke validation, architecture drift audit
related:
  - app_v1_facade_core_business_interface_20260510.md
  - photo_memory_awareness_true_connection_guide_20260509.md
  - obsidian_true_connection_guide_20260509.md
  - google_calendar_nanobot_true_connection_guide_20260509.md
---

# App V1 长线自检完成记录

## 0. 目标

本轮把第一版 App 需要的核心接口和业务接口跑到可自检状态，而不是只写设计草案。验收目标：

- 菜单画布可以通过统一 facade 读到 Google / Obsidian / GOSLO / Nanobot / Photo / XRHand / Canvas 七个模块状态。
- 2DWorkspace 与 IntentWorkspace 分开：2DWorkspace 只显示工作桌、纸条、照片 ref；IntentWorkspace 持有 draft、report、photo preview 等 payload/ref。
- Obsidian 三 profile 固化：`daily` / `roleplay` 设定不要求 UUID；`ref` 才是加强已有 Graphiti/L2-B 节点的 UUID 绑定源。
- Google 写操作先进入 IntentWorkspace draft，不让 App 菜单直接写外部日历。
- 照片链路支持 GOSLO Awareness v1：preview 到达时可 stage 短期 ref，让 GOSLO 知道拍照，但第一版不允许 interrupt。
- Web monitor 只读验证运行状态，先不做正式 Web 控制台。

## 1. 关键实现

| 模块 | 产物 | 说明 |
|:--|:--|:--|
| App facade | `src/parrot/brain/app_first_version.py` | 新增 `canvas_snapshot()`、`apply_workspace()`、纸条和照片 ref read model |
| Awareness | `src/parrot/brain/photo_awareness.py` | 三态 policy、preview TTL、`transient/photo_awareness_notice`、IntentWorkspace preview ref |
| Photo Observer | `src/parrot/brain/observer/photo.py` | `photo.taken_preview` 后按 AwarenessPolicy 决策并计数 |
| Web monitor | `src/parrot/brain/app_monitor_server.py` | FastAPI 本地只读页：Module Rail / Canvas Workspace / Paper Notes / L2-B Topology |
| L2-B export | `src/parrot/brain/l2b_monitor.py`、`src/parrot/dsg/l2b_graph.py` | 有界 JSON snapshot，read-only，不改图 |
| Self-check | `src/parrot/brain/app_v1_self_check.py`、`src/scripts/run_app_v1_self_check.py` | 自动跑业务验收：workspace、camera、awareness、Google draft、Nanobot paper note、canvas refs |

## 2. 架构审计结论

- Blackboard 只保存轻量状态和最近 notice，不保存照片 payload。
- IntentWorkspace 是照片 preview、Google draft、Nanobot report 的认知工作区，不等于 App 的 2DWorkspace。
- 2DWorkspace 可以显示 ref id、纸条、卡片和模块状态，但不直接写 L2-B / Graphiti / Google / Obsidian。
- L2-B 仍是运行时工作记忆图；Web monitor 只读导出节点/边快照，不提供写入口。
- Graphiti 长期归档不在 App 第一版即时 UI 中完成，照片默认不作为场景事实直接写 Graphiti。

## 3. 外部调研取舍

- Graphiti OSS 是 temporal context graph engine；Zep 托管版才有 dashboard / graph visualization，OSS 需要自建工具。参考 [Graphiti README](https://github.com/getzep/graphiti)。
- Graphiti ingestion 以 episode 为 provenance 单位，支持 text / message / json / bulk；监控页不能把“查看状态”变成写 episode。参考 [Graphiti Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes)。
- rustworkx 支持 PyDiGraph 节点/边查询与 visualization 工具，但 App 第一版只需要 bounded JSON，后续图视图再引入布局/渲染。参考 [rustworkx PyDiGraph](https://www.rustworkx.org/apiref/rustworkx.PyDiGraph.html) 与 [rustworkx visualization](https://www.rustworkx.org/dev/visualization.html)。

## 4. 验证记录

```text
uv run pytest tests/test_brain/test_app_first_version_facade.py tests/test_ecp_event/test_w8_observer_photo.py tests/test_brain/test_app_v1_monitor.py tests/test_dsg/test_l2b_views_and_compartments.py -q
28 passed

uv run pytest tests/test_brain tests/test_dsg tests/test_scripts tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py -q
274 passed

uv run ruff check <changed App V1 files and tests>
All checks passed

uv run python src/scripts/run_app_v1_self_check.py --obsidian-vault D:\GOSLOParrot\GOSLObsidian\GOSLOParrot
passed: true
```

Web monitor：

- `http://127.0.0.1:7892/health` 返回 `{"ok": true, "service": "app-v1-monitor"}`。
- 浏览器 DOM 验证存在 `Module Rail`、`Canvas Workspace`、`Paper Notes`、`L2-B Topology`。
- Pixel Asset 背景路径已修正为 `/pixel-assets/curated/00_previews/Paper_UI_preview.png`。

Unity MCP：

- `ParrotSmokeScene` validate：0 issues、missing scripts 0、broken prefabs 0。
- Unity Console：0 Error / 0 Warning。
- EditMode / PlayMode test jobs：Passed。当前 Unity test tree 暂无具体用例，所以 summary total=0。

## 5. 剩余问题

- 专业相机功能（镜头、曝光、焦距、白平衡、相册）还没有定 UI 与设备能力降级策略，建议下一轮先做方案对比再实现。
- `AWARE_REACT` 尚未接完整对话预算；第一版只给内部 notice / preview ref，不主动抢话。
- `AWARE_INTERRUPT` / `STARTLED` 不进第一版，需等 LiveKit 语音生命周期与隐私体验稳定后再开。
- Photo preview 还没有低 token caption / VLM 摘要；GOSLO 可以拿 ref，但不一定能低成本理解图像。
- Web monitor 仍是 smoke monitor，不是正式 Web 控制台；L2-B 图谱可视化、Graphiti memory core 管理需要下一轮产品设计参与。
