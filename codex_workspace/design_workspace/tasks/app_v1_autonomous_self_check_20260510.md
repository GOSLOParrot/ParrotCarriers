# App V1 自主长线自检记录

> 日期：2026-05-10  
> 作用：记录这轮 Codex 自检目标、验证结果、架构对齐点和下一轮要决策的问题。  
> 对应事实源：`.cursor/memory/architecture/Interface/app_v1_longline_self_check_completion_20260510.md`

## 1. 本轮目标

第一版 App 需要先达成“能测、能看、能知道哪里坏了”的基础状态：

- 菜单画布有统一业务接口，不让 Unity / Web 分别绕过后端读写。
- Google / Obsidian / Photo / Nanobot / GOSLO / XRHand / Canvas 七模块有状态 read model。
- Google 写操作和 Nanobot 报告进入 IntentWorkspace，2DWorkspace 只显示纸条和 ref。
- Photo Awareness 能让 GOSLO 知道拍照并拿到短期 preview ref，但不打断对话。
- Web smoke monitor 只读显示运行状态，帮助第一版 App 测试。

## 2. 当前测试目标

| 目标 | 验证方式 | 结果 |
|:--|:--|:--|
| App facade 七模块状态 | `tests/test_brain/test_app_first_version_facade.py` | pass |
| Awareness preview ref | `tests/test_ecp_event/test_w8_observer_photo.py` | pass |
| Web monitor endpoint / HTML | `tests/test_brain/test_app_v1_monitor.py` | pass |
| L2-B bounded export | `tests/test_brain/test_app_v1_monitor.py` | pass |
| App 业务自检 | `src/scripts/run_app_v1_self_check.py` | pass |
| Unity scene smoke | Unity MCP scene validate / console / test jobs | pass |

## 3. 关键设计对齐

- 2DWorkspace 是用户看见的桌面/工作区，不持有大 payload。
- IntentWorkspace 是认知任务里的暂存区，持有 Google draft、Nanobot report、photo preview / asset refs。
- Blackboard 只保存轻量状态和最近 notice。
- L2-B 是运行时工作记忆图；monitor 只读导出，不改图。
- Graphiti 是长期 temporal context graph，不在 App 第一版的相机/菜单交互里直接写。

## 4. 需要用户后续拍板

相机专业功能建议分三档：

| 方案 | 内容 | 风险 |
|:--|:--|:--|
| A. 自动档优先 | 只做拍照、相册、Awareness、少量状态提示 | 最稳，但不像专业相机 |
| B. 半手动 | 曝光补偿、焦点锁、镜头切换，设备不支持时降级 | 需要真机能力矩阵 |
| C. 专业面板 | 曝光、ISO、快门、白平衡、焦距、网格、直方图 | 第一版风险高，UI 和 AR 主流程会变重 |

建议第一版选 A+B 的小集合：拍照、相册入口、焦点锁、曝光补偿、Awareness 开关。镜头/白平衡/直方图后置。

Web 控制台下一轮需要用户参与：

- 是否要正式做 L2-B 图谱交互图，而不是 JSON。
- 是否要接 Graphiti / Memory Core 的管理视图。
- 是否允许 Web 写操作；若允许，哪些动作必须二次确认。

## 5. 当前可用命令

```text
uv run pytest tests/test_brain tests/test_dsg tests/test_scripts tests/test_scheduler tests/test_ecp_event/test_w8_observer_photo.py tests/test_ecp_event/test_w8_photo_upload_server.py -q

uv run python src/scripts/run_app_v1_self_check.py --obsidian-vault D:\GOSLOParrot\GOSLObsidian\GOSLOParrot

uv run python src/scripts/start_app_monitor_server.py --host 127.0.0.1 --port 7892
```
