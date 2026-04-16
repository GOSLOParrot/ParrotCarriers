# 仓库提交规范与注意事项

> 基于 2026-04-16 排查经验整理。核心问题：secrets 泄露 + 大文件阻塞 + .cursor/ 职责不清。

---

## 1. 这次出了什么问题（复盘）

| 问题 | 现象 | 根因 |
|------|------|------|
| Push 卡死 2 分钟以上 | git push 无任何输出 | Mihomo TUN 模式对 HTTP POST 有隐性超时；加上待上传包体达 **38MB** |
| HTTP 408 超时 | 偶尔出现后 fatal 报错 | 38MB 超过 Mihomo 代理对单次 POST 的容忍时长 |
| GitHub 推送被拒 | `GH013: Repository rule violations` | `deploy_snapshot_p2_20260412.md` 第 68/221 行含明文 `ghp_xxx` PAT |
| 包体 38MB | 正常代码只有 5MB | `nanobot.tar.gz`（31MB）和 `parrotcarriers.tar.gz` 意外进入 commit |

**修复过程**：两次 `git filter-branch` 重写历史 + 手动替换 secrets + `git gc` 压缩 → 5MB → push 成功（55 秒）。

---

## 2. .gitignore 规范（当前 + 补充建议）

### 已有且正确的规则
```
.env / .env.*        ← API key，绝对不提交
.venv/               ← Python 虚拟环境
*.tar.gz / *.zip     ← 归档文件（本次新增）
unity/*/Library/     ← Unity 自动生成
```

### 强烈建议新增

```gitignore
# Cursor 自动生成的技能参考文档（体积大，可随时重新生成）
.cursor/skills/*/references/

# Nanobot 本地工作区（含 persona / session 数据，可能有隐私）
.nanobot/

# 本地调试 / 临时脚本
*.local.py
Test/
restart*.sh
restart*.py
```

### 关于 .cursor/memory/ —— 要不要提交？

**结论：选择性提交，不是全部提交。**

| 文件类型 | 建议 | 原因 |
|---------|------|------|
| `architecture/*.md` | ✅ 提交 | 纯架构文档，无敏感信息，ECS 上有用 |
| `requirements.md` | ✅ 提交 | 产品需求，应版本化 |
| `deploy_snapshot_*.md` | ⚠️ 提交前审查 | 本次就在这里泄露了 PAT |
| `active_context.md` | ❌ 不提交 | AI session 状态，可能含临时 token/路径 |
| `BigIssue.md` / `log.txt` | ❌ 不提交 | 调试记录，无版本价值 |

**推荐的细粒度规则（加到 .gitignore）**：
```gitignore
# Memory: 排除动态/session 文件，保留架构文档
.cursor/memory/active_context.md
.cursor/memory/log.txt
.cursor/memory/BigIssue.md
.cursor/memory/deploy_snapshot_*.md
```

---

## 3. Secrets 管理原则

### 黄金规则：任何真实密钥永远不出现在 .md / .py 文件里

即使是"给自己看的笔记"也不例外，因为：
- `.cursor/memory/` 被 AI 反复读写，容易把你在聊天里提到的 token 写进文档
- GitHub Push Protection 会扫描所有文件，包括 Markdown

### 正确做法

```markdown
# deploy_snapshot 中只写占位符
GITHUB_TOKEN=<见 .env 第12行>
GOOGLE_API_KEY=<见 .env 第6行>
TELEGRAM_BOT_TOKEN=<见 .env 第28行>
```

```bash
# 真实值只放在 .env（已在 .gitignore 中）
GITHUB_TOKEN=ghp_xxx...
```

### 如果不小心提交了 secret

1. **立即吊销该 token**（GitHub → Settings → Developer settings → Tokens）
2. 生成新 token
3. 用 `git filter-branch` 或 `git filter-repo` 从历史中清除
4. Force push（`git push --force`）

---

## 4. VPN / Mihomo 使用注意事项

### 核心问题

Mihomo TUN 模式拦截所有流量，对 **长时间 HTTP POST**（git push 上传包体）有隐性超时，大约 60-90 秒。

### 实测：什么能用，什么不能用

| 方式 | 结果 | 说明 |
|------|------|------|
| `git push`（默认 HTTPS） | ❌ 无限卡死 | Windows Credential Manager 在非交互环境弹不出 UI |
| `git push`（HTTPS + token 内嵌 URL） | ✅ 成功（55s） | 5MB 包体可在超时内完成 |
| `git push`（SSH） | ❌ 卡死 | SSH 子进程无 TTY，密钥加载失败 |
| `gh` CLI 操作 | ✅ 正常 | 使用自己的 HTTPS 通道 |
| `git ls-remote` / `git fetch` | ✅ 正常 | 读操作不受影响 |

### 推荐的推送方式（当前最可靠）

```powershell
# 方式1：token 内嵌（一行命令，每次都有效）
$token = gh auth token
git push "https://GOSLOParrot:$token@github.com/GOSLOParrot/ParrotCarriers.git" master

# 方式2：GitHub Desktop（强烈推荐，见下节）
```

### 如果想根治 SSH push 问题

需要启动 SSH agent 服务（需管理员权限）：
```powershell
# 管理员 PowerShell 运行一次
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```
之后 `git push`（SSH 协议）就不会卡死了。

---

## 5. 推荐工作流：GitHub Desktop

**推荐用 GitHub Desktop 处理日常提交，Cursor 做代码编写。**

### 为什么

- GitHub Desktop 有自己的 HTTPS 认证通道，完全绕过 Windows Credential Manager 的弹窗问题
- 可以在 commit 前**可视化 diff**，避免意外提交大文件或 secrets
- 支持 Stash、Branch、Reset 等操作
- 遇到 push 失败有友好的错误提示

### 使用原则

| 操作 | 工具 |
|------|------|
| 日常 add / commit / push | GitHub Desktop |
| 历史重写、filter-branch | Git Bash 命令行 |
| 查看 remote 状态 | `gh` CLI 或 GitHub Desktop |
| ECS 同步 | `ssh Castle "cd /opt/parrotcarriers && git pull"` |

---

## 6. 关于"把整个工作区推到 git 让 ECS 拉取"

你的需求是合理的，但需要区分两类文件：

### A. 应该在 git 里的（✅）

- `src/` — 业务代码
- `infra/` — Docker / 部署脚本
- `tests/` — 测试
- `pyproject.toml` — 依赖声明
- `.cursor/memory/architecture/` — 架构设计文档
- `.cursor/skills/*/SKILL.md` — 技能入口文件（小，有价值）

### B. 不应该在 git 里的（❌）

- `.cursor/skills/*/references/` — **240个自动生成的 JSON/MD 文件**，完全可以重新生成，只占用仓库体积
- `.cursor/memory/active_context.md`、`deploy_snapshot_*.md` — 可能含 secrets 的 session 文件
- `nanobot.tar.gz`、`parrotcarriers.tar.gz` — 归档文件（deploy 脚本的产物）
- `.nanobot/` — nanobot 工作区（persona/session 数据）

### ECS 同步的更好方式

目前 deploy 脚本已经有 rsync，可以两套并行：

```bash
# 代码同步：用 git（干净、可追踪）
ssh Castle "cd /opt/parrotcarriers && git pull origin master"
ssh Castle "cd /opt/nanobot && git pull origin main"

# 工作区数据同步：用 rsync（不走 git，不污染历史）
rsync -avz ~/.nanobot/goslo-workspace/ root@8.216.45.45:~/.nanobot/goslo-workspace/
```

---

## 7. 快速检查清单（每次 commit 前）

```
□ git diff --stat  →  有没有意外的大文件（>1MB）？
□ grep -r "ghp_\|AIzaSy\|gho_" .cursor/  →  有没有明文 token？
□ .env 有没有出现在 git status 里？（不应该有）
□ 包体大小合理吗？（git count-objects -vH，size-pack < 10MB 为佳）
```

---

*生成时间：2026-04-16 | 基于 ParrotCarriers commit 排查*
