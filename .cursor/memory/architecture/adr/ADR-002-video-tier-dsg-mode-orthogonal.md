---
status: accepted
adr_id: ADR-002
supersedes: ""
superseded_by: ""
date: 2026-04-22
deciders: "用户 + AI (P2.5 讨论期决定, 写入 ar_feature_vision.md §3.6)"
---

# ADR-002: VideoTier × DsgMode 正交分离

## 1. 背景

P2.5 阶段 `ar_feature_vision.md §3.6` 讨论出两件容易被混淆的事:

1. **算力档位** (Sentinel / A10 / Flash 哪个在服务视频感知)
2. **玩法模式** (桌面扫描 / 持机漫游 / 遥控拍摄 ...)

早期讨论多次出现"切到 A10 模式 = 桌面模式"之类的措辞, 把档位和玩法捆死会导致:
- 换算力就得改 DSG / 触发器代码 (反)
- 换玩法就得重编 CV 管线 (反)

## 2. 决策

**两轴完全正交**:
- `VideoTier` (算力档位 — Sentinel / A10 / Gemini Flash / Off) 决定 **L1.5 感知管线**
- `DsgMode` (玩法模式 — DesktopScan / FreeRoam / PhotoFocus / ...) 决定 **DSG 触发器与 Ingest 过滤器启用集合**
- **L2-B / L3 永远不换**, 换的是 Ingest 过滤器和触发器

关键约束:
- `blackboard:vision/tier` 和 `blackboard:dsg/mode` 是两个独立 BB key
- VideoTier 降档 (高→低) 自动触发, DsgMode 只由 Brain `set_mode` 主动切
- Ingest 过滤器的"启用矩阵"以 `(VideoTier, DsgMode)` 二维表形式定义, 见 `ar_feature_vision.md §3.6`

## 3. 备选方案

| 方案 | 放弃原因 | 备注 |
|:-----|:---------|:-----|
| 单一 `Mode` 枚举合并两轴 | 组合爆炸, N×M 个模式维护不动 | 最初草图用过, 很快放弃 |
| 只按算力分档, 玩法靠 prompt | 触发器无法差异启用, DSG 会写脏数据 | 和 DSG 的 trigger 架构冲突 |
| 只按玩法分, 算力 autoscale | 算力不可预测 (抢占式 A10 随时被抢), 玩法不能假设算力在 | 东京双节点现实 |

## 4. 后果

**好**:
- 算力端 (运维) 和玩法端 (Brain tool + 用户) 独立演进, 不互相阻塞
- L2-B / L3 代码稳定, 只写 Ingest 过滤器表
- Sprint 2 可以先做 VideoTier 自动降档, Sprint 3 再做 DsgMode 切换

**坏 / trade-off**:
- (VideoTier × DsgMode) 笛卡尔组合表得显式维护, 少一项 = 某模式下某档位行为未定义
- 用户心智负担: 必须理解"我切了 DsgMode 不代表换算力"

**未知 / 需监控**:
- 某些组合可能运行时出现但事先没设计 (例: A10 被抢期间用户切到 PhotoFocus), 需要 fallback 策略
- 组合表什么时候需要**第三轴** (例: 用户画像/年龄)? 目前没看到必要

## 5. 关联

- 设计文档: `ar_feature_vision.md §3.5` (两轴) + `§3.6` (档位降级)
- 代码 (未来): `src/parrot/dsg/ingest/` 过滤器 (Sprint 2+)
- 相关 ADR: ADR-003 (调度层分治, 是 VideoTier 降档的兄弟问题)
- 验证闸门: Sprint 2 S2.{TBD} 过 Gate 2 时才从 tentative 升

## 6. Review 点

- 如果组合爆炸 (三轴以上), 考虑显式的 Policy 表 (类似 Nginx 配置)
- 如果 VideoTier 和 DsgMode 耦合出现 (例如 90% 的组合要求 VideoTier ≥ A10 才能跑某 DsgMode), 说明正交假设破了, 要重新 ADR
