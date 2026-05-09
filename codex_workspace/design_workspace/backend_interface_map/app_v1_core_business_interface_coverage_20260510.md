# 第一版 App 核心接口与业务接口覆盖

> 状态：代码对齐。  
> 对应测试：`tests/test_brain/test_app_first_version_facade.py`、`tests/test_brain/test_app_v1_monitor.py`、`tests/test_ecp_event/test_w8_observer_photo.py`。  
> 对应实现：`src/parrot/brain/app_first_version.py`、`src/parrot/brain/photo_awareness.py`、`src/parrot/brain/app_monitor_server.py`。

## 1. 覆盖范围

第一版 App 需要一个统一业务 facade，而不是让 Unity 分别读 Blackboard、IntentWorkspace、DSG 和 Nanobot。当前覆盖：

| App 功能 | 后端接口 | 第一版行为 |
|:--|:--|:--|
| 菜单画布连接 | `list_module_statuses()` | 返回 Google / Obsidian / GOSLO / Nanobot / Photo / XRHand / Canvas 状态 |
| 画布快照 | `canvas_snapshot()` | 返回 active workspace、模块状态、纸条、照片 ref |
| 2DWorkspace 切换 | `apply_workspace()` | 只切可见工作区，不断 LiveKit / 不切 Scene |
| Google 日程 | `create_calendar_draft()` | 写操作只进入 IntentWorkspace draft |
| Obsidian 设定 | `module_status(OBSIDIAN)` | 扫本地 vault，daily/roleplay 不要求 UUID，ref 才要求 |
| GOSLO Module | `set_photo_awareness()` | 后端写 BB policy，第一版不允许 interrupt |
| 相机模式 | `set_camera_mode()` | 后端写 `session/camera_mode` |
| XRHand | `set_xrhand_mode()` | 后端写 `session/xrhand_mode`，不切 Scene |
| Nanobot 报告 | `stage_nanobot_report()` | 结果进入 IntentWorkspace rich report |

## 2. Blackboard 新增键

| Key | Writer | 用途 |
|:--|:--|:--|
| `session/camera_mode` | `brain.app_first_version` | App 第一版相机状态 |
| `session/photo_awareness_policy` | `brain.app_first_version` | Photo Awareness 三态 |
| `session/photo_awareness_enabled` | `brain.app_first_version` | 是否通知 GOSLO |
| `session/photo_awareness_allows_interrupt` | `brain.app_first_version` | 第一版固定 false |
| `session/photo_awareness_preview_ttl_seconds` | `brain.app_first_version` | preview ref TTL |
| `transient/photo_awareness_notice` | `brain.photo_awareness` | 最近一次 Awareness 决策 |
| `session/xrhand_mode` | `brain.app_first_version` | XRHand 交互模式 |

Unity / Web 不能直接写这些 key，只能通过 backend-owned RPC / facade。

## 3. IntentWorkspace 使用

| 业务 | role | kind |
|:--|:--|:--|
| Google 写操作 | `calendar_draft` | `DOC` |
| Nanobot 报告 | `nanobot_report` | `RICH_REPORT` |
| Photo asset | 现有 `photo` staged ref | `PHOTO` |
| Photo preview | `photo_preview_awareness` | `PHOTO` |

2DWorkspace 只显示 ref id、卡片和纸条，不持有 payload。

## 4. Obsidian 修正

修正后的语义：

- `daily`：设定源，可无 UUID，用 path/title 作为 note identity。
- `roleplay`：设定源，可无 UUID，用于大小姐宅邸、RolePlay Mode、场景设定。
- `ref`：强化源，需要 UUID / Graphiti / L2-B 线索，最好在 Graphiti/L2-B runtime 中测试绑定。

菜单画布应把 `daily` / `roleplay` 放在“设定来源”视图，把 `ref` 放在“引用绑定/修复”视图。前者不显示 UUID 必填错误；后者缺 UUID 时才进入 invalid/ref-missing 状态。

## 5. 测试目标

`test_app_first_version_facade.py` 锁定：

- 七个模块状态齐全。
- Obsidian 无 UUID 设定 note 可被接受。
- 相机和 Awareness 只能由 backend writer 写入。
- Google 写动作进入 IntentWorkspace draft。
- Nanobot 结果进入报告纸条。
- XRHand 不切 Scene。
- `AWARE_SILENT` 能 stage 短期 preview ref，写入 `transient/photo_awareness_notice`，不打断对话。
- Web smoke monitor 能 read-only 显示 `Module Rail`、`Canvas Workspace`、`Paper Notes`、`L2-B Topology`。

## 6. 后续实现入口

Unity 第一版可以先对接这些 DTO：

- `AppModuleStatus.as_json()`
- `AppCanvasSnapshot.as_json()`
- `AppActionResult`
- `CameraMode`
- `PhotoAwarenessPolicy`
- `XrHandMode`

后续若要暴露 HTTP/RPC，只需要把 facade 方法包成 endpoint，不应该让前端绕过 facade 写 BB。
