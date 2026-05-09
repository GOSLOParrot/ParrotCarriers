---
title: Chat B True Connection Completion Record
date: 2026-05-09
status: completed
owner: Chat B / Interface
scope: Obsidian, Google Calendar, Photo memory, Nanobot routing, IntentWorkspace boundary
related:
  - .cursor/memory/architecture/Interface/chatB_obsidian_google_nanobot_realconnect_audit_20260509.md
  - .cursor/memory/architecture/Interface/obsidian_true_connection_guide_20260509.md
  - .cursor/memory/architecture/Interface/google_calendar_nanobot_true_connection_guide_20260509.md
  - .cursor/memory/architecture/Interface/photo_memory_awareness_true_connection_guide_20260509.md
---

# Chat B 真连接完成记录

## 0. 完成摘要

本轮完成了 Obsidian、Google Calendar、Photo 三条真实连接链路的代码修复、架构审计和文档落点。菜单画布里的 Google / Obsidian / GOSLO module / Nanobot 设定块仍建议等待这些链路在 App 第一版测试中稳定后再最终设计。

本轮特别确认了 IntentWorkspace 升级后的边界：

- **2DWorkspace** 是可视化画布和菜单表面，保存块状态、ref id 和用户可见 controls。
- **IntentWorkspace** 是认知任务内的大 payload / draft / staged ref 暂存区，保存照片、写回草稿、临时比较对象。
- **Blackboard** 是轻量运行态和调度摘要，不能当 payload 仓库。
- **L1.5 / RefTable** 是外部来源入池和跨模块引用绑定边界。
- **L2-B** 是 GOSLO 可用的轻量语义记忆，不保存图片字节、OAuth token 或完整外部 payload。

## 1. 已完成代码修复

### Google / Nanobot

- Scheduler 路由 `calendar_fetch` / `calendar_create` / `calendar_patch` / `calendar_delete` / `message_check` 到 Nanobot。
- Nanobot result 保留 `result_channel`，由 Scheduler 统一 fan-out 到 trigger result channel。
- 移除 TriggerRunner 对 Nanobot raw result 的重复订阅路径。
- Real Nanobot gateway 增加 Google calendar 任务 prompt 和 heartbeat/busy 状态。
- `CalendarTrigger` 进入 L1.5 `GOOGLE_CALENDAR` bucket，并创建 L2-B EVENT 节点。

### Obsidian

- `sync_obsidian_to_graphiti.py` 默认支持 `--target dsg`。
- 新增 `ObsidianIngestTrigger`。
- `UserTagFilter` 支持 `profile=ref | daily | roleplay`。
- `profile=ref` 只绑定已有节点，不创建新 L2-B 节点。
- `daily` / `roleplay` 是设定源 note，不要求 UUID，通过 L1.5 authority bucket 写入 L2-B。
- 菜单里的 Obsidian 设定模块默认读取 `daily` / `roleplay`；只有 Ref shelf / 绑定修复视图才要求 UUID。

### Photo

- HTTP upload server 返回并发布真实 `asset_path`。
- Photo observer 将 asset path 写入 PhotoNode `reference_image_path`。
- Photo observer 将上传后的照片作为 `StagedRefKind.PHOTO` stage 到 IntentWorkspace。
- Photo observer 在 L1.5 RefTable 创建 `RefKind.PHOTO_PATH` 绑定。
- Blackboard 继续只记录 `transient/last_photo_event` 轻量状态。

## 2. 已完成验证

```text
uv run pytest tests/test_dsg tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py -q
183 passed

uv run ruff check tests/test_dsg tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py src/scripts/sync_obsidian_to_graphiti.py
All checks passed

py -3 -m py_compile D:\GOSLOParrot\nanobot\nanobot\channels\parrot_bus.py
passed
```

## 3. 新增事实源文档

| 文档 | 作用 |
|:--|:--|
| `Interface/obsidian_true_connection_guide_20260509.md` | Obsidian 三 profile、L1.5、L2-B、IntentWorkspace 边界 |
| `Interface/google_calendar_nanobot_true_connection_guide_20260509.md` | Google Calendar + Nanobot 真实连接、读写链路、状态监控点 |
| `Interface/photo_memory_awareness_true_connection_guide_20260509.md` | Photo 落盘、IntentWorkspace、L2-B PhotoNode、GOSLO Awareness 策略 |

## 4. 2026-05-10 三 profile 固化审计

本轮针对“不要把 Obsidian 三种用法再次搞混”做了专项固化：

- 文档硬规则：`daily` / `roleplay` 是设定源 note，不要求 UUID；`ref` 是引用加强 note，必须有 UUID / Graphiti / L2-B 绑定线索。
- 实现硬规则：`UserTagFilter` 只在 `profile=ref` 且缺 UUID 时拒绝；`obsidian_note_key` 会随 source_meta 进入 L2-B，避免无 UUID 设定 note 在下游失去本地身份。
- 菜单硬规则：Obsidian 设定模块默认显示 `daily` / `roleplay`；Ref shelf / 绑定修复视图才显示 UUID 必填状态。
- 本地 vault 验证：`D:\GOSLOParrot\GOSLObsidian\GOSLOParrot` 当前 `profile_counts={'daily': 1, 'ref': 1, 'roleplay': 3}`，无 UUID 的大小姐宅邸 / RolePlay Mode 设定均可 dry-run 成 DSG event。

最新回归：

```text
uv run pytest tests/test_scripts/test_check_obsidian_vault.py tests/test_dsg/test_obsidian_true_connection.py tests/test_brain/test_app_first_version_facade.py -q
15 passed

uv run pytest tests/test_brain tests/test_dsg tests/test_scripts tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py -q
269 passed

uv run ruff check src/parrot/brain/app_first_version.py src/parrot/brain/obsidian_vault.py src/parrot/dsg/ingest/base.py src/parrot/dsg/ingest/user_tag_filter.py src/scripts/check_obsidian_vault.py src/scripts/sync_obsidian_to_graphiti.py tests/test_scripts/test_check_obsidian_vault.py tests/test_dsg/test_obsidian_true_connection.py tests/test_brain/test_app_first_version_facade.py
All checks passed
```

## 5. 仍需后续处理

1. **Photo AwarenessPolicy**：尚未实现，需要后端开关、策略决策和 GOSLO 通知行为。
2. **Photo preview IntentWorkspace cache**：高质量照片已入 IntentWorkspace，但 preview 还没有独立 TTL staged ref。
3. **Orphan asset recovery**：如果 preview 丢失但 asset 上传成功，仍需要恢复 PhotoNode 和 ref binding。
4. **Google writeback 闭环**：已有 Nanobot 路由，但仍需 IntentWorkspace draft、用户确认和结果回填。
5. **Obsidian writeback**：读取链路完成，写回仍需 draft + confirm。
6. **Web 控制台可视化**：建议 App 第一版稳定后展示 Nanobot、Google、Obsidian、Photo、IntentWorkspace、L1.5 bucket 状态。
7. **菜单画布最终设计**：等待三条真实连接稳定后，再设计 Google / Obsidian / GOSLO module / Nanobot 设定块。

## 6. 下一步建议

下一步优先实现 Photo Awareness v1，而不是镜头、曝光等专业相机功能：

1. 增加 `photo_awareness_enabled` 和默认 policy 的 backend-owned API。
2. 实现三态 v1：`UNAWARE_RECORDED`、`AWARE_SILENT`、`AWARE_REACT`。
3. 将 preview 作为 TTL staged ref 放入 IntentWorkspace。
4. 增加 orphan asset recovery。
5. 在 Web 控制台显示 photo pipeline 和 awareness decision。

专业相机能力可以在上述链路稳定后再做，因为镜头和曝光只改变 capture 质量，不解决 GOSLO 是否知道照片、如何读取照片、以及照片如何进入记忆的问题。
