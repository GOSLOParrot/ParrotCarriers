# Docker 配置修复报告

> 日期：2026-04-08  
> 范围：`infra/docker-compose.yml`、`infra/livekit/livekit.yaml`、部署相关 skill / rule

## 一、本次修复目标

根据前一轮审查结果，本次修复聚焦两个问题：

1. 让当前 Phase 1 的 `LiveKit + Redis` 最小部署在配置语义上真正成立，而不是“Redis 容器存在但未被使用”。
2. 修正部署知识层的错误口径，避免后续继续把错误的 LiveKit 端口、TLS、Docker 网络建议传播到新的配置或审查中。

## 二、已完成修改

### 2.1 `infra/livekit/livekit.yaml`

已新增 Redis 配置：

```4:12:infra/livekit/livekit.yaml
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 50200
  tcp_port: 7881
  use_external_ip: true

redis:
  # Phase 1 最小部署中使用同 compose 内的 Redis 服务。
  address: redis:6379
```

效果：

- `LiveKit` 现在会实际使用 compose 内部的 `redis` 服务。
- 当前部署终于和“Phase 1 = `LiveKit + Redis` 最小验证”这一定义保持一致。

### 2.2 `infra/docker-compose.yml`

已给 `livekit` 增加对 `redis` 健康状态的启动依赖，并给 `redis` 补上健康检查：

```9:34:infra/docker-compose.yml
services:
  livekit:
    image: livekit/livekit-server:v1.10.1
    depends_on:
      redis:
        condition: service_healthy
    ports:
      - "7880:7880"              # HTTP/WebSocket — 信令
      - "7881:7881"              # WebRTC TCP Fallback
      - "50000-50200:50000-50200/udp"  # WebRTC 媒体传输 (匹配 livekit.yaml port_range)
    volumes:
      - ./livekit/livekit.yaml:/etc/livekit.yaml
    command: --config /etc/livekit.yaml
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    expose:
      - "6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 5s
    restart: unless-stopped
```

效果：

- `livekit` 不再在 `redis` 尚未 ready 时抢跑。
- 容器状态更容易观察，也更利于后续排查“是服务没启动，还是链路没打通”。
- Redis 仍保持只在 Docker 内网暴露，没有额外暴露公网端口。

### 2.3 部署知识层修正

已修复：

- `.\.cursor\skills\bus-deploy-livekit-ecs\SKILL.md`
- `.\.cursor\rules\deploy-prep-routing.mdc`

关键修正点包括：

- 把 `7882` 从错误的 `TURN/TLS` 改回官方定义的 `ICE/UDP mux`
- 补回 `TURN/TLS = 5349`、无 LB 时常见对外广告为 `443`
- 纠正 `50000-60000` 与当前 `50000-50200` 的冲突表述
- 明确域名、SSL、LB/反代是更接近生产部署时的前提
- 明确 Docker 场景下 `host networking` 是官方推荐，而当前 `ports:` 映射只是 Phase 1 折中方案

## 三、验证结果

本次修改后，已执行：

- `docker compose -f infra/docker-compose.yml config`

结果：

- **通过**
- Compose 结构有效
- `depends_on.condition: service_healthy` 被正常解析
- `redis` 健康检查被正常解析
- 端口映射与当前 `livekit.yaml` 的 `50000-50200` 保持一致

## 四、当前仍保留的限制与风险

这次修复是“把当前 Phase 1 配置修正到自洽可审”的范围，不等于已经转为生产方案。当前仍有这些已知限制：

1. `7880` 仍然是直连暴露模式，适合开发 / MVP 连通性验证，不等于官方推荐的公网安全部署。
2. 仍未引入域名、可信证书、LB / 反向代理，因此还不是 `wss + TLS termination` 的完整方案。
3. 当前仍使用 `ports:` 映射，而不是官方更推荐的 `host networking`；这是有意保留的 Phase 1 折中。
4. `devkey: secret` 仍是开发占位值，若进入长期公网环境，必须替换。

## 五、结论

本次修复后，当前部署配置相较于之前有两个实质提升：

1. `LiveKit + Redis` 最小部署终于在语义上成立，不再是“Redis 容器空转”。
2. skill / 路由中的错误部署知识已被纠正，后续再写 Compose 或做审查时，不会继续沿用错误的端口和 TLS 口径。

因此，当前 `infra` 配置可以继续作为 **Phase 1 最小部署验证基线** 使用。  
但如果下一步目标切换为“公网稳定接入”或“更接近生产”，则应继续推进：

- 域名 + TLS
- LB / 反向代理
- TURN 策略
- 是否切换到 `host networking`
