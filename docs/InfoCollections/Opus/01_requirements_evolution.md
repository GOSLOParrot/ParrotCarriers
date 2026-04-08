# 需求演进：从旧 DSG Demo 到新 GOSLOParrot


> 生成日期: 2026-02-24
> 用途: 新项目启动前的需求梳理与对比，确保不遗漏核心价值、不搬运过时设计

---

## 1. 旧项目遗产盘点

### 1.1 值得保留的核心理念

| 理念 | 说明 | 新项目继承方式 |
|:-----|:-----|:--------------|
| **DSG 分层 (L1/L2→四层)** | 物理热循环与认知冷循环分离 | 升级为四层仿生架构：L1(视网膜/SAM2)→L2-A(背侧通路/RustworkX空间图)→L2-B(腹侧通路/RustworkX语义注意力图)→L3(前额叶接口/观察者+Gemini事件分割) |
| **语义锚定 (UUID Mapping)** | 瞬时像素 → 永恒语义实体的绑定 | 核心需求不变，实现从 LanceDB 本地向量库迁移到云端向量服务 |
| **XML 上下文注入** | 结构化 diff 推送给 LLM | **已过时**。新架构中通过 LiveKit Agent 的 `update_chat_ctx()` / `on_user_turn_completed` 注入场景上下文文本，不再使用 `client_content` XML |
| **Gemini 主导的事件分割** | LLM 决定认知边界，DSG 只提供线索 | 保留"Gemini 主导"原则，但交互协议从 BidiGenerateContent WebSocket 变为 LiveKit Agent Session |
| **双速知识引擎** | 快通道(直连DB) + 慢通道(Graphiti) | 进化。L2-B 用 RustworkX 做实时工作记忆(快)，Graphiti 做长期历史聚类(慢)。L2-B 实时折叠 + Graphiti Leiden 社区检测互补 |

### 1.2 明确废弃的设计

| 废弃项 | 原因 |
|:-------|:-----|
| **直连 Gemini BidiGenerateContent WebSocket** | 过时。新架构通过 LiveKit Agent Session 统一管理，不再裸写 WebSocket |
| **XML Schema (`<SCENE_GRAPH_UPDATE>`)** | 过时。SVA 使用 Processor 的 `attach_agent()` + 事件系统注入上下文，更优雅 |
| **本地 RTX 3070 运行** | 升级到阿里云 A10 24GB，视觉模型不再受本地显存限制 |
| **LanceDB 本地向量库** | 云端部署后使用 Qdrant 或 Graphiti 内置向量搜索 |
| ~~**RustworkX 图计算**~~ | ~~过度工程化~~ → **修正: 保留 RustworkX**。DSG 作为复合 Processor 后，GIL-free 和 `contract_nodes` 更加必要（详见 `09_dsg_technology_selection.md`） |
| **自研 ByteTrack 集成** | 视觉升级到 SAM2 后追踪逻辑完全不同 |
| **SpecKit 流程纪律** | 旧项目特有的重流程，新项目使用 Cursor Rules + Skills 轻量管理 |
| **Context Bank (.specify/context/)** | 被 Cursor Skills + Dynamic Context Discovery 替代（详见审计报告） |
| **_vendor/ 本地源码验证** | 不再需要，依赖通过 pip/uv 锁定版本管理 |

---

## 2. 新项目核心需求

### 2.1 终极愿景

**AR 鹦鹉伴侣**: 一只能在 AR 空间中飞行、停在手上、认识你的物品、记住你的故事的 AI 鹦鹉。它通过语音与你交流，通过视觉理解你的世界，拥有跨会话的持久记忆。

### 2.2 关键能力矩阵

| 能力层 | 具体需求 | 对应学习项目 |
|:-------|:---------|:------------|
| **基础设施 (Infra)** | WebRTC 低延迟音视频传输 + DataChannel 数据通道 | LiveKit Agents (`livekit/agents`, `python-agents-examples`) |
| **视觉感知 (Vision)** | 实时物体分割/追踪 + 特征提取 + ReID | SVA Processor 模式 (`GetStream/Vision-Agents`) |
| **认知交互 (Brain)** | 多模态 LLM 实时对话 + 视觉上下文感知 | SVA Gemini Realtime 集成 + LiveKit AgentSession |
| **AR 控制 (Body)** | 鹦鹉飞行/停靠/动画 + 手势反射响应 | OpenTeach 坐标映射 + LiveKit Unity SDK |
| **记忆系统 (Soul)** | 跨会话物体身份 + 情景记忆 + 用户偏好 | Graphiti 或轻量替代方案 |
| **调度系统 (Spine)** | 反射/意图/任务三级调度 | Redis Pub/Sub + LiveKit DataChannel |

### 2.3 分期实施路线

#### Phase 1: 语音骨架 (Voice Skeleton)
- 基于 LiveKit Agent 跑通语音对话
- Unity 端连接 LiveKit，方块响应语音指令
- **产出**: 可对话的基础 Agent

#### Phase 2: 反射与控制 (Reflex & Control)
- 接入 XR Hands 手势数据
- 实现 Redis 调度器: 手势 → 反射动作 (绕过 LLM)
- **产出**: 手张开 → 鹦鹉飞到手上

#### Phase 3: 视觉与记忆 (Vision & Memory)
- 部署 SAM2 + DINOv2 视觉管线
- 实现 SVA Processor 模式的上下文注入
- 接入记忆系统 (Graphiti 或替代)
- **产出**: 鹦鹉能识别"奶奶的杯子"并记住它

---

## 3. 新旧需求关键词对比

### 旧项目关键词
`YOLO-World` · `ByteTrack` · `RustworkX` · `LanceDB` · `Graphiti` · `Neo4j/FalkorDB` · `XML注入` · `BidiGenerateContent` · `WebSocket` · `LangGraph` · `RTX3070` · `本地部署` · `SpecKit`

### 新项目关键词
`LiveKit` · `AgentSession` · `SVA/Vision-Agents` · `Processor` · `SAM2` · `DINOv2` · `Gemini Realtime` · `WebRTC` · `DataChannel` · `Redis` · `Unity AR` · `XR Hands` · `OpenTeach` · `阿里云 A10` · `Cursor Skills` · `Dynamic Context Discovery`

---

## 4. 项目代号与目标声明

**项目代号**: `GOSLOParrot` (暂定)

**一句话目标**: 基于 LiveKit 基础设施，融合 SVA 视觉注入模式和 OpenTeach AR 映射经验，构建一个云原生的 AR 鹦鹉伴侣，实现实时语音交互、视觉场景理解、手势控制和跨会话记忆。

**成功标准**:
1. 鹦鹉能通过语音实时对话 (延迟 < 500ms)
2. 鹦鹉能识别手势并飞到手上 (反射延迟 < 100ms)
3. 鹦鹉能识别特定物体并关联记忆 (ReID 准确率 > 85%)
4. 系统支持跨会话记忆持久化
