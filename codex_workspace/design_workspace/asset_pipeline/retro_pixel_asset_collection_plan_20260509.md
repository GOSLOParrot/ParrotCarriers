# 复古像素风素材收集计划 2026-05-09

> 目标：先找一套统一风格的复古像素 UI / 室内物体 / 角色插槽资产，用于 App 第一版白膜。  
> 原则：素材可替换，但布局必须为素材预留稳定插槽。

## 当前设计结论

- 当前阶段继续用网页草图确定布局。
- Figma 后续用于正式视觉和组件库沉淀。
- Unity 第一版白膜需要素材“占位”，不必马上是最终美术。
- 需要优先找风格统一的素材包，而不是东拼西凑单张图。

## 需要的素材插槽

| 插槽 | 用途 | 建议尺寸/形态 |
|:--|:--|:--|
| `LogoBoard` | 启动页 `GOSLO Parrot` 标题牌 | 横向木牌 / 纸牌，可替换 LOGO |
| `2DModelPortrait` | 标题旁可替换 2D 鹦鹉 / 角色形象 | 64x64 / 96x96 sprite |
| `ScenePanel` | 启动页 `SCENE` 面板 | 木框 / 羊皮纸面板 |
| `StartButton` | 启动按钮 | 大木制按钮，含 pressed/hover/disabled |
| `ModeLever` | AR / 2D / Session mode 切换 | 像素拉杆 / toggle |
| `TransitionCarrier` | IPoAC 转场动画角色 | 飞行动物 + 包裹 / SD 卡 |
| `ProgressBar` | 转场页进度条 | 低保真像素进度条 |
| `HUDPanel` | 左上 HUD 展开栏 | 暗色状态板 / 仪表板 |
| `ToolDrawer` | 右下工具抽屉 | 木制抽屉柜 / 工具格 |
| `ToolIcons` | 相机、Photo、BBox、菜单、2D 工作区 | 16x16 / 32x32 icon |
| `WorkspaceTileset` | 2D 宅邸大厅 / 工作桌 | top-down interiors tileset |
| `PaperDesk` | Papers, Please 式工作桌 | 纸张、印章、垃圾桶、文件夹 |
| `ModuleCards` | 菜单画布节点块 | 木框卡片 / 插孔 / 连线 |

## 素材评估标准

1. 风格统一：UI、tileset、角色最好来自同一作者或同一系列。
2. 授权明确：能商用、能修改、能放进 Unity 项目。
3. 分辨率适合：16x16 / 32x32 / 48x48 / 64x64 为主。
4. UI 状态完整：按钮至少需要 normal / hover / pressed / disabled。
5. Unity 友好：PNG spritesheet、tileset、9-slice 边框优先。
6. 不急着买贵包：先用免费/低价包做白膜，再替换最终资产。

## 推荐收集顺序

1. 统一 UI 包：按钮、面板、进度条、图标。
2. 室内宅邸 / 工作室 tileset。
3. 工作桌物件：纸张、印章、文件夹、垃圾桶。
4. 角色 sprite：鹦鹉主角色先占位，后续自制或生成。
5. 转场动画小包：飞行动物、包裹、进度条。

## 第一轮候选素材包

### UI 包

| 优先级 | 素材包 | 用途 | 授权/备注 |
|:--|:--|:--|:--|
| A | Kenney `UI Pack (RPG Expansion)` | 按钮、面板、slider、RPG UI 基础白膜 | CC0；85 个文件；适合先放进 Unity 做无版权压力白膜 |
| A | Kenney `Fantasy UI Borders` | 9-slice fantasy/RPG window/dialog border | CC0；140 个文件；很适合做可拉伸木框/纸框 |
| A | Myuxen `Adventure UI Pixel Asset Pack` | START、Mode 拉杆、进度条、图标、按钮状态 | CC0；10 色版本；按钮有 pressed state；free 版够先试 |
| A | Myuxen `Ultimate UI Pixel Asset Pack` | Buttons、icons、bars、banners、sliders、toggles | CC0；700+ sprites；$2.99+ full pack，适合统一 UI 底座 |
| A- | FreePixel.Art `Free Pixel Art UI Kit Mini Pack` | window、close button、scrollbar、card、modal、form | 商用允许；透明 PNG；适合菜单画布和工具 UI 白膜 |
| A- | TJ Trewin `Pixel paper pack 1` | scrolls、ribbons、paper、map backgrounds、animated unrolling scroll | 商用允许；16x16；适合报告纸条 / Obsidian 设定 Node / 菜单标题条 |
| A- | LCSkeleton `Pixel Paper Pack` | 32x32 纸张、书、卷轴、信件、污渍纸 | 商用允许但需署名；适合 report / workdesk |
| B | mrtnli / Zofia `FREE Game UI Starter Pack - Pixel Art` | 9-slice 按钮、slider、icon、window | 商用允许、可修改；作者说 credit 不强制；状态为 in development |
| B | cuppar `Free - Elegant UI` | panel、progress、slider、tab、input | 免费、可商用、可改；需要署名；含 Aseprite 源文件 |
| B | itchabop `Stonebase UI pack` | frames、boxes、buttons、tiles、9-slice modular UI | $10；风格更石头/幻想，适合后续主题备选，不是第一选择 |

### 室内 / 2D 工作区

| 优先级 | 素材包 | 用途 | 授权/备注 |
|:--|:--|:--|:--|
| A | Aura `8x8 Vintage Mansion Tileset` | 宅邸大厅、复古 manor、whodunit 气质 | 免费/付费版；可商用可修改；不可转售/再分发 |
| A- | zedpxl `Pixelart Interior Top-Down RPG Asset Pack v2` | 16x16 室内、living room、tavern、fireplace、门窗 | free/paid；可商用可修改；不可转售/再分发；声明 no generative AI |
| A- | Penzilla `Top-Down Retro Interior` | 16x16 复古室内、家具、多方向/状态、小装饰 | Name your own price；商用需按 license/购买要求；适合 2D 工作区白膜 |
| A- | bitglow `Pixel World - Cozy Life Simulation 16x16 Top Down Tileset` | 厨房、走廊、客厅、儿童房、办公室、角色、Unity package/prefab | $2.99；商用可用、可修改、不可再分发；适合 Unity 快速白膜 |
| B | pixelalli `Vintage House Asset Pack - Topdown Tileset` | 小型 vintage 房间、桌子、书架、植物、壁灯 | $1；PNG；适合工作桌/房间局部占位，授权页需购买前再确认 |
| B | EMI EMI `Horror Interior Tileset` | Papers, Please / 桌面审查偏暗风格、桌椅、书架、灯 | CC0；偏 horror，适合作为工作桌/报告桌氛围备选 |
| B | BTL games `TopDown Interior Home Tileset` | 现代日常房间、9 种房间风格、地板 | CC0；偏现代，不够复古，但适合补普通家具 |
| B | Doppelmulti `Simple Interior Tileset + furniture` | 32x32 木质室内、宝可梦式 topdown 家具 | $1.50；商用允许，需再读完整 license；适合备选 |

## 当前推荐组合

白膜第一轮建议：

1. **UI 安全底座**：Kenney RPG UI + Kenney Fantasy UI Borders。
2. **UI 更完整底座**：Myuxen Ultimate UI Pixel Asset Pack。
3. **2D 宅邸主候选**：Aura Vintage Mansion。
4. **2D 工作区更完整候选**：bitglow Pixel World 或 Penzilla Top-Down Retro Interior。
5. **纸张/报告补充**：TJ Trewin Pixel Paper 或 LCSkeleton Pixel Paper。
6. **工作桌暗色备选**：EMI Horror Interior。

原因：

- UI 与室内 tileset 分开选，但都偏复古像素，不会和当前草图冲突。
- 先用 CC0 或商用许可清楚的包填插槽，后面再替换成定制素材。
- `2DModelPortrait` / 鹦鹉主角色仍建议后续自制或生成，不从通用包里硬找。

## 候选链接

- Kenney UI Pack RPG Expansion: https://kenney.nl/assets/ui-pack-rpg-expansion
- Kenney Fantasy UI Borders: https://kenney.nl/assets/fantasy-ui-borders
- Myuxen Adventure UI Pixel Asset Pack: https://myuxen.itch.io/adventure-ui-asset-pack
- Myuxen Ultimate UI Pixel Asset Pack: https://myuxen.itch.io/ultimate-ui-pixel-asset-pack
- TJ Trewin Pixel paper pack 1: https://tjtrewin.itch.io/pixel-art-paper-scrolls-and-ribbons-tileset
- LCSkeleton Pixel Paper Pack: https://lcskeleton.itch.io/pixelpaper
- Stonebase UI pack: https://itchabop.itch.io/stonebase-ui-pack
- FreePixel.Art UI Kit Mini Pack: https://freepixelart.itch.io/free-pixel-art-ui-kit-mini-pack-80-sprites
- FREE Game UI Starter Pack: https://mrtnli.itch.io/game-ui-starter-pack
- Free Elegant UI: https://cuppar.itch.io/elegant-ui
- 8x8 Vintage Mansion Tileset: https://aurathedev.itch.io/vintage-mansion-tileset-8x8
- Pixelart Interior Top-Down RPG Asset Pack v2: https://zedpxl.itch.io/pixelart-interior-top-down-rpg-asset-pack
- Top-Down Retro Interior: https://penzilla.itch.io/top-down-retro-interior
- Pixel World Cozy Life Simulation 16x16: https://bitglow.itch.io/pixel-world-complete-pack-pixel-art-assets
- Vintage House Asset Pack: https://pixelalli.itch.io/vintage-house-asset-pack
- Horror Interior Tileset: https://emiemigames.itch.io/horror-interior-tileset
- TopDown Interior Home Tileset: https://btl-games.itch.io/topdown
- Simple Interior Tileset + furniture: https://doppelmulti.itch.io/simple-interior-tileset-furniture
