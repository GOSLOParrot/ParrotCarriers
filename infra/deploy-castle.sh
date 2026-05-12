#!/usr/bin/env bash
# Castle ECS 部署脚本
#
# 用法:
#   bash infra/deploy-castle.sh <castle-ip> [ssh-key]
#       常规部署：rsync 代码 + 装依赖 + 启 docker 容器 (LiveKit/Redis/FalkorDB/token-mint)
#       Python 进程仍由 tmux 手工拉起（参见末尾说明）。
#
#   bash infra/deploy-castle.sh <castle-ip> [ssh-key] --systemd
#       Phase 3.5 入口：在常规部署之后**安装 systemd unit** 并启 orchestrator。
#       一旦切到 systemd，未来的 set_active_line / restart_component / 滚动重启
#       都通过 orchestrator (:7890) 完成；不再需要 SSH + tmux。
#
# 部署内容:
#   1. LiveKit Server + Redis + FalkorDB + token-mint (docker-compose.yml)
#   2. rsync 仓库到 ECS（含 `.cursor/` 除 plans / skill references / 嵌套 node_modules）
#   3. （可选 --systemd）Phase 3.1 systemd unit + orchestrator
#   4. （默认）Brain / Scheduler / Maid / GOSLO-chat 由 tmux 手工拉起
#
# 前提:
#   - Castle 上已安装 Docker + Docker Compose
#   - SSH 可达 (root)
#   - Castle 上 .env 已按 infra/env-castle.template 填好

set -euo pipefail

CASTLE_IP="${1:?Usage: deploy-castle.sh <castle-ip> [ssh-key-path] [--systemd]}"
shift || true

SSH_KEY=""
INSTALL_SYSTEMD=0
for arg in "$@"; do
    case "$arg" in
        --systemd) INSTALL_SYSTEMD=1 ;;
        *)
            if [ -z "$SSH_KEY" ]; then
                SSH_KEY="$arg"
            fi
            ;;
    esac
done

SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"
if [ -n "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

REMOTE_DIR="/opt/parrotcarriers"
REMOTE_NANOBOT="/opt/nanobot"
SSH_CMD="ssh $SSH_OPTS root@$CASTLE_IP"

echo "=== ParrotCarriers Castle Deploy ==="
echo "Target: $CASTLE_IP → $REMOTE_DIR + $REMOTE_NANOBOT"

# 1. 同步 ParrotCarriers 代码
#
# .cursor/ 策略（2026-05-12）：
#   - 以前整棵 `.cursor/` 被排除，ECS 上看不到 memory / config，agent 对照困难。
#   - 现在默认 **同步** `.cursor/` 下除「大且无关」外的内容。
#   - 仍排除：`.cursor/plans/`（Cursor 生成）、`.cursor/skills/*/references/`（体积大、可再生成）、
#     以及各层 `node_modules`。
#   - 根目录 `.env` 仍不同步（Castle 用远端自有 .env）；本机真值对照请放在
#     `.cursor/config/*.deploymirror`（见 `.cursor/config/README.md`），会随 rsync 上机。
#   - 切勿把运行时密钥只放在本机 `.env` 却指望 ECS 自动一致 — 上机后仍需人工对齐
#     `/opt/parrotcarriers/.env` 与 deploymirror 的差异。
echo ""
echo "[1/5] Syncing ParrotCarriers code..."
rsync -avz --delete \
    --exclude '.venv' \
    --exclude '.env' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '.ruff_cache' \
    --exclude 'unity/' \
    --exclude '.cursor/plans/' \
    --exclude '.cursor/skills/*/references/' \
    --exclude '.cursor/**/node_modules/' \
    --exclude 'docs/' \
    --exclude 'agent-transcripts/' \
    --exclude 'terminals/' \
    --exclude 'node_modules' \
    -e "ssh $SSH_OPTS" \
    . "root@$CASTLE_IP:$REMOTE_DIR/"

# 1b. 同步 nanobot fork 代码
echo ""
echo "[1b/5] Syncing nanobot fork..."
NANOBOT_LOCAL="$(dirname "$(pwd)")/nanobot"
if [ -d "$NANOBOT_LOCAL" ]; then
    rsync -avz --delete \
        --exclude '.venv' \
        --exclude '__pycache__' \
        --exclude '.pytest_cache' \
        --exclude '.ruff_cache' \
        --exclude '.cursor/' \
        --exclude 'node_modules' \
        -e "ssh $SSH_OPTS" \
        "$NANOBOT_LOCAL/" "root@$CASTLE_IP:$REMOTE_NANOBOT/"
else
    echo "  WARNING: nanobot not found at $NANOBOT_LOCAL, skipping"
fi

# 2. 安装 Python 依赖 + 系统工具
echo ""
echo "[2/5] Installing dependencies..."
$SSH_CMD "cd $REMOTE_DIR && python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -e '.[dev,memory]'"
$SSH_CMD "cd $REMOTE_DIR && .venv/bin/pip install 'redis>=7.1,<9.0' --index-url https://pypi.org/simple/"
$SSH_CMD "cd $REMOTE_DIR && .venv/bin/pip install -e '$REMOTE_NANOBOT[parrot]' 2>/dev/null || echo '  nanobot install skipped (sync first)'"
# Node.js for GitHub MCP (npx)
$SSH_CMD "which node > /dev/null 2>&1 || (apt-get update -qq && apt-get install -y nodejs npm > /dev/null 2>&1 && echo 'Node.js installed') || echo '  NOTE: install Node.js manually for GitHub MCP'"
# exiftool for photo metadata (optional but useful for file sorting)
$SSH_CMD "which exiftool > /dev/null 2>&1 || (apt-get install -y libimage-exiftool-perl > /dev/null 2>&1 && echo 'exiftool installed') || echo '  NOTE: exiftool not installed (optional)'"

# 3. Setup workspaces and data directories on Castle
echo ""
echo "[3/5] Setting up workspaces and data directories..."
$SSH_CMD "mkdir -p ~/.nanobot/goslo-workspace ~/.nanobot/workspace"
$SSH_CMD "mkdir -p /data/workshop/photos /data/workshop/documents /data/workshop/sorted"
$SSH_CMD "chmod 755 /data/workshop"
# Copy persona files via rsync if they exist locally
GOSLO_WS="$HOME/.nanobot/goslo-workspace"
MAID_WS="$HOME/.nanobot/workspace"
if [ -d "$GOSLO_WS" ]; then
    rsync -avz -e "ssh $SSH_OPTS" "$GOSLO_WS/" "root@$CASTLE_IP:~/.nanobot/goslo-workspace/"
    echo "  GOSLO workspace synced"
fi
if [ -d "$MAID_WS" ]; then
    rsync -avz -e "ssh $SSH_OPTS" "$MAID_WS/" "root@$CASTLE_IP:~/.nanobot/workspace/"
    echo "  Maid workspace synced"
fi

# 4. 启动 Docker 服务 (LiveKit + Redis)
echo ""
echo "[4/5] Starting Docker services..."
$SSH_CMD "cd $REMOTE_DIR && docker compose -f infra/docker-compose.yml up -d"

# 4b. （可选）Phase 3.5 — 安装 systemd unit
if [ "$INSTALL_SYSTEMD" -eq 1 ]; then
    echo ""
    echo "[4b/5] Installing systemd units (Phase 3.1)..."
    # 假设 Castle 上 ParrotCarriers 部署在 $REMOTE_DIR；systemd unit 默认期望
    # /opt/parrot/ParrotCarriers，所以这里做一个 symlink 让 unit 找得到。
    $SSH_CMD "mkdir -p /opt/parrot && [ -L /opt/parrot/ParrotCarriers ] || ln -sfn $REMOTE_DIR /opt/parrot/ParrotCarriers"
    # systemd 的 EnvironmentFile 同样指向 /opt/parrot/...，所以 .env 也要 symlink。
    $SSH_CMD "[ -f $REMOTE_DIR/.env ] && cp -f $REMOTE_DIR/.env $REMOTE_DIR/.env.castle || true"
    $SSH_CMD "id parrot 2>/dev/null || useradd -m -u 1000 parrot"
    $SSH_CMD "chown -R parrot:parrot $REMOTE_DIR"
    $SSH_CMD "cp -f $REMOTE_DIR/infra/systemd/parrot-*.service /etc/systemd/system/"
    $SSH_CMD "cp -f $REMOTE_DIR/infra/systemd/parrot-brain@.service /etc/systemd/system/ 2>/dev/null || true"
    $SSH_CMD "systemctl daemon-reload"
    $SSH_CMD "systemctl enable parrot-orchestrator parrot-brain parrot-scheduler parrot-maid parrot-goslo-chat"
    $SSH_CMD "systemctl restart parrot-orchestrator"
    $SSH_CMD "sleep 2 && systemctl status parrot-orchestrator --no-pager -n 15 || true"
    echo "  → orchestrator running on :7890. Manage other components via:"
    echo "    curl -X POST -H 'Authorization: Bearer \$PARROT_ORCH_SECRET' \\"
    echo "         http://$CASTLE_IP:7890/restart_component -d '{\"component\":\"brain\"}'"
fi

# 5. 验证
echo ""
echo "[5/5] Health check..."
$SSH_CMD "cd $REMOTE_DIR && docker compose -f infra/docker-compose.yml ps"
$SSH_CMD "curl -sf http://localhost:7880 > /dev/null && echo 'LiveKit: OK' || echo 'LiveKit: FAIL'"
$SSH_CMD "redis-cli -h localhost ping 2>/dev/null || $REMOTE_DIR/.venv/bin/python -c \"import redis; r=redis.Redis(); print('Redis:', r.ping())\" 2>/dev/null || echo 'Redis: check manually'"
$SSH_CMD "redis-cli -h localhost -p 6380 ping 2>/dev/null && echo 'FalkorDB: OK' || echo 'FalkorDB: FAIL (check docker logs falkordb)'"

echo ""
echo "=== Deploy complete ==="
echo ""
echo "Next steps on Castle:"
echo "  ssh root@$CASTLE_IP"
echo "  cd $REMOTE_DIR"
echo ""
echo "  # Copy .env template (first time only):"
echo "  cp infra/env-castle.template .env && vi .env"
echo "  # Required (phone-facing):"
echo "  #   GOOGLE_API_KEY / GEMINI_API_KEY     # Brain agent"
echo "  #   LIVEKIT_URL / LIVEKIT_API_KEY/SECRET # phone + Brain 共用此 URL"
echo "  #   PARROT_MINT_SECRET                   # Unity Resources/parrot_config.json 同值"
echo "  #   PARROT_ORCH_SECRET                   # orchestrator :7890 写操作 Bearer"
echo "  # Required (nanobot-only):"
echo "  #   TELEGRAM_BOT_TOKEN                   # GOSLO Chat bot"
echo "  #   GITHUB_TOKEN                         # nanobot MCP tool"
echo "  # NOTE: 不要再用 .env 切线；切线走 orchestrator /set_active_line 或写 data/runtime_config.json"
echo ""
echo "  # === tmux sessions layout ==="
echo ""
echo "  # 1. Brain Agent (GOSLO Live body):"
echo "  tmux new -s brain"
echo "  .venv/bin/python -m parrot.brain.agent dev"
echo ""
echo "  # 2. Scheduler service (BT routing for dispatch_task / nanobot reply fan-in):"
echo "  #    NOTE: this was a known deploy gap (deploy_snapshot_p2_20260412.md §4.2);"
echo "  #    the Phase 1 ECS Orchestrator audit decided to keep Scheduler as an"
echo "  #    independent process (\"file > BB > env > default\" config layering"
echo "  #    means Brain restart and Scheduler restart can be decoupled)."
echo "  tmux new -s scheduler"
echo "  .venv/bin/python src/scripts/start_scheduler.py"
echo ""
echo "  # 3. Nanobot Worker (猫娘女仆: parrot_bus + weixin):"
echo "  tmux new -s maid"
echo "  .venv/bin/python src/scripts/start_nanobot_worker.py"
echo ""
echo "  # 4. GOSLO Chat (鹦鹉大小姐 Telegram bot):"
echo "  tmux new -s goslo-chat"
echo "  .venv/bin/python src/scripts/start_goslo_chat.py"
echo ""
echo "  # 5. Castle Orchestrator API on :7890 (Phase 2 已落地，2026-05-12)："
echo "  #    - 走 systemd（推荐）:  bash infra/deploy-castle.sh <ip> [key] --systemd"
echo "  #    - 临时走 tmux:  tmux new -s orchestrator"
echo "  #                    .venv/bin/python -m parrot.castle.orchestrator"
echo "  #    切线 / 重启：curl -H 'Authorization: Bearer \$PARROT_ORCH_SECRET' \\"
echo "  #                       http://$CASTLE_IP:7890/set_active_line -d '{\"line_id\":\"line_a\"}'"
echo ""
echo "  # Dispatch agent to room (from another shell or sim client):"
echo "  # The sim_unity_client.py auto-dispatches when agent_name='parrot-brain'"
echo ""
echo "  # === 测试文件整理功能 (微信/Telegram 发给猫娘) ==="
echo "  # '帮我列一下 /data/workshop/photos 里有什么文件'"
echo "  # '帮我搜索 exiftool 按日期整理照片的命令'"
echo "  # '在 GitHub 上看看 GOSLOParrot/ParrotCarriers 的 README'"
echo ""
echo "  Firewall ports needed (TCP): 7880, 7881"
echo "  Firewall ports needed (UDP): 50000-50200"
