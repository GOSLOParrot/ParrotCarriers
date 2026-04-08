# 项目目标、关键词与路线图

> 生成日期: 2026-02-24
> 用途: 新项目的愿景声明、核心关键词、实施路线图、当前阶段任务

---

## 1. 愿景声明

**Parrot AR Cloud** 是一个云原生的 AR 鹦鹉伴侣系统。它能在 AR 空间中飞翔、停在你的手上、用语音和你对话、通过视觉认识你的物品、并跨会话记住你们的故事。

### 核心价值主张

| 价值 | 描述 |
|:-----|:-----|
| **具身交互** | 鹦鹉不是屏幕上的对话框，而是有物理存在感的 AR 角色 |
| **实时智能** | 毫秒级手势响应 + 亚秒级语音对话 + 实时视觉理解 |
| **持久记忆** | 跨会话的物体身份、用户偏好、情景记忆 |
| **主动好奇** | 鹦鹉主动发现新物体、评论环境变化，不只被动回答 |

---

## 2. 核心关键词

### 技术栈关键词
`LiveKit Agents` · `AgentSession` · `WebRTC` · `DataChannel` · `Gemini Realtime` · `SAM2` · `DINOv2` · `SVA Processor` · `Redis Pub/Sub` · `Unity AR Foundation` · `XR Hands` · `Docker` · `阿里云 A10`

### 架构关键词
`Cloud-Native` · `Embodied AI` · `Multimodal Agent` · `Context Injection` · `Three-Tier Dispatch` · `Adapter Pattern` · `Mock Mode` · `Progressive Complexity`

### 设计理念关键词
`Gemini-Led Cognition` · `Processor Pattern` · `Reflex-Intent-Task` · `Object Permanence` · `Latency Masking` · `Proactive Curiosity`

---

## 3. 实施路线图

### Phase 0: 资料收集与架构设计 (当前阶段)

**目标**: 完成调研、确定架构、配置新项目

| 任务 | 状态 | 产出 |
|:-----|:-----|:-----|
| 调研 LiveKit Agents 框架 | 完成 | `03_reference_projects.md` |
| 调研 SVA Processor 模式 | 完成 | `03_reference_projects.md` |
| 调研 OpenTeach AR 映射 | 完成 | `03_reference_projects.md` |
| 审计旧 Context Bank vs Skills | 完成 | `02_context_routing_audit.md` |
| 需求演进分析 | 完成 | `01_requirements_evolution.md` |
| 新项目结构设计 | 完成 | `04_new_project_structure.md` |
| Cursor Rules 设计 | 完成 | `05_cursor_rules_design.md` |
| 创建新项目仓库 | **待做** | `parrot-ar-cloud/` 初始化 |
| 拉取参考仓库 | **待做** | `reference/` 目录填充 |
| 生成 Cursor Skills | **待做** | `.cursor/skills/` 填充 |

### Phase 1: 语音骨架 (Voice Skeleton)

**目标**: Unity 里的方块能通过 Gemini 语音指令旋转

| 任务 | 依赖 | 预估工时 |
|:-----|:-----|:---------|
| 部署 LiveKit Server (Docker) | 阿里云实例 | 1天 |
| 实现 Python Agent 基础骨架 | `agent/main.py`, `agent/session.py` | 1天 |
| 实现 Gemini Realtime 连接 | LiveKit Gemini 插件 | 1天 |
| Unity 连接 LiveKit | LiveKit Unity SDK | 2天 |
| 实现 DataChannel 指令通道 | Agent ↔ Unity | 1天 |
| 端到端语音测试 | 全部 | 1天 |

**里程碑验收**: 用户对方块说"旋转"，方块旋转

### Phase 2: 反射与控制 (Reflex & Control)

**目标**: 手张开 → 鹦鹉飞到手上 (绕过 Gemini，纯物理反射)

| 任务 | 依赖 | 预估工时 |
|:-----|:-----|:---------|
| 实现 Redis Bus | `agent/dispatcher/redis_bus.py` | 1天 |
| 实现三级调度器 | `agent/dispatcher/router.py` | 2天 |
| 接入 XR Hands | Unity AR Foundation | 2天 |
| 实现鹦鹉飞行/停靠动画 | Unity Animator | 3天 |
| 手势 → 反射动作链路 | DataChannel → Redis → Unity | 2天 |

**里程碑验收**: 手张开 → 鹦鹉飞来；握拳 → 鹦鹉飞走

### Phase 3: 视觉与记忆 (Vision & Memory)

**目标**: 鹦鹉能飞到"奶奶的杯子"上，杯子移动后重新定位

| 任务 | 依赖 | 预估工时 |
|:-----|:-----|:---------|
| 部署 SAM2 + DINOv2 | 阿里云 A10 GPU | 2天 |
| 实现 VideoProcessor | `agent/perception/processor.py` | 3天 |
| 实现物体 ReID | `agent/perception/reid.py` | 3天 |
| 实现上下文注入器 | `agent/brain/context_injector.py` | 2天 |
| 接入记忆系统 | `agent/memory/` | 3天 |
| Gemini Tool 集成 | `agent/tools/` | 2天 |

**里程碑验收**: 用户说"飞到奶奶的杯子上" → 鹦鹉定位到正确物体

---

## 4. 当前阶段 (Phase 0) 剩余任务

### 4.1 立即执行
1. **创建新仓库** `parrot-ar-cloud`，按 `04_new_project_structure.md` 初始化
2. **拉取参考仓库**:
   - `git clone https://github.com/livekit/agents.git reference/livekit-agents`
   - `git clone https://github.com/GetStream/Vision-Agents.git reference/vision-agents`
   - `git clone https://github.com/livekit-examples/python-agents-examples.git reference/livekit-examples`
3. **初始化 Cursor Rules**: 按 `05_cursor_rules_design.md` 创建 `.cursor/rules/`

### 4.2 短期执行
4. **生成 Cursor Skills**: 基于参考仓库，为每个学习对象生成 SKILL.md
5. **总线设计文档**: 定义 DataChannel JSON 协议
6. **配置阿里云实例**: A10 GPU + Docker 环境

### 4.3 知识沉淀
7. 将本次调研的关键发现固化到新项目的 `doc/architecture.md`
8. 确保所有参考链接可追溯

---

## 5. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|:-----|:-----|:---------|
| LiveKit Unity SDK 仅支持 WebGL | AR 功能受限 | 确认原生 SDK 支持或寻找替代方案 |
| SAM2 推理延迟过高 | 视觉管线跟不上实时需求 | Phase 3 前做性能基准测试 |
| Gemini Realtime API 限制 | 并发/token/fps 限制 | 查阅最新配额，准备降级方案 |
| 阿里云网络延迟 | 跨境传输增加延迟 | 选择香港区域，测试 RTT |
| 新框架学习曲线 | LiveKit + SVA 双重学习成本 | Phase 1 先只用 LiveKit，Phase 3 再引入 SVA 思想 |
