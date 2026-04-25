---
name: bus-deploy-livekit-ecs
description: 用于ParrotCarriers在阿里云ECS上的Bus部署准备与执行，聚焦 LiveKit 官方拓扑与 2C8G 主机约束。
---

# bus-deploy-livekit-ecs

Use this skill when preparing or executing deployment-oriented Bus tasks on Alibaba Cloud ECS. This skill provides the definitive domain knowledge for LiveKit self-hosting within the ParrotCarriers project.

## 1. Purpose and Scope

这份 skill 只服务于：
- `ParrotCarriers` 的 Docker / LiveKit 自托管部署准备
- 阿里云 ECS 场景下的最小部署与后续扩展
- 明确 Castle (2C8G) 与 Mecha (A10) 的物理边界约束

它不负责：高级 Bus 协议设计、内部 Node 设计、纯 Docker 通用语法约束（参见 `docker-best-practices.mdc`）。

## 2. Trigger Scenarios

当涉及以下任务时，请主动应用本知识：
- 编写或审查 `docker-compose.yml` / `livekit.yaml`
- 讨论 LiveKit 自托管端口、TLS、域名、Redis 依赖
- 评估当前 `2C8G ECS` (Castle) 该部署哪些服务，哪些不该部署
- 执行部署前的 Go / No-Go 检查

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
- **开发 / 最小验证模式**：允许暂时使用 `ws://<ip>:7880` 或直接映射端口，目标是验证房间连接、DataChannel、RPC 等基础链路。
- **公网 / 更接近生产模式**：必须明确主域名、可信 CA 证书、SSL 终止位置（LB / 反向代理）、是否启用 TURN 以及 TURN 域名。
- **硬约束**：不要把“开发直连 IP 跑通”表述成“已经满足官方推荐的安全公网部署”。

### 3.3 Docker 化部署注意事项
- LiveKit 官方文档指出：**Docker 化部署优先使用 `host networking` 以获得最佳网络表现**。
- 但当前 ParrotCarriers Phase 1 为了可读性、可审查性和最小化操作复杂度，可接受继续使用显式 `ports:` 映射作为 **MVP 折中方案**。
- 若继续使用 `ports:` 映射，输出中必须显式提醒：这不是官方默认最佳实践；要额外关注 UDP 端口范围、外网 IP 发现与 NAT 行为。

### 3.4 机器资源边界 (Castle vs Mecha)
- **Castle** (`ecs.g9i.large`, 2C8G): 作为常驻控制面，内存与算力极度有限。
- **Mecha** (A10 抢占式): 作为未来的按需感知节点（跑 GPU 密集型任务）。
- 当前所有部署验证均发生在 Castle 上，因此**必须控制负载**。

### 3.5 部署分层策略 (Layered Deployment)
不要一上来就尝试部署完整拓扑。必须严格遵循分层落地策略：
- **最小部署验证 (当前执行重点)**：仅部署 `LiveKit` + `Redis`。目标是验证房间连接与 RPC/DataChannel 骨架是否通畅。
- **完整拓扑 (仅认知对齐，非当前执行)**：包含 Neo4j、Graphiti、多 Worker (Brain/Scheduler/DSG/Nanobot)。目前 2C8G 塞不下这些重负载服务，**严禁将 DSG、Graphiti、Neo4j 强塞进第一版实际落地的 `docker-compose.yml` 中。**

## 4. Output Style (强制输出规范)

每次基于此 skill 输出部署建议时，必须强制包含以下结构化模块：

1. **目标部署层级**: 明确当前是在做“通用 rule 检查”、“最小部署验证”还是“完整拓扑规划”，并说明依据。
2. **所需文件清单**: 列出将要涉及的文件（如 `docker-compose.yml`, `livekit.yaml`, `.env.example`）。
3. **接入模式与 TLS 前提**: 明确当前是“开发直连”还是“域名 + SSL + LB/反代”的公网方案，并写清主域名、TURN 域名、证书、SSL 终止位置是否已具备。
4. **端口 / 安全组清单**: 明确列出需要的 TCP/UDP 规则。默认可引用官方 `50000-60000/udp`，但项目实际放行范围必须与当前 `livekit.yaml` 保持一致；如果项目已收窄到 `50000-50200`，不得再强制要求放开 `50000-60000`。
5. **Docker 网络策略说明**: 明确当前采用的是官方推荐的 `host networking`，还是 Phase 1 的 `ports:` 映射折中方案。


## 5. References
- LiveKit Self-hosting: https://docs.livekit.io/transport/self-hosting/
- `docs/InfoCollections/GPT/2026-04-08_docker_skill_audit_report.md`
- `docs/InfoCollections/Opus/24_parrotcarriers_bus_architecture.md`
- `docs/middleaudit/ecs_infrastructure_snapshot_2026-03.md`
