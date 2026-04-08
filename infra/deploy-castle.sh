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

CASTLE_IP="${1:?Usage: deploy-castle.sh <castle-ip> [ssh-key-path]}"
SSH_KEY="${2:-}"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"
if [ -n "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

REMOTE_DIR="/opt/parrotcarriers"
SSH_CMD="ssh $SSH_OPTS root@$CASTLE_IP"

echo "=== ParrotCarriers Castle Deploy ==="
echo "Target: $CASTLE_IP → $REMOTE_DIR"

# 1. 同步代码
echo ""
echo "[1/4] Syncing code..."
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

# 2. 安装 Python 依赖
echo ""
echo "[2/4] Installing Python dependencies..."
$SSH_CMD "cd $REMOTE_DIR && python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'"

# 3. 启动 Docker 服务 (LiveKit + Redis)
echo ""
echo "[3/4] Starting Docker services..."
$SSH_CMD "cd $REMOTE_DIR && docker compose -f infra/docker-compose.yml up -d"

# 4. 验证
echo ""
echo "[4/4] Health check..."
$SSH_CMD "cd $REMOTE_DIR && docker compose -f infra/docker-compose.yml ps"
$SSH_CMD "curl -sf http://localhost:7880 > /dev/null && echo 'LiveKit: OK' || echo 'LiveKit: FAIL'"
$SSH_CMD "redis-cli -h localhost ping 2>/dev/null || $REMOTE_DIR/.venv/bin/python -c \"import redis; r=redis.Redis(); print('Redis:', r.ping())\" 2>/dev/null || echo 'Redis: check manually'"

echo ""
echo "=== Deploy complete ==="
echo ""
echo "Next steps:"
echo "  1. SSH to Castle: ssh root@$CASTLE_IP"
echo "  2. Start Brain Agent:"
echo "     cd $REMOTE_DIR && .venv/bin/python -m parrot.brain.agent dev"
echo "  3. Start Scheduler (new terminal):"
echo "     cd $REMOTE_DIR && .venv/bin/python src/scripts/start_scheduler.py"
echo "  4. Start Nanobot Worker (new terminal):"
echo "     pip install -e /opt/nanobot[parrot]"
echo "     cd $REMOTE_DIR && .venv/bin/python src/scripts/start_nanobot_worker.py"
echo ""
echo "  Firewall ports needed (TCP): 7880, 7881"
echo "  Firewall ports needed (UDP): 50000-50200"
