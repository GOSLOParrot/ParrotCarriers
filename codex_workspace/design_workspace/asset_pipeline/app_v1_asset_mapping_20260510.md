# App V1 素材对照表 2026-05-10

## 导入原则

- 只导入 curated 子集，不导入 `extracted/` 全量素材。
- 第一版以“槽位清楚、缺失明确”为主。
- 进入 Unity 的素材在 `unity/ArSpike/Assets/UI/ParrotApp`。
- Unity import 建议：`Sprite (2D and UI)`、Point filter、no mipmaps；拉伸面板后续做 9-slice。

## Slot Mapping

| Slot | Source | Unity | Status | 备注 |
|:--|:--|:--|:--|:--|
| ToolDrawerWood | `curated/02_ui_supplements_book_paper_wood/wood_ui/Wood UI/WOOD/Menu1.png` | `Assets/UI/ParrotApp/ToolCabinet/ToolDrawer_Wood_Menu1.png` | selected | 木质拉出工具柜 |
| ToolButtonWood | `curated/02_ui_supplements_book_paper_wood/wood_ui/Wood UI/Buttons & Bars/Button/Front.png` | `Assets/UI/ParrotApp/ToolCabinet/ToolButton_Wood_Front.png` | selected | 工具柜按钮 |
| PaperNoteSmall | `curated/02_ui_supplements_book_paper_wood/paper_ui/BlankNewspaper_New.png` | `Assets/UI/ParrotApp/Notifications/PaperNote_Blank_New.png` | selected | Nanobot 小纸条 |
| PaperNoteFilled | `curated/02_ui_supplements_book_paper_wood/paper_ui/FilledNewspaper_Old.png` | `Assets/UI/ParrotApp/Notifications/PaperNote_Filled_Old.png` | selected | 工作桌纸张/报告 |
| CameraIcon | `curated/06_icons_and_misc/pixelwood_valley_icon_pack/.../Items 16x16.png` | `Assets/UI/ParrotApp/Icons/Items_16x16.png` | placeholder | 现代相机图标还需要裁切或替换 |
| FocusMagnifierIcon | `curated/03_secondary_ui_adventure/AdventureUI/Icons/Icons.png` | `Assets/UI/ParrotApp/Icons/Adventure_Icons.png` | placeholder | 放大镜/望远镜图标待裁切 |
| BoundaryBoxIcon | `curated/02_ui_supplements_book_paper_wood/book_ui_v1/Sprites/Content/Boxes/Light/1.png` | `Assets/UI/ParrotApp/Icons/BoundaryBox_Frame.png` | placeholder | 先用白边 RectTransform 作为运行时主体 |
| WorkspaceDesk | `curated/04_2d_workspace_modern_interiors` | `Assets/UI/ParrotApp/Workspace` | slot_only | 2D 宅邸/工作桌待下一轮拼房间 |
| TransitionAnimation | none | `Assets/UI/ParrotApp/Transitions` | slot_only | IPoAC 转场动画插槽 |

## Unity 导入设置验证

- Unity MCP 已批量设置 7 个 PNG 为 `Sprite (2D and UI)`、Point filter、no mipmaps、alpha transparency。
- PNG `.meta` 已由 Unity 导入生成并随本轮提交。

## 已知缺口

- CameraIcon / FocusMagnifierIcon 是 sheet placeholder，还未裁切单图。
- Workspace/Transitions 目前是槽位目录，未放最终场景图。
