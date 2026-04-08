# 项目路由与文档一致性审查报告

> 日期：2026-04-08  
> 审查范围：`.cursor/memory/INDEX.md`、`.cursor/rules/workspace.mdc`、`.cursor/memory/active_context.md`、`.cursor/memory/architecture/module_division.md`、`docs/InfoCollections/*` 与仓库当前实际目录  
> 目标：检查项目路由、文档索引、阶段描述、目录树说明是否存在冲突或过时信息，并回答 `INDEX.md` 是否已具备足够的文档索引能力
> 注：本文保留审查时的发现快照；其中部分断链、术语和阶段口径问题已在同日修正。

## 一、结论摘要

当前项目的“路由入口”已经形成了基本骨架，但**还不能视为完全一致、完全新鲜的真相源**。主要问题集中在四类：

1. **核心断链**：多个主入口引用了一个并不存在的文档。
2. **阶段信息过时**：部分文档仍停留在 Phase 0、模块划分前、或 `Dispatcher` 术语时代。
3. **目录树超前于实际仓库**：若干文档描述的代码、Unity、infra、tests 结构比当前仓库更完整。
4. **文档索引不完整**：`INDEX.md` 不是完全没有文档索引，但没有形成一个自洽、可遍历的“文档总索引”。

结论上应把当前状态判断为：

- **有路由**
- **有部分文档入口**
- **但存在断链、漂移和索引缺口**
- **因此还不适合被称为“完整文档索引体系”**

## 二、关键发现

### A. 高优先级：核心入口引用了不存在的服务器审计文档

以下文件都把 `docs/InfoCollections/HumanPlan/bus server audit.md` 作为现行入口：

- `.cursor/memory/INDEX.md`
- `.cursor/rules/workspace.mdc`
- `docs/InfoCollections/HumanPlan/legacy.md`
- `docs/InfoCollections/Opus/23_directory_audit_and_cursor_routing.md`
- `docs/middleaudit/project_audit_report_2026-03.md`

但当前仓库 `docs/InfoCollections/HumanPlan/` 下实际只有：

- `legacy.md`

没有发现：

- `bus server audit.md`

这意味着当前最核心的“东京双节点”路由入口实际上是**断链**的。  
该问题优先级最高，因为它直接影响：

- `INDEX.md` 的可信度
- `workspace.mdc` 的入口有效性
- 服务器部署信息的唯一真相源归属

### B. 高优先级：多份文档仍停留在旧阶段或旧术语

#### B1. `legacy.md` 的阶段描述落后于当前实际阶段

`docs/InfoCollections/HumanPlan/legacy.md` 仍写：

- `Phase 0: 准备 (Current)`
- `Phase 1: 语音骨架`

而当前 `.cursor/memory/active_context.md` 已明确：

- Phase 0 调研完成
- Phase A/B 完成
- **Phase 1 骨架代码已创建，等待用户审查**

因此 `legacy.md` 的路线图口径已经不是当前状态描述，更适合作为**历史架构摘要**，不适合作为“当前阶段入口”。

#### B2. `NANOBOT_LOCATION_AND_ROUTING_REPORT.md` 仍写“模块划分前的审计准备阶段”

`docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md` 中仍有：

- 当前项目仍处于“模块划分前的审计准备阶段”
- `Dispatcher -> nanobot-worker -> Redis/Graphiti`

这与当前已完成模块划分、统一术语为 `Scheduler` 的状态冲突。

#### B3. `Opus/23_directory_audit_and_cursor_routing.md` 仍保留旧时代问题陈述

该文档生成于 2026-03-02，内部仍保留：

- `.cursor/rules/` 为空
- `.cursor/skills/` 不存在
- `active_context.md` 为空
- `Phase 0：目录整理与路由配置（当前阶段）`
- `Dispatcher` 用词

这些内容作为**历史审计过程**可以保留，但若继续被当成当前路由说明，会误导后续判断。

### C. 高优先级：目录结构文档明显超前于实际仓库

以下文档把仓库描述为一个比当前实际更完整的状态：

- `.cursor/memory/INDEX.md`
- `.cursor/memory/active_context.md`
- `.cursor/memory/architecture/module_division.md`

对照当前仓库实际目录，至少存在这些不一致：

#### C1. `brain/` 目录说明超前

文档中描述存在：

- `src/parrot/brain/agent.py`
- `src/parrot/brain/soul.py`
- `src/parrot/brain/context.py`
- `src/parrot/brain/tools/fly_to.py`
- `src/parrot/brain/tools/animate.py`
- `src/parrot/brain/tools/dispatch_task.py`
- `src/parrot/brain/tools/_rpc_bridge.py`

实际存在的只有：

- `src/parrot/brain/__init__.py`
- `src/parrot/brain/tools/__init__.py`

#### C2. `unity/` 目录说明超前

文档中描述：

- `unity/ParrotAR/...`
- `unity/README.md`
- “Unity 项目待初始化”

当前 `unity/` 目录实际为空。

#### C3. `infra/` 目录说明超前

文档中描述存在：

- `infra/redis/redis.conf`
- `infra/.env.castle`

实际存在的只有：

- `infra/docker-compose.yml`
- `infra/docker-compose.dev.yml`
- `infra/livekit/livekit.yaml`

#### C4. `tests/` 说明超前

`active_context.md` 写“2 个测试通过”，`INDEX.md` 写有：

- `integration/test_brain/test_bus/test_scheduler`

当前 `tests/` 下实际只发现：

- `tests/test_bus/test_registry.py`

#### C5. `src/scripts/` 说明超前

`module_division.md` 描述了：

- `src/scripts/start_brain.py`
- `src/scripts/start_scheduler.py`
- `src/scripts/health_check.py`

实际没有对应文件。

这类问题的本质不是“文档错了一点”，而是**文档已开始替代未来计划，冒充当前现状**。  
若继续把这些文件当作“唯一真相源”，后续会不断产生误读。

### D. 中优先级：`INDEX.md` 有文档入口，但没有形成完整文档索引

这个问题正面回答你的疑问：

> `@.cursor/memory/INDEX.md` 的项目目录里现在没有文档部分的索引吗？

答案是：

- **不是完全没有**
- **但不完整，且不够稳**

原因如下。

#### D1. 它确实已经有“部分文档入口”

`INDEX.md` 当前已经列出了若干文档入口，例如：

- `docs/InfoCollections/HumanPlan/legacy.md`
- `docs/InfoCollections/Opus/INDEX.md`
- `docs/InfoCollections/SkillSeekers/INDEX.md`
- `docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md`

而且目录树里也出现了：

- `docs/InfoCollections/              # HumanPlan / MVPPlan / Opus / SkillSeekers / GPT`

所以严格说，**它并不是完全没有文档索引**。

#### D2. 但它没有“文档总索引”这一层

当前缺的不是零个链接，而是**结构化索引层**。  
具体表现：

- 没有专门的“文档总览”小节，统一列出 `HumanPlan / MVPPlan / Opus / SkillSeekers / GPT / middleaudit / references` 的职责、状态、入口
- 没有 `docs/InfoCollections/GPT` 的入口说明
- 没有区分“当前有效文档”与“历史/候选/归档文档”
- 没有说明 `middleaudit/` 在整个知识体系中的位置
- 没有给 `HumanPlan/` 和 `GPT/` 各自提供子索引文件

换句话说，`INDEX.md` 现在更像是“散落若干文档入口”，还不是“文档系统导航页”。

#### D3. 它列出来的文档入口里还有断链

一旦入口本身断链，比如 `bus server audit.md` 不存在，那么“有索引项”并不等于“索引可用”。

因此更准确的判断是：

- **有文档入口**
- **没有完整文档索引体系**

### E. 中优先级：`SkillSeekers/INDEX.md` 存在归档断链

`docs/InfoCollections/SkillSeekers/INDEX.md` 仍引用：

- `_archive_skill_seekers/skill_list_comprehensive.md`
- `_archive_skill_seekers/usage_and_api_guide.md`
- `_archive_skill_seekers/scripts_audit_20260228.md`

但当前仓库中未发现 `_archive_skill_seekers/` 目录。

同时，该文件第 76 行仍指向归档版 `skill_list_comprehensive.md`，而当前同目录下实际已经存在：

- `docs/InfoCollections/SkillSeekers/skill_list_comprehensive.md`

这属于典型的“索引未跟随归档清理更新”。

### F. 中优先级：`Opus/INDEX.md` 当前可读性异常

`docs/InfoCollections/Opus/INDEX.md` 通过读取工具显示时存在明显乱码/编码异常，导致：

- 标题和说明大面积不可读
- 索引本身的导航价值下降

即便文件路径仍可用，这也意味着：

- 当前 `Opus/INDEX.md` 作为“调研总入口”的可用性偏弱

建议后续确认该文件是否为编码问题、字符集问题，或历史文件保存格式不一致。

### G. 中优先级：`GPT/` 分区存在，但没有自己的入口索引

当前 `docs/InfoCollections/GPT/` 目录实际已存在，且至少包含：

- `2026-04-08_docker_skill_audit_report.md`

说明 `INDEX.md` 目录树里提到 `GPT` 并非凭空捏造。  
但当前问题是：

- `INDEX.md` 没有显式列出 `GPT/` 的用途与入口
- `GPT/` 目录本身没有 `INDEX.md`

这会导致新写入的 GPT 审查报告长期处于“存在但不容易被发现”的状态。

## 三、影响评估

这些问题对项目的影响主要有三层：

### 1. 对路由系统的影响

`workspace.mdc -> INDEX.md -> docs/*` 这条路由链目前不是全断，但已出现关键断点。  
一旦 Agent 或人按当前索引继续跳转，会撞到：

- 不存在文件
- 旧阶段描述
- 过时术语
- 超前目录树

### 2. 对“唯一真相源”定位的影响

`INDEX.md` 被标记为唯一真相源，但它里面目前同时混有：

- 当前现状
- 未来目标结构
- 历史入口
- 已失效入口

这会削弱“唯一真相源”的可信度。

### 3. 对后续审查/开发的影响

最容易出现的问题是：

- 误以为 `bus server audit.md` 是现成可读资料
- 误以为 Brain/Unity/infra/tests 骨架比实际更完整
- 误把 `Dispatcher` 当现行术语继续扩散
- 误把历史审计文档当当前执行说明

## 四、建议修复顺序

### P0：先修复断链和入口真假问题

1. 处理 `docs/InfoCollections/HumanPlan/bus server audit.md`
2. 若该文档已丢失，应从 `INDEX.md`、`workspace.mdc`、`legacy.md` 中移除或改指向
3. 若该文档应存在，则补回并重新确立其为东京双节点入口

### P1：把“当前现状”和“目标结构”分开

建议对以下文件做口径收缩：

- `.cursor/memory/INDEX.md`
- `.cursor/memory/active_context.md`
- `.cursor/memory/architecture/module_division.md`

原则：

- 当前实际存在的内容写成“现状”
- 尚未创建但准备要做的内容写成“目标结构”或“Phase 1 目标”
- 不要把未来文件列表写成已存在目录

### P1：统一术语和阶段口径

优先更新：

- `docs/InfoCollections/HumanPlan/legacy.md`
- `docs/InfoCollections/SkillSeekers/NANOBOT_LOCATION_AND_ROUTING_REPORT.md`
- `docs/InfoCollections/Opus/23_directory_audit_and_cursor_routing.md`

至少统一以下事实：

- 当前阶段不是 Phase 0
- 模块划分已完成
- 当前术语是 `Scheduler`，不是 `Dispatcher`

### P2：补齐文档索引层

建议新增或补强以下索引：

1. 在 `.cursor/memory/INDEX.md` 增加一个“文档导航”小节
2. 为 `docs/InfoCollections/GPT/` 增加 `INDEX.md`
3. 为 `docs/InfoCollections/HumanPlan/` 增加索引，说明哪些是当前有效，哪些是历史摘要
4. 在 `INDEX.md` 中明确：
   - `Opus` = 调研遗产
   - `MVPPlan` = 候选计划参考
   - `HumanPlan` = 人工确认摘要
   - `SkillSeekers` = 技能/参考资料索引
   - `GPT` = 机器审查与专项报告
   - `middleaudit` = 中期审计与阶段性材料

### P2：清理次级断链

建议处理：

- `SkillSeekers/INDEX.md` 中 `_archive_skill_seekers/*` 的失效引用
- `Opus/INDEX.md` 的编码/可读性问题

## 五、关于 `INDEX.md` 文档索引问题的直接回答

如果只问一句：

> `INDEX.md` 现在有没有文档部分的索引？

最准确的回答是：

**有，但只是“零散入口”，还不是“完整文档索引”。**

更具体一点：

- 它已经能把你带到部分文档分区
- 但没有把整个 `docs/` 体系系统化整理出来
- 而且部分入口已经失效
- 所以从使用体验上看，确实可以认为“文档索引还没建完整”

## 六、建议的最小改造目标

若只做最小闭环，建议以以下标准为完成线：

1. `INDEX.md` 中所有文档入口都必须存在
2. `INDEX.md` 单独有“文档导航”小节
3. `GPT/` 和 `HumanPlan/` 至少各有一个可用入口
4. 所有“当前阶段”描述都统一到 `active_context.md`
5. 所有“目标结构”描述都显式标注为目标，而不是现状

---

如果后续要继续修，我建议先改 `INDEX.md` 和 `workspace.mdc`，因为这两处是所有后续路由的总开关。
