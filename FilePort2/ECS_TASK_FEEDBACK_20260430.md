# ECS 任务反馈 — nanobot 配置修复 + ParrotCarriers Sprint4 Phase 4 推送（2026-04-30）

> **最后更新**：2026-04-30 11:30  
> **状态**：本机工作全部完成，ECS 执行步骤已就绪，可直接操作

---

## 一、本机已完成清单（全部 DONE）

| 任务 | 状态 | 说明 |
|:--|:--|:--|
| nanobot `mcp.py` bug 正式修复 | ✅ | `MCPResourceWrapper` 名称净化，commit `870812e` 已推 GitHub |
| nanobot config 全部对齐 | ✅ | redisUrl / google_workspace key / env vars / redis args / github enabledTools，commit `870812e` |
| `docker-compose.yml` 更新 | ✅ | env_file + credentials volume + infra_default 网络，commit `870812e` |
| ParrotCarriers W8 + GAP-1 代码 | ✅ | commits `f6f3da9` `1ad3d37` `ca913ac` 已推 GitHub master |
| Google OAuth token 生成 | ✅ | 本机已完成 OAuth 授权，token 保存在本机 |
| OAuth token 上传 ECS | ⬜ | **你负责**：scp 命令见 §三 |

---

## 二、ECS 执行步骤（按顺序）

### 步骤 1：拉取两个仓库最新代码

```bash
# nanobot（P1~P4 所有配置修复）
cd /opt/nanobot
git pull origin main
# 验证：git log --oneline -1 → 应看到 870812e

# ParrotCarriers（W8 + GAP-1 + 审计修复）
cd /opt/parrotcarriers
git pull origin master
# 验证：git log --oneline -3 → 应看到 ca913ac / 1ad3d37 / f6f3da9
```

### 步骤 2：ParrotCarriers Brain 装新依赖（W8 引入 fastapi + uvicorn + httpx）

> ⚠️ **必须执行，漏掉则 photo_upload_server 启动失败**

```bash
cd /opt/parrotcarriers
.venv/bin/pip install fastapi uvicorn httpx
# 或完整重装（推荐）
.venv/bin/pip install '.[http,memory,dev]'

# 验证
.venv/bin/python -c "import fastapi, uvicorn, httpx; print('OK')"
```

### 步骤 3：Castle .env 补充两个变量

```bash
# photo_upload_server 必须绑定 0.0.0.0，否则真机 HTTP POST 打不进来
echo 'PARROT_PHOTO_UPLOAD_HOST=0.0.0.0' >> /opt/parrotcarriers/.env

# identify_object 工具默认关闭，smoke test 验收 #2 必须打开
echo 'PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1' >> /opt/parrotcarriers/.env

# 验证
grep -E "PARROT_PHOTO_UPLOAD_HOST|PARROT_ENABLE_IDENTIFY" /opt/parrotcarriers/.env
```

### 步骤 4：安全组确认

- TCP **7889** 放通（photo_upload_server，真机 POST 用）
- TCP **7880 / 7881** 已有（LiveKit，确认没变）

### 步骤 5：重建并重启 nanobot 容器

```bash
cd /opt/nanobot
docker compose build --no-cache
docker compose up -d
docker logs nanobot-api --tail 30
# 无 Gemini 400 / redis connection refused / function name invalid = OK
```

### 步骤 6：重启 Brain Agent

```bash
# 查找并重启 brain agent 进程（tmux / systemd 根据实际情况）
# 期望看到以下两行日志：
# "Sprint4 Phase 4 wired: ... + EcpStateIngest(GAP-1)"
# "[photo_upload] server started host=0.0.0.0 port=7889 ..."
```

### 步骤 7：Health Check

```bash
curl http://localhost:7889/health
# → {"status":"ok","service":"photo-upload"}

curl http://localhost:7888/health
# → {"status":"ok","service":"token-mint"}
```

---

## 三、OAuth Token 上传 ECS（本机执行）

Token 已生成，在本机路径：
```
C:\Users\Bin\AppData\Roaming\google-workspace-mcp\credentials\
  credentials.json          ← Node 格式（nanobot 用）
  credentials_python.json   ← Python 格式（备份）
```

**上传命令（本机 PowerShell）**：
```powershell
scp -r "$env:APPDATA\google-workspace-mcp\credentials\" root@8.216.45.45:/root/.nanobot/google-workspace-credentials/
```

**ECS 上设置权限**：
```bash
chown -R 1000:1000 /root/.nanobot/google-workspace-credentials/
```

**验证 nanobot Google 工具可用**：
```bash
docker exec nanobot-api nanobot agent \
  -m "list my Google Calendar events for today" \
  --config /home/nanobot/.nanobot/config.json --no-markdown
```

---

## 四、联机 smoke 关键验证提醒

| # | 提醒 | 后果 |
|:--|:--|:--|
| 1 | `pip install '.[http,memory,dev]'` 必须跑 | photo_upload_server 启动失败 |
| 2 | `PARROT_PHOTO_UPLOAD_HOST=0.0.0.0` 必须设 | 真机 HTTP POST 打不进来 |
| 3 | 安全组 TCP 7889 放通 | 同上 |
| 4 | `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=1` 必须设 | 验收 #2 跳过 |
| 5 | 验收 #3 看 `[GOSLO state] active_cmd=... locks=...` | GAP-1 关键验证 — 修复前永远空 |
| 6 | 验收 #5 photo 全链路 5 段 log 必须全出现 | 缺任一段 = bug |

### 验收 #5 Photo 5 段 log 串联

```
[1] Unity:  [PhotoController] photo_id=ph_xxx ... previewSent=True
[2] Brain:  [observer.photo] PhotoNode upserted photo_id=ph_xxx
[3] Unity:  [PhotoController] HTTP POST /upload/photo/ph_xxx → 200 bytes=N
[4] Brain:  [photo_upload] saved photo_id=ph_xxx ... publish_ok=True
[5] Brain:  [observer.photo] PhotoNode photo_id=ph_xxx asset_ref=...
            + Unity EcpEventDispatcher received photo.asset_uploaded
```

---

## 五、两仓库当前 HEAD

| 仓库 | 分支 | HEAD | 状态 |
|:--|:--|:--|:--|
| `GOSLOParrot/nanobot` | `main` | `870812e` | ✅ 已推 GitHub |
| `GOSLOParrot/ParrotCarriers` | `master` | `697ea1f` | ✅ 已推 GitHub |

---

## 六、问题追踪最终状态

| P# | 问题 | 状态 |
|:--|:--|:--|
| P1 | Redis localhost 容器不通 | ✅ 已修复 |
| P2 | GitHub MCP 工具过多 | ✅ 已修复 |
| P3 | google-workspace key 含连字符 | ✅ 已修复 |
| P4 | GWS Resource 名称含空格 | ✅ 正式修复（mcp.py）|
| P5 | OAuth 回调 ECS 无法访问 | ✅ 本机完成 OAuth → scp token（见 §三）|
| P6 | ECS 无法 git push | ✅ 本机推送完成 |
