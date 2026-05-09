# 2026-05-09 本轮需求原话摘录

> 本文件是为了设计工作区协作而整理的“原话级摘录”。完整对话仍以 Codex 线程为准。

## 工作方式

用户要求：

> 你可以 Think In English 的，这样 Token 比较省，Rule 什么的也可以用 English 写，把结果对话里中文汇报给我；但需求、完成汇报、任务和计划等需要我审查的要写成中文就行。

## 工作区目标

用户要求：

> 我还需要一个给我来配合你进行设计的简单的工作区。

> 这个工作区主要放一些我的原话和 idea 以及简单的设计草图页面什么的。

> 我想分成：Web 控制台 和 Unity AR App 两个文件夹？里面先放一些页面设计和功能组件设计，后续再继续分前端的设计路由？

当前处理：

- 建立 `codex_workspace/design_workspace/`。
- 保留 Web 控制台与 Unity AR App 两个主方向。
- 额外增加 `app_2d_workspace/`、`asset_pipeline/`、`backend_interface_map/`、`tasks/`，用于承接 App 内 2D 工作区、Figma / Unity 素材、后端业务流程和 Codex 进度记录。

## 原话搬迁

用户要求复制：

> `ideas.md`、`ar_app_flow_ui_design.md` 里的原话部分复制到给我用的设计和 idea、草图等的那个工作区。

当前处理：

- 已镜像 `ideas.md` 到 `00_original_words/ideas_lore_raw_copy_20260509.md`。
- 已镜像 `ar_app_flow_ui_design.md` 到 `00_original_words/ar_app_flow_ui_design_raw_copy_20260509.md`。

## 今天任务顺序

用户提出的顺序：

1. 工作区建好。
2. App 设计、Figma / Unity 资源寻找整理的手动工作区建好，插件的添加。
3. Obsidian 先完成 L1.5 相关设定 Node 的真连接，并设计业务流程 / 数据流。
4. Google 日程真连接也要对齐。
5. 照相机模式的 PhotoNode、照相机流程、图片保存位置和机制，以及 GOSLO Intent 层是否 aware。
6. 同时完成上述设计和 App 内需要保留的交互方式。
7. 不急着设计 Web 控制台，等 App 设计清楚后再知道 Web 要监控和管理哪些内容。
8. 完成第一版 App 设计和素材收集后，再进入 Figma 草图、idea 整合、LiveKit 连接、启动流程、画布菜单模块等具体实现。

## 不阻塞的并行线

用户补充：

> 可以先设计好 App 启动的菜单和指令上手的布局，和进入后的主界面（就是摄像头画面）和 HUD 和 工具栏三个组件。

> Obsidian 和 Google 可以 Cursor 并行同步进行相连得出连接方式；App 里的业务流程设计依旧由 Codex 完成。

