# Parrot App V1 UI Assets

This folder contains the curated App V1 Unity import subset only.

Do not import the full extracted pixel asset workspace into Unity. The App V1
shell uses these files as stable visual slots:

| Slot | Unity path | Status |
|:--|:--|:--|
| ToolDrawerWood | `Assets/UI/ParrotApp/ToolCabinet/ToolDrawer_Wood_Menu1.png` | selected |
| ToolButtonWood | `Assets/UI/ParrotApp/ToolCabinet/ToolButton_Wood_Front.png` | selected |
| PaperNoteSmall | `Assets/UI/ParrotApp/Notifications/PaperNote_Blank_New.png` | selected |
| PaperNoteFilled | `Assets/UI/ParrotApp/Notifications/PaperNote_Filled_Old.png` | selected |
| NanobotReportPaper | warm tint of `PaperNoteSmall` | runtime placeholder |
| CalendarReminderPaper | blue tint of `PaperNoteFilled` | runtime placeholder |
| TrashCrumpledPaper | layered UGUI paper chips | runtime placeholder |
| OrangeCatPaw | not imported yet | slot only |
| CameraIcon | `Assets/UI/ParrotApp/Icons/Items_16x16.png` | placeholder sheet |
| FocusMagnifierIcon | `Assets/UI/ParrotApp/Icons/Adventure_Icons.png` | placeholder sheet |
| BoundaryBoxIcon | `Assets/UI/ParrotApp/Icons/BoundaryBox_Frame.png` | placeholder |
| WorkspaceDesk | `Assets/UI/ParrotApp/Workspace` | slot only |
| TransitionAnimation | `Assets/UI/ParrotApp/Transitions` | slot only |
| SettingsDialoguePanel | runtime UGUI using wood/paper slots | implemented |
| CameraProToolbox | runtime UGUI using paper/BBox stamp slots | implemented |
| NanobotPaperAnimation | selectable/drag/drop paper note state machine | implemented placeholder |
| ParrotJoystick | runtime UGUI walk pad + knob | implemented placeholder |
| RealDeviceSmokeBadge | runtime text badge in Settings panel | implemented |

Unity import target for these PNGs: `Sprite (2D and UI)`, point filtering, no
mipmaps, and 9-slice borders later for stretched wood/paper panels.
