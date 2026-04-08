# ParrotDev — Unity 开发客户端

Phase 1 开发用 3D 项目，用方块代替鹦鹉模型。
连接 LiveKit Room，接收 Brain Agent 的 RPC 指令（flyTo / animate）。

## 快速搭建

### 1. 创建 Unity 项目

1. 打开 Unity Hub → New Project → **3D (Built-in Render Pipeline)**
2. 项目名 `ParrotDev`，路径选 `ParrotCarriers/unity/`
3. Unity 版本: **2022.3 LTS**（推荐 2022.3.50f1+）

> Unity 会在 `unity/ParrotDev/` 下生成 Assets/、Packages/、ProjectSettings/ 等。
> 我们已经预创建了 `Assets/Scripts/` 目录和 4 个 C# 脚本。

### 2. 安装 LiveKit Unity SDK

1. Unity Editor → **Window → Package Manager**
2. 左上角 **+** → **Add package from git URL...**
3. 输入:
   ```
   https://github.com/livekit/client-sdk-unity.git
   ```
4. 等待导入完成（会下载 native FFI 二进制，约 50MB）

> SDK 版本: v1.3.5 (2026-04-03)
> 平台支持: Windows / macOS / Linux / iOS / Android

### 3. 搭建场景

1. 创建空场景 `Assets/Scenes/Dev.unity`
2. 创建空 GameObject，命名 `LiveKitManager`:
   - 添加 `RoomManager` 组件
   - Inspector 中填入 Server URL: `ws://localhost:7880`
   - Token: 用 `python src/scripts/generate_token.py` 生成
3. 创建一个 **Cube**，命名 `Parrot`:
   - 添加 `ParrotRpcHandler` 组件（自动附带 `ParrotController`）
   - 调整 Cube 位置到原点
4. `UnityMainThread` 会自动初始化（`RuntimeInitializeOnLoadMethod`）

### 4. 生成 Join Token

在 ParrotCarriers 根目录执行:

```bash
python src/scripts/generate_token.py
```

默认生成 identity 为 `unity-dev` 的 token，连接 `parrot-main` 房间。
将输出的 JWT token 粘贴到 RoomManager Inspector 的 `Join Token` 字段。

### 5. 启动后端 + 验证

```bash
# 终端 1: 启动 Redis + LiveKit Server
docker compose -f infra/docker-compose.dev.yml up -d

# 终端 2: 启动 Brain Agent (dev 模式)
python -m parrot.brain.agent dev

# 终端 3 (可选): 启动 Nanobot Worker
python src/scripts/start_nanobot_worker.py
```

然后在 Unity Editor 中按 **Play**。

**预期验证链路:**

| 步骤 | 预期日志 |
|:-----|:---------|
| Unity Play | `[RoomManager] Connected — room='parrot-main' identity='unity-dev'` |
| RPC 注册 | `[ParrotRPC] Registered: flyTo, animate` |
| Brain 检测到 Unity | `Brain Agent session active in room 'parrot-main'` |
| Brain 调用 flyTo | `[ParrotRPC] flyTo ← brain: {"x":1,"y":2,"z":0}` → Cube 移动 |
| Brain 调用 animate | `[ParrotRPC] animate ← brain: {"animation":"dance"}` → Cube 变色 |

### 6. 语音对话测试

Brain Agent 使用 Gemini RealtimeModel，语音通过 LiveKit Room 传输。
Unity Editor 中:
- 远端音频自动播放（RoomManager 的 `OnTrackSubscribed` 处理）
- 如需发送麦克风，后续添加 `MicrophoneSource`（Phase 1 可选）

## 脚本说明

| 脚本 | 职责 |
|:-----|:-----|
| `Core/UnityMainThread.cs` | 主线程调度器 — LiveKit 回调 → Unity 主线程 |
| `LiveKit/RoomManager.cs` | Room 连接 + 音频订阅 + 单例 |
| `RPC/ParrotRpcHandler.cs` | 注册 flyTo/animate RPC → 转发给 ParrotController |
| `Parrot/ParrotController.cs` | 移动 + 动画控制（Phase 1 用颜色反馈代替模型动画） |

## 目录结构

```
Assets/
├── Scripts/
│   ├── Core/
│   │   └── UnityMainThread.cs
│   ├── LiveKit/
│   │   └── RoomManager.cs
│   ├── RPC/
│   │   └── ParrotRpcHandler.cs
│   └── Parrot/
│       └── ParrotController.cs
├── Scenes/
│   └── Dev.unity          ← 手动创建
├── Models/                ← Phase 2: Minecraft 鹦鹉模型
├── Animations/            ← Phase 2: 鹦鹉动画
└── Audio/                 ← Phase 2: 鹦鹉声音

Packages/
  └── (LiveKit SDK via UPM git URL)
```

## 已知限制 (Phase 1)

- 无 AR 组件（纯 3D 场景）
- Cube 代替鹦鹉模型，颜色变化代替动画
- 无麦克风发送（只接收 Brain Agent 音频）
- Token 手动粘贴（生产环境需要 token server）
