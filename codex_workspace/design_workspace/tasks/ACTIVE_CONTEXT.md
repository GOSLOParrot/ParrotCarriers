# Design Workspace Active Context

> 更新：2026-05-09

## 当前阶段

设计工作区刚建立。现在先做“原话 + 后端能力 + App 第一版流程”的对齐，不急着写 Unity UI 代码，也不急着定完整 Web 控制台。

## 当前完成

- 已建立 `codex_workspace/design_workspace/`。
- 已镜像 `ideas.md` 与 `ar_app_flow_ui_design.md` 原文。
- 已建立 Unity AR App / App 2D Workspace / Web Console / Asset Pipeline / Backend Interface Map / Tasks 目录。
- 已写入后端模块协作简述和业务接口写法。

## 下一步

1. 用户审查这个工作区结构。
2. 补 App 启动页、摄像头主界面、HUD、工具柜的草图说明。
3. 对齐 Obsidian L1.5 设定 Node 真连接流程。
4. 对齐 Google Calendar raw event → Node → 写回流程。
5. 对齐 PhotoNode 保存、绑定、GOSLO aware 流程。
6. 再回到 Figma 第一版和 Unity UI 目录 / TODO。

## Codex 进度记录方式

Codex 这边建议用轻量文件，而不是复制 Cursor 的全部 memory 系统：

- `tasks/ACTIVE_CONTEXT.md`：当前状态和下一步。
- `tasks/task_order_20260509.md`：今天任务顺序。
- 具体业务流完成后，放在 `backend_interface_map/*.md`。
- 页面 / 组件草图放在对应设计目录。
- 真正改 `.cursor/memory/**` 时才更新 `.cursor/memory/INDEX.md`。

