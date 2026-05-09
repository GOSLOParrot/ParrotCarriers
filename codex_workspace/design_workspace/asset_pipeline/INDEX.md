# Figma / Unity 素材工作区

> 用途：记录素材收集、Figma 草图、Unity 预览和导出规则。

## 目录建议

未来可在 Unity 内使用：

- `unity/ArSpike/Assets/UI/Boot/`
- `unity/ArSpike/Assets/UI/Hud/`
- `unity/ArSpike/Assets/UI/ToolCabinet/`
- `unity/ArSpike/Assets/UI/Workspace/`
- `unity/ArSpike/Assets/UI/Notifications/`
- `unity/ArSpike/Assets/UI/Skins/Pirate/`
- `unity/ArSpike/Assets/UI/Placeholders/`

设计区先只记录清单和草图，不急着复制大图。

## 插件 / 工具候选

| 工具 | 用途 | 状态 |
|:--|:--|:--|
| Figma 插件 | 做第一版页面、组件、导出 PNG / 9-slice 参考。 | Codex 已启用；可使用 `use_figma` / `generate_figma_design` / `search_design_system` |
| Unity Editor / Unity MCP | 场景、Prefab、UI 预览和自动化检查。 | 当前 Codex 未接入 Unity MCP；建议安装 CoplayDev MCP for Unity 后接 `http://localhost:8080/mcp` |
| Browser 插件 | 本地 Web 控制台预览。 | Web 阶段使用 |

## 当前版本锁

| 项 | 当前值 |
|:--|:--|
| Unity Editor | 2022.3.62f3 |
| AR Foundation / ARCore / ARKit | 5.2.2 |
| XR Interaction Toolkit | 3.1.2 |
| LiveKit Unity SDK | `https://github.com/livekit/client-sdk-unity.git#7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796` |

这些值来自 `unity/ArSpike/ProjectSettings/ProjectVersion.txt` 和 `unity/ArSpike/Packages/manifest.json`。

## MCP 设置记录

- Figma：Codex 配置中 `figma@openai-curated` 已 enabled。使用写入类工具前要先按 Figma workflow 加载 `figma-use` skill，并提供 Figma 文件 URL / file key。
- Unity：当前 Codex 工具列表里没有 Unity MCP。建议优先尝试 `CoplayDev/unity-mcp`：在 Unity Package Manager 用 Git URL 安装 `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity`，打开 `Window > MCP for Unity`，启动 HTTP server，Codex MCP 服务器地址用 `http://localhost:8080/mcp`。

## 第一批素材清单

| 类别 | 例子 |
|:--|:--|
| Boot | 启动页背景、按钮、加载动画、转场。 |
| HUD | 羊皮纸面板、连接 / 麦克风 / 视频 / Brain / 视觉状态 icon。 |
| ToolCabinet | 设置、相机、拍照、放大镜、注意力框、工作区、任务按钮。 |
| Notifications | 纸条、展开纸、猫爪 / 手、接受 / 垃圾桶。 |
| Pirate Skin | 望远镜、眼罩遮挡、脏镜片、海图面板、海盗字体。 |

## 2026-05-09 参考资产板

- `reference_assets_20260509.md`：Stardew Valley 标题页、Papers Please 标题/报纸/工作桌、像素大厅、nanobot 视觉、蓝白鹦鹉照片等参考图的用途归档。
- `reference_images/README.md`：重要参考图的图片目录与命名规则。
- `reference_images/manifest_20260509.md`：6 张关键参考图的固定文件名与用途清单。
# Asset Pipeline 设计区

## 2026-05-10

- `pixel_asset_audit_20260510.md`：用户提供的 Pixel Asset 候选素材审计与第一版 App 使用建议。
