# ParrotCarriers 完整功能需求清单 v2 (2026-04-08)

> 综合来源: Opus 01/06/16/20/25/26 + system_core v3.1 + bus_v4.2 + scene.md + legacy.md
> 口径: 需求级（功能→模块→阶段→依赖），不含协议 schema
> 原则: 完整功能全景 + 分阶段实现优先级
> v2: 整合人工确认的 10 个决策 + Phase 1 重新定义为 Bus-first

---

## 一、产品愿景与成功标准

**一句话**: 云原生 AR 鹦鹉伴侣——在真实物理空间中飞行、停靠、语音对话、视觉识物、跨会话记忆、主动好奇。

| 成功标准 | 量化指标 | 验收阶段 |
|:---------|:---------|:---------|
| 语音实时对话 | 延迟 < 500ms | Phase 1 |
| 手势反射响应 | 反射延迟 < 100ms | Phase 2 |
| 物体识别与记忆关联 | ReID 准确率 > 85% | Phase 3 |
| 跨会话持久记忆 | 系统级支持 | Phase 3 |

---

## 二、已确认决策（来自 Q&A，防翻案）

| # | 决策 | 影响 |
|:--|:-----|:-----|
| D1 | **Phase 1 = Bus-first**：先搞好 Bus 基础设施和模块化，使各模块可独立开发 | Phase 1 交付物不是"方块旋转 demo"，而是"可工作的模块化 Bus" |
| D2 | **Nanobot 直接适配**：Phase 1 即 fork + 适配连接，不做"最小部署"过渡 | F1+F2 合并到 Phase 1 |
| D3 | **A10 非前置条件**：Phase 1 只为 DSG 留 Processor 挂载接口，不实现视觉管线 | D1~D5 从 Phase 1 移出，Phase 1 只留接口设计 |
| D4 | **Minecraft 鹦鹉模型**：使用 Minecraft 鹦鹉模型+动画+声音 | 用户负责收集美术资产（可与 Phase 1 并行） |
| D5 | **Gemini 二重身 = 远期**；Phase 1 留"宅邸聊天群"架构空间 | H2 保持 Phase 3+；Nanobot channel 设计需支持群聊语义扩展 |
| D6 | **SimpleRouter 足够**：Phase 1 只要跑通链路 + 模块化 | E1 = Phase 1；py-trees = Phase 3+ |
| D7 | **仓库策略**：笔记本先 clone/fork 改造，再部署到 Castle | 开发在笔记本，部署在服务器 |
| D8 | **2C8G 前期够用**：压力主要在 Neo4j，Phase 2 才加入 | Phase 1 无 Graphiti，内存充裕；Phase 2 加入时 Neo4j heap 硬限 |
| D9 | **DSG Sentinel = 纯远期概念**：笔记本在泉州，物理距离不实用 | D15 标注为"远期概念"，降级策略 = 直接失去 DSG 功能 |
| D10 | **WebClient Phase 2**：独立模块，Phase 1 用 LiveKit Playground 调试 | H5 保持 Phase 2 |
| D11 | **外部聊天渠道 Phase 2**：与 Bus 设计相关（渠道如何与 Scheduler 连接） | F3 保持 Phase 2 |

---

## 三、统一术语

| 术语 | 含义 | 替代/废弃名称 |
|:-----|:-----|:-------------|
| **Scheduler** | 调度器模块（统一名称） | ~~Dispatcher~~（不再使用）|
| **SimpleRouter** | Scheduler 在 Phase 1 的实现方式 | — |
| **py-trees BT** | Scheduler 在 Phase 3+ 的实现方式 | — |
| **Bus** | ParrotCarriers 三层总线（L1+L2+L3） | — |
| **Brain Agent** | 云端大脑（Gemini RealtimeModel） | ~~Brain~~（口语可用，文档写全称）|
| **Nanobot Worker** | 后台复杂任务处理器（HKUDS nanobot 改造） | ~~猫娘女仆~~（口语可用）|

---

## 四、完整功能清单（按领域分组）

### A. 基础设施与传输 (Infra)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| A1 | LiveKit Server 自托管 | Docker 部署，Room 管理 | infra/livekit | 1 | Castle ECS | M1 |
| A2 | Redis 状态总线 | Blackboard + Pub/Sub + Stream | infra/redis | 1 | Castle ECS | M1 |
| A3 | Neo4j + Graphiti 栈 | Docker 部署，知识层基础 | infra/neo4j | 2 | Castle ECS | M2 |
| A4 | WebRTC 音视频通道 | Unity ↔ LiveKit ↔ Agent | L1 Bus | 1 | A1 | M1 |
| A5 | RPC 指令通道 | 可靠双向 15KB，Agent→Unity 命令 | L1 Bus | 1 | A1 | M1 |
| A6 | DataChannel 遥测 | Lossy 1300B，Pose/Hands/Sensors 10Hz | L1 Bus | 1 | A1 | M1 |
| A7 | Docker Compose 编排 | 全栈容器化部署 | infra/ | 1 | A1,A2 | M1 |

### B. 云端大脑 (Brain Agent)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| B1 | Agent 骨架 | AgentSession + Gemini RealtimeModel | brain/agent | 1 | A1,A4 | M1 |
| B2 | ParrotSoul 人格注入 | SOUL.md → system prompt + BehaviorMode | brain/soul | 1 | B1 | M1 |
| B3 | Tool Forwarding | @function_tool → perform_rpc() 转发到 Unity | brain/tools | 1 | B1,A5 | M1 |
| B4 | fly_to Tool | 查位置 → RPC → Unity Animator | brain/tools | 1 | B3 | M1 |
| B5 | animate Tool | 触发 Unity 动画 | brain/tools | 1 | B3 | M1 |
| B6 | focus_on Tool | 注意力引导 → L2-B top-down | brain/tools | 2 | B3,D7 | M2 |
| B7 | describe_object Tool | 查询 DSG 物体详情 | brain/tools | 2 | B3,D5 | M2 |
| B8 | remember Tool | 写入 Graphiti 单分区 | brain/tools | 2 | B3,A3 | M2 |
| B9 | query_scene Tool | 查询空间+语义图 | brain/tools | 2 | B3,D5,D7 | M2 |
| B10 | event_end Tool | 事件分割 → Archive Observer | brain/tools | 3 | B3,B13 | M3 |
| B11 | dispatch_task Tool | 分发任务到 Scheduler → Nanobot | brain/tools | 1 | B3,E1 | M1 |
| B12 | Context Injector | 感知/对话/氛围线索注入 Agent 上下文 | brain/context | 2 | B1,D8 | M2 |
| B13 | Observer 系统（4个） | Perception/Conversation/Atmosphere/Archive | brain/observers | 3 | B12 | M3 |
| B14 | Gemini 降级处理 | API 超时/429 → 备用 LLM → 预录回复 | brain/fallback | 2 | B1 | M2 |

### C. Unity AR 客户端 (Client)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| C1 | LiveKit 连接 | client-sdk-unity 入房 | unity/livekit | 1 | A1 | M1 |
| C2 | AR Foundation 基础 | ARCore Plane/Anchor/Depth | unity/ar | 1 | — | M1 |
| C3 | 鹦鹉模型+基础动画 | Minecraft 鹦鹉; Animator HSM (Idle/Fly/Land) | unity/animator | 1 | C2 | M1 |
| C4 | RPC Handler | 接收 fly_to/animate 并执行 | unity/rpc | 1 | C1,A5 | M1 |
| C5 | 遥测上报 | Pose/Hands/Sensors → DataChannel | unity/telemetry | 1 | C1,A6 | M1 |
| C6 | TTS Speaker | 接收音频流播放 | unity/audio | 1 | C1,A4 | M1 |
| C7 | APP 生命周期管理 | OnApplicationPause → 通知 Agent | unity/lifecycle | 1 | C1 | M1(P0) |
| C8 | XR Hands 手势输入 | 手部追踪数据 | unity/xr_hands | 2 | C2 | M2 |
| C9 | 手势反射动作 | 张手→飞来，绕过 LLM | unity/reflex | 2 | C8,E1 | M2 |
| C10 | 鹦鹉高级动画 | Perch/Dance/微行为 | unity/animator | 2 | C3 | M2 |
| C11 | 平面行走 | AR 平面上走动/跳舞 | unity/locomotion | 2 | C2,C3 | M2 |
| C12 | 网络质量提示 | 弱网 UI 反馈 | unity/network_ui | 2 | C1 | M2(P0) |

### D. 视觉感知 DSG (Perception)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| D0 | **DSG Processor 挂载接口** | Bus 侧预留 VideoStream + DataChannel 接口，参考 SVA Processor 模式 | bus/processor | **1** | A1 | M1 |
| D1 | StabilityGate 简版 | 3 级: Lost/Moving/Stable | dsg/stability | 2 | C5 | M2 |
| D2 | L1 视觉管线简版 | SAM2 追踪 + YOLO-World 发现（无 ReID） | dsg/l1 | 2 | D1, Mecha A10 | M2 |
| D3 | DINOv2 ReID | 跨帧物体一致性 | dsg/reid | 2 | D2 | M2 |
| D4 | L2-A 空间图简版 | RustworkX: ObjectNode + SurfaceNode（无 Zone/Hand） | dsg/l2a | 2 | D2 | M2 |
| D5 | L2-A 空间查询 API | on/near/in_zone/facing | dsg/l2a | 2 | D4 | M2 |
| D6 | 节点状态机 | ACTIVE/OCCLUDED/LOST（3 种） | dsg/l2a | 2 | D4 | M2 |
| D7 | L2-B 语义图简版 | 简单新奇度评分（非完整注意力） | dsg/l2b | 3 | D4 | M2 |
| D8 | 触发器输出 | NEW/MISSING/DISPLACED → Brain | dsg/triggers | 2 | D4,D6 | M2 |
| D9 | L2-B 完整注意力 | novelty_gain + habituation_decay + top-down | dsg/l2b | 3+ | D7 | M3 |
| D10 | ExpectationChecker | EXPECTED 状态 + 预期偏离检测 | dsg/l2b | 3+ | D9 | M3 |
| D11 | 场景折叠 | fold/unfold 节点 | dsg/l2b | 3 | D7 | M2 |
| D12 | ActivityThrottle | 无变化时降低扫描频率 | dsg/l1 | 2 | D1 | M2 |
| D13 | 帧质量检查 | Laplacian 模糊检测 | dsg/l1 | 2 | D2 | M2 |
| D14 | StabilityGate 完整版 | 4 Tier + 三层缓冲 | dsg/stability | 3 | D1 | M3 |
| D15 | DSG Sentinel 哨兵 | 纯远期概念；笔记本泉州不实用 | dsg/sentinel | 远期 | A2 | M3 |
| D16 | ZoneNode / HandNode | L2-A 扩展节点类型 | dsg/l2a | 3+ | D4 | M3 |

### E. 调度器 (Scheduler)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| E1 | SimpleRouter | 简单优先级路由（if-else），Phase 1 的 Scheduler 实现 | scheduler/router | 1 | A2 | M1 |
| E2 | 三级调度 | 反射/意图/任务分层 | scheduler/router | 2 | E1 | M2 |
| E3 | Redis Blackboard 读写 | 共享状态 | scheduler/blackboard | 1 | A2 | M1 |
| E4 | py-trees 行为树 | 完整 BT: Safety/Priority/Parallel/Idle | scheduler/bt | 3+ | E2 | M3 |
| E5 | ResourceLockManager | body 通道互斥 | scheduler/locks | 2 | E1 | M2 |

### F. 后台任务处理 (Nanobot Worker)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| F1 | Nanobot fork + 适配 | fork HKUDS nanobot + parrot_bus.py channel adapter + Redis 连通 | nanobot/ | **1** | A2 | **M1** |
| F2 | 外部聊天渠道 | WeChat/Telegram Gateway 保留 | nanobot/channels | 2 | F1 | M2 |
| F3 | 任务消费+结果回写 | Stream dispatch → 执行 → Blackboard/Graphiti 回写 | nanobot/agent | 2 | F1,A2,A3 | M2 |
| F4 | Memory Consolidation | 后台上下文压缩 | nanobot/memory | 3 | F1 | M3 |
| F5 | Cron 定时任务 | 周期性维护（vocabulary_learn 等） | nanobot/cron | 3 | F1 | M3 |
| F6 | Research 能力 | 联网调研+结果写入 Graphiti | nanobot/tools | 3 | F3,A3 | M3 |

### G. 记忆与知识 (Memory)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| G1 | Graphiti 基础（1 分区） | episodic 分区，基本读写 | memory/graphiti | 2 | A3 | M2 |
| G2 | Graphiti 5 分区 | episodic/objects/personality/vocabulary/nanobot_research | memory/graphiti | 3 | G1 | M3 |
| G3 | 社区检测预加载 | Leiden Community → L2-B 语义预加载 | memory/graphiti | 3 | G2,D7 | M3 |
| G4 | Obsidian SSOT 同步 | 关键物体节点同步作为稳定锚点 | memory/obsidian | 3+ | G2 | M3 |

### H. 桥接与生态 (Bridges)

| ID | 功能 | 说明 | 实现模块 | Phase | 依赖 | 优先级 |
|:---|:-----|:-----|:---------|:------|:-----|:-------|
| H1 | MCP Sidecar | FastMCP + FastAPI 外部 API | bridge/mcp | 3 | A1,A2 | M3 |
| H2 | Gemini 二重身 | 外部分身通过 Drive 同步（纯远期愿景） | bridge/gemini | 远期 | — | M3 |
| H3 | LobeChat Bridge | 多智能体群聊 UI（宅邸聊天群候选载体） | bridge/lobechat | 3+ | A2 | M3 |
| H4 | Obsidian Bridge | MCP Client + Canvas 同步 | bridge/obsidian | 3+ | G4 | M3 |
| H5 | Web Client 调试 | LiveKit JS SDK 调试界面 | bridge/webclient | 2 | A1 | M2 |

---

## 五、阶段交付矩阵（v2 修订）

### Phase 1: Bus-first — 模块化基础设施

**里程碑**: 所有核心模块可独立连接 Bus + L1/L2 层跑通验证

**定义**: 搭好总线基础设施，确保每个模块（Brain、Scheduler、Nanobot、Unity、未来的 DSG）都能独立连接和通信。**不追求完整功能 demo，追求模块化可独立开发。**

| 交付 | 功能 ID | 说明 |
|:-----|:--------|:-----|
| **Bus 基础设施** | A1,A2,A7 | LiveKit Server + Redis + Docker Compose |
| **L1 验证: Brain ↔ Unity** | A4,A5,A6 | Agent 入房 + Unity 入房 + RPC 通 + DataChannel 通 |
| **Brain Agent 骨架** | B1,B2,B3,B4,B5 | Gemini 语音 + Tool Forwarding + fly_to/animate |
| **Scheduler 骨架** | E1,E3 | SimpleRouter + Redis Blackboard |
| **dispatch_task 链路** | B11 | Brain → Scheduler → Redis 分发验证 |
| **Nanobot 适配** | F1 | fork + parrot_bus.py + Redis Stream 消费验证 |
| **DSG 挂载接口** | D0 | 预留 Processor 挂载口（参考 SVA 模式），不实现视觉 |
| **Unity 最小验证** | C1,C4 | 入房 + RPC Handler（模型/动画可后补） |
| **宅邸聊天群架构空间** | — | Nanobot channel 设计支持群聊语义扩展 |

**Phase 1 不做**:
- DSG 视觉管线（D1~D5, 等 A10）
- Graphiti/Neo4j（A3, Phase 2）
- 复杂 Unity 功能（C2~C7 除 C1/C4 外可并行补）
- 外部聊天渠道（F2, Phase 2）
- Web Client（H5, Phase 2）

### Phase 2: 功能叠加 — 反射+视觉+记忆

**里程碑**: 手张开→鹦鹉飞来 + 能识别并记住物体

| 交付 | 功能 ID | 模块 |
|:-----|:--------|:-----|
| Neo4j + Graphiti 部署 | A3 | infra |
| DSG 视觉管线（需 A10） | D1~D6,D8,D12,D13 | dsg |
| 更多 Brain Tools | B6~B9,B12,B14 | brain |
| XR Hands + 手势反射 | C8,C9 | unity |
| Unity 完整功能 | C2,C3,C5~C7,C10~C12 | unity |
| 三级调度 + 资源锁 | E2,E5 | scheduler |
| Nanobot 外部渠道 + 任务消费 | F2,F3 | nanobot |
| Graphiti 基础 | G1 | memory |
| Web Client 调试 | H5 | bridge |

### Phase 3: 视觉与记忆完整版

**里程碑**: "飞到奶奶的杯子上" → 正确定位 + 跨会话记忆

| 交付 | 功能 ID | 模块 |
|:-----|:--------|:-----|
| L2-B 语义图 + 场景折叠 | D7,D11 | dsg |
| event_end + 4 Observer | B10,B13 | brain |
| Graphiti 5 分区 + 社区预加载 | G2,G3 | memory |
| Nanobot 完整能力 | F4,F5,F6 | nanobot |

### Phase 3+: 远期扩展

| 交付 | 功能 ID |
|:-----|:--------|
| 完整注意力 + ExpectationChecker | D9,D10 |
| StabilityGate 完整版 | D14 |
| ZoneNode/HandNode | D16 |
| py-trees 行为树 | E4 |
| Obsidian SSOT + Bridge | G4,H4 |
| MCP Sidecar | H1 |
| LobeChat 宅邸聊天群 | H3 |
| DSG Sentinel（远期概念） | D15 |
| Gemini 二重身（远期概念） | H2 |

---

## 六、上游仓库策略

### 需要 fork（改造源码）

| 仓库 | 用途 | 引入方式 |
|:-----|:-----|:---------|
| **HKUDS/nanobot** | 后台任务处理器，需加 parrot_bus.py | fork 到用户 GitHub → clone 到笔记本改造 → 部署到 Castle |

### pip/package 依赖（不改源码）

| 仓库 | 用途 | 引入方式 |
|:-----|:-----|:---------|
| **livekit/agents** | Brain Agent 框架 | `pip install livekit-agents` |
| **getzep/graphiti** | 知识图谱（Phase 2） | `pip install graphiti-core` |
| **livekit/client-sdk-unity** | Unity SDK | Unity Package Manager |

### 参考模板（clone 来读，自己写代码）

| 仓库 | 参考什么 | Phase |
|:-----|:---------|:------|
| **livekit-examples/agent-starter-python** | Brain Agent 写法 | 1 |
| **livekit-examples/agents-example-unity** | Unity 接 LiveKit 写法 | 1 |
| **livekit-examples/python-agents-examples** | 各种 Agent 示例 | 1 |
| **GetStream/Vision-Agents (SVA)** | DSG Processor 挂载模式设计 | **1**（读 skill 了解架构设计 Processor 接口） |

### SVA 注意事项

Phase 1 不用 SVA 代码，但设计 DSG Processor 挂载接口（D0）时**必须参考 SVA 的 Processor 模式**。否则 Phase 2 实际挂载 DSG 时可能发现接口不兼容需要重构。

做法：Phase 1 设计挂载接口前，读 `sva-vision-agents` skill 了解架构，确保 Bus 预留的 VideoStream 订阅 + DataChannel 发布接口与 Processor 模式兼容。

---

## 七、关键依赖链（v2 修订）

```
Phase 1 关键路径（Bus-first）:
笔记本开发环境就绪
  → fork nanobot + clone 参考仓库
    → 本地写 Bus 框架 (模块注册/心跳/挂载协议)
    → 本地写 Brain Agent 骨架
    → 本地写 Scheduler 骨架
    → 本地写 Nanobot parrot_bus.py adapter
      → 本地 Redis 验证模块间通信
Castle 部署就绪（可与开发并行）
  → Docker Compose (LiveKit + Redis)
    → 推送代码到 Castle
      → L1 验证: Brain ↔ Unity (入房 + RPC)
      → L2 验证: Brain ↔ Scheduler ↔ Nanobot (Redis)

Phase 2 关键路径:
Phase 1 Bus 跑通
  → 各模块独立开发（可并行）：
    ├── Unity 完整功能 (AR + 动画 + XR Hands)
    ├── DSG Worker (需 A10)
    ├── Nanobot 外部渠道 + 任务消费
    ├── Graphiti 部署 + 记忆 Tools
    └── Web Client 调试
```

---

## 八、用户准备清单（你需要做的事）

### Phase 1 前必须准备

| # | 准备项 | 状态 | 备注 |
|:--|:-------|:-----|:-----|
| P1 | GitHub SSH Key | **已完成** | — |
| P2 | GitHub 账号 | **已确认**: `GOSLOParrot` | fork 路径: `GOSLOParrot/nanobot` |
| P3 | Python 环境 | **已就绪**: Cursor venv | 需确认版本 ≥ 3.11 |
| P4 | 笔记本 Redis | **已就绪**: Docker Desktop | 本地开发用 |
| P5 | Castle ECS 访问 | **调查中** | 用户并行推进 |
| P6 | Gemini API Key | **已就绪**: .env 中有 2 个 key | GOOGLE_API_KEY / GOOGLE_API_KEY_2 |
| P7 | Nanobot LLM Key | **待补充** | 用户计划用 Google API，后续按文档补充 |

### 可并行准备（不阻塞 Phase 1）

| # | 准备项 | 说明 |
|:--|:-------|:-----|
| P8 | **Minecraft 鹦鹉资产收集** | 模型+动画+声音；Unity 格式 |
| P9 | **Unity 开发环境** | Unity 2022 LTS + AR Foundation + Android Build Support |
| P10 | **LiveKit 域名/TLS（Castle 部署时）** | 可选：域名+证书；或先用 IP+开发模式 |

---

## 九、完整网络拓扑参考

**已在 `bus_v4.md` v4.2 中完整定义**，本文不重复。

v4.2 拓扑是完整功能拓扑（含所有远期模块）。Phase 1 实际使用的是它的子集：
- L1: LiveKit Room (Brain + Unity + Scheduler)
- L2: Redis (Brain + Scheduler + Nanobot)
- L3: 不启用（Phase 2 才加 Graphiti）

---

## 十、场景压测映射（9 场景 → 功能覆盖）

| 场景 | 核心测试 | 涉及功能 ID | 暴露的 P0 缺口 |
|:-----|:---------|:------------|:---------------|
| 深夜桌前工作 | 长时间稳定运行 | D12,B2,E1 | — |
| 边走边说话 | 场景切换+移动中对话 | D1,D4,B1,C5 | — |
| 展示新物品 | 新物体识别+记忆写入 | D2,D3,B6,B8,G1 | — |
| 手机来电 | 系统级中断恢复 | C7,B1 | **P0: APP 生命周期** |
| 两手都忙 | 手势歧义 | C8,C9,E1 | — |
| 目标物体被拿走 | 目标失效处理 | D6,B4,B9 | **P0: fly_to 容错** |
| 弱网 WiFi | 网络降级 | C12,B14 | **P0: 网络质量监控** |
| Gemini 超时 | 云端故障 | B14 | — |
| 多人在场 | 非预期人员 | D2,B1 | — |

---

## 十一、新概念记录

### 宅邸聊天群（Phase 3+ 候选方向）

多角色在同一聊天空间协作的概念：
- 参与者可能包括：Nanobot（猫娘女仆）、GOSLO 状态机器人、大姐外部分身、用户
- 载体候选：微信群、Telegram 群、LobeChat、自建聊天室
- Phase 1 架构影响：Nanobot channel 设计需支持群聊语义（不仅 1v1 私聊）
- 候选实现载体：H3 LobeChat Bridge 或 Nanobot 自身的群聊 channel

不影响 Phase 1 实现，但在设计 Nanobot channel adapter 时需预留群消息路由能力。
