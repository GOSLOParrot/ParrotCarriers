# Phase 1 手测入口（`Test` 端口）

本目录是 **本地手测/笔记端口**（思路类似 `FilePort/`）：与 pytest、`src/` 主代码分开，以后整包删掉或迁移即可。业务脚本仍在 `src/scripts/`，此处只放 **索引 + 步骤 + 结果**。

在 Cursor 里若不想常驻上下文，可把仓库根 `Test/` 加进 `.cursorignore`；需要时用 `@Test` 引用本目录。

| 文档 | 用途 |
|:-----|:-----|
| [../../docs/P1_VERIFICATION_GUIDE.md](../../docs/P1_VERIFICATION_GUIDE.md) | 完整目标、数据流、架构偏差 |
| [RESULTS.md](./RESULTS.md) | 实测记录（勿写密钥） |

---

## A. Python `sim_unity_client` 链路（笔记本）

**终端 1**

```text
.venv\Scripts\python.exe src/scripts/run_dev.py
.venv\Scripts\python.exe -m parrot.brain.agent dev
```

**终端 2**

```text
.venv\Scripts\python.exe src/scripts/sim_unity_client.py --mic --full
```

### `src/scripts` 索引（P1 要不要用）

| 脚本 | 在 P1 手测里 | 说明 |
|:-----|:-------------|:-----|
| `run_dev.py` | **必用** | 起 Docker 开发栈并生成 token |
| `sim_unity_client.py` | **必用** | `--mic --full` 覆盖语音 + Scheduler + Nanobot stub |
| `generate_token.py` | 可选 | 改 identity/TTL、单独出 token |
| `start_scheduler.py` | 一般不用 | `--full` 已带 Scheduler |
| `start_brain.py` | 可选 | 等价 `python -m parrot.brain.agent dev` |
| `start_nanobot_worker.py` | **非 P1 默认** | 真 Nanobot；stub 路径不必开 |

**Brain**：`python -m parrot.brain.agent dev`（与 `start_brain.py` 二选一）。

---

## B. Unity Editor（`unity/ParrotDev`）链路

**当前工程能力**：`RoomManager` 会 **连接房间、订阅 Agent 远程音频**；`ParrotRpcHandler` 会注册 **flyTo / animate**。Editor **未**内置麦克风发布时，可用 **下面「B2双开」** 让 Python 进程只负责上麦，RPC 仍落到 Unity。

**不要**两个 **`unity*`** 身份同时进房（例如默认 `unity-sim` + `unity-dev`）：Brain 的 RPC 会找第一个 `unity*` 远端，目标不确定。若要与 Editor 同场说话，请用 **B2**（`--identity voice-user`，非 `unity` 前缀）。

### B2. Unity Play + Python 只上麦（语音 → RPC进 Unity）

1. 先 **Unity Play**（`unity-dev` 已连上、Agent 已在房）。  
2. 再开终端（Brain、Docker 保持运行）：

```text
.venv\Scripts\python.exe src/scripts/sim_unity_client.py --identity voice-user --mic --no-agent-playback
```

（需要 Scheduler/Nanobot 时再加 `--full`。）  
这样对 Gemini 说话走 **`voice-user` 的麦克风流**，`flyTo` / `animate` 的 RPC 仍发往 **唯一的 `unity-*`（Editor）**；`--no-agent-playback` 避免 Python 再播一遍 TTS（声音以 Unity 为准）。

1. **准备后端**（与 A 相同）：Docker/LiveKit + Redis已起；终端里启动 `python -m parrot.brain.agent dev`。
2. **生成 token**：在仓库根执行   ` .venv\Scripts\python.exe src/scripts/generate_token.py`使用 **`unity-` 前缀** 的 identity（如默认 `unity-dev`），房间 `parrot-main`，与 [`_rpc_bridge.py`](../../src/parrot/brain/tools/_rpc_bridge.py) 的 `UNITY_IDENTITY_PREFIX = "unity"` 一致。
3. **Unity Hub**：打开 `unity/ParrotDev`，建议 **2022.3 LTS**；打开场景 `Assets/Scenes/Dev.unity`。
4. **填连接信息**：选中 `LiveKitManager` → `RoomManager`：`Server URL` = `ws://localhost:7880`，`Join Token` = 刚生成的 JWT（勿把长期 token 提交进 Git；场景里若已有旧 token，过期后重贴）。
5. **Play**：Console 期望类似：
   - `[RoomManager] Connecting to ws://localhost:7880 ...`
   - `[RoomManager] Connected — room='parrot-main' identity='unity-dev'`
   - `[RoomManager] + agent-...`（或类似 Agent 参与者）
   - `[ParrotRPC] Registered: flyTo, animate`
   - 有 Agent 音频轨时：`[RoomManager] Audio track from ...`
6. **听感**：Agent 启动后会 `generate_reply` 打招呼，应能从扬声器听到简短欢迎（本机音量/WebRTC 正常的前提下）。
7. **RPC / 动画**：仅 Editor、无麦时不会有语音指令；用 **B2** 或 **A 节纯 sim** 触发工具。Editor 侧 **Handler 已注册** + B2 下方块有反应，即 **P1 前端指令连通**。

更详细的搭场景步骤见 [`unity/ParrotDev/README.md`](../../unity/ParrotDev/README.md)。

---

## pytest自动化测试仍在仓库根 [`tests/`](../../tests/)（如 `tests/integration/`），与本 `Test/` 目录无关。
