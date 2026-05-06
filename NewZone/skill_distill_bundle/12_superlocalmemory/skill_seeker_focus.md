# Skill Seeker distillation focus — SuperLocalMemory (SLM)

> **Repo:** qualixar/superlocalmemory | **Pin:** main (2026-05-05) | **License:** AGPL v3
> **Paper:** arXiv 2604.04514 — "SuperLocalMemory V3.3: The Living Brain"
> **Site:** https://superlocalmemory.com

蒸馏目标：理解 SLM 如何用 RustworkX 构建 9 层记忆架构 + 生物启发遗忘 + 多通道检索。
对 ParrotCarriers DSG L2-B（已是 RustworkX）有架构借鉴价值。

## §A — 9-Layer Architecture

- L1: Data Ingestion — 接入 IDE / MCP / CLI
- L2: Memory Processing — 提取 + 标准化
- L3: Context Engine — 当前会话上下文匹配
- L4: Knowledge Graph — RustworkX 实现的认知图谱
- L5: Adaptive Learning — 模式学习 + soft prompt 注入
- L6: Privacy Layer — local-first / SQLite
- L7: Search & Retrieval — 6 通道混合检索
- L8: Multi-Agent Coordination — 跨 agent 共享记忆
- L9: IDE Integration — 17+ IDE / MCP 集成

## §B — Layer 4: Knowledge Graph (RustworkX)

- `code_graph.db` — Tree-sitter AST + 对话事件统一图
- 双向事件总线 (Bidirectional Event Bus)
- 节点类型: function / class / import / conversation_event / decision
- 稳定 ID 映射；亚毫秒级邻居查询
- 异构节点群（句法 + 语义混合）

## §C — Biologically-Inspired Forgetting

- Synaptic Pruning（突触修剪）模型
- 衰变方程: 时间 + 访问频率 + 信任评分
- Trust-Weighted Forgetting (TWF) — 贝叶斯动态衰减
  - τ_eff = τ_base / trust_score
  - 高信任源（架构文档）→ 极慢衰减
  - 低信任源（临时调试对话）→ 快速衰减
- 后台异步循环更新全网权重

## §D — Cognitive Quantization

- 量子化降维压缩 (up to 32x storage savings)
- Fisher-Rao 度量原则
- 量子化导致存储向量方差增加 → 检索时相似度下降
- 模拟"陈旧记忆模糊"

## §E — 6-Channel Hybrid Retrieval

- Channel 1: 关键词全文 (FTS)
- Channel 2: 语义向量
- Channel 3: 图遍历
- Channel 4: 时间衰减加权
- Channel 5: ONNX 跨编码器重排序
- Channel 6 (新版): 部分查询补全 (Query Completion)
- 融合方式: Reciprocal Rank Fusion (RRF)
- 命中延迟: 10.6ms

## §F — Operating Modes

- Mode A: zero-LLM, pure local retrieval (74.8% LoCoMo)
- Mode A Raw: 无 LLM 全程 (60.4%)
- Mode B: 本地 Ollama
- Mode C: cloud LLM at every layer (87.7%)

## §G — Daemon / IPC

- Daemon Serve Mode at `127.0.0.1:8767`
- 热启动零延迟
- MCP server (35 tools)
- Agent-native CLI with `--json` envelope: `{success, command, version, data, next_actions}`

## §H — Source Tree of Interest (qualixar/superlocalmemory)

- `src/` — Python 实现
- `bin/` — CLI 入口（slm 命令）
- `ide/` — IDE 集成代码
- `integrations/` — MCP / OpenAI / Claude / Cursor 适配
- `docs/`, `wiki-content/` — 文档
- `examples/` — 用例
- `skills/` — Cursor skills（meta!）
- `tests/` — 测试

## §I — Key Symbols / Modules to Distill

- `MemoryStore` (or equivalent) — 主存储类
- `Graph4` / `KnowledgeGraph` — L4 图层
- `TWF` / `TrustWeightedForgetting`
- `Quantizer` / `CognitiveQuantization`
- `Retriever` / `HybridRetriever` (6 channels)
- `ReciprocalRankFusion`
- `Daemon` / `slm_daemon`
- MCP tools: remember, recall, list, status, health, trace, forget...

## §J — LoCoMo Benchmark Numbers

- Mode A Retrieval: 74.8% (highest local-first)
- Mode A Raw (zero-LLM): 60.4%
- Mode C (cloud LLM): 87.7%
- vs Mem0 (~58-66%) / EverMemOS SOTA (92.3%)

## What NOT to focus on (out of scope for ParrotCarriers DSG)

- IDE 集成具体代码（与我们 Unity AR 无关）
- 商业许可 / EU AI Act 合规细节
- npm 发布 / 自动更新机制
- 部分 ATTRIBUTION / AUTHORS / 治理文件
