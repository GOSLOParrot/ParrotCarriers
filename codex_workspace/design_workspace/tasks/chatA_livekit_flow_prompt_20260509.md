# ChatA 启动提示词：LiveKit 启动流程与连接稳定性

> 用途：复制到一个新 Codex Chat，专门处理 LiveKit 房间连接、启动流程、切屏/2D 工作区保活、业务接口和安全稳定性设计。  
> 目标：先设计流程和接口，再按仓库现状实施。不要做 UI 美术，不要改无关前端结构。

## 提示词

你是 Codex，在 `D:\GOSLOParrot\ParrotCarriers` 工作。请用中文向用户汇报，但可以 Think in English。  

本 Chat 的任务是完成 **ChatA：LiveKit 启动流程、连接稳定性、模式切换业务接口设计与必要代码实现**。

### 项目策略说明

这是单人项目，当前阶段目标是让大架构能力覆盖产品需求。不要因为“协议还没写死”而回避设计核心接口；相反，缺少的核心接口和大部分业务接口都需要你补齐。

允许你设计/新增后端接口、Unity DTO、业务接口、状态枚举、菜单/Session/Workspace 相关协议字段，但必须遵守：

- 先读现有架构和协议真源，不凭空重复造一套。
- 每个新增核心接口/协议字段都写一句 `reason:`，说明为什么现有接口不足。
- 尽量向后兼容，给旧 preset / 旧 DTO 默认值。
- 不随意改已有 enum/topic/BB key 语义；如果必须改，写清楚迁移方式。
- 所有新增接口都要有最小验证路径。

### 必读入口

先读取并理解这些文件，不要全仓库乱扫：

- `.cursor/memory/INDEX.md`
- `.cursor/rules/workspace.mdc`
- `.cursor/skills/livekit-unity/SKILL.md`（如存在）
- `.cursor/skills/ar-foundation-api/SKILL.md`（如存在）
- `.cursor/memory/architecture/user_ideas_and_backend_capability_brief_20260509.md`
- `.cursor/memory/architecture/module_map_p2.md`
- `.cursor/memory/architecture/module_map_p4_snapshot.md`
- `.cursor/memory/architecture/protocol_snapshot_p4.md`
- `.cursor/memory/architecture/bus_v4.md`
- `.cursor/memory/architecture/sprint4_protocol_v2_ecp.md`
- `.cursor/memory/architecture/backend_interface_refinement_20260507.md`
- `.cursor/memory/architecture/Interface/INDEX.md`
- `.cursor/memory/architecture/Interface/menu_design_complete_20260507.md`
- `.cursor/memory/architecture/ar_app_flow_ui_design.md`
- `.cursor/memory/architecture/ar_feature_implementation_plan.md`
- `unity/ArSpike/README.md`
- `unity/ArSpike/Packages/manifest.json`
- `unity/ArSpike/Assets/Scripts/ParrotApp/**`

### 当前环境事实

- 正式 Unity App 在 `unity/ArSpike/Assets/Scripts/ParrotApp/`。
- Unity 版本：`2022.3.62f3`。
- AR Foundation / ARCore / ARKit：`5.2.2`。
- XR Interaction Toolkit：`3.1.2`。
- LiveKit Unity SDK 当前 pin 在 `unity/ArSpike/Packages/manifest.json`。
- Unity MCP 已可用，可以读场景、读 Console、抓 Scene/Game View、控制 Play。
- Token 获取策略：使用 Mint 获取 LiveKit token。先找仓库里已有 token mint / room config / env 配置，不要凭空新增外部服务。

### 第一版要实现/设计的流程

1. 启动页选择配置：
   - Scene
   - Room Setting
   - Model / Persona / Pattern / Mode
2. 权限检查：
   - 麦克风
   - 扬声器 / 蓝牙设备
   - 摄像头 / AR 权限
   - 网络连接
3. 点击 START 后进入单独转场页：
   - 播放进度条 / IPoAC 风格启动动画。
   - 同时开始 LiveKit 连接。
4. LiveKit 连接成功后：
   - 不立即打招呼。
   - 进入主界面。
5. AR 主界面：
   - 等 AR 平面识别完成。
   - 用户点击放置好鹦鹉。
   - 放置完成后，鹦鹉才做疑问动作并打招呼。
6. 输入输出设备：
   - 支持蓝牙设备和扬声器。
   - 设备切换要安全，不崩溃。
   - 断开蓝牙 / 切到扬声器 / 麦克风变化都需要稳定处理。
7. 进入 2D 工作区：
   - LiveKit session 需要保持连接。
   - 不因为切到 2D 工作区就销毁房间。
8. 菜单画布与模块连接状态：
   - GOSLO 模型模块和 2D 工作区模块没连上时，Session 不销毁。
   - 菜单设置没打开时，Session 不销毁。
   - 需要支持四档能力模式：
     - `SessionOnlySilent`：保持 Session，不说话。
     - `VoiceOnlyNoVideo`：保持对话，不启用视频。
     - `VoiceVideoNoActionMonitor`：保持对话和视频，但不监控动作。
     - `FullARCompanion`：全开。
9. 菜单画布第一轮 MVP：
   - 原菜单核心是 `Model / Persona / Mode / Scene`。
   - 本项目决定新增第五块 `2DWorkspace`。
   - 第一轮 MVP 只需要完成/设计：
     - `Model`
     - `Persona`
     - `2DWorkspace`
   - `Scene` 仍然表示感知环境 baseline，例如 `ar_handheld` / `desktop_webcam`。
   - `2DWorkspace` 表示 App 内工作表面，例如 `mansion_hub` / `workdesk` / `report_desk`。
   - 切换 `2DWorkspace` 不应销毁 LiveKit Session。
   - 如果需要新增 `global/active_workspace_id`、Workspace registry、Preset schema v2、Unity DTO，请直接设计并实现，但写明 reason。

### 需要产出

1. 先给用户一份简短架构理解：
   - 当前 LiveKit / Unity / Brain / ECP / BB / Menu 模块怎么协作。
   - 哪些是现有代码已经有的，哪些是缺口。
2. 设计业务接口：
   - 启动配置 DTO / 状态枚举 / 模式切换接口。
   - LiveKit session 生命周期接口。
   - 设备切换接口。
   - AR 放置完成后触发打招呼的事件边界。
   - 2D 工作区切换时的 session 保活接口。
   - 菜单画布 `Model / Persona / 2DWorkspace` 的最小核心接口和业务接口。
   - 如新增第五块 `2DWorkspace`，补齐 list/apply/save/fallback 的接口边界。
3. 如需改核心协议 / DTO / enum / topic / BB key：
   - 可以改，但先说明为什么。
   - 遵守 `Interface/INDEX.md` 和 `protocol_snapshot_p4.md`。
   - 在代码注释或设计文档中写 `reason:`。
4. 代码实现：
   - 只改必要文件。
   - 不动冻结测试床 `unity/ParrotDev/`。
   - 正式 App 写在 `unity/ArSpike/Assets/Scripts/ParrotApp/`。
5. 验证：
   - 用 Unity MCP 读 Console。
   - 如有 Play Mode 测试，说明测试步骤和结果。
   - 如果外部 LiveKit 房间无法真实连接，给出 mock / dry-run 和剩余风险。

### 注意事项

- 不要在连接成功后自动问候，问候必须等“AR 平面识别 + 用户放置鹦鹉完成”。
- 切换 AR / 2D / 菜单模块开关时，不应轻易销毁 LiveKit session。
- 设备切换优先稳定性，不追求复杂 UI。
- 先读现有代码再设计，不要凭空发明大架构。
- 允许补核心接口；不要因为接口缺失而把需求降级成 mock。
- 但实现顺序可以分层：先接口白膜/DTO/状态机，再接真实 LiveKit 流程。
- 最终中文汇报：改了什么、接口设计、验证结果、下一步风险。
