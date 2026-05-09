# App 内 2D 工作区设计区

> 这是 Unity AR App 内的“纸面工作桌”，不是 Web 控制台。

## 用途

- Nanobot / Maid 跑完任务后递交报告。
- Google 日程以“可批改 / 可确认”的方式展示。
- Obsidian / Ref / PhotoNode 相关结果可以作为纸条或卡片被打开。
- 用户能接受、拒绝、归档、以后再看；写回动作必须显式确认。

## 第一版候选页面

| 页面 | 作用 | 是否现在做 |
|:--|:--|:--|
| 报告阅读 | 打开纸条，阅读 Nanobot 结果。 | 是 |
| 日程批改 | 今日摘要、冲突提醒、修改建议。 | 待 Google 流程确定 |
| Ref / 设定查看 | Obsidian 设定 Node 的只读状态。 | 待 Obsidian 真连接确定 |
| 照片绑定 | 刚拍照片和 ObjectNode / Scene 的绑定预览。 | 待 PhotoNode 流程确定 |

## 设计原则

- App 里做轻量确认，不做复杂数据库管理。
- 外部工具仍在外部工具里管理：Obsidian 文件在 Obsidian，Google 日程在 Google。
- App 只展示“GOSLO / Nanobot 帮你整理出的候选结果”，由用户确认。

## 2026-05-09 设计草稿

- `workspace_mansion_reference_20260509.md`：纯 2D 像素宅邸工作区、工作桌、角色和 Papers, Please 式交互参考。
- `../unity_ar_app/menu_canvas_external_modules_20260509.md`：外部模块如何进入 2DWorkspace 的工作桌、报告桌、日程区、Ref shelf。
