# Skill Seeker focus — AriGraph

> **Repo:** AIRI-Institute/AriGraph | **Pin:** main (2026-05-05)
> **Paper:** Anokhin et al., 2024, arXiv:2407.04363

蒸馏目标：**只**取"agent 工作记忆图的双类节点组织"——episodic vs semantic 节点
如何共存、如何相互引用、如何在文本游戏 agent 中查询。**不要**蒸馏 TextWorld 环境
适配、prompt 工程、训练循环。

## §A — 双类记忆节点（**最重要**）

- `episodic memory` — 事件记忆（具体 observation / 时间戳 / 上下文）
- `semantic memory` — 语义记忆（事实 / 实体属性 / 一般知识）
- `episodic node` vs `semantic node` 的字段差异
- 双类节点之间的桥接边（episodic 引用 semantic 实体）

## §B — 图操作

- triplet 抽取 → 节点 / 边 add 流程
- 节点合并（同一实体多次提及）
- 节点更新（属性变化）
- 检索：从 query 出发的图遍历 / 子图抽取

## §C — Agent 查询模式

- exploration mode 与 exploitation mode 的查询差异
- 工作记忆作为 LLM 输入的格式化方法
- working set 的容量管理（不一定有，看仓库实测）

## What NOT to focus on

- TextWorld / Jericho 环境的具体接口
- LLM 决策循环 prompt 工程
- 训练 / 微调脚本
- 评测 benchmark 复现
