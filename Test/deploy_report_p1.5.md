# P1.5 部署与连通性测试报告 (2026-04-13)

## 1. 测试目标
验证 ParrotCarriers V1 骨架在阿里云 ECS（Castle）部署后的端到端连通性，包括：
- 客户端（Unity Editor / Python 模拟脚本）通过公网直连云端 LiveKit 的稳定性。
- Brain Agent 的语音交互（听与说）。
- 基于 LiveKit 的 RPC 动作指令下发（`flyTo` / `animate`）。
- nanobot 后台任务链路与返回（查询字典并播报结果）。

## 2. 测试环境
- **服务端**: 阿里云 ECS (东京节点 `8.216.45.45`)，运行 `LiveKit Server`、`Redis`、`parrot-brain` 进程及 `nanobot` 后台进程。
- **客户端**: 
  - 本机 Unity Editor（身份: `unity-dev`，负责画面与 RPC 接收）。
  - 本机命令行脚本 `sim_unity_client.py`（身份: `voice-user`，负责麦克风输入与日志观察）。
- **网络**: 国内直连东京（**注：关闭代理以避免 UDP 丢包**）。

## 3. 关键测试用例与结果

| 测试项 | 预期表现 | 结果 | 耗时/备注 |
|:---|:---|:---|:---|
| **双端独立进房** | Unity 与 Python 脚本凭借统一 Token 成功进入同一房间，且身份不冲突。 | ✅ 通过 | 脚本使用 `--identity voice-user` 隔离。 |
| **基础语音交互** | 对着麦克风说话，云端 Gemini Agent 能够听懂并使用 Parrot 语音流回复。 | ✅ 通过 | 关代理后公网直连，响应延迟低至毫秒级。 |
| **动作 RPC 靶向** | 语音触发位移或动作（如“The fall”），Agent 精准查找到 `unity-dev` 并下发 RPC。 | ✅ 通过 | Unity 端成功注册并收到 `flyTo`/`animate` 指令。 |
| **Nanobot 后台链路** | 触发查询任务后，Scheduler 转发至 Redis，猫娘处理完毕，鹦鹉播报结果。 | ✅ 通过 | 鹦鹉播报："My research is done!" |

## 4. 阻碍与修复记录
- **阻碍 1: Token 校验失败 (401 Unauthorized)**
  - **原因**: 部署脚本采用的 `livekit.yaml` 默认密码为 `secret`，而本地 `.env` 使用了强密码，导致 Token 验签失败。
  - **修复**: 通过 SSH 直接修改云端 `livekit.yaml` 对齐本地密码，重启 LiveKit 服务，问题解决。两端必须保证 `LIVEKIT_API_SECRET` 一致。
- **阻碍 2: 语音响应延迟巨大 (3~5秒)**
  - **原因**: 本机开启了 VPN 代理，接管了全局流量，导致本该直连东京的 UDP 媒体包绕道或被迫降级为 TCP，造成严重拥堵和丢包。
  - **修复**: 关闭 VPN 或在代理软件中为 ECS IP 添加直连（DIRECT）白名单。修复后延迟恢复至顺畅对话水平。

## 5. 结论
P1.5 后端骨架在生产环境（ECS）部署验收圆满成功，云端基建已稳固。可以正式进入 P2 阶段（ARFoundation 动画接入与 Graphiti 记忆共享）。
