# Web 监控小 demo 范围

> 状态：验证工具草案，不是最终 Web 控制台设计。  
> 原则：先 read-only，看连接层是否真的在跑；视觉和信息架构等用户参与后再定。
> 2026-05-10 更新：已落地最小 smoke monitor，见 `src/parrot/brain/app_monitor_server.py` 与 `src/scripts/start_app_monitor_server.py`。

## 1. 为什么先做小 demo

App 第一版需要先证明 Google / Obsidian / Photo / Nanobot 的连接层稳定。Web 控制台现在不应该抢设计主导权，但可以作为调试窗口，帮助发现：

- Nanobot 是否 busy、是否 heartbeat。
- Google result 是否回到 Scheduler 和 L1.5。
- Obsidian vault 是否有合法 note。
- Photo 是否完成 preview、asset upload、IntentWorkspace staged ref。
- Blackboard 是否只有轻量状态，没有被塞 payload。

## 2. 第一版面板

| 面板 | 显示内容 | 写操作 |
|:--|:--|:--|
| Runtime | Brain / Scheduler / Nanobot / Redis heartbeat | 无 |
| Menu State | active model/persona/mode/scene/workspace | 无 |
| Obsidian | vault status、md count、ingest-ready count、last sync | 无 |
| Google | last calendar fetch、event count、error、pending draft count | 无 |
| Photo | preview count、asset count、latest staged ref、orphan count | 无 |
| Nanobot | busy、task type、last result、last error | 无 |
| IntentWorkspace | open refs by kind、pressure、expired refs | 无 |

## 3. 不做

- 不在 Web 里编辑 Obsidian。
- 不在 Web 里改 Google 日程。
- 不设计最终 dashboard 视觉。
- 不替代 App 内菜单画布。
- 不写 LiveKit 控制面，最多显示连接健康。

## 4. demo 判据

- 能在本机启动。
- 没有外部账号时也能显示空态。
- 每个面板都有明确的更新时间。
- 所有按钮都是 refresh 或 open-local，不产生外部写操作。
- 能帮助 App 第一版测试定位连接问题。

## 5. 已实现的 smoke monitor

启动：

```text
uv run python src/scripts/start_app_monitor_server.py --host 127.0.0.1 --port 7892
```

端点：

| Endpoint | 用途 | 写操作 |
|:--|:--|:--|
| `/` | 黑灰紫色只读页面，使用 Pixel Asset 背景 | 无 |
| `/health` | 进程健康检查 | 无 |
| `/api/app/canvas` | App V1 `canvas_snapshot()`，含模块、workspace、纸条、photo refs | 无 |
| `/api/app/modules` | 七个模块状态 | 无 |
| `/api/l2b/snapshot?limit=80` | L2-B bounded JSON snapshot | 无 |

页面区块：

- `Module Rail`：Google / Obsidian / GOSLO / Nanobot / Photo / XRHand / Canvas。
- `Canvas Workspace`：当前 2DWorkspace 和可选 workspace。
- `Paper Notes`：Google draft 与 Nanobot report 的 IntentWorkspace ref。
- `Photo / Awareness`：照片 ref 与 Awareness notice。
- `L2-B Topology`：只读节点/边 JSON，不提供图写入口。

## 6. 继续暂缓

- 正式 Web 控制台的信息架构和交互设计。
- L2-B 图谱交互布局、Graphiti memory core 管理、Graphiti 写回。
- 任何 Google / Obsidian / L2-B / IntentWorkspace 写操作。
