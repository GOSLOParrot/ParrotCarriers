# ParrotCarriers Phase 1 Bus 架构审查与 ModuleManifest 溯源报告

> 日期：2026-04-08  
> 范围：`.cursor/memory/architecture/module_division.md`、`.cursor/memory/architecture/bus_v4.md`、`.cursor/memory/BigIssue.md`、`docs/InfoCollections/Opus/24_parrotcarriers_bus_architecture.md`、`src/parrot/bus/*.py`、`src/parrot/scheduler/*.py`  
> 口径：本报告审查的是 `Phase 1` 的模块划分、职责边界和逻辑风险，不是网络攻防或上线安全审计。

## 一、本次结论

先给结论：

1. 当前 `bus / brain / scheduler / dsg / shared / nanobot` 的模块大方向是合理的，没有发现根本性的模块拆分错误。
2. 当前最主要的问题不是“模块名错了”或“目录分错了”，而是一些边界还停留在文档/候选协议层，没有真正变成运行时约束。
3. `ModuleManifest` 确实可以溯源到更早的计划稿，带有明显的“预设计”血统；但当前文档体系已经多次把它标成“候选口径”，所以现阶段的问题不是“它存在”，而是“后续是否会被不加区分地固化”。

换句话说：

- `模块边界级预设计`：当前是必要且合理的。
- `字段级协议冻结`：当前不应该发生。

## 二、对当前模块划分的判断

### 2.1 大方向是对的

当前顶层划分与文档口径基本一致：

- `bus` 负责挂载、注册、心跳、Processor hook，作为总线外壳存在，这个定位成立。
- `brain` 负责 Agent/Tool 前台交互与实时入口，这个定位成立。
- `scheduler` 从 `brain` 中拆出来，预留从 `SimpleRouter` 演化到更复杂调度器的空间，这个方向是对的。
- `dsg` 独立为 Phase 2 感知模块，并且允许单独落在 `Mecha A10`，这也是合理拆分。
- `nanobot` 保持独立仓库、作为 Integration 模块去适配，这一点反而是比较干净的边界。

所以从“模块划分是否完全跑偏”这个角度看，答案是：**没有跑偏**。

### 2.2 当前真正的风险点

真正需要警惕的，不是顶层模块是否成立，而是下面三件事：

1. 分层声明还没有完全落到运行时约束。
2. `ModuleManifest` 有演化成“大一统协议包”的风险。
3. 调度与共享状态仍然偏“隐式约定”，后续容易长出模块间隐形耦合。

## 三、Top 3 结构性问题

### 3.1 `L1/L2` 分层目前是“设计成立”，但还不是“运行时成立”

`bus_v4.md` 已经很明确地区分了：

- 路径 A：`L1 + L2 (+L3)` 模块
- 路径 B：`L2 (+L3)` 模块

而当前代码中的 `mounting.py` 虽然保留了这两个路径，但两者的真实差异还非常有限：它们目前都只是“注册 Redis + 启动心跳”的变体。

这意味着当前分层成立的方式，仍然主要靠：

- 文档说明
- 注释
- `manifest` 的声明字段

而不是靠一个真正会约束模块生命周期的挂载流程。

这不是说当前实现错了，而是说明：

**你现在完成的是“模块边界的预设计与骨架化”，不是“边界已被系统强制执行”。**

这点必须在报告里说清，否则后面很容易产生一种错觉：好像 `L1/L2` 边界已经在代码里落地了。实际上还没有。

### 3.2 `ModuleManifest` 已带明显预设计来源，最大风险是变成 God Contract

当前 `src/parrot/bus/manifest.py` 的 dataclass 不是凭空长出来的，它明显继承了更早文档中的接口草案。

问题不在于“manifest 出现了”，而在于它天然容易承载过多东西：

- 模块身份
- 层级参与
- LiveKit 能力
- Redis 通道
- Blackboard 键访问
- Graphiti 分区
- 外部渠道
- 运行时约束

如果这些字段都被提前当成正式协议，就会出现两个后果：

1. 模块边界会被一个大 dataclass 重新揉平。
2. 协议会从“候选挂载清单”滑向“必须完整填写的冻结 schema”。

这正是 `.cursor/memory/BigIssue.md` 已经点名过的风险：

> 不要先在纸上定义完整 `ModuleManifest` 字段，再反过来按字段写代码。

所以我对 `manifest` 的判断是：

- 现在保留它，作为 `候选挂载清单`，是合理的。
- 现在就把它扩成最终协议，或者围绕它提前补全所有字段，是不合理的。

### 3.3 `Scheduler + Blackboard` 仍偏隐式协作，后续最容易形成逻辑耦合

当前 Phase 1 作为 demo/骨架，这样写是自然的；但从架构角度看，这里已经暴露出一个长期风险：

- `router.py` 目前吃的是 `dict[str, Any]`
- `blackboard.py` 目前写的是自由格式 `key/value`
- 任务类型、状态结构、结果回写、失败语义都还没有形成最小契约

这会导致一个非常典型的问题：

模块目录虽然已经拆开了，但运行时真正协作时，仍然可能依赖“大家默认知道某个 dict 里有什么字段、某个 blackboard key 里放什么”。

这种耦合在 demo 阶段很隐蔽，因为它一开始看起来特别灵活；但一旦：

- `brain`
- `scheduler`
- `nanobot`
- `dsg`

同时开始向 `L2` 层写入和消费状态，它就会迅速变成后续最难清理的逻辑债。

所以这里的核心问题不是“现在要不要立刻冻结字段”，而是：

**在模块划分已经成立后，下一步应该优先收口最小消费契约，而不是继续扩字段表。**

## 四、`ModuleManifest` 来源溯源

这里直接回答你的问题：**是的，当前 `ModuleManifest` 非常大概率来源于计划阶段出现的预设计，而且这个来源链是可以明确追出来的。**

### 4.1 来源链条

#### 第一层：`plan03` 的概念源头

在 `docs/InfoCollections/Opus/24_parrotcarriers_bus_architecture.md` 中，已经明确写出：

- `plan03` 的核心思路是“三插槽”
- 但“三插槽只是概念描述，没有接口定义”

因此它给出的改进动作是：

- **定义 `ModuleManifest` 协议**

这说明 `ModuleManifest` 的原始动机并不是来自现有代码，而是来自对早期计划稿的“接口形式化”。

#### 第二层：`Opus 24` 把概念形式化为 dataclass

同一份文档在 `3.1 ModuleManifest 定义` 中，已经给出了一版非常完整的 `ModuleManifest` dataclass，包含：

- `version`
- `livekit_identity`
- `rpc_methods_provided`
- `rpc_methods_consumed`
- `tracks_published`
- `tracks_subscribed`
- `data_channels`
- `redis_channels_publish`
- `redis_channels_subscribe`
- `blackboard_keys_read`
- `blackboard_keys_write`
- `graphiti_partitions`
- `requires_gpu`
- `min_memory_mb`
- `health_check_interval_s`

这已经不是“一个轻量挂载清单”，而是明显带有较强预设计色彩的候选协议草案。

#### 第三层：`bus_v4.md` 继承并重新降级为“候选字段”

到 `.cursor/memory/architecture/bus_v4.md`，`ModuleManifest` 被继续保留，但文档口径已经明显更谨慎：

- 明确标注为 `候选方向`
- 明确写出“具体字段需代码验证后收敛”
- 为了支持 `L2-only` 模块，又新增了 `layers_participated`
- 为了支持双入口模块，又新增了 `external_channels`

也就是说，`bus_v4.md` 没有否定 manifest 这个想法，但开始承认：

**它是候选契约，不是已经证成的最终协议。**

#### 第四层：当前代码实现是一个“裁剪版 manifest”

当前 `src/parrot/bus/manifest.py` 又从 `bus_v4.md` 继续裁掉了一部分字段，保留了一个更轻的版本。

当前代码相对于更早的文档版，至少做了这些收缩：

- 去掉了 `version`
- 去掉了 `tracks_published`
- 去掉了 `tracks_subscribed`
- 去掉了 `data_channels`
- 去掉了 `min_memory_mb`
- 把 `layers_participated` 简化成了 `layers`

这个收缩动作本身是一个正信号，说明当前代码并没有无脑照抄最重的预设计版本。

### 4.2 溯源结论

因此，比较准确的说法不是：

- “当前 manifest 完全是凭空胡思乱想”

而是：

- “当前 manifest 源于计划阶段的预设计草案，之后经过 `Opus 24 -> bus_v4 -> 当前代码` 的逐步裁剪和降级”

所以答案是：

**会，而且已经发生过。`ModuleManifest` 的确带着计划稿时期的预设计遗产。**

但同时也要补一句：

**当前项目文档并没有掩盖这件事，反而已经在多处明确承认它只是候选口径。**

## 五、如何区分“合理预设计”与“过度预设计”

你刚才提醒得很对：不能把“代码验证”拔高到压过“协议制定”和“预设计”的位置。

我对这个边界的判断是：

### 5.1 当前合理且必要的预设计

下面这些东西，属于 Phase 1 非常合理的预设计：

- 顶层模块边界：`bus / brain / scheduler / dsg / nanobot`
- 三层总线分层：`L1 / L2 / L3`
- 路径 A / 路径 B 的挂载思路
- `module_id` / `module_type` / `layers`
- `requires_gpu`
- `health_check_interval_s`

这些内容属于“你必须先把地图画出来，后面才能知道往哪写代码”。

### 5.2 当前已经偏重、需要持续警惕的预设计

下面这些字段更接近“未来可能成立，但现在还不宜被当成正式协议”：

- `rpc_methods_provided`
- `rpc_methods_consumed`
- `blackboard_keys_read`
- `blackboard_keys_write`
- `graphiti_partitions`
- `external_channels`
- 更早版本里的 `tracks_*`、`data_channels`、`min_memory_mb`

原因不是它们没有价值，而是：

- 当前消费代码还不完整
- 运行时约束还没落地
- 这些字段一旦被测试、注册逻辑、部署脚本提前依赖，就会反向锁死实现

所以真正该防的不是“出现预设计”，而是：

**候选字段太早被误当成正式契约。**

## 六、协议应该在什么时候定

这部分直接回答你后面最关心的问题：**挂载协议、任务协议、Blackboard 约定，到底该在什么时候定。**

我的建议不是“现在都别定”，而是把协议分成两类：

- `先定边界级协议`
- `后定字段级协议`

### 6.1 现在就应该定下来的东西

现在就可以定，而且应该定下来的，是那些**不定就没法继续写代码**的边界：

- 模块有哪些顶层类型：`CORE / PERCEPTION / WORKER / BRIDGE / CLIENT`
- 模块参与哪些层：`L1 / L2 / L3`
- 挂载生命周期有哪些阶段
- 哪些模块属于 `L1+L2`，哪些属于 `L2-only`
- `Bus heartbeat` 和 `nanobot heartbeat` 不是一回事

这些东西属于“地图级定义”，不是过度设计。

### 6.2 现在不应该定死的东西

下面这些内容现在最多保持“候选”，不要急着写成正式 `v1`：

- `rpc_methods_provided` / `rpc_methods_consumed` 的完整字段表
- Blackboard 键全集
- `dispatch` / `results` 的最终 envelope 结构
- Graphiti 分区的最终写入协议
- 外部渠道如何映射到 Bus 的最终消息格式

原因很简单：

- 这些内容都依赖真实消费方出现
- 现在还没有足够多的真实调用路径
- 一旦过早定死，后面会反过来绑架实现

### 6.3 挂载协议 `v1` 应该在什么时候冻结

我的建议是：**不要现在冻结 `Mount Protocol v1`，而是在 Phase 1 的三个最小挂载场景跑通之后再冻结。**

推荐的冻结条件是同时满足下面三条：

1. 一个 `L1+L2` 模块能完整挂载、上线、下线。
2. 一个 `L2-only` 模块能完整挂载、上线、下线。
3. 至少观察过一次真实的重启、离线、重新挂载或心跳超时恢复。

换成你这个项目里更具体的话，就是：

1. `Brain` 或 `Scheduler` 先跑通路径 A。
2. `Nanobot Worker` 跑通路径 B。
3. 验证一次 `register -> heartbeat -> offline -> remount` 的真实行为。

**这三个点都跑过以后，再写 `Mount Protocol v1`，时机才对。**

### 6.4 其他协议应该在什么时候收敛

建议按“谁先有真实消费者，谁先收敛”的顺序来：

- `挂载协议 v1`：Phase 1 中段，路径 A/B 都跑通后。
- `dispatch/result 协议 v1`：第一条真实任务从 `Brain/Scheduler -> Nanobot -> 回写` 跑通后。
- `Blackboard 最小约定 v1`：至少两个模块共享并稳定消费同一批 key 之后。
- `Graphiti / L3 协议 v1`：Phase 2，接入真实写入链路后。

关键点不是“先有完整协议再写代码”，而是：

**先有最小跑通链路，再把已经被用到的部分收敛成 `v1`。**

## 七、有没有更好的挂载方式

有。当前文档里的 `路径 A / 路径 B` 作为思维模型是成立的，但如果问“实现上更稳、更不容易越写越乱的挂载方式是什么”，我更推荐：

- `文档上保留 A/B 口径`
- `实现上采用阶段式挂载 pipeline`

### 7.1 当前 A/B 的优点

当前 A/B 的好处是非常直观：

- A = `L1+L2(+L3)`
- B = `L2(+L3)-only`

这对模块划分和沟通都很好，所以**不需要推翻**。

### 7.2 更适合代码实现的方式：阶段式挂载

比起“如果是 A 就走这一套、如果是 B 就走另一套”，更稳妥的实现思路是把挂载拆成几个阶段：

1. `preflight`
2. `attach_l1`（如果模块参与 `L1`）
3. `attach_l2`（如果模块参与 `L2`）
4. `attach_l3`（如果模块参与 `L3`）
5. `start_optional_gateways`（如果模块有外部渠道）
6. `start_heartbeat`
7. `publish_ready`

这样做的好处是：

- 不会因为后面多出 `L1+L3`、`L2-only+external`、`sentinel` 等变体，就把路径分支炸成一堆。
- `L2-only` 模块天然就是“跳过 `attach_l1` 的同一条流水线”，而不是另一套世界观。
- 更适合处理失败恢复、重连、幂等启动。
- 更容易测试每个阶段真正保证了什么。

### 7.3 我建议你把挂载协议 `v1` 定成“生命周期协议”，而不是“字段大全协议”

如果你要定 `Mount Protocol v1`，我建议它定的重点应该是：

- 生命周期阶段
- 每个阶段的前置条件
- 哪一步失败算“未挂载成功”
- 什么时候开始心跳
- 什么时候才算 `ready`
- 下线时按什么顺序停止

而不是先去定：

- 所有模块都要填哪些能力字段
- 所有通道都要怎么列全
- 所有 Blackboard key 都要提前报备

**换句话说，先把“怎么挂上去”定住，再把“挂上去以后会干什么”慢慢从代码里长出来。**

## 八、`ModuleManifest` 应该怎么设计

我建议你把 `ModuleManifest` 设计成一个**轻量挂载声明**，而不是“总线全知识总表”。

### 8.1 一个好用的判断标准

如果一个字段回答的是“这个模块挂载时，运行时框架必须立刻知道什么”，它适合放进 `manifest`。

如果一个字段回答的是“这个模块未来可能会做什么”，它大概率不适合放进 `manifest`，至少现在不适合。

### 8.2 现阶段建议保留在 `manifest` 里的内容

现阶段我建议只把下面三类东西放进去：

#### 第一类：身份

- `module_id`
- `module_type`

#### 第二类：参与层级

- `layers`
- `livekit_identity`，但只在参与 `L1` 时出现

#### 第三类：硬约束

- `requires_gpu`
- `health_check_interval_s`

这些字段有一个共同点：

- 它们直接影响挂载路径
- 直接影响生命周期
- 不需要等复杂消费代码出现才能成立

### 8.3 现阶段不建议塞进 `manifest` 的内容

下面这些更适合后续单独收敛，而不是现在一起塞进 `manifest`：

- 完整 RPC 方法清单
- Blackboard 读写键全集
- 任务消息 schema
- 结果消息 schema
- 详细 DataChannel 语义
- Graphiti 分区策略

原因不是它们不重要，而是它们属于**模块行为契约**，不是纯粹的**挂载事实**。

### 8.4 一个更健康的拆法

长期来看，我更建议你把这些东西拆成四层，而不是都塞给 `manifest`：

- `ModuleManifest`：我是谁，我挂哪些层，我有哪些硬约束
- `Mount Protocol`：我如何上线、下线、心跳、ready
- `Task/Result Envelope`：Scheduler 和 Worker 之间怎么通信
- `Blackboard Contract`：哪些共享状态已经稳定、哪些 key 可以跨模块依赖

这样一来，`manifest` 就不会变成 God Contract。

## 九、现在应该继续审，还是继续写代码

我的判断是：**大范围架构审计到这里可以先收手，应该继续写代码了。**

原因不是“审计没价值”，而是你现在已经过了“需要继续扩大审查范围”的阶段。

你现在最需要的不是再做一轮更大的审计，而是用代码把几个关键点撞出来：

1. 路径 A 真实挂载一次。
2. 路径 B 真实挂载一次。
3. `dispatch -> consume -> result` 真实跑通一次。

### 9.1 现在最合适的节奏

我建议你接下来按这个节奏推进：

1. 先继续写代码，不再做大范围审查。
2. 每跑通一条真实链路，就只做一次小范围收口。
3. 把“已经被真实代码消费的部分”升格成 `v1`。
4. 其他没被消费的字段继续保持候选。

### 9.2 什么叫“审计收手”

所谓“收手”，不是以后不审，而是：

- 不再围绕候选协议反复空转
- 不再为了未来模块把字段越加越全
- 不再在没有消费代码的前提下追求协议完美

### 9.3 什么时候再回来审

下一次适合回头审的时间点，不是“你有点不安的时候”，而是下面这些里程碑到了以后：

- 路径 A 第一次真实跑通
- 路径 B 第一次真实跑通
- Nanobot adapter 第一次真实吃到任务
- 结果回写第一次真实完成

到那时再回来看：

- `Mount Protocol v1`
- `dispatch/result v1`
- `manifest` 最小字段集

就会非常自然，而且不会空转。

## 十、当前结论

### 10.1 对模块划分的结论

当前 Phase 1 的模块划分总体合理，可以继续沿这个方向推进，不需要推倒重来。

### 10.2 对 `ModuleManifest` 的结论

`ModuleManifest` 的来源确实可以追溯到更早的计划稿与概念形式化，因此它带有明确的预设计背景。

但当前更准确的判断不是“manifest 不该存在”，而是：

- 它现在应该被视为 `候选挂载清单`
- 不应该被视为 `已冻结协议`

### 10.3 当前最该警惕的事情

当前最需要避免的不是继续做预设计，而是下面这件事：

**在尚未进入对应 Phase 的真实消费代码前，就让 `manifest` 的字段、Blackboard 键、任务格式过早固化。**

如果守住这条边界，那么你现在这套骨架是健康的。

如果失守，这套骨架后面最容易演化成：

- 目录看上去模块化了
- 实际协作却被一堆预先写死的字段表牵着走

---

## 附：一句话版本

当前架构方向是对的，`ModuleManifest` 也不是乱来，它确实来自早期计划稿的形式化产物；现在最好的策略不是继续扩大审计，而是继续写代码，把路径 A、路径 B 和第一条真实任务链路跑通，再把真正用到的那部分协议收敛成 `v1`。
