#!/usr/bin/env bash
# Castle ECS 部署脚本 — Phase 1 最小部署
# 用法: bash infra/deploy-castle.sh <castle-ip> [ssh-key]
#
# 部署内容:
#   1. LiveKit Server + Redis (docker-compose.yml)
#   2. Brain Agent + Scheduler + Nanobot Worker (systemd 或 tmux)
#
# 前提:
#   - Castle 上已安装 Docker + Docker Compose
#   - SSH 可达
#   - Castle 上 .env 已按 .env.castle 模板填好

set -euo pipefail

# Windows (Git Bash): install rsync first, e.g.  scoop install rsync  OR  choco install rsync
# WSL: sudo apt install -y rsync openssh-client
command -v rsync >/dev/null 2>&1 || {
    echo "ERROR: rsync not found."
    echo "  Git Bash: install rsync (scoop install rsync / Chocolatey rsync / MSYS2 pacman -S rsync) and ensure it is on PATH."
    echo "  WSL: sudo apt update && sudo apt install -y rsync"
    exit 1
}

CASTLE_IP="${1:?Usage: deploy-castle.sh <castle-ip> [ssh-key-path]}"
SSH_KEY="${2:-}"
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
echo ""
echo "[1/5] Syncing ParrotCarriers code..."
rsync -avz --delete \
    --exclude '.venv' \
    --exclude '.env' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '.ruff_cache' \
    --exclude 'unity/' \
    --exclude '.cursor/' \
    --exclude 'docs/' \
    --exclude 'agent-transcripts/' \
    --exclude 'terminals/' \
    --exclude 'node_modules' \
    -e "ssh $SSH_OPTS" \
    . "root@$CASTLE_IP:$REMOTE_DIR/"

# 1a. 单独同步 .cursor/memory（主同步排除了整个 .cursor/，但 Castle 上需要架构/验证文档）
if [ -d ".cursor/memory" ]; then
    echo ""
    echo "[1a/5] Syncing .cursor/memory..."
    rsync -avz \
        -e "ssh $SSH_OPTS" \
        .cursor/memory/ "root@$CASTLE_IP:$REMOTE_DIR/.cursor/memory/"
fi

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
echo "  # Fill: GOOGLE_API_KEY, GEMINI_API_KEY, TELEGRAM_BOT_TOKEN"
echo ""
echo "  # === tmux sessions layout ==="
echo ""
echo "  # 1. Brain Agent (GOSLO Live body):"
echo "  tmux new -s brain"
echo "  .venv/bin/python -m parrot.brain.agent dev"
echo ""
echo "  # 2. Nanobot Worker (猫娘女仆: parrot_bus + weixin):"
echo "  tmux new -s maid"
echo "  .venv/bin/python src/scripts/start_nanobot_worker.py"
echo ""
echo "  # 3. GOSLO Chat (鹦鹉大小姐 Telegram bot):"
echo "  tmux new -s goslo-chat"
echo "  .venv/bin/python src/scripts/start_goslo_chat.py"
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
