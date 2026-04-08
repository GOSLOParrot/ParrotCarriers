# Docker / LiveKit Skill 审查报告

> 日期：2026-04-08  
> 审查对象：`.\.cursor\skills\bus-deploy-livekit-ecs\SKILL.md`  
> 审查方法：对照 LiveKit 官方自托管文档、VM 部署文档、当前仓库 `infra` 配置进行一致性核对

## 一、结论摘要

当前仓库里真正提供 Docker / LiveKit 自托管部署指导的 skill，实质上只有 `bus-deploy-livekit-ecs`。  
它的总体方向是对的：强调 `LiveKit + Redis` 的最小部署、强调 `2C8G ECS` 的资源约束、强调 Redis 不暴露公网，这些都与当前 Phase 1 目标一致。

但该 skill 仍存在数个会误导后续部署与审查的关键问题：

1. **端口事实错误**：将 `7882` 错写成 `TURN/TLS`，且协议类型也错。
2. **端口策略自相矛盾**：前文允许按 `50000-50200` 收窄，后文却强制“不可遗漏 `50000-60000`”。
3. **官方前提缺失**：没有把域名、SSL 证书、LB / 反向代理前置条件写成明确约束。
4. **Docker 部署建议缺失**：官方明确提到 Docker 化部署时优先使用 `host networking` 以获得最佳效果，但该 skill 完全未提。
5. **阶段验收项轻微越界**：在“最小部署验证”阶段示例里引入了 `Worker 可连入 Room`，容易把 Phase 1 的最小验收边界说乱。

结论：**该 skill 可继续作为部署讨论的入口，但不能再被当作“确定无误的领域真相源”直接复用，需先修正。**

## 二、审查范围与证据来源

### 2.1 被审查文件

- `.\.cursor\skills\bus-deploy-livekit-ecs\SKILL.md`
- `.\.cursor\rules\deploy-prep-routing.mdc`
- `infra\docker-compose.yml`
- `infra\livekit\livekit.yaml`

### 2.2 官方参考

- [LiveKit Self-hosting: Ports and firewall](https://docs.livekit.io/transport/self-hosting/ports-firewall/)
- [LiveKit Self-hosting: Deployment](https://docs.livekit.io/transport/self-hosting/deployment.md)
- [LiveKit Self-hosting: Virtual machines](https://docs.livekit.io/home/self-hosting/vm)

## 三、详细发现

### 3.1 高风险：`7882` 端口语义写错

当前 skill 写法：

```30:37:.cursor/skills/bus-deploy-livekit-ecs/SKILL.md
LiveKit 的网络配置优先级高于通用 Docker 习惯，核心端口清单必须在安全组和网络映射中体现：
- **TCP 7880**: HTTP/WebSocket (API 访问与 WebRTC 信令)
- **TCP 7881**: WebRTC TCP Fallback
- **TCP 7882**: TURN TLS（Phase 1 暂未启用，compose 中不暴露）
- **UDP 50000-60000**: WebRTC 媒体传输通道（LiveKit 官方推荐安全组范围）
  - 当前 `livekit.yaml` 实际分配范围收窄为 `50000-50200`，安全组可对应只开 50000-50200
  - 云安全组开的范围 ≥ livekit.yaml 的 port_range 即可；两者需一致，否则 WebRTC 媒体不通
- **TCP 6379**: Redis（仅内网访问，严禁暴露到公网）
```

官方文档说明：

- `7882` 是 **ICE/UDP Mux**
- 对应配置项是 `rtc.udp_port`
- 它是 **UDP** 端口，不是 `TCP`
- `TURN/TLS` 默认端口是 `5349`
- 若不使用 LB，官方建议 `turn.tls_port` 对外广告端口应设为 `443`

影响：

- 会误导安全组放行策略
- 会误导 `livekit.yaml` 配置讨论
- 会误导后续“为什么某些网络环境仍连不上”的排障方向

结论：这是本次审查里最明确、最需要先修复的一项。

### 3.2 中风险：端口范围策略前后冲突

当前 skill 同时表达了两种互相冲突的规则：

1. 当前 `livekit.yaml` 已收窄到 `50000-50200`，安全组可只开这段。
2. 输出时又要求“端口 / 安全组清单不容遗漏 `50000-60000`”。

对应文本：

```53:56:.cursor/skills/bus-deploy-livekit-ecs/SKILL.md
1. **目标部署层级**: 明确当前是在做“通用 rule 检查”、“最小部署验证”还是“完整拓扑规划”，并说明依据。
2. **所需文件清单**: 列出将要涉及的文件（如 `docker-compose.yml`, `livekit.yaml`, `.env.example`）。
3. **端口 / 安全组清单**: 明确列出需要的 TCP/UDP 规则（不容遗漏 50000-60000）。
4. **本阶段不做什么**: 显式声明被排除在本次部署外的高负载组件（如 DSG, Graphiti）。
```

官方文档本意是：

- 默认推荐范围是 `50000-60000`
- 真实开放范围必须与 `rtc.port_range_start/end` 匹配
- 如果启用了 `rtc.udp_port`，则 `port_range_start/end` 不再使用

因此，这里的正确表述应是：

- **默认参考范围** 可写 `50000-60000`
- **项目当前实际放行范围** 应以 `livekit.yaml` 为准
- 如果项目明确采用 `50000-50200`，则报告中不应再强制要求必须开 `50000-60000`

否则会破坏“最小暴露面”的部署目标，也会让安全组审查结果反复摇摆。

### 3.3 中风险：把 `7880` 说成“必须在安全组和映射中体现”过于绝对

官方文档对 `7880` 的表述是：

- `7880` 是 API / WebSocket 端口
- 通常应放在可终止 SSL 的 LB 或反向代理后面
- 它并不像 `7881`、媒体 UDP 端口那样天然等价于“必须直接向公网暴露”

这和 skill 当前语气存在偏差：

- 现在 skill 写法容易让人理解为 `7880` 必须裸暴露
- 但官方更接近“它是服务端监听端口，公网暴露方式要结合 SSL / LB / 反代设计”

对于当前项目的最小 MVP 直连验证，可以继续临时暴露 `7880`。  
但 skill 应把以下两种模式分开写：

1. **开发 / 最小验证模式**：可临时直连 `7880`
2. **更接近生产的公网模式**：通过域名 + SSL + LB / 反代接入

否则临时做法会被误固化成长期规范。

### 3.4 中风险：遗漏了官方的域名、SSL、LB 前提

官方部署文档把以下内容写得很明确：

- 安全部署需要域名
- 需要可信 CA 签发的 SSL 证书
- 需要 LB 或反向代理做 HTTPS/SSL termination
- 若启用 TURN，还需要单独的 TURN 域名和证书

但 `bus-deploy-livekit-ecs` 当前虽然在触发场景里提到了 “TLS、域名”，却没有把它们提升到“输出时必须明确说明”的级别。

这会带来两个常见误读：

1. 读者以为只要 `docker-compose up` 就已经接近官方推荐部署。
2. 读者以为 `ws://IP:7880` 跑通就等同于公网 `wss://domain` 已准备完毕。

建议把以下内容补入强制输出模块：

- 当前是 **开发直连** 还是 **带域名/SSL 的公网部署**
- 是否已有主域名
- 是否已有 TURN 域名
- 是否已具备可信证书
- 是否已有 LB / 反向代理承担 TLS 终止

### 3.5 中风险：遗漏官方对 Docker 场景优先 `host networking` 的建议

官方部署文档明确写到：

> If running in a Dockerized environment, host networking should be used for optimal performance.

这不代表项目当前一定必须立刻改成 `network_mode: host`，但 skill 至少需要体现：

- 这是 **官方推荐**
- 当前项目如果继续使用显式 `ports:` 映射，是一种 **为 MVP / 可读性 / 操作便利做出的折中**
- 使用 `ports:` 的情况下，要特别注意 UDP 范围、外网地址发现与 NAT 行为

若 skill 完全不提，后续使用者会误以为“Compose 端口映射就是官方默认最佳实践”，这并不准确。

### 3.6 低风险：最小部署验收项表述有轻微越界

当前 skill 的最小部署策略写的是：

- 仅部署 `LiveKit + Redis`
- 目标是验证房间连接与 `RPC/DataChannel` 骨架是否通畅

但输出规范示例又写了：

- `Worker 可连入 Room`

这里的问题不在于这个指标本身错误，而在于它会把“最小部署验证”和“接入 Worker 的下一阶段验证”混在一起。

更稳妥的最小验收项应优先包括：

- `docker compose up` 后容器健康启动
- `7880 / 7881 / UDP 媒体端口` 与实际配置一致
- SDK 客户端可以入房
- DataChannel / RPC 最小链路打通
- Redis 仅容器内可见，不对公网开放

若要验证 Worker，应显式写成“Phase 1.5 / 下一步扩展验收项”。

## 四、与当前仓库实现的关系

### 4.1 当前 `infra` 配置没有直接继承 `7882` 错误

当前仓库 `infra\livekit\livekit.yaml` 为：

```4:9:infra/livekit/livekit.yaml
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 50200
  tcp_port: 7881
  use_external_ip: true
```

并且注释中的 TURN 端口写法是：

```22:26:infra/livekit/livekit.yaml
# Phase 2: TURN server (如果需要穿越 NAT)
# turn:
#   enabled: true
#   udp_port: 3478
#   tls_port: 5349
```

这说明：

- 当前实际配置并未把 `7882` 当成 `TURN/TLS`
- 当前项目对 TURN 的注释方向反而更接近官方文档

### 4.2 当前 Compose 选择了“端口映射 + 收窄 UDP 范围”的 MVP 折中方案

```10:19:infra/docker-compose.yml
  livekit:
    image: livekit/livekit-server:v1.10.1
    ports:
      - "7880:7880"              # HTTP/WebSocket — 信令
      - "7881:7881"              # WebRTC TCP Fallback
      - "50000-50200:50000-50200/udp"  # WebRTC 媒体传输 (匹配 livekit.yaml port_range)
    volumes:
      - ./livekit/livekit.yaml:/etc/livekit.yaml
    command: --config /etc/livekit.yaml
    restart: unless-stopped
```

这个实现和 skill 的“最小部署验证”方向基本一致。  
但它更像“可运行的 MVP 折中方案”，并不等于官方推荐的长期部署基线。

## 五、相邻流程问题

### 5.1 `deploy-prep-routing` 将 LiveKit 自托管部署路由到 `livekit-agents` skill，并不合适

当前路由规则：

```22:25:.cursor/rules/deploy-prep-routing.mdc
### 2) LiveKit 自托管部署
- 主 skill: `livekit-agents`
- 辅参考: LiveKit self-hosting 官方文档
- 输出: `livekit.yaml` / env 字段清单、端口需求、最小部署拓扑
```

问题在于：

- `livekit-agents` skill 本质是 LiveKit Agents 仓库的通用参考技能
- 它关注的是 agents SDK / repo / issue / release 信息
- 它不是专门的 self-hosting / Docker / firewall / TURN / LB 部署技能

因此，当前路由会造成“部署问题进入了 agents 资料路由”的错配。  
这不是本次官方文档核对出的端口事实错误，但它会放大部署建议不稳的问题。

## 六、修正建议

### 6.1 对 `bus-deploy-livekit-ecs` 的最低限度修正

建议至少改成以下口径：

1. 将 `7882` 修正为 `ICE/UDP mux`，协议改为 `UDP`。
2. 将 `TURN/TLS` 的说明改到 `5349`，并补充“不走 LB 时通常对外广告为 `443`”。
3. 将 “不容遗漏 `50000-60000`” 改为：
   “默认参考官方推荐范围 `50000-60000`，但项目实际放行范围必须与 `livekit.yaml` 当前 `port_range` 保持一致。”
4. 在输出规范里新增 “接入模式 / 域名 / SSL / LB 状态” 一节。
5. 在 skill 里明确：
   “Docker 化部署官方推荐 `host networking`；若项目暂用 `ports:` 映射，应说明这是 MVP 折中方案，而非默认最佳实践。”
6. 将 `Worker 可连入 Room` 从最小验收示例移出，或标记为下一阶段扩展验收。

### 6.2 对路由规则的修正建议

建议把 `deploy-prep-routing.mdc` 中的 LiveKit 自托管部署主 skill 改为：

- 继续以 `bus-deploy-livekit-ecs` 承担项目内部署约束
- 同时强制参考 LiveKit self-hosting 官方文档
- 不再把 `livekit-agents` 当作 LiveKit 自托管部署的主 skill

## 七、最终判定

`bus-deploy-livekit-ecs` 目前属于：

- **方向正确**
- **细节存在实质性错误**
- **在继续使用前应先修**

如果只看“能否指导当前 `LiveKit + Redis` 最小部署”，它还勉强可用；  
但如果把它当作今后所有 Docker / ECS / LiveKit 部署审查的事实基线，当前版本风险偏高。

最优先修复项排序如下：

1. 修正 `7882` / `TURN` 事实错误
2. 消除 `50000-60000` 与 `50000-50200` 的规则冲突
3. 补上域名 / SSL / LB 前提
4. 补上 Docker 场景下 `host networking` 的官方建议
5. 收紧最小部署验收项边界
