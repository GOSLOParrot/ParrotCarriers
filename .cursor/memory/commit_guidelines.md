# 仓库提交 & ECS 同步工作流

> 版本：2026-04-16 | 基于实际排查经验整理

---

## 快速索引

| 我要做什么 | 看哪一节 |
|-----------|---------|
| 日常 commit + push | § 1 |
| 同步代码到 ECS | § 2-A |
| 同步 nanobot persona 到 ECS | § 2-B |
| 同步 .env 到 ECS | § 2-C |
| push 失败排查 | § 3 |
| 不小心提交了 secret | § 4 |
| 什么文件该/不该进 git | § 5 |

---

## § 1  日常 Commit 工作流（GitHub Desktop）

### 推荐工具分工

| 任务 | 工具 |
|------|------|
| 写代码 | Cursor |
| add / commit / push | **GitHub Desktop** |
| ECS 同步 | `infra/sync-castle.ps1`（见 § 2） |
| 历史重写、filter-branch | Git Bash 命令行 |

### 为什么用 GitHub Desktop 而不用命令行

- **彻底绕过 Mihomo 代理问题**：GitHub Desktop 有自己的 HTTPS 认证和上传通道，不受 TUN 模式 60-90 秒超时影响
- **可视化 diff**：commit 前能看到每个文件的改动，避免意外提交大文件或 secrets
- **友好的错误提示**：push 失败时直接告诉你原因

### Commit 前的三秒检查

在 GitHub Desktop 的 diff 界面确认：

```
□ 没有意外的大文件（单文件 > 1MB 要想想为什么）
□ 没有 .env 文件出现在变更列表里
□ deploy_snapshot / active_context 等 memory 文件如果出现了，看看里面有没有明文 token
```

---

## § 2  ECS 同步工作流

### 全局说明

ECS Castle（`8.216.45.65`）上有三个独立区域需要维护：

```
/opt/parrotcarriers/     ← 业务代码，走 git pull
/opt/nanobot/            ← nanobot fork，走 git pull
~/.nanobot/              ← persona / workspace 数据，走 rsync
/opt/parrotcarriers/.env ← secrets，走 rsync（只在改动时同步）
```

### 一键同步脚本

位置：`infra/sync-castle.ps1`

```powershell
# 在 ParrotCarriers 根目录下运行（PowerShell）

# 场景 A：只同步代码（最常用）
.\infra\sync-castle.ps1

# 场景 B：代码 + nanobot persona 文件
.\infra\sync-castle.ps1 -Workspace

# 场景 C：代码 + .env（改了 secrets 时用）
.\infra\sync-castle.ps1 -Env

# 场景 D：全量同步
.\infra\sync-castle.ps1 -All
```

---

### § 2-A  代码同步（git pull）

**触发时机**：每次 GitHub Desktop push 完成后

脚本自动执行以下操作：
1. `git pull origin master`（ParrotCarriers）
2. `git pull origin main`（nanobot）
3. 如果有代码变更，自动重跑 `pip install`

手动方式（SSH 进去执行）：
```bash
ssh Castle
cd /opt/parrotcarriers && git pull origin master
cd /opt/nanobot && git pull origin main
```

---

### § 2-B  Nanobot Workspace 同步（rsync）

**触发时机**：修改了 persona 文件（SOUL.md、AGENTS.md、TOOLS.md、USER.md）后

本地路径 → ECS 路径：

```
C:\Users\Bin\.nanobot\goslo-workspace\  →  ~/.nanobot/goslo-workspace/
  AGENTS.md                                  AGENTS.md
  SOUL.md                                    SOUL.md
  TOOLS.md                                   TOOLS.md
  USER.md                                    USER.md

C:\Users\Bin\.nanobot\workspace\        →  ~/.nanobot/workspace/
  AGENTS.md / SOUL.md / TOOLS.md / USER.md   （persona 文件）
  HEARTBEAT.md
  （sessions/ 和 memory/ 不同步，那是 ECS 运行时产生的本地状态）
```

运行：
```powershell
.\infra\sync-castle.ps1 -Workspace
```

---

### § 2-C  .env 同步

**触发时机**：只在新增/修改了 API key 时手动运行一次

```powershell
.\infra\sync-castle.ps1 -Env
```

> ⚠️ `.env` 绝对不进 git，只通过 rsync 点对点传输。

---

### § 2-D  完整首次部署（新 ECS 或重置环境）

首次或重置时，用原有的完整部署脚本（需要 Git Bash / WSL，因为要用 bash）：

```bash
# 在 Git Bash 里运行
bash infra/deploy-castle.sh 8.216.45.45
```

该脚本会：
1. rsync 全量同步代码
2. 安装 Python 依赖 + Node.js
3. 同步 nanobot workspace
4. 启动 Docker 服务（LiveKit + Redis）
5. 健康检查

---

## § 3  Push 失败排查

### 用了 GitHub Desktop 还是失败？

| 现象 | 原因 | 解法 |
|------|------|------|
| 上传进度条卡住很久 | 包体太大（> 20MB） | 检查是否有大文件/归档被误 commit |
| `GH013: Repository rule violations` | 文件里有明文 token（`ghp_`、`AIzaSy` 等） | 见 § 4 |
| `Authentication failed` | GitHub Desktop 未登录 | 重新在 GitHub Desktop 里登录账号 |

### 命令行临时方案（GitHub Desktop 不可用时）

```powershell
$token = gh auth token
git push "https://GOSLOParrot:$token@github.com/GOSLOParrot/ParrotCarriers.git" master
```

> 包体需 < 15MB 才能在 Mihomo 代理超时内完成。

### 彻底根治 SSH Push 问题（管理员 PowerShell 运行一次）

```powershell
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
# 之后把 remote 改为 SSH 协议
git remote set-url origin git@github.com:GOSLOParrot/ParrotCarriers.git
```

---

## § 4  不小心提交了 Secret

**立刻做这三件事：**

1. **吊销 token**（先于一切）
   - GitHub PAT：`github.com → Settings → Developer settings → Personal access tokens → 删除`
   - Google API Key：`console.cloud.google.com → Credentials → 删除`
   - Telegram Bot Token：向 `@BotFather` 发 `/revoke`

2. **从 git 历史中清除**
   ```bash
   # Git Bash 里运行
   FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --tree-filter \
     "sed -i 's/ghp_[A-Za-z0-9]*/REDACTED/g; s/AIzaSy[A-Za-z0-9_-]*/REDACTED/g' \
      .cursor/memory/deploy_snapshot_p2_20260412.md 2>/dev/null || true" \
     origin/master..HEAD
   git update-ref -d refs/original/refs/heads/master
   git reflog expire --expire=now --all
   git gc --prune=now
   ```

3. **Force push + ECS 同步**
   ```powershell
   $token = gh auth token
   git push --force "https://GOSLOParrot:$token@github.com/GOSLOParrot/ParrotCarriers.git" master
   .\infra\sync-castle.ps1
   ```

### 事后：为什么会发生？

Cursor AI 在读写 `.cursor/memory/` 时，如果对话里出现了真实 token，**可能直接把它写进 markdown 文档**。

预防方法：
- 对话里只说"用 .env 里的 GITHUB_TOKEN"，不要粘贴真实值
- `.cursor/memory/deploy_snapshot_*.md` 已加入 `.gitignore`，不会再被误提交

---

## § 5  文件分类：什么进 git，什么不进

### ✅ 应该在 git 里

```
src/                          业务代码
tests/                        测试
infra/                        Docker / 部署脚本（含本文件！）
pyproject.toml                依赖声明
.cursor/memory/architecture/  架构设计文档（纯文档，无 secrets）
.cursor/memory/requirements.md
.cursor/memory/milestone_*.md
.cursor/memory/commit_guidelines.md   ← 本文件
.cursor/skills/*/SKILL.md     技能入口文件（小，有价值）
unity/ParrotDev/Assets/       Unity 场景 / 脚本
```

### ❌ 不应该在 git 里（已在 .gitignore）

```
.env / .env.*                 Secrets，用 rsync 单独传
.cursor/skills/*/references/  240+ 自动生成的 JSON/MD，随时可再生
.cursor/memory/active_context.md      AI session 状态
.cursor/memory/deploy_snapshot_*.md   可能含 token
.cursor/memory/log.txt
.nanobot/                     nanobot persona/session，用 rsync 传
*.tar.gz / *.zip              归档文件
.venv/                        Python 虚拟环境
unity/*/Library/              Unity 自动生成
```

---

## § 7  Nanobot 配置变更流程

### 配置文件分类

| 文件 | 仓库 | 同步方式 |
|------|------|---------|
| `nanobot/config/parrot_config.json` | **nanobot** git | commit → push → ECS `git pull` |
| `~/.nanobot-parrot/config.json` | ❌ 不进 git | 由 `start_nanobot_worker.py` 从模板自动生成 |
| `~/.nanobot/goslo-workspace/*.md` | ❌ 不进 git | `sync-castle.ps1 -Workspace` |

> `parrot_config.json` 是**模板**，在 nanobot 仓库里。运行时脚本读它生成实际的 `~/.nanobot-parrot/config.json`，注入环境变量（GEMINI_API_KEY、GITHUB_TOKEN 等）。

### 修改 parrot_config.json（模板）

```powershell
# 1. 本地修改 D:\GOSLOParrot\nanobot\config\parrot_config.json
# 2. 在 GitHub Desktop 里 commit（选 nanobot 仓库）
# 3. Push 到 origin/main
# 4. ECS 同步（sync-castle.ps1 会同时 git pull nanobot）
.\infra\sync-castle.ps1

# 5. ECS 上重启 nanobot worker（如果正在运行）
ssh Castle "tmux send-keys -t nanobot 'C-c' Enter 'python /opt/parrotcarriers/src/scripts/start_nanobot_worker.py --force-config' Enter"
```

> ⚠️ 重启后运行时配置会从最新模板重新生成，覆盖任何 ECS 上的手动改动。

### 修改 Workspace 文件（SOUL / TOOLS / AGENTS / USER.md）

```powershell
# 本地编辑完后直接 rsync（不需要 git）
.\infra\sync-castle.ps1 -Workspace
# nanobot worker 下次收到新任务时自动读取新 workspace，无需重启
```

### 本地 vs ECS 直接修改

| 场景 | 推荐 |
|------|------|
| 改代码/模板配置 | 本地改 → git → sync |
| 临时测试配置 | 可以 SSH 进 ECS 改 `~/.nanobot-parrot/config.json`，但 `--force-config` 重启会被覆盖 |
| 紧急热修复 | SSH 改 + 记录下来同步回本地 |

---

## § 6  常用命令速查

```powershell
# 同步代码到 ECS（最常用）
.\infra\sync-castle.ps1

# 同步代码 + persona
.\infra\sync-castle.ps1 -Workspace

# 全量
.\infra\sync-castle.ps1 -All

# SSH 进 ECS
ssh Castle

# 查看 ECS 进程（Brain / Maid / Goslo-Chat）
ssh Castle "tmux ls"

# 检查 ECS 上的最新 commit
ssh Castle "cd /opt/parrotcarriers && git log --oneline -3"

# 检查本地包体大小（push 前确认）
git count-objects -vH
```

---

*生成时间：2026-04-16 | 适用仓库：ParrotCarriers + nanobot*

---

## § 8  Drift 说明条款 (S0.N, 2026-04-22)

### 8.1 什么是 Drift

**Drift** = 代码或协议的实现**偏离**对应架构文档 (tentative / ratified) 的情况。

- **合法 drift** (tentative → 需升级): tentative 文档被代码跑通后, 代码的真实行为和文档对不齐。这是**正常的**, 反映"设计落地时发现漏洞"。
- **违规 drift** (ratified → 需 ADR): ratified 文档被改了而没 ADR 记录, 或代码偷偷偏离了 ratified 文档。**禁止**。

### 8.2 Drift 记录的最低规范

**每个 commit message 都可能需要一句 drift 说明**, 格式:

```
drift: <文档路径> <tentative|ratified> — <一句话说明>
```

**触发情形**:
- 改了 tentative 文档里的约定 (字段语义 / 状态名 / 协议字段) → `drift: <doc> tentative — renamed key foo → bar`
- 发现 ratified 文档和代码不一致 → 先打开一个 ADR (`ADR-XXX-drift-*`), commit 里带 `drift: <doc> ratified — see ADR-XXX`

### 8.3 Drift 审计点

- Sprint 收尾时 Gate 3 跑完, **扫一遍本 Sprint 所有 commit**, drift 说明汇总到 `sprint{N}_kickoff.md` 问题池底部
- 累积 drift 过多 (≥5 条/Sprint) = 信号: 当前设计 tentative 状态没管好, 需要回炉而不是硬上

---

## § 9  三闸门回归基线 (S0.6, 2026-04-22)

### 9.1 为什么要基线

每个 Sprint 收尾时必须跑 Gate 3 (回归), 但用例太多全跑不现实。**基线** = 每个 Sprint 必抽的 1-2 条关键回归用例, 越后面 Sprint 基线越厚。

### 9.2 当前基线 (随 Sprint 滚动追加)

| 完成 Sprint | 必抽回归用例 | 通过标准 |
|:-----------|:------------|:---------|
| Sprint 0 收 | (基线, 无) | N/A |
| Sprint 1 收 | Brain + sim_unity_client 语音往返 (P2 基线) + Gemini tool `remember` / `query_memory` | 日志看到 RPC 成功 + Graphiti 查得到 |
| Sprint 2 收 | Sprint 1 全部 + vision/state 状态机切换 + Blackboard 订阅日志 | BB set/get 一致 |
| Sprint 3 收 | Sprint 1 + Sprint 2 的 VideoTier 降档 | video_tier 变化时无崩溃, 有日志 |
| Sprint 4 收 | Sprint 3 AR 桌面 MVP + Gemini 能看到视频 | Gemini 调用 identify_object 得到真实结果 |

### 9.3 基线维护规则

- 每个 Sprint 收尾 commit **必须**:
  1. 跑 §9.2 对应那行的用例
  2. commit message 里附 `regression: ok` 或 `regression: <用例名> fail → fix in next`
  3. 如果加了新的**关键**回归用例, 在本节表格追加一行 (Sprint N+1 起生效)
- 基线不允许"临时关闭"某条用例, 只能"找到原因修掉"或"写 ADR 显式放弃"
- 相关依据文档: `test_gate_rules.md §3.2` (源表, 本节与之保持一致)

### 9.4 特例: 只改文档的 commit

只动文档的 commit 也要过 Gate 1 (Markdown 渲染 + 链接 alive), 但**不需要**跑 §9.2 用例, commit message 用 `regression: n/a (docs only)`。

