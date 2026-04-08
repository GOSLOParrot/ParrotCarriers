# 当前进度与下一步

> 最后更新: 2026-04-08 (Unity 客户端 C# 代码 + Castle 部署配置 + 首次提交准备)

---

## 当前阶段: Phase 1 实施 — Unity 客户端代码就绪，待 Editor 验证

### 当前真实状态

**L2 层三条核心链路已真实跑通（有集成测试证明）：**

1. **Path A 挂载**: Brain Agent + Scheduler 通过阶段式 pipeline 挂载到 Bus（L1+L2）
2. **Path B 挂载**: Nanobot Consumer 作为 L2-only Worker 挂载到 Bus
3. **dispatch → consume → result**: Brain dispatch_task → Scheduler 路由 → Redis Stream → Nanobot 消费 → 结果发布

**L1 层 Brain Agent 真实入房验证通过（Dev 模式日志证明）：**

4. **Console 模式**: Bus mount 全流水线 → Gemini Realtime API 连接 → READY
5. **Dev 模式**: Worker 注册到 LiveKit Server → 参与者加入触发 job → Bus mount → Gemini 连接 → 音频 IO 建立 → READY

**Unity 客户端 C# 代码已创建（待 Editor 验证）：**

6. **RoomManager**: LiveKit Room 连接 + 远端音频自动播放 + 单例
7. **ParrotRpcHandler**: 注册 flyTo / animate RPC → 转发给 ParrotController
8. **ParrotController**: 方块移动 + 颜色反馈（Phase 1 dev mode，无鹦鹉模型）
9. **UnityMainThread**: 线程调度器，LiveKit 回调 → Unity 主线程
10. **generate_token.py**: 生成 Unity join token（identity=unity-dev, room=parrot-main）

**Castle 部署配置已创建：**

11. **docker-compose.yml**: Redis 绑定 127.0.0.1（宿主机可达+不暴露公网）
12. **.env.castle**: Castle 环境变量模板
13. **deploy-castle.sh**: rsync + pip + docker compose + 健康检查

### 验证矩阵进度

| # | 链路 | 状态 | 验证方式 |
|:--|:-----|:-----|:---------|
| V1 | Brain ↔ Unity (语音) | **C# 代码就绪** | RoomManager 音频订阅已实现；待 Unity Editor Play |
| V2 | Brain → Unity (指令) | **C# 代码就绪** | ParrotRpcHandler flyTo/animate 已注册；待 Editor 连通验证 |
| V3 | Brain → Scheduler → Nanobot | **✅ 已验证** | 集成测试 2/2 通过 |
| V4 | 模块注册与心跳 | **✅ 已验证** | Console + Dev 模式日志确认 register + heartbeat |
| V5 | Nanobot → Bus (结果回写) | **✅ 已验证** | 集成测试 dispatch_to_nanobot 通过 |

### 已完成

- [x] 需求清单 v2 + 模块划分 + 目录结构
- [x] Bus 骨架代码（manifest/registry/heartbeat/mounting/processor_hook）
- [x] 审计通过 → ModuleManifest 精简 → mounting 重构
- [x] Brain Agent 入口 + Scheduler 服务 + Nanobot Consumer
- [x] dispatch_task Tool：Brain → Scheduler → Nanobot 完整链路
- [x] 集成测试 2/2 + 单元测试 5/5 + ruff lint 全通过
- [x] Brain Agent 接入 Gemini RealtimeModel（AgentServer + AgentSession）
- [x] ParrotAssistant(Agent) 人格 + function tools (fly_to, animate, dispatch_task)
- [x] RPC 桥接 (`_rpc_bridge.py`): Unity RPC 转发
- [x] docker-compose.dev.yml LiveKit Server + Redis 开发栈
- [x] Console 模式验证: Bus mount → Gemini 连接 → READY ✅
- [x] Dev 模式验证: Worker 注册 → 参与者触发 → 完整入房 → READY ✅
- [x] **Unity C# 客户端**: RoomManager + ParrotRpcHandler + ParrotController + UnityMainThread
- [x] **Token 生成脚本**: `src/scripts/generate_token.py`
- [x] **Castle 部署配置**: docker-compose.yml + .env.castle + deploy-castle.sh
- [x] **项目 README.md + Unity README.md**
- [x] **.gitignore 更新**: ParrotDev + ParrotAR 通配

### 当前不做

- [ ] 不冻结协议字段（等路径 A/B 真实跑过多次后再收敛 Mount Protocol v1）
- [ ] 不扩展 ModuleManifest 字段（等真实消费代码出现）
- [ ] 不加 VAD/Silero（Gemini RealtimeModel 自带 turn detection，需要时再加）
- [ ] 不加 AR 组件（Phase 1 用 3D Cube 代替鹦鹉模型）
- [ ] 不做 DSG / Graphiti / 外部渠道（Phase 2）

### 下一步

**Phase 1 剩余验证项（V1/V2 人工操作）：**
- [ ] 在 Unity Editor 中创建 ParrotDev 项目，安装 LiveKit SDK
- [ ] 搭建 Dev 场景（LiveKitManager + Parrot Cube）
- [ ] 生成 token → 粘贴到 Inspector → Play → 验证 V1/V2 连通
- [ ] 真实语音对话验证（Brain Agent 对话 + flyTo/animate 执行）

**Castle 部署：**
- [ ] SSH 到 Castle → 确认 Docker 就绪
- [ ] 运行 `deploy-castle.sh` 或手动部署
- [ ] 从笔记本/手机 Unity 客户端连接 Castle 验证

**首次 Git 提交：**
- [ ] `git init` + 首次 commit（ParrotCarriers 仓库）
- [ ] nanobot fork 仓库独立提交

### 关于 Tool 阻塞（已确认）

- `fly_to` / `animate`: 等待 Unity RPC 响应（<10s），不阻塞 Agent 事件循环
- `dispatch_task`: 火即忘（publish → return），不等 Nanobot 结果

### 已确认事实（防翻案）

- Phase 1 = Bus-first（模块化基础设施，非 demo）
- Nanobot 直接适配（fork + parrot_bus.py），不做"最小部署"过渡
- A10 非前置条件：Phase 1 只为 DSG 留 Processor 挂载接口
- 调度器统一叫 Scheduler；查旧稿时注意历史名称 Dispatcher
- 双仓库架构：ParrotCarriers（主）+ nanobot（fork）
- 2C8G 前期够用，压力在 Phase 2 的 Neo4j
- 协议由代码驱动，不在纸上空转
- ModuleManifest = 轻量挂载声明，不是 God Contract
- Brain Agent 使用 `agents.cli.run_app(server)` 作为入口点
- Agent dispatch 需显式调用 `agent_dispatch.create_dispatch()`
- Console 模式可以在无 LiveKit Server 时测试
- Unity 客户端 identity 必须以 "unity" 前缀开头（_rpc_bridge.py 检测）
- LiveKit Unity SDK v1.3.5 通过 UPM git URL 安装

---

## 关键上下文

- **项目**: `ParrotCarriers` — GOSLOParrot 通信总线子项目
- **GitHub**: `GOSLOParrot/ParrotCarriers` + `GOSLOParrot/nanobot`
- **服务器**: 东京 `ecs.g9i.large`（常驻）+ 东京 `A10`（按需），同 VPC
- **全局索引**: `.cursor/memory/INDEX.md`
- **需求清单**: `.cursor/memory/requirements.md` v2
- **模块划分**: `.cursor/memory/architecture/module_division.md`
- **总线架构**: `.cursor/memory/architecture/bus_v4.md` v4.2
- **审计报告**: `docs/report/2026-04-08_p1_bus_architecture_manifest_trace_report.md`
- **设计护栏**: `.cursor/memory/BigIssue.md`

### 运行命令速查

```bash
# 开发栈
docker compose -f infra/docker-compose.dev.yml up -d   # Redis + LiveKit Server

# Brain Agent
python -m parrot.brain.agent console                    # 终端模式（无需 LiveKit）
python -m parrot.brain.agent dev                        # 开发模式（需 LiveKit）

# Scheduler
python src/scripts/start_scheduler.py

# Nanobot Worker（真实任务处理）
pip install -e ../nanobot[parrot]                       # 安装 nanobot fork
python src/scripts/start_nanobot_worker.py              # 启动 nanobot gateway

# Unity Token
python src/scripts/generate_token.py                    # 生成 Unity join token
python src/scripts/generate_token.py --identity unity-phone  # 手机用

# 测试
pytest tests/test_bus/ -v                               # 单元测试
pytest tests/integration/ -v                            # 集成测试（需 Redis）

# Castle 部署
bash infra/deploy-castle.sh <castle-ip> [ssh-key]
```
