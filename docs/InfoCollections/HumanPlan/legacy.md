# 项目架构与决策总览 (Project Architecture and Decision Overview)

> **前身**: `legacy.md`
> **更新日期**: 2026-04-08
> **用途**: 项目的架构摘要文档，概括 Opus 调研精华，并保留当前仍有效的高层架构、部署方向与关键技术决策。
> **详细设计**: 见 `docs/InfoCollections/Opus/` 下的详细文档。
> **当前阶段状态**: 以 `.cursor/memory/active_context.md` 为准；本文不再承担阶段进度真相源角色。

---

## 一、项目愿景

**项目名称**: **GOSLOParrot**
**总线代号**: **ParrotCarriers** (RFC 1149: IPoAC, but powered by parrots)

**核心价值**:
构建一个云原生的 AR 鹦鹉伴侣，它不仅仅是屏幕上的像素，而是拥有：
*   **具身交互**: 通过 AR 在真实物理空间中飞行、停靠。
*   **实时智能**: 毫秒级的手势反射与亚秒级的语音对话。
*   **持久记忆**: 记住你的物品、故事和偏好，跨越会话存在。
*   **主动灵魂**: 拥有好奇心，主动探索环境，而非被动等待指令。

---

## 二、核心架构 (The Big Picture)

系统采用 **四层仿生架构**，模拟生物神经系统：

### 2.1 物理拓扑
```mermaid
graph TD
    Client[Unity Client (Android)] <-->|WebRTC/RPC| Bus[LiveKit Bus (Tokyo)]
    Bus <--> Backend[Python Brain (Tokyo ecs.g9i.large)]
    Backend <-->|Internal| Workers[Perception/Memory (Tokyo A10)]
```

### 2.2 逻辑分层

| 层级 | 脑区类比 | 职责 | 关键技术 |
|:-----|:---------|:-----|:---------|
| **L1 视网膜** | 感觉皮层 | 原始信号过滤、稳定性门控、物体追踪 | SAM2, DINOv2, ARCore |
| **L2-A 背侧通路** | 顶叶 (Where) | 空间拓扑、位置关系、运动追踪 | RustworkX 空间图 |
| **L2-B 腹侧通路** | 颞叶 (What) | 语义联想、注意力分配、身份识别 | RustworkX 语义图, Graphiti |
| **L3 前额叶** | 前额叶皮层 | 事件边界、叙事氛围、Gemini 通信 | Observer, Gemini Realtime |

---

## 三、部署架构与服务器决策 (Updated)

> 替代旧的香港+新加坡方案，采用 **东京双节点** 方案。

### 3.1 东京双节点 (Tokyo Region)

| 节点 | 角色 | 规格 | 运行模式 | 职责 |
|:-----|:-----|:-----|:---------|:-----|
| **Castle (城堡)** | **控制面** | ecs.g9i.large (2核8G) | **常驻 (24/7)** | LiveKit Server, Redis, Neo4j, Python Agent (逻辑/路由) |
| **Mecha (机甲)** | **数据面** | ecs.gn7i (A10 GPU) | **按需 (Spot)** | 重型视觉计算 (SAM2, DINOv2, DSG L1/L2) |

### 3.2 关键优势
*   **内网互通**: 两台机器位于同一 VPC 可用区，内网延迟 < 0.1ms。
*   **成本优化**: 大脑(ecs.g9i.large)常开保持在线，肌肉(A10)按需开启节省成本。
*   **网络优势**: 东京节点直连 Google Gemini API 延迟极低，且对国内连接相对友好。

---

## 四、关键技术决策 (Key ADRs)

### 4.1 基础设施 (Infra)
*   **LiveKit**: 选用 LiveKit 作为通信骨架。
    *   *理由*: 统一封装了 WebRTC (音视频)、RPC (可靠指令)、DataChannel (遥测)，且有成熟的 Agent 框架。
*   **RPC over DataChannel**: 控制指令使用 RPC。
    *   *理由*: 保证指令到达的可靠性，且语义更清晰 (`fly_to`, `animate`)。
*   **Redis**: 状态黑板与消息总线。
    *   *理由*: 解耦各模块，支持 Pub/Sub 模式。

### 4.2 视觉与感知 (Vision & DSG)
*   **DSG 四层架构**: 见上文。
    *   *理由*: 清晰分离"快直觉"(L1/L2)与"慢思考"(Gemini)，解决实时性与认知深度的矛盾。
*   **RustworkX**: 用于 L2 图计算。
    *   *理由*: 高性能、GIL-free，适合在 Python Agent 中实时维护空间/语义图。
*   **SVA Processor 模式**: 借鉴 SVA 的设计。
    *   *理由*: 将视觉处理封装为独立的 Processor，易于插拔和编排。

### 4.3 记忆与人设 (Memory & Soul)
*   **Graphiti**: 知识图谱记忆后端。
    *   *理由*: 支持非结构化数据到图谱的自动转换，内置 Leiden 社区检测。
*   **5 分区设计**: `episodic`, `objects`, `personality`, `vocabulary`, `nanobot_research`。
    *   *理由*: 隔离不同类型的知识，防止污染，提高检索精度。
*   **ParrotSoul**: 静态 Prompt + 动态 Graphiti 注入。
    *   *理由*: 保证人格一致性的同时，允许性格随经历成长。

### 4.4 调度与控制 (Scheduling)
*   **py-trees**: 后端行为树调度器。
    *   *理由*: 支持优先级中断、并行执行，比简单的状态机更适合复杂 Agent。
*   **双状态机**: 前端 (动画/物理) + 后端 (决策/逻辑)。
    *   *理由*: 明确分工，后端做决策权威，前端做平滑执行与预测。

---

## 五、实施路线图 (Roadmap)

### Phase 0: 准备 (已完成)
*   [x] 深度调研 (Opus)。
*   [x] 架构设计与决策。
*   [x] 目录结构整理与 Skill 拉取。
*   [ ] 基础设施部署 (Castle/Mecha)。

### Phase 1: Bus-first 实施 (Current)
*   [x] 需求清单 v2 完成。
*   [x] 模块划分与目录结构方案完成。
*   [x] Bus / Brain / Scheduler / Shared 骨架代码已创建。
*   [ ] Brain Agent 填充与本地 Redis 联调。
*   [ ] Unity 客户端最小接入验证。

### Phase 2: 反射与控制 (Reflex & Control)
*   [ ] 接入 XR Hands。
*   [ ] 实现 Redis 调度总线。
*   [ ] 实现手势反射 (绕过 LLM，伸手指->飞来)。

### Phase 3: 视觉与记忆 (Vision & Memory)
*   [ ] 部署 SAM2 + DINOv2。
*   [ ] 实现 DSG L1/L2。
*   [ ] 接入 Graphiti 记忆。
*   [ ] 实现"飞到奶奶的杯子上"。

---

## 六、参考资源

*   **详细调研与设计**: `docs/InfoCollections/Opus/` (共 22+ 篇文档)
*   **Skill 库**: `.cursor/skills/`
*   **当前进度与阶段状态**: `.cursor/memory/active_context.md`
