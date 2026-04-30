# ECS nanobot Google OAuth 接入 — 跟踪报告

> 创建时间：2026-04-30  
> 状态：**部分完成 — 等待本机 OAuth token 生成 + 上传**

---

## 一、目标

在 ECS Castle 节点上让 `nanobot` 能够通过 `google-workspace` MCP server 访问 Google Workspace API（Gmail、Calendar、Drive），需要完成一次 OAuth 2.0 认证并持久化 token。

---

## 二、已完成的工作

### 2.1 nanobot 配置修复（`GOSLOParrot/nanobot`，commit `29a0f88`）

**已在 ECS 上 commit，等待 push 到 GitHub：**

#### `config/parrot_config.json`

| 项目 | 旧值 | 新值 | 原因 |
|---|---|---|---|
| `channels.parrot_bus.redisUrl` | `redis://localhost:6379/0` | `redis://infra-redis-1:6379/0` | Docker 容器内 localhost ≠ 宿主机，复用 infra 网络已有 Redis |
| `tools.mcpServers` 中 `google-workspace` key | `google-workspace` | `google_workspace` | Gemini API 不接受 function name 含连字符 |
| `tools.mcpServers.google_workspace.env` | `{}` | `{ GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET }` | 需要注入 OAuth 凭证 |
| `tools.mcpServers.github.enabledTools` | 无限制 | `["get_file_contents","search_repositories","list_issues","get_issue"]` | GitHub MCP 有 40+ 工具，全部注册会超过 Gemini function_declarations 限制触发 400 |
| `tools.mcpServers.redis.args` | `"${REDIS_URL}"` | `"redis://infra-redis-1:6379/0"` | REDIS_URL 环境变量在容器内解析为 localhost，硬编码避免歧义 |

#### `config/goslo_config.json`

| 项目 | 改动 |
|---|---|
| `tools.mcpServers.google_workspace.env` | 同上，注入 OAuth 凭证 |

#### `docker-compose.yml`

| 项目 | 改动 |
|---|---|
| `x-common-config.env_file` | 新增 `- .env`，从 `/opt/nanobot/.env`（symlink → `/opt/parrotcarriers/.env`）注入所有环境变量 |
| `x-common-config.volumes` | 新增 `~/.nanobot/google-workspace-credentials:/home/nanobot/.local/share/google-workspace-mcp/credentials` 持久化 OAuth token |
| `x-common-config.networks` | 新增 `nanobot_internal`（容器内通信）+ `infra_default: external: true`（复用 infra Redis） |

### 2.2 ECS 宿主机配置

```bash
# OAuth token 持久化目录（已创建）
~/.nanobot/google-workspace-credentials/

# nanobot 配置文件（已同步）
~/.nanobot/config.json  → 与 parrot_config.json 内容一致

# env symlink（已创建）
/opt/nanobot/.env  →  /opt/parrotcarriers/.env
```

### 2.3 发现并临时修复的 nanobot Bug

**Bug 位置**：`nanobot/agent/tools/mcp.py`，`MCPResourceWrapper.__init__`

**问题**：`@aaronsb/google-workspace-mcp` MCP server 暴露了 4 个 Resource，名称含空格：
- `Active Safety Policies`
- `Available Services`
- `Workspace Directory`
- `Server Version`

nanobot 把这些 Resource 注册为 function tool，名称变成 `mcp_google_workspace_resource_Active Safety Policies`，含空格，Gemini API 拒绝（400: Invalid function name）。

**临时修复**（ECS 容器内 monkey-patch，容器重建后失效）：
```python
# 在 docker exec 时通过 PYTHONPATH=/tmp 加载 /tmp/sitecustomize.py 注入
def _patched_init(self, session, server_name, resource_def, resource_timeout=30):
    import re
    self._name = "mcp_" + server_name + "_resource_" + re.sub(r"[^a-zA-Z0-9_]", "_", resource_def.name)
    ...
```

**正式修复（需要在本机 nanobot fork 提交）**：

```python
# 文件：nanobot/agent/tools/mcp.py
# 类：MCPResourceWrapper.__init__
# 约第 146 行

# 旧代码：
self._name = f"mcp_{server_name}_resource_{resource_def.name}"

# 新代码：
import re
self._name = "mcp_" + server_name + "_resource_" + re.sub(r"[^a-zA-Z0-9_]", "_", resource_def.name)
```

---

## 三、待完成任务（本机操作）

### 任务 A：推送 nanobot commit（优先）

```bash
# 在本机 nanobot 仓库
cd ~/path/to/nanobot  # 你的本机 nanobot 路径
git pull origin main  # 拉取 ECS 上的 commit 29a0f88
git push origin main  # 推到 GitHub（ECS 没有 GitHub 凭据，无法推）
```

### 任务 B：正式修复 mcp.py bug 并提交

在本机 nanobot 仓库修改 `nanobot/agent/tools/mcp.py`：

```python
# 找到 MCPResourceWrapper.__init__ 方法
# 将第 146 行替换：
self._name = f"mcp_{server_name}_resource_{resource_def.name}"
# 改为：
self._name = "mcp_" + server_name + "_resource_" + __import__("re").sub(r"[^a-zA-Z0-9_]", "_", resource_def.name)
```

然后：
```bash
git add nanobot/agent/tools/mcp.py
git commit -m "fix(mcp): sanitize MCP resource names for Gemini API compatibility

Resource names from MCP servers (e.g. google-workspace) can contain spaces
and other characters invalid for Gemini function_declarations names.
Replace non-alphanumeric/underscore chars with underscores."
git push origin main
```

### 任务 C：完成 Google OAuth（关键）

在**本机**（有浏览器的环境）执行：

```bash
# 设置 OAuth 凭证（与 .env 一致）
export GOOGLE_CLIENT_ID="<见 ECS .env GOOGLE_CLIENT_ID>"
export GOOGLE_CLIENT_SECRET="<见 ECS .env GOOGLE_CLIENT_SECRET>"

# 方式一：如果本机装了 nanobot CLI
nanobot agent -m 'Use the google_workspace manage_accounts tool with {"operation": "authenticate"}'
# 浏览器会自动打开，授权完成后 token 保存在：
# ~/.local/share/google-workspace-mcp/credentials/

# 方式二：直接用 npx（推荐，不需要安装 nanobot）
# 需要一个 MCP 客户端工具，例如 mcp-cli 或类似工具
# 或者用 Python 脚本直接调用 gws-mcp
```

**最简单的方式（推荐）**：

```bash
# 本机安装 nanobot
pip install nanobot  # 或按官方文档安装

# 配置最小 config（只需 google_workspace MCP）
mkdir -p ~/.nanobot
cat > /tmp/oauth_config.json << 'EOF'
{
  "providers": { "gemini": { "apiKey": "YOUR_GEMINI_KEY" } },
  "agents": { "defaults": { "model": "gemini-2.5-flash", "provider": "gemini" } },
  "tools": {
    "mcpServers": {
      "google_workspace": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@aaronsb/google-workspace-mcp"],
        "env": {
          "GOOGLE_CLIENT_ID": "<见 ECS .env GOOGLE_CLIENT_ID>",
          "GOOGLE_CLIENT_SECRET": "<见 ECS .env GOOGLE_CLIENT_SECRET>"
        },
        "enabledTools": ["manage_accounts"]
      }
    }
  }
}
EOF

PYTHONPATH=/tmp nanobot agent \
  -m 'Use the google_workspace manage_accounts tool with {"operation": "authenticate"}' \
  --config /tmp/oauth_config.json --no-markdown
```

授权完成后 token 文件在（取决于操作系统）：
- **macOS/Linux**：`~/.local/share/google-workspace-mcp/credentials/`
- **Windows**：`%APPDATA%\google-workspace-mcp\credentials\`

### 任务 D：把 token 上传 ECS

```bash
# 把本机生成的 token 文件上传到 ECS
scp -r ~/.local/share/google-workspace-mcp/credentials/ root@ECS_IP:~/.nanobot/google-workspace-credentials/

# 设置权限（容器内是 UID 1000）
ssh root@ECS_IP "chown -R 1000:1000 ~/.nanobot/google-workspace-credentials/"
```

### 任务 E：重新构建容器（拿到正式 mcp.py 修复）

```bash
# 在 ECS 上，拉取新代码后重建
cd /opt/nanobot
git pull origin main
docker compose build
docker compose up -d
```

### 任务 F：验证

```bash
# 在 ECS 上验证 OAuth token 生效
docker exec -e PYTHONPATH=/tmp nanobot-api nanobot agent \
  -m 'list my Google Calendar events for today' \
  --config /home/nanobot/.nanobot/config.json --no-markdown
```

---

## 四、问题追踪

| # | 问题 | 状态 | 解法 |
|---|---|---|---|
| P1 | Redis `localhost:6379` 在容器内不通 | ✅ 已修复 | redisUrl 改为 `infra-redis-1:6379` |
| P2 | Gemini 400: github MCP 工具过多 | ✅ 已修复 | 加 `enabledTools` 限制为 4 个 |
| P3 | Gemini 400: `google-workspace` key 含连字符 | ✅ 已修复 | 改为 `google_workspace` |
| P4 | Gemini 400: GWS Resource 名称含空格 | ⚠️ 临时修复 | 需要在 mcp.py 正式修复（任务 B） |
| P5 | OAuth 回调 `127.0.0.1:46037` ECS 无法访问 | ⏳ 待完成 | 在本机完成 OAuth 后 scp token（任务 C+D） |
| P6 | ECS 无法 git push（无 GitHub 凭据） | ⏳ 待完成 | 本机 `git pull` 拉取 commit `29a0f88` 后推送（任务 A） |

---

## 五、nanobot 配置文件对齐说明

**配置不在 git 中，以下文件需要手动同步：**

| 配置文件 | ECS 位置 | 本机说明 |
|---|---|---|
| `parrot_config.json` | `/opt/nanobot/config/parrot_config.json` | 已在 commit `29a0f88`，`git pull` 即得 |
| `goslo_config.json` | `/opt/nanobot/config/goslo_config.json` | 同上 |
| `docker-compose.yml` | `/opt/nanobot/docker-compose.yml` | 同上 |
| `~/.nanobot/config.json` | ECS 宿主机 | 与 `parrot_config.json` 内容一致，手动 cp 同步 |
| `.env` | 不在 git（正常） | 本机工作区需要有 `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` |

---

## 六、关键路径摘要

```
本机操作顺序：
① git pull nanobot → 获取 commit 29a0f88
② 修复 mcp.py → git commit → git push
③ 完成 OAuth（本机 nanobot agent 跑一次）
④ scp token → ECS ~/.nanobot/google-workspace-credentials/
⑤ ECS: git pull + docker compose build + docker compose up -d
⑥ ECS 验证 Calendar/Gmail 工具可用
```
