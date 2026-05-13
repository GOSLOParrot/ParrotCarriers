# Parrot App V1 UI Assets

This folder contains the curated App V1 Unity import subset only.

Do not import the full extracted pixel asset workspace into Unity. The App V1
shell uses these files as stable visual slots:

| Slot | Unity path | Status |
|:--|:--|:--|
| ToolDrawerWood | `Assets/ParrotApp/Art/AppV1/ToolCabinet/ToolDrawer_Wood_Menu1.png` | selected |
| ToolButtonWood | `Assets/ParrotApp/Art/AppV1/ToolCabinet/ToolButton_Wood_Front.png` | selected |
| PaperNoteSmall | `Assets/ParrotApp/Art/AppV1/Notifications/PaperNote_Blank_New.png` | selected |
| PaperNoteFilled | `Assets/ParrotApp/Art/AppV1/Notifications/PaperNote_Filled_Old.png` | selected |
| NanobotReportPaper | warm tint of `PaperNoteSmall` | runtime placeholder |
| CalendarReminderPaper | blue tint of `PaperNoteFilled` | runtime placeholder |
| TrashCrumpledPaper | layered UGUI paper chips | runtime placeholder |
| OrangeCatPaw | `Assets/ParrotApp/Art/AppV1/Notifications/NekoClaw_Cutout.png` | selected |
| CameraIcon | `Assets/ParrotApp/Art/AppV1/Icons/Items_16x16.png` | placeholder sheet |
| FocusMagnifierIcon | `Assets/ParrotApp/Art/AppV1/Icons/Adventure_Icons.png` | placeholder sheet |
| BoundaryBoxIcon | `Assets/ParrotApp/Art/AppV1/Icons/BoundaryBox_Frame.png` | placeholder |
| WorkspaceDesk | `Assets/ParrotApp/Art/AppV1/Workspace` | slot only |
| TransitionAnimation | `Assets/ParrotApp/Art/AppV1/Transitions` | slot only |
| SettingsDialoguePanel | runtime UGUI using wood/paper slots | implemented |
| CameraProToolbox | runtime UGUI using paper/BBox stamp slots | implemented |
| NanobotPaperAnimation | selectable/drag/drop paper note state machine | implemented placeholder |
| ParrotJoystick | runtime UGUI walk pad + knob | implemented placeholder |
| RealDeviceSmokeBadge | runtime text badge in Settings panel | implemented |

Unity import target for these PNGs: `Sprite (2D and UI)`, point filtering, no
mipmaps, and 9-slice borders later for stretched wood/paper panels.
