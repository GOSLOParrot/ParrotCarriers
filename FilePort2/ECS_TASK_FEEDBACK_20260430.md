# ECS 任务反馈 — nanobot 配置修复 + ParrotCarriers Sprint4 Phase 4 推送（2026-04-30）

> **创建时间**：2026-04-30  
> **状态**：本机工作完成，ECS 执行步骤已就绪

---

## 一、本机已完成的工作

### 1.1 nanobot 仓库修复（commit `870812e`，已推 GitHub）

| P# | 问题 | 修复内容 | 文件 |
|:--|:--|:--|:--|
| P4 | MCP Resource 名称含空格 → Gemini 400 | `MCPResourceWrapper.__init__` 改用 `re.sub(r"[^a-zA-Z0-9_]","_", name)` 净化 | `nanobot/agent/tools/mcp.py:146` |
| P1 | `redis://localhost:6379` 容器内不通 | `redisUrl` → `redis://infra-redis-1:6379/0` | `config/parrot_config.json` |
| P3 | Gemini 400: `google-workspace` key 含连字符 | 两个 config 都改为 `google_workspace` | `parrot_config.json` + `goslo_config.json` |
| — | `google_workspace` 缺 OAuth env | 注入 `${GOOGLE_CLIENT_ID}` / `${GOOGLE_CLIENT_SECRET}` | 同上 |
| — | Redis MCP args 用 `${REDIS_URL}` → 容器内解析为 localhost | 硬编码 `redis://infra-redis-1:6379/0` | `parrot_config.json` |
| P2 | GitHub MCP 40+ 工具超限 | `github.enabledTools` 限为 4 项 | `parrot_config.json` |
| — | 容器无法注入 env / OAuth token | `env_file: .env` + credentials volume + `infra_default` 外部网络 | `docker-compose.yml` |

**GitHub 最新 HEAD**：`https://github.com/GOSLOParrot/nanobot` branch `main` = `870812e`

### 1.2 ParrotCarriers 仓库（master = `de9e716`，已推 GitHub）

| Commit | 内容 |
|:--|:--|
| `f6f3da9` | W8 Unity 半边 PhotoController + 256px preview + HTTP POST |
| `1ad3d37` | GAP-1 EcpState ingest handler + 10 tests (230/230) |
| `ca913ac` | 审计修复：reconnect bytes / HTTP 4次重试 / schema_version skip / scene meta |
| `f3cba34` | 完成报告更新（W8 + GAP-1）|
| `2188848` | 联机 smoke 测试计划 |
| `de9e716` | OAuth tracker 文件入库 |

**GitHub 最新 HEAD**：`https://github.com/GOSLOParrot/ParrotCarriers` branch `master` = `de9e716`

---

## 二、ECS 需要执行的步骤（按顺序）

### 步骤 1：拉取两个仓库最新代码

```bash
# nanobot（包含 P1/P2/P3/P4 所有修复）
cd /opt/nanobot
git pull origin main
# 验证：git log --oneline -3 应该看到 870812e

# ParrotCarriers（包含 W8 + GAP-1 + audit fixes）
cd /opt/parrotcarriers
git pull origin master
# 验证：git log --oneline -5
```

### 步骤 2：确认 .env 包含 OAuth 凭证

```bash
grep -E "GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET" /opt/parrotcarriers/.env
# 两行都必须有值，否则 nanobot 容器里 google_workspace MCP 无法启动 OAuth 流程
```

如果不存在，手动添加：
```bash
echo 'GOOGLE_CLIENT_ID=<你的 OAuth Client ID>' >> /opt/parrotcarriers/.env
echo 'GOOGLE_CLIENT_SECRET=<你的 OAuth Client Secret>' >> /opt/parrotcarriers/.env
```

### 步骤 3：确认 symlink（.env → ParrotCarriers .env）

```bash
ls -la /opt/nanobot/.env
# 应该是 /opt/nanobot/.env -> /opt/parrotcarriers/.env
# 如果不存在：
# ln -sf /opt/parrotcarriers/.env /opt/nanobot/.env
```

### 步骤 4：确认 OAuth token 目录

```bash
ls -la ~/.nanobot/google-workspace-credentials/
# 如果目录不存在或为空 → 需要本机完成 OAuth 后 scp
mkdir -p ~/.nanobot/google-workspace-credentials/
chown -R 1000:1000 ~/.nanobot/google-workspace-credentials/
```

### 步骤 5：重建 nanobot 容器（包含 mcp.py 修复）

```bash
cd /opt/nanobot
docker compose build --no-cache
docker compose up -d
docker ps | grep nanobot
```

### 步骤 6：验证 nanobot 启动无报错

```bash
docker logs nanobot-api --tail 50
# 不应有 Gemini 400 / redis connection refused / function name invalid 等错误
```

### 步骤 7：ParrotCarriers Brain 依赖安装（W8 引入 fastapi + uvicorn + httpx）

> **关键提醒（漏装则 brain agent boot 时 photo_upload_server 启动失败）**

```bash
cd /opt/parrotcarriers
.venv/bin/pip install fastapi uvicorn httpx
# 或重装完整依赖（推荐，确保所有 extras 都有）
.venv/bin/pip install '.[http,memory,dev]'
```

验证：
```bash
.venv/bin/python -c "import fastapi, uvicorn, httpx; print('OK')"
```

### 步骤 8：Castle .env 关键配置项

> 以下几项与本机不同，**Castle 必须设**：

```bash
# Castle 上 photo_upload_server 要接受真机 HTTP POST，必须绑定 0.0.0.0
# （本机默认 127.0.0.1；Castle 上改为 0.0.0.0）
echo 'PARROT_PHOTO_UPLOAD_HOST=0.0.0.0' >> /opt/parrotcarriers/.env

# 验收 #2 identify_object 工具默认关闭（安全 gate），Castle 必须打开
echo 'PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1' >> /opt/parrotcarriers/.env
```

同时确认安全组放通 **TCP 7889**（photo_upload_server）— 否则 Unity 真机 POST 无法到达 Castle。

### 步骤 8：Brain health check

```bash
# tmux 里重启 Brain（或检查现有进程）
# 看日志里是否有：
# "Sprint4 Phase 4 wired: ... + EcpStateIngest(GAP-1)"
# "[photo_upload] server started host=127.0.0.1 port=7889 cache_root=data/photos"
```

---

## 三、OAuth 认证（本机还需完成，任务 C+D）

> P5 问题（OAuth 回调 127.0.0.1 ECS 无法访问）尚未解决。需要在**本机**完成一次 OAuth 授权，再 scp token 到 ECS。

### 本机操作

```bash
# 确认本机 .env 有 GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
# 运行一次 nanobot agent 触发 OAuth 浏览器弹窗
cd d:\GOSLOParrot\nanobot
.venv\Scripts\python.exe -m nanobot agent \
  -m "Use the google_workspace manage_accounts tool with operation authenticate" \
  --no-markdown
# 浏览器打开 → 授权 → token 保存到本机
```

Token 位置（Windows）：`%APPDATA%\google-workspace-mcp\credentials\`

### 上传 ECS

```powershell
# 本机 PowerShell
scp -r "$env:APPDATA\google-workspace-mcp\credentials\" root@<ECS_IP>:/root/.nanobot/google-workspace-credentials/
ssh root@<ECS_IP> "chown -R 1000:1000 /root/.nanobot/google-workspace-credentials/"
```

---

## 四、联机 smoke 准备（ParrotCarriers）

ECS 上 ParrotCarriers 服务就绪后，下一个 chat 按 `sprint4_phase4_online_smoke_test_plan_20260430.md` §3 跑：

1. `curl http://localhost:7889/health` → `{"status":"ok","service":"photo-upload"}`（W8 新增）
2. Brain tmux log 含 `EcpStateIngest attached`（GAP-1 新增）
3. Brain log 含 `Sprint4 Phase 4 wired: ... + EcpStateIngest(GAP-1)`
4. `curl http://localhost:7888/health` → token_mint OK
5. `git log --oneline -3` 应看到 `1ad3d37 / ca913ac / f6f3da9`

---

## 五、问题追踪更新

| P# | 问题 | 状态 |
|:--|:--|:--|
| P1 | Redis localhost 容器不通 | ✅ 本机修复 commit `870812e` |
| P2 | GitHub MCP 工具过多 | ✅ 本机修复 commit `870812e` |
| P3 | google-workspace key 含连字符 | ✅ 本机修复 commit `870812e` |
| P4 | GWS Resource 名称含空格 | ✅ **本机正式修复** `mcp.py` commit `870812e`（不再是猴子补丁）|
| P5 | OAuth 回调 ECS 无法访问 | ⏳ 本机完成 OAuth → scp token（任务 C+D）|
| P6 | ECS 无法 git push | ✅ 本机推送 GitHub 完成 |

---

## 五、联机 smoke 关键验证提醒

> 以下几点是 ECS 上跑联机 smoke 时特别容易踩坑的地方，ECS 执行人必看：

| # | 提醒 | 后果（不做会怎样）|
|:--|:--|:--|
| 1 | **`pip install '.[http,memory,dev]'`** 必须跑 | `photo_upload_server` 启动失败（`ImportError: fastapi`），brain boot 报错但不 fatal，W8 链路全断 |
| 2 | **`PARROT_PHOTO_UPLOAD_HOST=0.0.0.0`** Castle 必须设 | photo_upload_server 只监听 127.0.0.1，Unity 真机 HTTP POST 打不进来 |
| 3 | **安全组 TCP 7889 放通** | 同上，HTTP POST 超时失败 |
| 4 | **`PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1`** | 验收 #2 identify_object 工具被跳过，Brain 不注册该函数，Gemini 调不到 |
| 5 | **验收 #3 看 `[GOSLO state] active_cmd=... locks=...`** | GAP-1 关键验证点 — 修复前这两字段永远空；出现了才算 GAP-1 真正接通 |
| 6 | **验收 #5 photo 全链路 5 段 log 必须全出现** | 任意一段缺失即 bug：preview EcpEvent → BB transient → HTTP 200 → Brain disk 落盘 → photo.asset_uploaded 回程 |

### 验收 #5 Photo 5 段 log 串联参考

```
[1] Unity:  [PhotoController] photo_id=ph_xxx ... previewSent=True
[2] Brain:  [observer.photo] PhotoNode upserted photo_id=ph_xxx
            BB transient/last_photo_event stage="preview"
[3] Unity:  [PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=N
[4] Brain:  [photo_upload] saved photo_id=ph_xxx ... publish_ok=True
[5] Brain:  [observer.photo] PhotoNode photo_id=ph_xxx asset_ref=/upload/photo/.../ph_xxx.jpg
            BB transient/last_photo_event stage="asset_uploaded"
            (Unity EcpEventDispatcher) received event_type=photo.asset_uploaded
```

缺 [2] = EcpEvent 未到 Brain；缺 [3] = photo_upload_server 未启动或端口不通；缺 [4]/[5] = fastapi/uvicorn 缺包。

---

## 六、两仓库当前 HEAD 摘要

| 仓库 | 分支 | HEAD commit | 状态 |
|:--|:--|:--|:--|
| `GOSLOParrot/nanobot` | `main` | `870812e` | ✅ 已推 GitHub |
| `GOSLOParrot/ParrotCarriers` | `master` | `de9e716` | ✅ 已推 GitHub |
