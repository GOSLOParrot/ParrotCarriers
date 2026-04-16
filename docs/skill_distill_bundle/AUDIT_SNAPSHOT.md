# 联网核实快照（节选）

> 来源：`docs/report/2026-04-11_skill_strategy.md` §5.0–5.2  
> 日期：2026-04-12  

## 项目选型审计

| 项目 | 最新版本 | 结论 |
|:-----|:---------|:-----|
| livekit/agents | v1.5.2 (2026-04-08) | ✅ 继续使用 |
| py-trees | v2.4.0 (2025-11-13) | ✅ 继续使用；async 用包装而非 async-btree |
| graphiti | v0.28.2 (2026-03-11) | ✅ 继续使用（temporal graph） |
| SVA Vision-Agents | v0.3.8 (2026-02-24) | ✅ Processor + attach_agent |
| client-sdk-unity | v1.3.5 (2026-04-03) | ✅ 唯一官方 Unity SDK |
| nanobot | v0.1.4.post6 (2026-03-27), HKUDS/nanobot | ✅ 继续使用 |
| agents-example-unity | 2026-03-14 push | ✅ 官方示例 |
| ConceptGraphs / Spark-DSG | 见主报告 | L2-A / DSG 参考，非本包 focus |

## 已完成 vs 待蒸馏

| 状态 | Skill | 仓库 | Pin |
|:-----|:------|:-----|:----|
| ✅ good | livekit-agents | livekit/agents | v1.5.2 |
| ✅ good | py-trees | splintered-reality/py_trees | v2.4.0 |
| 待重做 | graphiti | getzep/graphiti | v0.28.2 |
| 待重做 | sva-vision-agents | GetStream/Vision-Agents | v0.3.8 |
| 待重做 | client-sdk-unity | livekit/client-sdk-unity | v1.3.5 |
| 待重做 | nanobot-overview | HKUDS/nanobot | v0.1.4.post6 |
| 待重做 | agents-example-unity | livekit-examples/agents-example-unity | latest |

## 补充学习（不替代本包七项）

- **OpenFunGraph** (CVPR 2025) — functional 3D scene graph  
- **Mem0** — 轻量记忆；不替换 Graphiti 的 temporal 需求  

全文见主仓库 `docs/report/2026-04-11_skill_strategy.md`。
