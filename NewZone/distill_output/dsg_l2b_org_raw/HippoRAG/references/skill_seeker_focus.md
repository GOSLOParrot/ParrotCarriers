# Skill Seeker focus — HippoRAG

> **Repo:** OSU-NLP-Group/HippoRAG | **Pin:** main (2026-05-05)
> **Paper:** Gutiérrez et al., NeurIPS 2024, arXiv:2405.14831

蒸馏目标：**只**取"海马索引型记忆图组织方式"——Node 是什么、Edge 是什么、
预加载/检索如何走 Personalized PageRank。**不要**蒸馏 LLM 调用、API server、benchmark 复现。

## §A — 节点 / 边 / 图组织（**最重要**）

- `OpenIE triple` — (subject, predicate, object) → 节点候选与边候选的来源
- `entity node` — 实体节点（皮层概念）
- `passage node` — 文段节点（episodic 实例的指针）
- `synonym edge` — 同义/共指边（节点合并的依据）
- `relation edge` — 三元组关系边
- node embedding storage vs node id pointer to source
- node deduplication / linking by embedding similarity

## §B — Personalized PageRank 检索（潜意识联想式）

- `personalized_pagerank` — 从 query 触发节点出发的扩散激活
- `damping factor` — 衰减系数
- `seed node selection` — query → 哪些种子节点
- `restart probability` — 回到种子的概率
- `top-k retrieval` — 排序后取前 k

## §C — 持续整合 / 增量更新

- `index_continual_update` — 新文档进入时的增量索引
- `OpenIE on new docs` — 增量三元组抽取
- `node merge across documents` — 跨文档实体合并

## §D — 实现切入点

- `src/hipporag` 顶层入口
- 配置：retriever / extractor / 模型选项
- KG 存储格式（json / pickle）

## What NOT to focus on

- LLM 调用具体 prompts
- 评测脚本（hotpot QA / 2WikiMultihopQA）
- vllm / openai client 适配
- 数据下载脚本
