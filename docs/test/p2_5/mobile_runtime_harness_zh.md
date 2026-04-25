# 真机 / 手持端 — Runtime 测试条与自检（ParrotDiagnostics）

> **适用场景**：`Dev`（或带同一套 `ParrotDiagnostics` 预制/物体的场景）打 **Android/iOS** 包做 P2.5 / Sprint3 连通与日志对表。  
> **不适用**：无 `ParrotDiagnostics` 物体的正式上架包（若将来裁剪 harness，以 Build 配置为准）。

## 为何不能依赖 F3

`ParrotRuntimeHud` 在 **Windows / Editor** 下用键盘 **F3** 展开 IMGUI 面板。真机无物理键盘，因此从 2026-04 起在 **Android / iOS / `DeviceType.Handheld`** 上改为：

- 状态条下方显示 **大触控按钮**；
- **无需 F3** 即可打开「日志 / 自检」面板，或直接在折叠态点「运行自检」「复制最近日志」。

## 屏幕布局（真机）

1. **左上角灰框**：LiveKit / Brain / Video / AR / RTT 等快照（约每 1.5s 刷新，见 `ParrotSelfTestCoordinator`）。
2. **「打开日志 / 自检面板（真机）」**：展开与桌面 F3 相同的面板（长日志 + RTT 按钮等）。
3. **「收起日志 / 自检面板」**：折叠面板。
4. **折叠态第二行**：
   - **运行自检**：等价于面板内「Run self-test」，写日志到 `ParrotDiagnosticsLog`；
   - **复制最近日志**：`GUIUtility.systemCopyBuffer`，便于粘贴到微信/备忘录再发到电脑对表。

## 日志落盘位置（对表用）

`ParrotDiagnosticsLog` 在设备上会写：

- **`Application.persistentDataPath/parrot_diagnostics.log`**

具体路径因厂商而异，可在展开面板顶部 **Log file:** 一行查看完整路径；`adb pull` 时按该路径拉取。

## 与 Launcher / Mint 的关系

- **Launcher → Dev**：若 `DontDestroyOnLoad` 保留 `ParrotDiagnostics`，HUD 仍可用；若场景未挂该物体则无条。
- **Mint**：真机用 `parrot_config.json` 走 Mint 时，与 HUD 无关；HUD 只反映 **LiveKit 房间快照** 与 **本机发布状态**。

多通道（视频 / 麦克风 / RPC / DataChannel）与「Brain 未开能否对话」的结论见 **`unity_channels_audit_mobile_zh.md`**。

## 相关脚本（维护入口）

| 脚本 | 职责 |
|:-----|:-----|
| `ParrotRuntimeHud.cs` | IMGUI 状态条 + 真机触控 + 桌面 F3 |
| `ParrotSelfTestCoordinator.cs` | 周期快照 + 启动约 3s 后一次性自检日志 |
| `ParrotDiagnosticsLog.cs` | 控制台镜像 + 可选文件 + 剪贴板 |
| `ParrotRpcRttProbe.cs` | Brain RPC 往返探测（面板内按钮） |

## 回归检查清单（真机）

- [ ] 启动后能看到状态条与 **「打开日志/自检」** 按钮（无需键盘）。
- [ ] 点「运行自检」后，`adb logcat` 或拉取的 `parrot_diagnostics.log` 中有 `[SelfTest]` 段落。
- [ ] 展开后面板内 **Brain RPC RTT x3** 可点（需 Brain 已在房且 RPC 路由正常）。
