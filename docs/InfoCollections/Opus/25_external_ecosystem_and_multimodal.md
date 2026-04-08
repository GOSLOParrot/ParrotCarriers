# 25 · 外部生态双生机制与多模态记忆路由

> 生成日期: 2026-03-18
> 依据: 用户的 `HumanPlan` (plan4.md) 与最新架构探讨
> 目的: 澄清并固化 Gemini App 外部生态、Nanobot 猫娘在调度器内的定位，以及多模态记忆(图片/视频/URL)在 Graphiti + Obsidian 中的落地方案。

---

## 一、Gemini App 外部生态与二重身机制

由于 Gemini App 闭源，且仅能通过有限的 Extension 管理 Google 生态，无法让我们自定义 MCP Server、Client 或定制工具。因此我们引入**“双生态共治” (二重身)** 机制。

### 1.1 内部与外部 Agent 分离
- **内部唤醒端 (Gemini App)**：当用户主动打开 Gemini App 时唤醒，作为与用户的交互总控。
- **外部活动 Agent (分身)**：专门用于与外部（如聊天室、系统后台）直接交互的独立 Agent。

### 1.2 状态同步与协作 (基于 Drive 工作区)
二者通过 **Google Drive 划分出的固定工作区** 进行信息对齐。
- 工作区内包含系统设定、记忆拓扑和状态交互模式。
- 外部分身通过后台运行脚本（如 Python/C#）沉淀数据。
- 内部唤醒端在唤醒时，利用 Extension 探针去查询、读取这个设定区与报告区（例如带特定 Tag 的邮件、特定的 Drive 文档）。
- **注意读写锁防冲突**：内部唤醒端主要是**检索与宣读**工作（Read-Heavy），外部活动 Agent 主要是**事件记录与沉淀**工作（Write-Heavy），需要注意避免对同一设定文件的高频写冲突。

---

## 二、Nanobot 猫娘的重塑与调度器融合

在早期的初步调研中，因不了解 HKUDS nanobot 项目内情，曾误将其视为仅通过 MCP 挂载的黑盒 Bot。现在纠正并明确其在架构中的真实定位：

### 2.1 不只是 MCP，而是本地调度节点
- **形态转变**：它不是外部调用的 API，而是跑在与 GOSLO 同一台物理服务器上的独立实体（女仆设定）。另一张 GPU 会专职跑 CV Flow Worker。
- **职责划分**：GOSLO 负责环境感知、AR 交互与高优先级指令；Nanobot 负责协助 GOSLO 处理复杂的长程任务与记忆梳理。

### 2.2 融入 py-trees 行为树调度器
Nanobot 将被改造并直接融入系统的**任务调度器**设计中。
- 它深度了解 `Scene` 和 `Preference`，但不应阻塞 GOSLO 的实时视听管线。
- 在 `py-trees` 架构里，Nanobot 应当作为一个 **始终并行的异步子树 (Always-Parallel Background Worker)** 存在。
- 它通过 `Redis Blackboard`（黑板机制）与 GOSLO 进行数据交换和状态传递，从而避免占用主线程资源。

---

## 三、多模态输入与 Graphiti 的耦合度设计

关于图片、视频帧以及各种多模态引用链接（References）的存放与索引机制，我们采用 **Graphiti 语义网 + Obsidian SSOT + 向量数据库** 的协同策略。

### 3.1 Graphiti 的 URL 管理能力
**结论：Graphiti 完全胜任对象关联与 URL 托管。**
- **技术可行性**：Graphiti 核心支持通过自定义的 `Pydantic` 模型创建实体（Custom Entity Definitions）。这意味着我们可以自定义 `MultimodalNode`，将 URL 或对象存储路径作为节点属性或边的属性进行托管。
- **实践模式**：在 Graphiti 的节点中只存 **元数据 (Metadata) 与 URL/路径**。如：`{ entity_type: "Image", url: "drive://path/to/img", timestamp: "..." }`。大文件实体（如图像二进制、预制体配置）绝不进入图数据库内部。

### 3.2 存储落盘路由 (Where to store)
- **大文件载体**：存放在 Google Drive、Obsidian 的附件目录（对于核心资产）或专用的本地/云端对象存储（OSS）中。
- **逻辑寻址 (Graphiti)**：Graphiti 的动态图中维护这些多模态文件的逻辑关系（比如某天下午 GOSLO 看到了某个苹果，关联到某个 URL）。
- **SSOT 兜底 (Obsidian)**：当一个物体成为常态信息（比如“用户的常用键盘”），该物体的确切属性（以及它的主图 URL）将通过 Obsidian 笔记同步固化，利用 SSOT + GraphRAG 大幅降低图数据库在多轮推理中的幻觉率。
- **特征匹配 (Vector DB)**：纯视觉层面的相似度搜索、人脸检索或图像向量匹配，下放给具体的专门向量服务器（如 Qdrant、Milvus），这是后续设计 CV Flow 时的具体分工。Graphiti 主要负责语义逻辑与事件溯源。