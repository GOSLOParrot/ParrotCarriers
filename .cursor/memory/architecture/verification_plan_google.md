# Google 生态接入与回流联调计划

本计划规定了如何从零开始，安全、稳定地验证 `Nanobot` 到 `Google Workspace` (Gmail, Calendar) 的接入，并确保任务结果能正确回流给 `ParrotCarriers` 的 `Brain Agent` 与 `Scheduler`。

---

## 阶段 1：Mock 验证 (不真实连接 Google)

在绑定真实的个人 Google 账号之前，必须确认 `Trigger -> Scheduler -> Nanobot -> Brain` 的闭环没有逻辑阻塞或崩溃。

### 1. 启动服务
- 启动 `Redis` 基础设施 (如 `docker-compose.dev.yml`)
- 启动 **Mock 版 Nanobot Worker**:
  ```bash
  python src/scripts/start_nanobot_worker.py --stub
  ```
- 启动 `Brain Agent` (Dev 或 Console 模式):
  ```bash
  python -m parrot.brain.agent console
  ```

### 2. 注入 Mock 结果
在开一个新终端，手动向 `parrot.nanobot.results` 发送符合约定的 Mock JSON 消息，模拟 Nanobot 完成了日历查询：

```bash
redis-cli publish parrot.nanobot.results '{"task_id": "test_cal_1", "type": "calendar_fetch", "status": "completed", "result": "{\"events\": [{\"id\": \"e1\", \"title\": \"Mock Event\", \"start_time\": \"2026-04-16T14:00:00Z\", \"objects\": [\"coffee\"]}]}"}'
```

### 3. 验收标准
- `CalendarTrigger` 或 `MessageNotificationTrigger` 正确解析出 `Mock Event`。
- `Brain Agent` (终端输出) 打印出 "A background task just completed..." 或类似的通知语句。
- `Graphiti` (如果已启动) 中记录了这段记忆（可选，主要看 Trigger 层的 L2-B graph 更新）。

---

## 阶段 2：真实 MCP 授权联调 (连接 Google)

一旦内部管线通了，接下来就是引入真正的 `@aaronsb/google-workspace-mcp`。

### 1. 配置准备
确保 `nanobot/config/parrot_config.json` 或自动生成的 `~/.nanobot-parrot/config.json` 中，包含 `google-workspace` 这一项：
```json
"mcpServers": {
  "google-workspace": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@aaronsb/google-workspace-mcp"]
  }
}
```

### 2. 启动全功能 Worker
```bash
python src/scripts/start_nanobot_worker.py
```
*此时，Nanobot 会拉起 MCP Server。*

### 3. 进行 OAuth 授权
Nanobot 默认情况下不会自己跳转浏览器。
- 你可能需要使用 Nanobot 聊天界面 (比如 Telegram) 发送一条指令：“调用 manage_accounts 工具进行 authenticate”。
- MCP server 应当会在终端输出一行授权 URL 让你在浏览器里点开，完成 Google 登录授权。
- 确认授权成功后，MCP server 本地会保存 Token。

### 4. 触发真实任务
- 重启 `Brain Agent` 触发 `on_startup`，或者等待 15 分钟让 `CalendarTrigger` 自然触发 `on_tick`。
- 观察 Nanobot 的控制台输出，确认它接收到了 `calendar_fetch` 任务，并选择了 `manage_calendar` 工具。
- 观察 `Brain Agent` 控制台，等待真实 Google Calendar 的事件摘要被播报出来。

### 5. 验收标准
- 不产生任何 `[Error] missing credentials`。
- 获取到了你真实账号当天的日历事件/Gmail 新邮件。
- 日程/邮件中的对象（如“买花”、“准备电脑”）进入了 L2-B 记忆图，被 GOSLO 妹妹用 TTS 念出来。

---

## 阶段 3：Drive Bridge 实验 (远期)

- 当阶段 2 稳定后，在你的 Google Drive 中手动创建 `ParrotWorkspace` 目录结构。
- 手机端打开 `Gemini App`，尝试提问：“查找我的 Google Drive 中 ParrotWorkspace/state/context.md 的内容，告诉我有什么事。”
- 验证大姐（Gemini App）能否读懂格式，并完成“二重身同步”。
