# 部署快照 P2 — 2026-04-12

> 状态: 代码与环境已全量部署至 Castle，等待 Tmux 进程启动及连通性验证
> 本文记录本轮对话（2026-04-12）所有决策、新增文件、注意事项，供部署 chat 直接引用

---

## 0. 一句话现状

**ParrotCarriers V1 + P2 多角色骨架代码已完成。所有文件就绪，可以进行 Castle 首次部署。**

已验证（笔记本模拟）：Brain ↔ Unity 语音、Brain → Nanobot 全链路、猫娘微信 Bot  
待验证（Castle 上）：WebRTC NAT/TLS、双 bot 并行、GOSLO Telegram bot

---

## 1. 本轮新增/修改的文件

### ParrotCarriers 侧

| 文件 | 变更内容 |
|:-----|:---------|
| `src/parrot/shared/constants.py` | 新增 `HASH_GOSLO_MODE = "parrot.goslo.mode"` |
| `src/parrot/brain/agent.py` | Brain 连接时写 `mode=live`，Room 断开时写 `mode=chat` |
| `src/scripts/start_goslo_chat.py` | GOSLO Chat bot 启动脚本（in-process gateway + mode hook 注入） |
| `src/scripts/start_nanobot_worker.py` | 注入 GITHUB_TOKEN 到 MCP 配置 |
| `infra/deploy-castle.sh` | 双仓库同步 + nanobot 安装 + workspace 同步 + Node.js/exiftool + 3 tmux session 说明 |
| `infra/env-castle.template` | 新增 GEMINI_API_KEY / TELEGRAM_BOT_TOKEN / REDIS_URL / GITHUB_TOKEN |

### nanobot 侧

| 文件 | 变更内容 |
|:-----|:---------|
| `nanobot/channels/base.py` | `BaseChannel` 新增 `pre_handle_hook` 可选字段 + 调用点 |
| `nanobot/channels/goslo_mode.py` | 新增：模式感知中间件（查 Redis → live 转发/chat 放行） |
| `nanobot/config/parrot_config.json` | exec 开启 + GitHub MCP + web search maxResults 8 |
| `nanobot/config/goslo_config.json` | 新建：GOSLO Chat 配置（Telegram + exec + GitHub MCP） |

### 本地工作区文件（Castle 部署时 rsync 同步）

| 文件 | 内容 |
|:-----|:-----|
| `~/.nanobot/workspace/TOOLS.md` | 猫娘工具说明：文件系统 + `/data/workshop/` + GitHub MCP |
| `~/.nanobot/goslo-workspace/SOUL.md` | GOSLO ParrotSoul 人格 |
| `~/.nanobot/goslo-workspace/AGENTS.md` | GOSLO 行为指南 |
| `~/.nanobot/goslo-workspace/USER.md` | 共享用户画像 |
| `~/.nanobot/goslo-workspace/TOOLS.md` | GOSLO 工具说明 |

---

## 2. Castle 部署 checklist（逐步执行）

### 2.1 前置条件（在新 chat 里先确认）

- [x] Castle ECS 当前 IP 地址确认（当前已知：东京 `ecs.g9i.large`，IP: `8.216.45.45`）
- [x] SSH 可达（`ssh root@8.216.45.45`）
- [ ] Docker + Docker Compose 已安装
- [ ] `.env` 中的 secrets 准备好（见下方 Secrets 清单）

### 2.2 Secrets 清单

在 Castle 上 `.env` 文件需要填写：

```env
GOOGLE_API_KEY=<GOOGLE_API_KEY_REDACTED>   # .env 第6行已有
GEMINI_API_KEY=<GOOGLE_API_KEY_REDACTED>   # 同上（或用 KEY_2）
TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN_REDACTED>  # .env 第28行已有
GITHUB_TOKEN=<GITHUB_TOKEN_REDACTED>     # .env 第12行已有
REDIS_URL=redis://localhost:6379/0
LIVEKIT_URL=ws://<castle-ip>:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=parrot_carriers_local_dev_livekit_secret_key_v1
```

> ⚠️ 注意：`.env` 中的 LIVEKIT_URL 要改为 Castle 的外部 IP，不是 localhost

### 2.3 部署命令

```bash
# 从笔记本执行（ParrotCarriers 目录下）
cd D:\GOSLOParrot\ParrotCarriers
bash infra/deploy-castle.sh <castle-ip> [ssh-key-path]
```

deploy-castle.sh 会自动：
1. rsync ParrotCarriers 代码
2. rsync nanobot fork 代码
3. 同步本地 ~/.nanobot/workspace 和 ~/.nanobot/goslo-workspace 到 Castle
4. 创建 /data/workshop/{photos,documents,sorted}
5. pip install -e 两个仓库
6. 安装 Node.js（GitHub MCP 需要）+ exiftool（文件整理）
7. 启动 Docker services（LiveKit + Redis）
8. 健康检查

### 2.4 Castle 上手动步骤（deploy 后）

```bash
ssh root@<castle-ip>
cd /opt/parrotcarriers

# 复制并填写 .env
cp infra/env-castle.template .env
vi .env   # 填入所有 secrets

# 加载环境变量（每个 tmux session 都需要）
export $(cat .env | grep -v '#' | xargs)

# tmux session 1: Brain Agent (GOSLO Live 身体)
tmux new -s brain
cd /opt/parrotcarriers
export $(cat .env | grep -v '#' | xargs)
.venv/bin/python -m parrot.brain.agent dev

# tmux session 2: 猫娘女仆 (parrot_bus + weixin)
tmux new -s maid
cd /opt/parrotcarriers
export $(cat .env | grep -v '#' | xargs)
.venv/bin/python src/scripts/start_nanobot_worker.py --no-weixin  # 先不挂微信

# tmux session 3: GOSLO Chat (Telegram)
tmux new -s goslo-chat
cd /opt/parrotcarriers
export $(cat .env | grep -v '#' | xargs)
.venv/bin/python src/scripts/start_goslo_chat.py
```

### 2.5 验证顺序

1. **Docker 健康**: `docker compose -f infra/docker-compose.yml ps` → LiveKit + Redis 都 Up
2. **Redis 通**: `redis-cli ping` → PONG
3. **Brain Agent**: Console 模式先测 `python -m parrot.brain.agent console` → 看 Gemini 连接
4. **GOSLO Chat**: Telegram 找你的 bot → 发一条消息 → 看 GOSLO 是否回复
5. **全链路**: Brain dev 模式 + sim_unity_client → 语音触发 dispatch_task → 猫娘处理 → Brain 语音反馈

---

## 3. 本轮关键设计决策

### 3.1 GOSLO 双身体

- **Redis Key**: `parrot.goslo.mode` (Hash: active_body / live_session_id / updated_at)
- **Brain Agent**: mount 时写 `live`，Room `disconnected` 事件写 `chat`
- **GOSLO Chat bot**: `pre_handle_hook` 每条消息前查 Redis，`live` 时转发到 `parrot.external.commands` 并回"我在 Live 模式哦~"
- **两个 nanobot 实例**: 独立进程、独立 config、独立 workspace，Redis 做跨实例通信

### 3.2 多角色架构定位

- **ParrotCarriers = 副协作模块 + 信息提供商**，不做 one-for-all 工作区
- **Obsidian** = SSOT 文件/知识锚点（P3+ 通过 MCP Bridge 接入）
- **LobeChat/Telegram 群** = 群聊 UI（P3）
- **不引入 AutoGen/CrewAI** — Agent 是多进程独立实例，Redis Bus 已够用

### 3.3 工具能力扩展

- `exec` 开启（exec: true），猫娘可执行 shell 命令（文件整理、mv/cp/find 等）
- GitHub MCP 接入（npx @modelcontextprotocol/server-github + GITHUB_TOKEN）
- DuckDuckGo 搜索 maxResults 提升到 8
- Castle 上 `/data/workshop/` 作为文件整理测试区

### 3.4 Obsidian/GitHub 工作区路线图

- **近期（P2）**: GitHub MCP 已接入，可读写 GOSLOParrot/* 仓库文件
- **中期（P3）**: Obsidian MCP（obsidian-local-rest-api）接入，vault 通过 git 同步
- **策略**: 成熟外部项目作为主工作区，ParrotCarriers 作为信息输入源

---

## 4. 部署连通性测试与已知问题处理 (2026-04-13)

### 4.1 ECS 部署连通性排坑记录

本阶段在验证端到端（Unity/Python Client -> 公网 -> Castle LiveKit -> Brain Agent）通信时遇到了两个关键坑，均已解决，特此记录以防后患：

1. **LiveKit Token 校验失败 (401 Unauthorized) 与 Key 不一致问题**
   - **症状**：客户端拿本地 Token 连云端报错 401，且引发云端 Agent 多次重连崩溃。
   - **原因**：部署脚本采用了 `infra/livekit/livekit.yaml` 里的开发默认密钥 `secret`，而本地工作区 `.env` 里存储了长密钥 `parrot_carriers_local_dev_...`。两者不对齐。
   - **解决方案**：**强烈要求双端对齐**。以后大部分时间以 ECS 作为后端测试，必须保证云端 LiveKit 配置密码与本地 `.env` 的 `LIVEKIT_API_SECRET` 绝对一致。本轮已通过直接修改云端 yaml 强行对齐。未来如涉及重新部署，应确保模板配置文件与实际环境对应。

2. **语音响应与 RPC 延迟极高 (UDP 丢包与代理干扰)**
   - **症状**：能连通，但发语音后 3~5 秒才有回应。
   - **原因**：本地开启了全局科学上网 VPN（如 Mihomo/Clash），接管了发往阿里云东京（8.216.45.45）的流量。由于 UDP 媒体包在代理下极易被丢弃或转 TCP 降级，导致剧烈延迟。
   - **解决方案**：测试时**关闭全局 VPN**，或者在代理软件里将 ECS IP 添加至**直连白名单**（`DIRECT`）。直连后延迟可降至 30~50 毫秒，体验极为丝滑。

### 4.2 已知遗留问题（Castle 部署后处理）

| # | 问题 | 处理方式 |
|:--|:-----|:---------|
| 🔶 | `Scheduler._connect_livekit` 仍是空壳 | Castle 部署调试时补充 |
| 🔶 | `reflex_direct` / `brain_direct` BT 分支无下游执行器 | P2 接入 DataChannel/XR Hands 时实现 |
| 🔶 | GOSLO Chat 模式感知 hook 的 Redis URL 在 Castle 上需确认为 `redis://localhost:6379/0` | start_goslo_chat.py 读 REDIS_URL 环境变量，已处理 |
| 🔶 | 微信 Bot 在 Castle 上需要重新扫码登录 | `nanobot channels login weixin -c <config>` |
| 🔶 | GitHub MCP 需要 Node.js（npx），deploy 脚本已自动安装 | 若安装失败手动 `apt install nodejs npm` |
| 🔶 | `start_goslo_chat.py` 中 `AgentLoop` constructor 参数可能随 nanobot 版本略有不同 | 首次启动如报错，按错误提示调整参数 |
| 🔶 | **双工作区代码推送与同步策略尚未清晰** | 当前直接使用了简单的 ssh 命令，未来多机（本地 IDE 工作区 vs ECS nanobot 生产工作区）同步策略有待讨论。 |

---

## 5. 下一个 chat（ECS + Remote SSH）的上下文

### 给新 chat 的背景说明

```
项目: GOSLOParrot/ParrotCarriers — 云原生 AR 鹦鹉伴侣 Bus 基建子项目
当前阶段: V1 代码完成，准备首次 Castle (ECS) 部署

两个 GitHub 仓库:
- https://github.com/GOSLOParrot/ParrotCarriers  (主)
- https://github.com/GOSLOParrot/nanobot          (fork, P2 已改造)

部署脚本: infra/deploy-castle.sh <castle-ip> [ssh-key]
环境变量模板: infra/env-castle.template

Castle 上需要运行的 3 个进程 (tmux):
1. brain      — .venv/bin/python -m parrot.brain.agent dev
2. maid       — .venv/bin/python src/scripts/start_nanobot_worker.py
3. goslo-chat — .venv/bin/python src/scripts/start_goslo_chat.py

所有 secrets 在笔记本 D:\GOSLOParrot\ParrotCarriers\.env 中:
- GOOGLE_API_KEY / GEMINI_API_KEY
- TELEGRAM_BOT_TOKEN = <TELEGRAM_BOT_TOKEN_REDACTED>
- GITHUB_TOKEN = <GITHUB_TOKEN_REDACTED>
- LIVEKIT_API_KEY=devkey / LIVEKIT_API_SECRET=parrot_carriers_local_dev_...

关键内存文件:
- .cursor/memory/active_context.md        — 进度 + 命令速查
- .cursor/memory/architecture/protocol_snapshot_p1.md  — V1 协议全量快照
- .cursor/memory/deploy_snapshot_p2_20260412.md        — 本文（本轮决策快照）
```

### 新 chat 需要你提供的信息

- [x] Castle ECS 当前 IP 地址 (8.216.45.45)
- [x] SSH 连接方式（已通过本地 ssh-copy-id/追加公钥配置免密）
- [x] ECS 上当前已安装的软件（Ubuntu 22.04, Docker 29.3, Compose v5, Python 3.10.12, tmux 3.2a均就绪）
- [x] ECS 防火墙/安全组规则（需在阿里云控制台确保入方向放行 TCP 7880/7881, UDP 50000-50200）
- [x] 是否有其他进程在跑（端口 7880/7881/6379 皆处于空闲状态）

---

## 6. 文件路径速查

```
D:\GOSLOParrot\
├── ParrotCarriers\                    # 主仓库
│   ├── src\parrot\
│   │   ├── shared\constants.py        # HASH_GOSLO_MODE 等 Redis key 定义
│   │   ├── brain\agent.py             # Brain Agent + 模式信号写入
│   │   └── brain\soul.py              # ParrotSoul 人格（Live 身体用）
│   ├── src\scripts\
│   │   ├── start_nanobot_worker.py    # 猫娘启动（parrot_bus + weixin）
│   │   └── start_goslo_chat.py        # GOSLO Chat 启动（Telegram + mode hook）
│   └── infra\
│       ├── deploy-castle.sh           # 一键部署脚本
│       ├── docker-compose.yml         # Castle 生产栈
│       └── env-castle.template        # Castle .env 模板
└── nanobot\                           # Fork 仓库
    ├── nanobot\channels\
    │   ├── parrot_bus.py              # Redis Stream 消费 adapter (已验证)
    │   └── goslo_mode.py              # GOSLO 模式感知中间件 (新增)
    └── config\
        ├── parrot_config.json          # 猫娘配置（exec+MCP 已加）
        └── goslo_config.json           # GOSLO Chat 配置（新建）

C:\Users\Bin\.nanobot\
├── workspace\                         # 猫娘 workspace
│   ├── SOUL.md                        # 猫娘人格
│   ├── USER.md                        # 用户画像
│   └── TOOLS.md                       # 工具说明（新增）
└── goslo-workspace\                   # GOSLO Chat workspace
    ├── SOUL.md                        # ParrotSoul 人格（新增）
    ├── AGENTS.md                      # GOSLO 行为指南（新增）
    ├── USER.md                        # 共享用户画像（复制）
    └── TOOLS.md                       # 工具说明（新增）
```
