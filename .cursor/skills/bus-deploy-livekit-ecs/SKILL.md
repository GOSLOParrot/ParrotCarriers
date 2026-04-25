---
name: bus-deploy-livekit-ecs
description: 用于 ParrotCarriers 在阿里云 ECS 上推进 LiveKit Bus 稳定性验证与部署策略决策，聚焦 Castle 2C8G、Gemini Live 低延迟、移动端连接、TURN/直连对照与视频档位。
---

# bus-deploy-livekit-ecs

Use this skill when preparing or executing deployment-oriented Bus tasks on Alibaba Cloud ECS. This skill guides post-MVP decisions for LiveKit self-hosting in ParrotCarriers: the goal is no longer simply "it connects", but to identify which deployment, network, and video-tier strategy best supports stable low-latency Gemini Live conversation and future A10-assisted perception.

## 1. Purpose and Scope

这份 skill 只服务于：
- `ParrotCarriers` 的 LiveKit Bus 部署策略、稳定性验证和后续扩展决策
- Castle (`2C8G ECS`) 上的移动端连接质量、Gemini Live 低延迟体验、TURN/直连对照和视频档位验证
- 明确 Castle 与 Mecha/A10 的物理边界，避免把 A10 感知负载或长期高质量视频压力错误放到 Castle
- 把尚未取得的 ECS 测试事实转化为明确验证目标，而不是把“最小连通”当成后续架构目标

它不负责：高级 Bus 协议设计、内部 Node 设计、纯 Docker 通用语法约束（参见 `docker-best-practices.mdc`）。

## 2. Trigger Scenarios

当涉及以下任务时，请主动应用本知识：
- 编写或审查 `docker-compose.yml` / `livekit.yaml`
- 讨论 LiveKit 自托管端口、TLS、域名、Redis 依赖
- 评估当前 `2C8G ECS` (Castle) 该部署哪些服务，哪些不该部署
- 设计直连 / TURN / 视频档位对照测试
- 讨论 Gemini Live 低延迟与主视频质量上限
- 分析 ECS 实测中出现的 ICE failed、DTLS timeout、TRANSPORT_FAILURE、Brain 缺席、房间 idle close 等现象
- 执行 Sprint 4 稳定性验证的 Go / No-Go 检查

## 3. Key Domain Knowledge (领域真相)

### 3.1 LiveKit 官方拓扑与网络要求
LiveKit 的网络配置优先级高于通用 Docker 习惯，但必须区分“服务监听端口”和“需要对公网开放的端口”：
- **TCP 7880**: API / WebSocket 信令端口。开发或最小验证阶段可临时直连；更接近生产的公网部署通常应放在可终止 SSL 的 LB 或反向代理后面，而不是默认裸暴露。
- **TCP 7881**: WebRTC TCP Fallback。需要对公网开放。
- **UDP 50000-60000**: WebRTC 媒体默认端口范围（官方默认值）。
  - 当前项目 `livekit.yaml` 实际分配范围已收窄为 `50000-50200`，安全组和端口映射必须与当前 `rtc.port_range_start/end` 保持一致。
  - 如果未来启用了 `rtc.udp_port`，则使用单端口 UDP mux，`port_range_start/end` 将不再生效。
- **UDP 7882**: ICE/UDP mux（可选，对应 `rtc.udp_port`），不是 TURN/TLS。
- **TCP 5349**: TURN/TLS（可选，对应 `turn.tls_port`）。若不使用 LB、且需要对客户端广告公网 TURN/TLS，官方建议使用 `443`。
- **UDP 3478**: TURN/UDP（可选，对应 `turn.udp_port`）。
- **TCP 6379**: Redis（推荐用于生产或扩展场景；仅内网访问，严禁暴露到公网）。

### 3.2 域名 / TLS / 接入模式约束
- **当前目标不是证明能连通**：`ws://<ip>:7880` 直连已经只能作为 smoke test 或回归基线。
- **Sprint 4 前置目标**：比较移动端在 `IP 直连`、`域名 + WSS`、`TURN/UDP`、`TURN/TLS 443` 下的连接稳定性、延迟和断链恢复。
- **公网 / 更接近生产模式**：必须明确主域名、可信 CA 证书、SSL 终止位置（LB / 反向代理）、是否启用 TURN 以及 TURN 域名。
- **硬约束**：不要把“开发直连 IP 跑通”表述成“已经满足官方推荐的安全公网部署”；也不要因为直连理论路径短，就默认它对移动端最稳。

### 3.3 Docker 化部署注意事项
- LiveKit 官方文档指出：**Docker 化部署优先使用 `host networking` 以获得最佳网络表现**。
- 当前 `ports:` 映射可以继续作为可审查基线，但它不再是目标策略，只是对照组。
- Sprint 4 稳定性验证必须把 `ports:` 映射、host networking 或等价低开销网络路径作为明确变量，关注 UDP 端口范围、外网 IP 发现、NAT 行为和 DTLS/SRTP timeout。

### 3.4 机器资源边界 (Castle vs Mecha)
- **Castle** (`ecs.g9i.large`, 2C8G): 作为常驻控制面，内存与算力极度有限。
- **Mecha** (A10 抢占式): 作为未来的按需感知节点（跑 GPU 密集型任务）。
- 当前所有部署验证均发生在 Castle 上，因此**必须控制负载**。

### 3.5 当前阶段目标：稳定性验证
Bus/LiveKit 已过“能不能通”的 MVP 阶段。后续部署建议必须围绕 **目标、缺失事实和验证动作** 展开：

- **目标 A：Gemini Live 低延迟对话**  
  保持音频、信令和 Brain Agent 稳定，目标体感约 1.5s；主视频默认档不应为了画质牺牲对话。
- **目标 B：移动端连接稳定**  
  验证直连 UDP 是否真的稳定；对照 TCP fallback、TURN/UDP、TURN/TLS 443。
- **目标 C：主视频档位可控**  
  默认按 Gemini 需求低码率低延迟；`identify_object` 走按需截图；A10/SAM2/DINOv2 在线且有任务时才短时升档。
- **目标 D：Castle 负载边界清楚**  
  Castle 运行 LiveKit、Redis、Token Mint、Brain 控制面和轻量日志；不承载持续 DSG 重感知和 A10 级 CV。
- **目标 E：问题可定位**  
  ECS 测试要区分 Brain 缺席、Token 成功但 Agent 未派单、ICE/DTLS 失败、Android 前后台断链、房间 idle close、视频首帧/发布问题。

### 3.6 仍待 ECS 实测补齐的事实
后续建议必须显式指出哪些事实还没拿到，不能假装已经知道答案：

- Castle 2C8G 在当前 LiveKit + Brain + Token Mint 下的 CPU、内存、网络、容器负载曲线。
- 东京 ECS 到 Android 真机的 direct UDP RTT、packet loss、jitter、selected candidate pair。
- `ports:` 映射和 host networking/等价低开销路径的差异。
- `ws://IP`、`wss://域名`、TURN/UDP、TURN/TLS 443 的延迟和稳定性差异。
- 默认视频档从 720p/30fps/1.5Mbps 降到 Gemini 友好档后的音频/对话/断链变化。
- Android 切后台、回前台、正常退出、强杀 App 时服务端分别呈现的断链原因。
- Brain 默认派单修复后，Agent 是否稳定进房，以及 HUD `Brain=yes` 是否可靠。

### 3.7 Sprint 4 稳定性策略
- Castle 直连 `ws://<ip>:7880` 只是 smoke test，不等于稳定公网部署。
- Gemini Live 是低延迟流式对话 Agent，默认应优先音频、信令和稳定连接；主视频默认档不应为了画质牺牲对话体感。
- 主视频上限由消费者反推：Gemini 默认低码率低延迟，`identify_object` 用按需截图补充，A10/SAM2/DINOv2 在线且有任务时才短时升档。
- 直连理论路径短，但移动 NAT、UDP 映射、Android 前后台和 Wi-Fi/蜂窝切换可能让 TURN 更稳。必须用同一脚本对照 direct vs TURN，而不是凭直觉决定。
- 若继续使用 Docker `ports:` 映射做稳定性验证，必须明确这是历史折中和对照组；需要单独评估 host networking 或等价低开销部署路径。
- 低质量测试束只能证明连通性和断线层级。Sprint 4 架构决策优先参考 LiveKit 官方建议、类似 WebRTC/移动项目经验和少量高信号指标。

## 4. Output Style (强制输出规范)

每次基于此 skill 输出部署建议时，必须强制包含以下结构化模块：

1. **目标与待验证问题**: 明确本次要支撑 Gemini 低延迟、移动端稳定、视频档位、TURN/直连对照、Castle 负载中的哪一个目标，以及目前缺哪些 ECS 事实。
2. **所需文件清单**: 列出将要涉及的文件（如 `docker-compose.yml`, `livekit.yaml`, `.env.example`）。
3. **接入模式与 TLS 前提**: 明确当前是在用 smoke-test 直连、域名 + WSS、TURN/UDP、TURN/TLS，还是在做对照测试，并写清主域名、TURN 域名、证书、SSL 终止位置是否已具备。
4. **端口 / 安全组清单**: 明确列出需要的 TCP/UDP 规则。默认可引用官方 `50000-60000/udp`，但项目实际放行范围必须与当前 `livekit.yaml` 保持一致；如果项目已收窄到 `50000-50200`，不得再强制要求放开 `50000-60000`。
5. **Docker 网络策略说明**: 明确当前采用的是官方推荐的 `host networking`、等价低开销路径，还是把 `ports:` 映射作为对照组。
6. **稳定性验证策略**: 若任务涉及 Sprint 4、视频流、Gemini Live、A10 或移动端断链，必须说明 direct / TURN 对照、视频档位、采集指标、预期成功标准和哪些测试数据不能用于架构决策。


## 5. References
- LiveKit Self-hosting: https://docs.livekit.io/transport/self-hosting/
- `.cursor/memory/architecture/sprint4_livekit_stability_and_video_strategy.md`
- `docs/InfoCollections/GPT/2026-04-08_docker_skill_audit_report.md`
- `docs/InfoCollections/Opus/24_parrotcarriers_bus_architecture.md`
- `docs/middleaudit/ecs_infrastructure_snapshot_2026-03.md`
