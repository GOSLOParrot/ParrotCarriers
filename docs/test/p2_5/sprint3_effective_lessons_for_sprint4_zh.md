# Sprint3 真机测试有效经验与 Sprint4 输入

> 日期：2026-04-28  
> 状态：Sprint3 smoke 收口稿  
> 用途：把散落在对话、log、测试矩阵和完成报告里的结论筛选成 Sprint4 可用输入；避免把测试束噪声继续带入 AR App 设计。

## 1. 当前结论

Sprint3 真机测试的核心目标是验证 P2.5 数据流生命周期，而不是完成正式 AR App 启动流程。

截至 2026-04-26 的最后一轮 smoke，以下骨架可视为已跑通：

- Token Mint / LiveKit 入房基本可用。
- Unity 真机能进入 `parrot-main`，Brain agent 能进房。
- Gemini Live 能发起对话，短句对话体感可接受。
- AR Foundation / ARCore 基本链路能到 `SessionTracking`。
- 主视频通道能产生 fresh frames，Gemini 能描述画面内容。
- Unity→Brain RPC RTT 约 129ms，说明信令/应用层不是主要瓶颈。
- 麦克风 48k baseline 在非蓝牙条件下可用。
- Graphiti 对话归档骨架可写入，但写入耗时属于后台化问题。

因此，Sprint3 可以按 **连接性 / AR / LiveKit / Gemini smoke 成功** 收口。剩余问题不应继续阻塞 Sprint3，而应进入 Sprint4 前置与协议/数据流设计。

## 2. 真正有效的遗留问题

这些问题对 Sprint4 有设计价值，应该保留为输入：

| 问题 | 为什么有效 | Sprint4 处理方向 |
|:--|:--|:--|
| 外放回声 / 自己声音被 VAD 当用户输入 | 影响移动端语音产品形态，不是简单 bug | 设计音频入口、输出路由、耳机/蓝牙 baseline、push-to-talk 或自建 ASR/VAD 备选 |
| Gemini Live 黑盒 turn-taking | 原生管线可用但时间轴和状态不可完全控 | 协议 V2 预留 `TurnEvent`、`SpeechStateEvent`，兼容未来 Line B 自建 ASR/TTS |
| 视频 publish 成功不等于有真实帧 | HUD 早期误导过调试方向 | 视频健康应拆成 track published / first frame / fresh frame / tier ack / consumer ack |
| AR Foundation 宏与真实 Android 构建漂移 | Editor/测试脚本可能掩盖真机构建问题 | 正式 AR App 场景必须基于 Unity AR Foundation 正规项目/场景搭建，不从 Dev 测试场景反推 |
| Graphiti 写入 20-46s | 长期记忆不能卡实时对话 | 通过 MemoryWriter / EpisodeArchiver / 后台投影器异步写入 |
| identify_object 缺 screenshot evidence | Gemini 黑盒“看到”不能作为可追溯证据 | Sprint4 做 `captureSnapshot` + `SnapshotEvent` + Graphiti/DSG 引用 |
| `setVideoTier` / ECP ack 时序 | Brain 不能在 Unity ack 前过度承诺 | 协议 V2 引入 command id、ack/reject、expires_at、source_turn_id |
| DSG / L2-B 与 Graphiti 边界 | 场景工作记忆与长期图不能混写 | L0 Event Stream → L2-B → 后台归档 Graphiti → Obsidian SSOT |

## 3. 应降级为测试束或噪声的问题

这些问题可以留档，但不应影响 Sprint4 产品设计方向：

- Runtime HUD 布局、按钮样式、F3/触控展开方式。
- `ParrotSelfTestCoordinator` 的 3 秒等待和自检文本。
- `Dev.unity` 的临时对象布局、测试方块、自动查找绑定。
- `Launcher -> Dev` 当前临时跳转流程。
- WebCam fallback 的产品含义；它只用于避免测试零视频轨。
- Editor 菜单静态审计是否好用。
- `unity_join_token.txt` 是否存在；这是桌面/dev-token 路径，不是真机产品判断。

## 4. 对 Sprint4 的直接输入

Sprint4 应以这些设计输入为准：

1. **双管线适配**
   - Line A：Gemini Live 原生音视频管线继续作为已跑通路径。
   - Line B：自建 ASR/TTS/VLM 管线只做协议预留，不要求 Sprint4 全实现。

2. **数据流升级**
   - 连续低码率视频：给 Gemini Live / 陪伴感知。
   - 按需截图：给 `identify_object` / Graphiti / DSG 可追溯证据。
   - Audio publish / speech state / turn event 要和 ECP 时间轴对齐。

3. **协议 V2 / ECP**
   - 从 `flyTo` / `animate` 这种纯 RPC 指令，升级到目标驱动命令 + 前端状态机 ack。
   - 指令必须有 `command_id`、时间戳、过期、优先级、可打断性、来源 turn / sighting。

4. **DSG L2-B**
   - 作为短期场景工作记忆、注意力、潜意识工作区。
   - 不直接每帧写 Graphiti。
   - 与 Graphiti / Obsidian 通过可追溯事件和后台归档解耦。

5. **正式 AR App 场景**
   - 应新建/搭建独立 AR Foundation 初始场景与正式启动流程。
   - 不从 `Dev.unity` 继承产品启动方式。
   - 但不要在 Sprint3 收口前为“UI 完整性”继续扩测试脚本。

## 5. 建议下一步

1. 更新 `active_context.md`：Sprint3 smoke 已通过，当前阶段进入 Sprint4 前置收口。
2. 更新 Sprint3 完成报告：旧的“待真机测试”口径替换为 smoke 结果和有效遗留。
3. Sprint4 前置先输出：
   - App 功能入口与生命周期
   - 数据流设计
   - 协议 V2 / ECP 草案
   - DSG L2-B / Graphiti / Obsidian 最小接口
   - P2.5 后端接口提炼清单
4. 然后再决定是否新建正式 Unity AR Foundation 初始场景。

**结论**：现在不应先创建正式 AR Foundation 场景；应先把 Sprint3 结果状态收清，再进入 Sprint4 前置设计。正式 AR 初始场景是 Sprint4 / AR App 工作区的早期实现任务，而不是用来修复测试记录混乱的手段。
