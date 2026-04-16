# P1 手测结果记录

> 不要在此文件写入 API 密钥、token 全文或 `.env` 内容。


## 历史记录

### 2026-04-11 — Python sim全链路（笔记本）

- **环境**: Windows；本机 Docker LiveKit dev；Brain `parrot.brain.agent dev`；sim `sim_unity_client.py --mic --full`。
- **链路**: 仅 **sim**（`unity-sim`），未跑 Unity Editor 同场。
- **T1 语音**: **通过** — 麦克风进房、Gemini 语音回复；TTS 经 sim 播放（24k 路径）；转写可见（房间流 + Brain `[Gemini·用户]` / `[Gemini·鹦鹉]`）。
- **T2 dance**: **通过** — 终端侧出现对 `animate` / dance 的 RPC 与工具调用痕迹。
- **T3 flyTo**: **通过** — `flyTo` 坐标类 RPC 与日志一致。
- **T4 Nanobot 链路**: **通过** — Scheduler + stub consumer 路径；Brain 侧 `dispatch_task` / 结果回流与语音播报相关日志可核对（架构上以指南「偏差声明」为准）。
- **T5 语音打断（可选）**: **未专项记录** — 日志侧可见 AEC/打断相关行时可备注；未单独记通过/失败。
- **其它**: 曾遇 LiveKit **401**（`.env` API secret 与 `livekit-dev.yaml` 不一致），对齐长 secret 后恢复；曾遇 **无 TTS**（sim 未播放远端音频）与 **长聊卡顿**（mic 回压队列），已在 sim 侧修复；**勿**将短效 JWT 写入版本库。

### 2026-04-11 — Unity Editor（单端）

- **环境**: 同4/11；Brain + Docker；`unity/ParrotDev` `Dev` 场景；token 经 `unity_join_token.txt` 或 Inspector。
- **链路**: 仅 **Unity**（`unity-dev`），无 `voice-user`。
- **结论**: **通过（接线）** — Console：`[RoomManager] Connected`、`+ agent-...`、`[ParrotRPC] Registered: flyTo, animate`、Agent 音频轨；可听到开场白。
- **说明**: 此模式 **无麦克风上行**，不覆盖「语音 → 工具」；T2–T4 语音驱动见 sim 或下方 B2。

### 2026-04-11 — Unity Play + `voice-user`（B2 全链路）

- **环境**: Windows；Docker LiveKit + Redis；Brain `parrot.brain.agent dev`；**先 Unity Play连上**，再 `sim_unity_client.py --identity voice-user --mic --no-agent-playback`（未在本次会话确认是否加 `--full`，**T4 以本行为准：若未加 `--full` 则本轮未测 Nanobot**）。
- **链路**: **`unity-dev` + `voice-user`**（房内仅一个 `unity*`，RPC 单播目标明确）。
- **T1 语音**: **通过** — 麦克风经 `voice-user` 进房；转写可见（含偶发 `<noise>`、多语言混用）；鹦鹉语音由 **Unity** 播放（`--no-agent-playback`）。
- **T2 dance / animate**: **通过（指令与 RPC）** — Unity Console 收到 `animate` / `dance`；无 Animator 时走 `ParrotController` **Dev 回退**（缩放 + Yaw 摆动；曾加强振幅以便 Game 视图可见）。
- **T3 flyTo**: **通过** — 例：`Fly to one to three` → 载荷 `(1,2,3)`、`Arrived at`；口述 `556` → 模型解析为约 `(5,5,6)` 并到达。
- **T4 Nanobot 链路**: **未在本次 B2 记录中确认** — 若仅 `--mic --no-agent-playback` 无 `--full`，则 **未跑** Scheduler/stub 路径；此前 **sim `--full`** 已单独验证过 T4。
- **T5 语音打断（可选）**: **未专项测**。
- **其它**:终端曾出现 `ignoring byte stream ... 'lk.agent.session'`（无回调，**未处理**）；会话结束 `voice-user` 侧 `Disconnected` 正常。**fly_to** RPC 在 Unity 侧于 **`FlyTo` 调用后即返回**，**无**「到达终点后再通知 Gemini」的独立回传（见架构说明，P1 不要求）。

---

## 未测 / 延后 / 已知缺口（汇总，截至 2026-04-11）

| 项 | 状态 | 备注 |
|:---|:-----|:-----|
| **T5 语音打断** | 未专项记录 | 可作烟测补一行 |
| **B2 + T4（Nanobot）** | 未与 Unity 同场确认 | 需要时在 `voice-user` 进程加 `--full` 再跑一轮 |
| **落地后再通知 Gemini** | 未实现 | 可行但非 P1；需 Unity 到达点 + Brain 订阅/注入 |
| **`lk.agent.session` 字节流** | 未接入 | 当前日志忽略，不影响本轮语音与 RPC |
| **Animator 真动画** | 未用资源验证 | Dev 仍为 Cube + 程序化回退；GOSLO/Clip 属后续美术 |
| **双 `unity*` 同场 RPC 争抢** | 刻意避免 | 设计为单 `unity*` + `voice-user`；未做压力/乱序测试 |
| **Nanobot 真检索与结果回填** | 未实现 | 当前 stub 无正文；胡编风险见本节「T4 Nanobot 时延与内容」 |

**总评**: P1 **主链路可行性已验证** — 含 **sim 全栈**、**Unity 接线**、**Unity + voice-user 语音驱动 RPC 与位移/动画回退**。上表缺口为 **增强项或后续阶段**，不推翻 P1 结论。

---

### 2026-04-11 — T4 Nanobot（stub）结果内容、时延与「胡编」说明**来源**: Cursor 采集的 sim 终端 `403624.txt`（`sim_unity_client.py --mic --full`，LiveKit 重启后一轮）。

**Nanobot / 调度是否在跑**: **是。** 日志可见 `Nanobot processing task: research (id=35be8363)`、`Task routed to: nanobot`、`Nanobot task completed`、`>>> NANOBOT RESULT: ... status=completed`；另有一条 `type=search_web (id=b5b639cd)` 几乎同一时刻完成。**未接 GOSLOParrot/nanobot 真 worker**，进程内为 **`NanobotConsumer` stub**（仅 echo `completed`），**不访问外网、不执行真检索**；你提供的 API 主要给 **Gemini Realtime**，不是给 stub 做搜索。

**「查到了什么」的正文有没有**: **没有。** Stub 发回 Redis Pub/Sub 的 payload 只有骨架字段（`task_id`、`type`、`status: completed`、`completed_at` 等），**无摘要、无链接、无检索结果**。Brain 侧再用 `generate_reply` 让模型「用鹦鹉口吻告诉用户完成了」——**模型没有真实材料可引用，容易听起来像查到了东西（胡编或泛泛而谈）**。这是 **当前仓库仅为项目骨架、未实现结果回填** 的预期现象，**不是**「Nanobot 模型选错」一类问题；要准需要真 worker 把结构化结果写进 result 再注入会话。

**主观「等了很久」vs 日志时间差**:

- 鹦鹉在转写里说完 *dispatched the search for "IPoAC"*约在 **23:55:07–23:55:10**。
- Stub 侧 **`Nanobot processing` / `NANOBOT RESULT`** 出现在 **23:57:22–23:57:23**。
- 粗算 **约 2 分 10秒～2 分 15 秒** 的间隔（与你体感「快一分钟」同量级；精确取决于你开口时刻）。  
- 同一秒内两条 result：`research` 与 `search_web` 完成时间戳相差约 **0.23s**，说明 **Scheduler → Stream → stub 消费 → publish** 在 **出结果那一刻是很快的**；**长等待主要不在这几段 Python**，而在 **Gemini Realtime 何时真正调用 `dispatch_task`、多轮语音与工具调度的节奏**（以及中间是否还有别的调度路径，例如同日志里 **23:55:02** 曾出现 `Task routed to: brain_direct`，与进 Nanobot 的条目不同时）。

**任务调度器「应该很快」**: **路由与 Redis 操作本身很快**；本轮日志也支持「一旦任务进 stub，毫秒～秒级就 `completed`」。体感慢 = **对话模型侧延迟 + 工具调用时机**，不是「Scheduler 用 Python 所以拖分钟级」。

**并行两任务**: 日志显示 **极短时间窗口内两条不同类型任务完成**（`research` 与 `search_web`），**可视为 stub 路径能连续处理多条**；**未**做严格压测（例如同时刻大量 dispatch、顺序与去重）。

**sim 里同一条 `NANOBOT RESULT` 多次打印**: 终端里同一 task出现多行相同 `>>> NANOBOT RESULT`（可能为 Pub/Sub 多订阅方或重复投递的观测现象）；**不影响**「stub 已跑通」的结论，细节未在本次深究。

**要不要复测**: 若要 **量化「从 dispatch_task 日志到 RESULT」** 纯链路时延，可在 Brain 日志里对齐 `dispatch_task: ...` 与 stub 的 `Nanobot processing`（本轮未把 Brain 子进程日志一并归档）。**功能上 stub 已连通**，复测优先级不高，除非要接真 Nanobot 或收紧 SLA。
