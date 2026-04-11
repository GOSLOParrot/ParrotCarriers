# Cursor SSH 远程 Agent 配置报告

> 创建日期：2026-04-11  
> 实例：i-6weco3gg4ombb0bhym0fZ（日本东京 ap-northeast-1）  
> 公网 IP：8.216.45.45  
> 状态：**✅ SSH 连接测试通过**

---

## 一、背景与版本信息

**Cursor 3.0** 于 2026-04-02 发布，正式将 SSH 远程 Agent 纳入一级支持特性。核心特性：

- **Agents Window**：通过 `Cmd+Shift+P → Agents Window` 打开，可跨本地/Worktree/Cloud/Remote SSH 并行运行多个 Agent
- **Remote SSH Agent**：在远端机器上运行 `agent worker start`，即可将该机器注册为 Worker 节点，从任意设备（包括手机）远程控制
- **自托管 Cloud Agent**（2026-03-25）：代码和工具执行完全留在自己网络内，适合企业内网

---

## 二、ECS 实例快照（城堡节点）

| 属性 | 值 |
|:-----|:---|
| 实例 ID | `i-6weco3gg4ombb0bhym0fZ` |
| 地域 | 日本东京（ap-northeast-1） |
| 公网 IP | `8.216.45.45` |
| 登录用户 | `root` |
| 密钥对名称 | `my-ed25519-key` |
| 操作系统 | Ubuntu 22.04.5 LTS (Jammy Jellyfish) |
| 内核 | `5.15.0-170-generic` |
| CPU | 2 核 |
| 内存 | 7.2 GiB（空闲 6.3 GiB） |
| 磁盘 / | 99 GB（已用 5.3 GB，可用 89 GB） |
| Swap | 无 |
| 基础工具 | `curl` / `wget` / `git` / `python3` |

### SSH 连接测试结果

```
SSH_CONNECTION_OK
Linux iZ6weco3gg4ombb0bhym0fZ 5.15.0-170-generic x86_64 GNU/Linux
Filesystem: /dev/nvme0n1p3  99G  5.3G  89G  6% /
Mem: 7.2Gi  used=269Mi  free=6.3Gi
```

**测试命令（本地执行）：**

```bash
ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=10 root@8.216.45.45 "echo SSH_CONNECTION_OK && uname -a"
```

---

## 三、Cursor SSH 远程 Agent 配置方法

### 方式 A：传统 Remote SSH（类 VSCode，编辑器直连）

1. **本地安装 Cursor**（≥ 3.0）并确认 Remote SSH 扩展已启用

2. **配置 `~/.ssh/config`**（Windows 路径：`C:\Users\Bin\.ssh\config`）：

   ```
   Host castle-tokyo
       HostName 8.216.45.45
       User root
       IdentityFile ~/.ssh/id_ed25519
       ForwardAgent yes
       ServerAliveInterval 60
       ServerAliveCountMax 3
   ```

3. **在 Cursor 中连接**：
   - `Cmd/Ctrl+Shift+P` → `Remote-SSH: Connect to Host`
   - 选择 `castle-tokyo`
   - 打开远端目录，Agent 即在远端运行

### 方式 B：Agent Worker 模式（Cursor 3.0 新特性，推荐）

> **适合场景**：在 ECS 上长期运行任务，从本地/手机远程控制

**第一步：在 ECS 上安装 Cursor CLI**

```bash
# SSH 登录到 ECS
ssh -i ~/.ssh/id_ed25519 root@8.216.45.45

# 安装 Cursor CLI
curl https://cursor.com/install -fsS | bash
```

**第二步：登录 Cursor 账号**

```bash
cursor login
# 按提示用浏览器完成 OAuth 认证，订阅自动同步
```

**第三步：启动 Worker**

```bash
# 建议用 tmux 保持会话不中断
tmux new -s cursor-worker
agent worker start
# 或保留详细日志
agent worker start --verbose
```

输出示例：
```
Starting worker...
Worker is now running.
Name: castle-tokyo
Directory: /root/ParrotCarriers
Worker URL: https://cursor.com/agents?worker=71e1e6b3-ddc2-49c1-9d3b-xxx
Automations URL: https://cursor.com/automations?worker=71e1e6b3-xxx
```

**第四步：从任意设备控制**

- 浏览器打开 `cursor.com/agents`，选中 `castle-tokyo` worker
- 或在 Cursor IDE 的 Agents Window 中选择该 worker
- 手机（iOS）：App Store 安装 "Cursor AI Mobile"
- 手机（Android）：Chrome 打开 `cursor.com/agents`

### 方式 C：Cursor Tunnel（轻量穿透，无需公网 IP 也可用）

```bash
# 在远端下载 CLI 并建立隧道
curl -Lk 'https://api2.cursor.sh/updates/download-latest?os=cli-alpine-x64' --output cursor_cli.tar.gz
tar -xzf cursor_cli.tar.gz
./cursor tunnel --accept-server-license-terms --name castle-tokyo
```

本地 Cursor：`Remote-SSH: Connect to Tunnel` → 选择 `castle-tokyo`

---

## 四、使用注意事项（重要）

### ⚠️ 端口与 LiveKit 的关系（无冲突）

报告中提到"Worker 只需 443 端口出站"，这是 **Cursor 自身的连接**，与 LiveKit 端口体系完全独立：

| 服务 | 方向 | 端口 | 说明 |
|:-----|:-----|:-----|:-----|
| Cursor Agent Worker | **出站**（ECS → cursor.com） | 443/TCP（WebSocket） | ECS 主动拨出，连接 Cursor 云路由 |
| LiveKit Server（入站信令） | **入站**（客户端 → ECS） | 7880/7881/TCP，443/TLS（可选） | 客户端连进来 |
| LiveKit WebRTC（媒体） | 双向 | 7882/UDP（TURN） | 音视频传输 |

两者不冲突：一个出站、一个入站，操作系统不会冲突。即使 LiveKit 配了 nginx 占用 443 入站，Cursor worker 同时跑 443 出站也完全共存（如同你同时访问网页又运行 web server）。

### ⚠️ 内存占用参考（2C8G 仅调试用：安全）

| 场景 | 内存占用 | 风险 |
|:-----|:--------|:-----|
| CLI worker 刚启动 | ~500MB | 无 |
| CLI worker 运行 1 小时 | ~1.5GB | 低 |
| CLI worker 运行 3 小时 | ~4GB（V8 堆满崩溃） | **有内存泄漏 Bug** |
| Remote SSH 全量 IDE | 1~4GB | 小实例慎用 |
| 大型项目 + Agent 长时间 | 7GB+ | 危险区 |

**结论：调试时用，用完立刻停掉 → 完全没问题。**

关键规则：
- 用完立刻 `tmux kill-session` 或 Ctrl+C 停掉 worker
- 不要让 worker 空跑超过 2 小时（内存泄漏会导致崩溃）
- 不要同时跑 Cursor worker + LiveKit + Docker 全套（8G 会撑满）
- 调试优先用 CLI worker 模式，而非全量 Remote SSH IDE

### ⚠️ Token 消耗管控

| 问题 | 说明 |
|:-----|:-----|
| 每条消息基础消耗 | 约 13K+ tokens（含系统 prompt、工具定义、Rules 开销） |
| 长对话叠加 | 对话越长，上下文越大，后续消息可达 170K+ tokens |
| Agent 模式加倍 | Agent 自动调用工具（Search/Terminal/Edit），每步都消耗 |
| 贵模型慎用 | Claude Opus 4.6 比 Gemini Flash 贵 10 倍以上 |

**控制策略：**
- 任务完成立即开新对话（不要延续旧 chat）
- 聚焦单一任务，不要在一个 chat 里做多件事
- 远端调试优先用 `gemini-flash` 等轻量模型
- 在 `cursor.com/settings` → Usage Dashboard 监控消耗

### ⚠️ 禁止行为（防止 Token 浪费）

```
❌ 禁止：让 Agent 读取大段报错日志（超过 50 行应先 grep 过滤）
❌ 禁止：Agent 自行跑大型编译/测试而不设超时（会消耗大量 token 等待输出）
❌ 禁止：在同一 chat 里反复重试失败的操作（超过 3 次应换思路）
❌ 禁止：让 Agent 扫描整个 Library/ 或 node_modules/ 目录
❌ 禁止：对话太长还不换新 chat（上下文 > 100K 时效率极低）
```

**推荐做法：**
```
✅ 先用 .cursorignore 排除 Library/、node_modules/、__pycache__/ 等
✅ 报错日志先用 grep/rg 过滤关键行再贴给 Agent
✅ 长任务用 tmux + agent worker start 后台保活，不要直接跑在 SSH 会话里
✅ 设置 ServerAliveInterval 防止 SSH 连接超时断开
✅ 每次 Agent 任务前明确给出范围（文件路径、函数名、行数）
```

### ⚠️ 已知 Bug（截至 2026-04-11）

| 版本 | 问题 | 解决方案 |
|:-----|:-----|:---------|
| Cursor 2.4.22 | SSH 下 Agent 卡在 "waiting for extensions"，git 扩展激活失败 | 降级至 2.4.21 或重装 |
| 所有版本 | Agent 超时（Agent Execution Timed Out on Remote SSH） | 重启 worker，检查网络 |
| 所有版本 | Agent 阻止 `/etc/`、`/sys/` 等系统目录操作 | 正常安全限制，不要绕过 |
| Windows | CLI 稳定性不如 Linux/macOS | 优先在 ECS (Ubuntu) 上运行 worker |

### ⚠️ 网络要求

- Worker 通过 **HTTPS/WebSocket（443 端口）出站** 连接到 Cursor 云，不需要开放入站端口
- 日本东京节点访问 `cursor.com` 延迟低，适合做 Worker
- 企业防火墙若封锁 WebSocket，worker 无法连接

---

## 五、.cursorignore 推荐配置（减少无效 Token）

在 ECS 项目根目录创建 `.cursorignore`：

```
# Unity 构建产物（巨大，Agent 不需要）
unity/ParrotDev/Library/
unity/ParrotDev/Logs/
unity/ParrotDev/Temp/
unity/ParrotDev/obj/
unity/ParrotDev/Build/

# Python 缓存
**/__pycache__/
**/*.pyc
**/.pytest_cache/

# 依赖目录
node_modules/
.venv/
venv/

# 大型二进制
*.glb
*.fbx
*.wav
*.mp4
```

---

## 六、参考链接

| 资源 | 链接 |
|:-----|:-----|
| Cursor 3.0 Changelog（官方） | https://cursor.com/changelog/3-0 |
| Cursor CLI 官方页面 | https://www.cursor.sh/en-US/cli |
| Cursor 官方 Changelog 总览 | https://cursor.com/changelog |
| Agent 最佳实践（官方博客） | https://cursor.sh/blog/agent-best-practices |
| Cloud Agent 文档 | https://cursor.com/docs/cloud-agent |
| Cursor AI Mobile（iOS） | https://apps.apple.com/us/app/cursor-ai-mobile-remote-ide/id6755931330 |
| CursorRemote 扩展（社区） | https://marketplace.visualstudio.com/items?itemName=cursor-remote.cursor-remote |
| Harvard FASRC SSH/Tunnel 教程 | https://docs.rc.fas.harvard.edu/kb/cursor-remote-development-via-ssh-and-tunnel/ |
| 社区：SSH Agent 卡住 Bug | https://forum.cursor.com/t/no-longer-able-to-use-cursor-agent-features-when-sshing/150218 |
| 社区：Agent 超时 Bug | https://forum.cursor.com/t/agent-execution-timed-out-on-remote-ssh-everything-else-works-fine/154891 |
| 社区：Token 消耗过高分析 | https://forum.cursor.com/t/hi-message-used-13k-tokens-why-is-token-usage-so-high/153344 |
| Remote Agent 详解博客 | https://www.buildfastwithai.com/blogs/cursor-remote-agents-any-device-2026 |
| 手机远程控制社区帖 | https://forum.cursor.com/t/cursor-on-your-phone-open-source-remote-control-for-agent-mode/155524 |

---

## 七、下一步行动清单

- [ ] 在 ECS 上安装 Cursor CLI：`curl https://cursor.com/install -fsS | bash`
- [ ] 配置本地 `~/.ssh/config` 添加 `castle-tokyo` 别名
- [ ] 安装 tmux 并创建 `cursor-worker` 会话
- [ ] 运行 `agent worker start` 并记录 Worker URL
- [ ] 在 Cursor Agents Window 中验证 Worker 在线
- [ ] 在项目根目录创建 `.cursorignore` 排除大型目录
- [ ] 在 ECS 上配置 ParrotCarriers 仓库（clone 或 mount）

---

*本报告由 Cursor Agent 生成，基于官方 Changelog、社区 Forum 及连接测试结果整理。*
