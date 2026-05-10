---
title: App V1 Facade Core Business Interface
date: 2026-05-10
status: ratified
owner: Chat B / App V1
scope: first app shell facade, menu canvas external modules, camera/photo awareness, Google draft, Obsidian settings, XRHand, Nanobot reports
code:
  - src/parrot/brain/app_first_version.py
  - src/parrot/brain/photo_awareness.py
  - src/parrot/brain/app_v1_self_check.py
  - src/parrot/brain/app_monitor_server.py
  - src/parrot/brain/l2b_monitor.py
  - src/parrot/brain/obsidian_vault.py
  - src/parrot/shared/bb_schema.py
tests:
  - tests/test_brain/test_app_first_version_facade.py
  - tests/test_brain/test_app_v1_monitor.py
  - tests/test_ecp_event/test_w8_observer_photo.py
---

# App V1 Facade 核心/业务接口

## 0. 结论

第一版 App 的 Unity 菜单画布和临时 Web smoke monitor 不应分别读取 Blackboard、IntentWorkspace、DSG、Nanobot。新增 `AppFirstVersionFacade` 作为统一业务 facade：

- `list_module_statuses()` 返回 Google / Obsidian / GOSLO / Nanobot / Photo / XRHand / Canvas 七个模块状态。
- `canvas_snapshot()` 返回菜单画布、2DWorkspace、纸条、照片 ref 的统一只读视图。
- Google 写操作只创建 IntentWorkspace `calendar_draft`。
- Nanobot 结果只创建 IntentWorkspace `nanobot_report`。
- Obsidian daily / roleplay 设定 note 不要求 UUID；`profile=ref` 才要求 UUID / Graphiti / L2-B 绑定线索。
- 相机模式、Photo Awareness、XRHand 状态通过 backend-owned BB keys 写入。
- Photo Awareness v1 已实现短期 preview ref：`AWARE_SILENT` / `AWARE_REACT` 会把低质 preview stage 到 IntentWorkspace，GOSLO 可知道“拍照发生了”，但第一版不打断说话。

## 0.1 Obsidian 三 profile 守护规则

App V1 facade、Unity 菜单、Web smoke monitor 必须把 Obsidian 拆成两种业务表面：

- **Setting notes**：`daily` / `roleplay`，不要求 UUID，以 `obsidian_note_key`、path、title 作为本地 note 身份；可进入 L1.5 bucket 与 L2-B 设定节点。
- **Ref binding notes**：`ref`，要求 UUID / Graphiti / L2-B 绑定线索；只用于加强已有节点，不作为菜单里的普通设定文件创建新节点。

因此，菜单中的“设定 Obsidian 模块”不能把 UUID 作为必填项；只有 Ref shelf / 绑定修复视图才要求 UUID。

## 1. 新增公开表面

| API | 用途 |
|:--|:--|
| `AppFirstVersionFacade.list_module_statuses()` | 菜单画布 / Web smoke monitor 读取所有模块状态 |
| `module_status(module_id)` | 读取单个模块状态 |
| `canvas_snapshot()` | 读取菜单画布 + 2DWorkspace + IntentWorkspace refs 的只读快照 |
| `apply_workspace(workspace_id)` | 切换 App 可见 2DWorkspace，不切 LiveKit Room / Scene |
| `set_camera_mode(CameraMode)` | 设置第一版相机模式 |
| `set_photo_awareness(PhotoAwarenessPolicy, enabled, preview_ttl_seconds)` | 设置 GOSLO 是否知道拍照，第一版不允许 interrupt |
| `set_xrhand_mode(XrHandMode)` | 设置 XRHand 交互模式，不切 Scene |
| `create_calendar_draft(...)` | Google 写动作进入 IntentWorkspace draft |
| `stage_nanobot_report(...)` | Nanobot result 进入报告纸条 |
| `list_paper_notes()` | 读取给 2DWorkspace / nanobot 纸条 UI 的 ref 列表 |
| `list_photo_refs()` | 读取相机模式 / Awareness UI 可展示的轻量照片 ref |

## 2. Blackboard keys

| Key | Writer | 说明 |
|:--|:--|:--|
| `session/camera_mode` | `brain.app_first_version` | `off / preview / photo_ready / capture_locked` |
| `session/photo_awareness_policy` | `brain.app_first_version` | `UNAWARE_RECORDED / AWARE_SILENT / AWARE_REACT` |
| `session/photo_awareness_enabled` | `brain.app_first_version` | 是否让 GOSLO 内部知道拍照 |
| `session/photo_awareness_allows_interrupt` | `brain.app_first_version` | 第一版固定 false |
| `session/photo_awareness_preview_ttl_seconds` | `brain.app_first_version` | preview ref 的短期 TTL，限制在 60-1800 秒 |
| `transient/photo_awareness_notice` | `brain.photo_awareness` | 最近一次拍照觉知决策，供 GOSLO / monitor 读取 |
| `session/xrhand_mode` | `brain.app_first_version` | `off / tracking / gesture_select` |

## 3. IntentWorkspace roles

| role | kind | 来源 |
|:--|:--|:--|
| `calendar_draft` | `DOC` | Google create / patch / delete 草稿 |
| `nanobot_report` | `RICH_REPORT` | Nanobot 任务结果纸条 |
| `photo` | `PHOTO` | 既有照片高质量 asset staged ref |
| `photo_preview_awareness` | `PHOTO` | Photo Awareness 短期 preview ref，默认不长期归档 |

2DWorkspace 只显示 ref id / card / paper note，不持有 payload。

## 4. App 白膜设计落点

设计文档：

- `codex_workspace/design_workspace/unity_ar_app/app_v1_whitebox_shell_20260510.md`
- `codex_workspace/design_workspace/backend_interface_map/app_v1_core_business_interface_coverage_20260510.md`
- `codex_workspace/design_workspace/asset_pipeline/pixel_asset_audit_20260510.md`

Pixel Asset 先作为白膜皮肤候选，不把大 zip 移入仓库。

## 5. 验证

已跑：

```text
uv run pytest tests/test_brain tests/test_dsg tests/test_scripts tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py -q
274 passed

uv run pytest tests/test_brain/test_app_first_version_facade.py tests/test_ecp_event/test_w8_observer_photo.py tests/test_brain/test_app_v1_monitor.py tests/test_dsg/test_l2b_views_and_compartments.py -q
28 passed

uv run python src/scripts/run_app_v1_self_check.py --obsidian-vault D:\GOSLOParrot\GOSLObsidian\GOSLOParrot
passed: true
```

新增 facade / monitor / observer 单测覆盖七模块状态、Obsidian 无 UUID 设定、相机/Awareness 写边界、preview ref、Google draft、Nanobot report、XRHand 不切 Scene、Web monitor 只读快照和 L2-B JSON export。

Unity MCP 验证（测试场景证据，仅证明接口/组件能被 smoke scene 装配；不代表正式 App 前端完成）：

- `ParrotSmokeScene` scene validate：0 issues，missing scripts 0，broken prefabs 0。
- Unity Console：0 Error / 0 Warning。
- EditMode / PlayMode test jobs：Passed（当前 Unity test tree 暂无具体用例，total=0）。

本地 Web smoke monitor：

- 启动脚本：`src/scripts/start_app_monitor_server.py --host 127.0.0.1 --port 7892`
- 健康检查：`/health -> {"ok": true, "service": "app-v1-monitor"}`
- 页面区块已用浏览器验证：`Module Rail`、`Canvas Workspace`、`Paper Notes`、`L2-B Topology`。

## 6. Web / L2-B 可视化边界

第一版 Web monitor 只读，不写 Obsidian / Google / Graphiti / L2-B / IntentWorkspace。L2-B 可视化先走 `build_l2b_snapshot()` 的 bounded JSON export。后续若要做真正图谱视图，再选择布局/渲染库。

外部调研结论：

- Graphiti OSS 是 temporal context graph core；Zep 托管版才提供 dashboard / graph visualization，Graphiti OSS 需要自建周边工具。参考 [Graphiti README](https://github.com/getzep/graphiti)。
- Graphiti ingestion 以 episode 为 provenance 单位，支持 text / message / json 和 bulk episode；App monitor 不应直接写 episode。参考 [Graphiti Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes)。
- rustworkx 本身提供 PyDiGraph 节点/边 API 和 `to_dot` / Graphviz / Matplotlib 绘制能力；当前先导出 JSON，避免把监控页做成新的图写入口。参考 [rustworkx PyDiGraph](https://www.rustworkx.org/apiref/rustworkx.PyDiGraph.html) 与 [rustworkx visualization](https://www.rustworkx.org/dev/visualization.html)。
