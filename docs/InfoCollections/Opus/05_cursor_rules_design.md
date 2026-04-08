# 新项目 Cursor Rules 设计

> 生成日期: 2026-02-24
> 用途: 为新项目 `parrot-ar-cloud` 设计初始的 .cursor/rules/ 文件内容

---

## 1. 规则架构

```
.cursor/rules/
├── workspace.mdc          # 全局工作流 — alwaysApply: true
├── architecture.mdc       # 架构决策 — alwaysApply: false
├── backend-python.mdc     # Python 约定 — globs: ["agent/**/*.py"]
└── unity-client.mdc       # Unity 约定 — globs: ["unity-client/**/*.cs"]
```

---

## 2. workspace.mdc (全局工作流)

```markdown
---
description: 全局工作流与沟通规范
globs: []
alwaysApply: true
---

## 语言
- 所有回复使用**简体中文**。

## 工作流
- 直接修改当前文件，不使用 worktree。
- 每个 Phase 的变更必须独立可运行、可验证。
- 优先使用成熟方案，如果比参考项目官方示例复杂 2 倍以上需要说明理由。

## 依赖管理
- Python 依赖通过 `pyproject.toml` 管理，锁定主要版本。
- 新增依赖前检查是否与现有依赖冲突。
- 不允许浮动依赖进入核心链路。

## 知识来源优先级
1. 项目内 `.cursor/skills/` 中的 Skill 文件
2. `reference/` 目录中的参考仓库源码
3. 官方文档 (通过 @docs 或联网搜索)
4. 不信任训练数据中的 API 签名，遇到不确定时联网验证
```

---

## 3. architecture.mdc (架构约束)

```markdown
---
description: 项目架构决策与分层约束，在讨论架构、设计新模块或审计现有代码时应用
globs: []
alwaysApply: false
---

## 项目代号
parrot-ar-cloud — 云原生 AR 鹦鹉伴侣

## 核心基础设施
- **传输层**: LiveKit (WebRTC + DataChannel)，不使用裸 WebSocket
- **LLM 交互**: 通过 LiveKit Agent Session + Gemini Realtime，不直连 BidiGenerateContent
- **状态总线**: Redis (Pub/Sub + Blackboard)
- **部署**: 阿里云 A10 24GB (Docker)

## 分层架构

```
[Unity Client] ←→ [LiveKit] ←→ [Python Agent]
                                    ├── perception/  (视觉感知)
                                    ├── brain/       (认知交互)
                                    ├── dispatcher/  (调度路由)
                                    ├── memory/      (记忆持久化)
                                    └── tools/       (Gemini 工具)
```

## 关键约束
1. **适配器隔离**: 所有外部服务（记忆/向量库/视觉模型）必须通过抽象接口访问
2. **模拟器模式**: 必须支持无外部服务的端到端开发
3. **三级调度**: Reflex (无LLM, <100ms) / Intent (LLM, <500ms) / Task (异步, 无上限)
4. **Gemini 主导**: 视觉系统提供线索，Gemini 做最终认知决策

## 参考项目借鉴原则
- **LiveKit Agents**: 骨架与通信
- **SVA Vision-Agents**: Processor 模式与上下文注入思想
- **OpenTeach**: 坐标映射与手势数据格式
- 借鉴 Pattern，不照搬代码
```

---

## 4. backend-python.mdc (Python 后端)

```markdown
---
description: Python Agent 后端编码约定
globs: ["agent/**/*.py", "tests/**/*.py"]
alwaysApply: false
---

## 代码风格
- Python 3.10+，使用 type hints
- 使用 Pydantic v2 做数据验证（严禁 v1 API）
- 异步优先：所有 I/O 操作使用 async/await
- 使用 ruff 格式化，行宽 120

## LiveKit Agent 规范
- Agent 入口通过 `AgentSession` 配置
- 工具函数使用 `@function_tool` 装饰器
- 事件处理使用 `session.on("event_name")` 注册

## 模块职责边界
- `perception/`: 只处理视觉数据，输出结构化检测结果，不做 LLM 调用
- `brain/`: 只与 Gemini 交互，不直接读取视频帧
- `dispatcher/`: 只做路由决策和 Redis 通信，不包含业务逻辑
- `memory/`: 只通过 `MemoryAdapter` 接口访问，不暴露底层实现细节
- `tools/`: 只定义 Gemini 可调用的工具接口

## 错误处理
- 使用结构化日志 (structlog 或 logging + JSON formatter)
- 外部服务调用必须有超时和重试
- 视觉管线错误不应中断语音对话
```

---

## 5. unity-client.mdc (Unity 客户端)

```markdown
---
description: Unity AR 客户端编码约定
globs: ["unity-client/**/*.cs"]
alwaysApply: false
---

## 基本约定
- Unity 2022 LTS+，C# 9.0+
- 使用 LiveKit Unity SDK 进行通信
- AR Foundation + XR Hands 进行手势追踪

## 通信协议
- 音视频: 通过 LiveKit WebRTC Track
- 控制指令: 通过 LiveKit DataChannel (JSON 格式)
- 遥测数据: 通过 DataChannel Unreliable 模式 (10Hz)

## 鹦鹉控制
- 反射动作 (手势触发) 由本地状态机执行，不等待服务器
- 意图动作 (LLM 指令) 通过 DataChannel 接收后执行
- 动画平滑: 所有位移使用插值，不直接 SetPosition

## 坐标系
- Unity 使用左手坐标系 (Y-up)
- Python Agent 使用右手坐标系
- 坐标转换在 DataBridge 层统一处理
```
