# Sprint 4 前置：LiveKit 稳定性、视频上限与门控策略

> 更新时间：2026-04-25  
> 状态：Sprint 4 前置决策稿  
> 用途：在进入 Sprint 4 前，把 LiveKit Bus、Unity 主视频流、Gemini Live、未来 A10 DSG/SAM2/DINOv2 的稳定性目标和调研方向固定下来。

## 1. 当前判断

ParrotCarriers 的 Bus 与数据流已经超过最小 MVP 的“能不能通”阶段。下一步不应继续堆低质量真机按钮日志，而应转向：

1. 先把最小连通链路修通并复测：Token Mint、LiveKit 入房、Brain 在房、音视频发布、RPC/DataChannel。
2. 用官方建议和类似项目经验更新部署与视频策略。
3. 用少量高信号探针验证关键假设，而不是自建一套不成熟的质量分析系统。

当前架构方向仍然成立：

- Unity 发布一个主视频源 `ar-camera`。
- LiveKit 负责分发。
- Gemini Live 低频、低分辨率语义消费。
- `identify_object` 通过按需 `captureSnapshot` 补充可存档图像。
- 未来 A10 DSG Worker 订阅主流或补充通道，按 SAM2/DINOv2 需要做采样和重计算。

但“主视频必须始终高质量”不再作为默认原则。Sprint 4 应把主视频理解成 **策略控制的共享源**：质量上限由最重消费者的真实需要决定，平时按 Gemini Live 的稳定对话需求降到更稳的档位。

## 2. 部署策略升级

### 2.1 当前 Castle 角色

Castle (`ecs.g9i.large`, 2C8G) 仍是常驻控制面与最小媒体入口：

- 适合常驻：LiveKit、Redis、Token Mint、Brain 控制面、轻量日志。
- 不适合常驻：Graphiti/Neo4j 重负载、DSG 重感知、SAM2/DINOv2、持续视频分析。
- Mecha/A10 仍应作为按需感知节点。

### 2.2 从“最小直连”升级到“稳定性验证”

最小直连 `ws://<ip>:7880` + `ports:` 映射只证明链路可用，不代表生产稳定。

Sprint 4 前置应对照三种接入：

| 模式 | 目标 | 适用阶段 |
|:--|:--|:--|
| IP 直连 + 当前 `ports:` | 快速验证 Token/Room/RPC/DataChannel | 仅 smoke test |
| 域名 + TLS/WSS + 现有端口映射 | 验证移动端信令稳定性和证书路径 | Sprint 4 前置 |
| 官方推荐网络形态：Linux host networking 或等价低开销路径 + TURN | 验证媒体稳定性上限 | Sprint 4 稳定性评估 |

LiveKit 官方重点包括：

- 自托管生产需要域名和可信 TLS，客户端应使用 `wss://`。
- Docker 化媒体服务官方建议优先 `host networking` 获得最佳网络表现。
- UDP 媒体端口、外网 IP 广告、NAT 行为比普通 HTTP 服务更关键。
- TURN/TLS 443 能覆盖更严格网络，但会增加延迟和带宽成本。

### 2.3 直连并不必然最快或最稳

“直连”省掉 TURN relay，理论路径更短，但移动网络下可能被 NAT、运营商、Wi-Fi、电源策略和 UDP 映射刷新影响。当前日志里的 `TRANSPORT_FAILURE`、ICE failed、DTLS timeout 更像移动端连接路径或生命周期问题，而不是单纯带宽不够。

因此要比较的是：

- direct UDP srflx：最低延迟，最依赖 NAT/UDP 稳定。
- direct TCP fallback：更可达，媒体体验通常更差。
- TURN/UDP：更可控，可能略增延迟和服务器带宽。
- TURN/TLS 443：最可达，延迟最高，作为容灾路径。

Sprint 4 不应默认强制 TURN；应先做直连 vs TURN 的对照测试。

## 3. 视频上限策略

### 3.1 当前 720p/30fps/1.5Mbps 的位置

`1280x720@30fps H.264 1.5Mbps` 是一个可用的开发上限，不应被视为长期默认。

对 Gemini Live 来说：

- 视频质量需求不高。
- 语义采样低频，云端采样不可控。
- 对话体感目标约 1.5s，更在意低延迟、稳定音频、持续连接。

对未来 A10 SAM2/DINOv2 来说：

- 发现中物体不一定需要持续 720p/30fps。
- 更可能需要“低频高质量关键帧 + 必要时短时升档”。
- 重计算应在 Mecha/A10，不应让 Castle 或手机长期承担高负载。

因此主视频上限建议按以下顺序确定：

1. Gemini Live 默认档：优先稳定和低延迟，建议从 480p/15fps/600-900kbps 级别评估。
2. 识别按需档：`captureSnapshot` 走低分辨率 JPEG，例如 320x240 或 512 宽边，带时间戳。
3. A10 感知档：只有 A10 在线且任务需要时，短时请求更高帧率或更高分辨率。
4. 调试高质量档：保留 720p/30fps/1.5Mbps 作为测试上限，不作为默认。

## 4. 门控设计需求

Sprint 4 应设计“两端闸口”，但不要一次实现复杂策略。

### 4.1 Unity 端闸口

Unity 是唯一知道 AR 生命周期、前后台、相机帧是否真实、手机热/电/权限状态的一端。Unity 端应负责：

- 首帧门：没有真实帧不宣称视频可用。
- 生命周期门：切后台、锁屏、权限丢失时主动 mute/暂停/重建。
- 视频档位门：根据 Brain/A10/用户动作切换 publish 参数或重建 track。
- 补充截图门：按需 `captureSnapshot`，不把所有视觉需求都压到主视频流。

Unity 端不应做重识别逻辑；它只做采集、门控、降级与补充数据发送。

### 4.2 云端/Bus 闸口

云端更适合做消费者调度和策略决策：

- Brain 是否在房。
- A10 是否在线。
- 当前是否有识别任务。
- 是否需要临时升档。
- 网络质量是否应降档。
- 失败时是否切换到截图/RPC 补充通道。

Bus 不应把视频质量策略写死在某个消费者里，应通过轻量控制信号驱动 Unity 端。

## 5. 测试策略

### 5.1 低质量测试数据的边界

手动按钮、HUD、自检文本、手机照片和零散 logcat 适合回答：

- 能不能连上。
- Brain 是否在房。
- 哪个通道完全不工作。
- 断线发生在前后台、关 app、网络切换还是正常运行中。

它们不适合直接回答：

- 最优 bitrate。
- 是否启用 TURN。
- 该不该 simulcast。
- A10 需要什么视频上限。
- 质量切换阈值。

### 5.2 高信号最小数据

Sprint 4 前置只需要少量可复现指标：

- LiveKit 服务端：participant join/leave、agent dispatch、track publish、ICE state、selected candidate type、RTP stats、room close reason。
- Unity 客户端：connect/reconnect/disconnect、foreground/background、quit、publish config、first frame、connection quality。
- WebRTC stats：RTT、packet loss、jitter、FPS、sent bitrate、quality limitation reason、candidate pair type。

输出形式可以是 JSONL ring buffer，一键导出最近 2 分钟。不需要长期数据库化。

## 6. Sprint 4 研究清单

联网调研应优先找以下资料：

1. LiveKit 官方 self-hosting deployment：TLS/WSS、TURN、host networking、Redis、端口范围、Prometheus metrics。
2. LiveKit firewall / TURN field guide：ICE、DTLS/SRTP timeout、TURN/TLS 443、relay-only 的适用场景。
3. LiveKit Unity SDK 或底层 WebRTC stats：如何在 Unity/Android 获取 RTT、packet loss、jitter、bitrate、candidate pair。
4. LiveKit simulcast / dynacast / adaptive stream：发布端 CPU/带宽成本，订阅端视图驱动降级，是否适合 Unity SDK。
5. Android 后台与网络切换：App pause/quit、ICE disconnected、reconnect 的真实行为。
6. 移动 AR/WebRTC 项目经验：720p/30 vs 480p/15，H264/VP8，硬编性能，发热与电池。
7. 低延迟语音 Agent 经验：视频对实时对话延迟的影响，如何优先保障音频与信令。
8. SAM2/DINOv2 视频输入经验：中物体发现需要的关键帧分辨率、采样率、短时 burst 策略。

## 7. 推荐决策

当前不建议继续扩大真机测试脚本。推荐顺序：

1. 修复 Brain 默认派单问题并复测连通。
2. 将当前部署从“能跑”升级为“可对照”：直连、TURN、低视频档、高视频档。
3. 先把默认视频档调低到 Gemini Live 友好档，保留高档作为任务触发。
4. 设计 Unity 端首帧/生命周期/视频档位闸口。
5. 设计云端 A10 在线与识别任务闸口。
6. 只采集最小高信号指标，避免让低质量测试数据主导架构。

## 8. 新 Chat 提示

```markdown
请先阅读 `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`。

当前 Sprint 4 前置目标不是继续堆真机测试脚本，而是：
1. 确认最小连通链路；
2. 依据 LiveKit 官方和类似项目经验升级部署策略；
3. 把主视频流从“固定高质量”改成“策略门控共享源”；
4. 区分 Gemini Live 默认低延迟档、identify_object 按需截图档、A10 感知升档；
5. 设计 Unity 端与云端 Bus 双闸口；
6. 只收集少量高信号 WebRTC/LiveKit 指标。
```
