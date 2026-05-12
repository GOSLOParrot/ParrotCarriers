---
status: ratified
category: prompt-asset
last_reviewed: 2026-05-12
ai_priority: high
ai_audience: "ECS Castle operator agent (复制粘贴用，不需要 Cursor 端读)"
parent_doc: "ecs_orchestrator_lifecycle_completion_20260512.md"
related:
  - "ecs_orchestrator_lifecycle_completion_20260512.md (完成报告本体，与本 prompt 配对发给 ECS)"
  - "../../infra/env-castle.template (审计依据 — phone-facing vs nanobot-only 分段)"
  - "../../infra/deploy-castle.sh (--systemd 开关说明)"
---

# ECS Castle 升级后审计 Prompt（2026-05-12）

> 把下面"### 复制起点"以下的内容**整段复制**给 ECS 上的运维 agent（或 ssh 进去自己跑也可以）。配套发 `ecs_orchestrator_lifecycle_completion_20260512.md` 作为升级背景。

---

### 复制起点

你是 ParrotCarriers 在 Castle ECS 上的运维 agent。今天（2026-05-12）后端把 ECS Orchestrator + Tier 化设置 + systemd 全套升级落地了。任务：**对照升级，把现网状态审计一遍，确认没有 phone-facing 与 nanobot-only 配置混淆，并把控制面跑起来。**

#### 1. 同步代码 + .env

宿主机上：

```bash
cd /opt/parrotcarriers
git pull            # 或者由开发端 deploy-castle.sh rsync 下发
diff -u .env infra/env-castle.template | less   # 看新模板新增了哪些字段（PARROT_MINT_SECRET / PARROT_ORCH_SECRET / 分段注释）
```

**必须填的新字段**：

- `PARROT_MINT_SECRET` — Unity Resources/parrot_config.json 必须用同一字符串
- `PARROT_ORCH_SECRET` — orchestrator :7890 写操作 Bearer；建议 32 字节随机串

**老字段语义变更**：

- `PARROT_LLM_PIPELINE` 仅作 boot fallback，**不是切线入口**。切线走 orchestrator `/set_active_line` 或写 `data/runtime_config.json`。

#### 2. 区分 Phone-facing 与 Nanobot-only 设置（关键审计点）

逐项确认 .env：

| 类别 | 字段 | 检查要点 |
|:---|:---|:---|
| Phone-facing | `LIVEKIT_URL` | 必须是 Castle 公网 IP（手机访问入口）；Brain 也用同一 URL，没有内外分流 |
| Phone-facing | `LIVEKIT_API_KEY/SECRET` | 与 token-mint 签发用 |
| Phone-facing | `PARROT_MINT_SECRET` | 与 Unity 客户端 Resources 配置一致 |
| Phone-facing | `PARROT_ORCH_SECRET` | 不要与 mint secret 同值；orchestrator 独立鉴权 |
| Phone-facing | `GOOGLE_API_KEY/GEMINI_API_KEY` | Brain agent 用 |
| Nanobot-only | `TELEGRAM_BOT_TOKEN` | GOSLO Chat bot；与 Phone 通道完全无关 |
| Nanobot-only | `GITHUB_TOKEN` | nanobot MCP tool；与 Phone 通道完全无关 |
| 共享 | `REDIS_*` / `FALKORDB_*` | Phone + Nanobot 都用 |

**易错点**：千万**不要**把 `TELEGRAM_BOT_TOKEN` 或 `GITHUB_TOKEN` 暴露到对手机有效的端点（Brain / token-mint 都不读这两项），也不要把 `PARROT_MINT_SECRET` / `PARROT_ORCH_SECRET` 写进 nanobot fork 的配置里。

#### 3. 装 systemd（推荐路径）

```bash
# 由本地端调（非 ECS 内）：
bash infra/deploy-castle.sh <castle-ip> [ssh-key] --systemd
```

或在 ECS 上手动安装（已有代码同步过来）：

```bash
cd /opt/parrotcarriers
mkdir -p /opt/parrot && ln -sfn /opt/parrotcarriers /opt/parrot/ParrotCarriers
cp -f .env .env.castle
id parrot 2>/dev/null || useradd -m -u 1000 parrot
chown -R parrot:parrot /opt/parrotcarriers

cp -f infra/systemd/parrot-*.service /etc/systemd/system/
cp -f infra/systemd/parrot-brain@.service /etc/systemd/system/  # 滚动重启用
systemctl daemon-reload
systemctl enable parrot-orchestrator parrot-brain parrot-scheduler parrot-maid parrot-goslo-chat
systemctl restart parrot-orchestrator
```

#### 4. 验证控制面

```bash
# 4.1 orchestrator 健康
curl -sf http://localhost:7890/health
# 预期：{"status":"ok"}

# 4.2 全景 status（不需要 Bearer）
curl -s http://localhost:7890/status | jq

# 重点字段：
#   .runtime_config       ← file 层（data/runtime_config.json）
#   .brain_runtime_snapshot  ← BB 层（global/brain_runtime_snapshot）
#   .selection_drift      ← active vs running 不一致时不为空，正常应为 null/空
#   .processes.brain.alive ← 由 Redis 心跳计算
#   .containers           ← docker compose ps 解析
#   .brain_boot_preflight ← Redis / port 7889 / runtime_config 三项检查
#   .brain_last_crash     ← 最近一次 unhandled exception（正常应为 null）
#   .restart_stats        ← 每个 component 的 5/300s 滑窗剩余配额

# 4.3 切线（Tier 1，Unity 自动重连）
export PARROT_ORCH_SECRET=$(grep -E '^PARROT_ORCH_SECRET=' /opt/parrotcarriers/.env | cut -d= -f2)
curl -X POST -H "Authorization: Bearer $PARROT_ORCH_SECRET" \
     -H 'Content-Type: application/json' \
     -d '{"line_id":"line_b"}' \
     http://localhost:7890/set_active_line | jq
# 之后再 GET /status，看 .runtime_config.line_id 是否已变 + Unity 是否重连
```

#### 5. 启 Brain 等服务

```bash
systemctl start parrot-brain          # 主 Brain
systemctl start parrot-scheduler      # py-trees BT 路由
systemctl start parrot-maid           # 猫娘 nanobot worker（微信 + parrot_bus）
systemctl start parrot-goslo-chat     # 鹦鹉大小姐 Telegram bot

# 验证心跳
sleep 10 && curl -s http://localhost:7890/status | jq '.processes'
# 预期 brain / scheduler / maid / goslo_chat 各自 .alive == true
```

#### 6. 审计 phone connection 是否真的能通

不要假定 LiveKit 通了就完了。**手机端开 Unity App 真连一次**：

- 启动 → 看 token-mint 日志（`journalctl -u parrot-orchestrator -f` 或 `journalctl -u parrot-brain -f`）有没有 `mint_token` request
- 进 Room 后看 `/status` 的 `.brain_runtime_snapshot.room_name` 是不是手机所连 Room
- 切线：在手机端启动页选 Line B → orchestrator 必须在 5s 内看到 `runtime_config.line_id == "line_b"` + Brain 在下一 entrypoint 用 line_b
- 拍照：手机上传 photo → orchestrator `/status.brain_boot_preflight.photo_upload_port_in_use == true`

如果哪一步没通，看 `.brain_last_crash` + `journalctl -u parrot-brain` —— 不要去翻 tmux scrollback（已经废弃 tmux 路径）。

#### 7. Nanobot 区分检查（避免误报）

如果 Maid / GOSLO Chat 启动失败，**先确认是不是配置混淆**：

```bash
journalctl -u parrot-maid -n 50
# 常见错：缺 GITHUB_TOKEN / nanobot fork 没装 / 微信端配置缺失
# Maid 不应抱怨 LIVEKIT_* — 它不连 LiveKit

journalctl -u parrot-goslo-chat -n 50
# 常见错：缺 TELEGRAM_BOT_TOKEN / Telegram API 网络问题
# GOSLO Chat 不应抱怨 LIVEKIT_* / PARROT_MINT_SECRET
```

#### 8. 限频 / 雪崩防御

orchestrator 每个 component 限制 5 次重启 / 300s。如果某个服务真崩到第 6 次：

```bash
curl -s http://localhost:7890/status | jq '.restart_stats'
# 看 .blocked_until_ts 与 .recent_crashes 数量
```

不要硬反复 restart，先看 `.brain_last_crash.traceback` 找根因。

#### 9. 审计输出（请回报这几项给我）

1. `.env` 里 `PARROT_MINT_SECRET` / `PARROT_ORCH_SECRET` 是否都填了（不要贴值，只回 yes/no）
2. `curl localhost:7890/status` 返回的 JSON（**先 redact `.brain_runtime_snapshot.room_name` 之外的敏感字段**）
3. 4 个 systemd unit 的 `is-active` 状态
4. 第 6 步真机连接是否成功；如失败，附 `journalctl -u parrot-brain -n 100`
5. 第 7 步 nanobot 区分检查是否有混淆痕迹

完成后告诉我"ECS 升级审计 OK"或"ECS 升级审计 FAIL: <原因>"。

### 复制终点

---

> **本地端注意**：把上面"复制起点"到"复制终点"之间内容拷给 ECS agent，**配套发** `ecs_orchestrator_lifecycle_completion_20260512.md`（升级报告作为背景）。
