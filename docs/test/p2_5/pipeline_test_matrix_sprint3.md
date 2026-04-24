# P2.5 / Sprint 3 — 端到端数据流测试矩阵（可填表）

> **位置说明**：本文件位于 **`docs/test/p2_5/`**（Git 跟踪，可 push）；与 **`tests/`**（pytest）区分。原 **`Test/`** 目录在 `.gitignore` 中**不会进远程**，请勿再把唯一真源只放在 `Test/`。  
> **关联**：`architecture/sprint3_completion_report_20260423.md` §7 AC 表（摘要）← 本表为 **展开版**（含日志对表、目的标签）。  
> **Unity 会话留档**：`docs/report/2026-04-23_unity_parrotdev_sprint3_ar_testing_context.md`（含 §10.5 测试 vs 产品设计边界）。  
> **ECS 同步**：`git push` 后 Castle `git pull` 即得本文；nanobot persona 仍走 `sync-castle.ps1 -Workspace`（见 `commit_guidelines.md` §2）。  
> **远端独立报告**：见同目录 **`ECS_RUN_REPORTS/README.md`**（新建 `report-*.md`，避免多人改矩阵冲突）。

---

## 0. 三阶段顺序（先 Editor，再真机 — 日志对齐）

**原则**：**P0 → P1 → P2** 不可颠倒；同一阶段内按小节步骤号做。**日志**里会按时间出现 `[SEQ] …`（阶段边界）+ `[SelfTest]` / `[RpcRtt]` / `[RoomManager]`（具体动作），写 **§F 报告** 或 **`ECS_RUN_REPORTS/report-*.md`** 时按时间抄即可对齐。

| 阶段 | 名称 | 是否 Play | 做什么 |
|:---|:---|:-----------|:--------|
| **P0** | 工程静态 + Unity 设置 | **否** | 打开 `unity/ParrotDev` → **Console 无红错**（可 `Clear`）→ **Project Settings** 按 `docs/report/2026-04-23_…` §2 核对 XR / Input → 菜单 **`Parrot/Test/Editor/Sequence — Log P0 static checklist done`** 点一次（打 `[SEQ] P0-done…` 到 Console；若已在 Play 且场景有 `ParrotDiagnostics` 则同时进 `parrot_diagnostics.log`） |
| **P1** | Editor-only 联调 | **是** | 只做 **§B 打勾 → §C**（`Dev.unity` 七步）；**不要**在此阶段要求 AC1–AC8 全过 |
| **P2** | 真机 APK + Launcher | **设备** | **§D** AC1→AC8；与 Castle 日志对表 |

**容灾（已落地到代码）**：诊断 HUD 的 **OnGUI** 若抛异常会 **打日志但不退出 Play**；Self-test / RTT **单步失败** 不中断后续样本；详见 `ParrotRuntimeHud` / `ParrotRpcRttProbe`。

---

## A. 文档对齐关系（谁听谁的）

| 文档 | 实习生怎么用 |
|:-----|:-------------|
| **本文件 §0 → §B → §C / §D** | **唯一推荐操作顺序** — 先 **P0**，再 **P1（§C）**，通过后再 **P2（§D）**。 |
| **本文件 §3** | 每一步做完在矩阵对应 **ID** 行打 `状态`，并填「Unity 锚点 / 后端锚点」。 |
| **`.cursor/memory/architecture/sprint3_completion_report_20260423.md` §7** | **需求验收口径**（AC1–AC8 一句话）；状态栏与 §3 里 **AC 行**同步勾选。 |
| **`docs/report/2026-04-23_unity_parrotdev_sprint3_ar_testing_context.md`** | 工具从哪来、AR/XR 注意点；**若与操作顺序冲突，以本文件 §0/§C/§D 为准**。 |
| **`HANDOFF_ACTIVE_CONTEXT_FOR_ECS.md`** | 真 `active_context.md` 不进 Git 时，把 **脱敏进度** 填给远端。 |

---

## B. 动手前核对（易错 — P0 + 进 P1 前全打 ✓）

- [ ] **P0 已完成**：Console 无编译红错；XR / Player 已按留档核对；已点 **`Sequence — Log P0 static checklist done`**（或 §F 手写等效一行）。  
- [ ] Unity **2022.3 LTS**，工程 `unity/ParrotDev`。  
- [ ] 测 **Editor 菜单** 的项：必须已进入 **Play Mode**（否则菜单会弹窗提示）。  
- [ ] 测 **断连 / RTT**：先确认 **Brain 已在房**（HUD 里 `Brain agent: yes` 或 Self-test OK）。  
- [ ] **勿**把 **JWT / Mint secret** 贴进 IM、报告全文；报告里只写 **token 长度或有无**。  
- [ ] **Dev.unity** = 集成台；**AC1–AC2、Launcher 流程** = 真机为主（与留档 §10.5 一致）。  

---

## C. P1 — Editor（`Dev.unity`）— 固定顺序 7 步 → 对应矩阵 ID

**进入条件**：**§0 的 P0** 已完成。按序号执行；**每步通过再做下一步**。

| 步 | 操作（复制菜单名） | 通过判据（一眼） | 填 §3 行 ID |
|---:|-------------------|------------------|-------------|
| 1 | 打开 `Dev.unity`，菜单 **`Parrot/Sprint3 — Augment Open Scene (AR + receivers)`** | Hierarchy 有 AR Session / XR Origin；有 `ParrotDiagnostics`（Augment 会顺带加） | 场景就绪（可不填行，或备注在 T-SELF-01） |
| 2 | 若无诊断根：菜单 **`Parrot/Test/Editor/Add Runtime Diagnostics (HUD + Log + SelfTest)`** | 有 `ParrotDiagnostics`，其上有 **ParrotRpcRttProbe** 组件 | 同上 |
| 3 | 点击 **Play** | 左上角 HUD 出现；约 10s 内 `LiveKit: ON`（视网络） | **T-LK-01** |
| 4 | 看 HUD：`Brain agent: yes` | 若为 `no`，等几秒或查 Brain 是否进同一 room | **T-LK-01**（备注 Brain 延迟入房） |
| 5 | 键盘 **F3** → **`Run self-test`** | `parrot_diagnostics.log` 或 Console 有 `[SelfTest]` 块；无连续 FAIL | **T-SELF-01** |
| 6 | 仍 F3 面板 → **`Brain RPC RTT x3`** | 出现 `[RpcRtt]` 三行 OK + `RTT avg …ms` | **T-RPC-01** |
| 7 | （可选）菜单 **`Parrot/Test/Editor/Network — Disconnect → wait 1s → Reconnect`** | 重连后 HUD `LiveKit: ON` | **T-LK-02** |

**菜单全文（防抄错）**  
- `Parrot/Test/Editor/RPC — Brain RTT (onGosloPlaced x3, Play Mode)` ≡ 与步 6 同一探针。  
- `Parrot/Test/Editor/Network — Disconnect → wait 1s → Reconnect` ≡ 步 7。

---

## D. P2 — 真机（Launcher / APK）— AC1–AC8 与报告对齐

**进入条件**：**P1（§C）** 已通过或已知缺陷已记录（不要带着「未名红错」直接打 APK）。**验收一句话**仍以 **`sprint3_completion_report_20260423.md` §7** 表格为准；按下面 **顺序** 做，并在 **§7 同一行** 改 `状态` 列（⬜→✅/❌）。

| 顺序 | AC | 做什么（摘要） | 与 §3 矩阵 |
|---:|:---|:----------------|:-----------|
| D1 | **AC1** | 装 APK → Launcher → 权限全允许 → 就绪 | `[产品]`；矩阵 **AC1–AC8** 行 |
| D2 | **AC2** | 点连接 → Mint 成功 → 连接成功 | 同上 |
| D3 | **AC3** | 进 AR → 问候（`onSceneReady` 链） | **T-RPC-02** |
| D4 | **AC4** | 点平面放 GOSLO → Brain 见 `onGosloPlaced` | **T-RPC-03**、**T-AR-01** |
| D5 | **AC5** | 语音「视频全开」→ tier / bitrate | **T-VID-01** |
| D6 | **AC6** | 「视频关闭」→ mute / DSG | **T-VID-01** |
| D7 | **AC7** | 断网 30s 等恢复（A10 心跳链） | **T-LK-02** 仅 Editor smoke **不能替代**；以 AC7 为准 |
| D8 | **AC8** | 切 Profile → `setScene` | **T-RPC-04** |

---

## E. AC ↔ 矩阵 ID 速查（填表不串行）

| AC | 必覆盖矩阵 ID（证据可共用） |
|:---|:----------------------------|
| AC3 | T-RPC-02 |
| AC4 | T-RPC-03, T-AR-01 |
| AC5 | T-VID-01 |
| AC6 | T-VID-01 |
| AC7 | （真机专项；Editor 只做 T-LK-02 参考） |
| AC8 | T-RPC-04 |

---

## F. 测试报告最小回填（贴到 §7 下方或 PR 描述）

```
日期(UTC): 
执行人: 
Git SHA: 
环境: Editor / 真机型号: 
P0 完成: 是/否  ([SEQ] P0-done 或 §F 手写)
P1 步 C1–C7: 通过 __ 失败 __ (步号:__)
真机 AC1–AC8: 通过 __ 失败 __ (AC号:__)
parrot_diagnostics.log: 有/无 路径摘要:
Brain 日志锚点: 一行 grep 关键字 + 时间:
备注(一条): 
```

**ECS 远端追加**：可复制 §F 块到 **`ECS_RUN_REPORTS/report-YYYYMMDDThhmmZ-{id}.md`**（见该目录 `README.md`），与主矩阵 **脱钩** 防冲突。

---

## 0.1 策略：现在测还是等 Sprint 4？

| 问题 | 建议 |
|:-----|:-----|
| 要等 Sprint 4 再测吗？ | **不必等**。当前矩阵覆盖的链路（Token、进房、RPC、视频 tier、断连 smoke）**现在就能**给 Sprint 4 提供瓶颈方向（例如信令 RTT vs 视频重建时序）。 |
| Sprint 4 之后多测什么？ | **相机采样 / identify_object 升级版 / Gemini 视觉通道** 的门控与 **体感人机** — 依赖 Sprint 4 代码后再扩行。 |
| 「相机模式 / 发现链路」性能 | **信令与控制面**（本表 T-RPC-01、连接耗时）**现在可测**；**编码码率、帧抓取、全链路视觉延迟** 以 Sprint 4 实现后再作为主 KPI。 |

---

## 1. 测试目的标签（填写时必填其一）

| 标签 | 含义 |
|:-----|:-----|
| `[连通]` | LiveKit 房间 / 断连 / 重连 |
| `[RPC]` | LiveKit PerformRpc（多为 **Unity→Brain**；`T-RPC-01` 仅测该向的往返时延，**不含** Brain→Unity 工具链） |
| `[视频]` | ARVideoPublisher / tier / mute / 重建 |
| `[AR]` | AR Foundation / 平面 / 锚点 |
| `[产品]` | Launcher 启动、权限、Mint — **与 harness 分离**（见留档 §10.5） |
| `[后端]` | 需对照 Castle / `tmux` Brain 日志 |

---

## 2. 后端日志从哪里来（对表用）

| 来源 | 典型命令 / 位置 | 在本表「后端锚点」列写什么 |
|:-----|:----------------|:---------------------------|
| Brain（Gemini Live + RPC） | Castle 上 `tmux attach -t brain`（或你实际 session 名） | 贴 **同一 UTC 时间** 附近含 `onGosloPlaced` / `setScene` / `push_video_tier` / `onSceneReady` 的一行 |
| Token Mint | `docker compose logs token-mint` 或 API 访问日志 | `/mint` HTTP 状态 + 响应体 **长度**（勿贴 JWT 全文） |
| LiveKit Server | `docker compose logs livekit` | `participant_connected` / `track_published` 关键字行 |
| Redis / BB（可选） | `redis-cli` 查 `tick/last_rpc_ack`、`session/scene` | 键名 + 摘要值 |

**给执行测试的人一段「后端任务介绍」**（可贴到 runbook 顶部）：

1. 启动 Castle 上 `redis` + `livekit` + `brain` + `token-mint`（与 `docker-compose.yml` 一致）。  
2. Brain 使用当前 Sprint 默认模型/语音（见 `ParrotConfig` / 环境变量）；确保 **Unity 与 Brain 进同一 room**。  
3. Unity 身份前缀 `unity*`；Brain 侧参与者一般为 `agent-*` 或 `brain` — 客户端已用 `BrainParticipantResolver` 统一解析。  
4. 对表时：**Unity** `parrot_diagnostics.log` + **Console** `[RpcRtt]` / `[RoomManager]` / `[SelfTest]` 与 **Brain 终端** 同一分钟内。

5. **Remote SSH 上另开 Cursor 陪跑**：把 **`docs/test/p2_5/remote_cursor_test_monitor_boot_prompt.md`** 里「引用区」整段贴进新会话；远端先 **`git pull`**。

---

## 3. 测试矩阵（主表）

| ID | 目的标签 | 用例简述 | 前置条件 | 执行步骤（摘要） | Unity / 设备锚点 | 后端锚点 | 通过标准 | Sprint | 状态 |
|:---|:---------|:---------|:---------|:-----------------|:-----------------|:---------|:---------|:-------|:-----|
| T-LK-01 | `[连通]` | 首次进房 | LiveKit + token 有效 | Play / 启动场景，等待 `RoomManager` 连上 | Console `[RoomManager] Connected`；HUD `last connect` | LiveKit participant | 10s 内 `IsConnected` | S3 | ⬜ |
| T-LK-02 | `[连通]` | Editor 断连→1s→重连 | Play + Diagnostics | 菜单 `Parrot/Test/Editor/Network — Disconnect → wait 1s → Reconnect` | `[EditorTest]` + `[RoomManager]` | 可选：LiveKit disconnect 日志 | 重连后 HUD `LiveKit: ON` | S3 | ⬜ |
| T-RPC-01 | `[RPC]` | Unity→Brain 轻载 RPC RTT | 已连房且 Brain 在房 | F3 → **Brain RPC RTT x3** 或菜单 `Parrot/Test/Editor/RPC — Brain RTT…` | `[RpcRtt]` 三行 OK + `RTT avg …ms` | `onGosloPlaced` log 行 | 3/3 成功，记录 avg ms | S3 / P2.5 | ⬜ |
| T-RPC-02 | `[RPC]` | onSceneReady 问候闭环 | 同 T-LK-01 | 连上后等待 ~0.5s 自动触发 | `[RoomManager] onSceneReady sent` | `onSceneReady: greeting generated` | 无 RPC error；听到/看到问候（主观） | S3 | ⬜ |
| T-RPC-03 | `[RPC]` | 放置上报 | AR 平面可点 | 点击平面放置 GOSLO | `[TapToPlace]` | `onGosloPlaced` | 无 error | S3 | ⬜ |
| T-RPC-04 | `[RPC]` | setScene | `SceneProfileManager` 在场景 | 切换 AR / Webcam profile | Console `[SceneProfileManager] setScene` | `setScene RPC: session/scene` | BB / 日志场景一致 | S3 | ⬜ |
| T-VID-01 | `[视频]` | tier 下行 | `VideoTierReceiver` 已绑定 | 语音或工具触发 `setVideoTier` | HUD `Tier:` 变化 | `push_video_tier` / supervisor 日志 | 与指令一致 | S3 | ⬜ |
| T-VID-02 | `[视频]` | track 重建 | 发布中 | 切 tier 触发重建 | `[ARVideoPublisher]` | `onVideoDegraded` / obs | 无 NullRef；轨恢复 | S3 | ⬜ |
| T-AR-01 | `[AR]` | 平面 + 锚点 | XR / ARCore 已配置 | 射线命中平面放置 | AR Session state | — | 稳定锚定 | S3 | ⬜ |
| T-SELF-01 | `[连通]` | Self-test 快照 | Diagnostics 根物体 | F3 → Run self-test | `[SelfTest]` 块 | 可选 | WARN 可接受；FAIL 需解释 | S3 | ⬜ |
| **AC1–AC8** | 混合 | **验收状态只填一处**：`architecture/sprint3_completion_report_20260423.md` **§7** | 真机 + Launcher | **操作顺序按本文件 §D** | 按 §7「预期」列 | 按 §7 表 | 在 **§7** 勾选 ⬜/✅/❌ | S3 | （在 §7 维护） |

**说明**：`T-RPC-01` 使用 **已有** `onGosloPlaced` handler，**不新增** Brain RPC 名；测的是 **PerformRpc 往返 + Python 侧极轻逻辑**，不是 Gemini 延迟。

---

## 4. Unity 菜单 ↔ UI 对照（防「脚本有了但 UI 没有」）

| 能力 | Editor 菜单路径 | Runtime UI |
|:-----|:-----------------|:-----------|
| **P0 顺序锚点** | `Parrot/Test/Editor/Sequence — Log P0 static checklist done (no Play required)` | — |
| 加诊断根（HUD + Log + SelfTest + **RTT**） | `Parrot/Test/Editor/Add Runtime Diagnostics (HUD + Log + SelfTest)` | — |
| 断连 / 重连 smoke | `Parrot/Test/Editor/Network — …` | — |
| Brain RPC RTT x3 | `Parrot/Test/Editor/RPC — Brain RTT (onGosloPlaced x3, Play Mode)` | F3 展开 → **Brain RPC RTT x3** |

---

## 4.1 测试 vs 产品 / Sprint 4 — 读法边界（**勿写进「最终 AR 结论」**）

**本矩阵与 Editor 工具链的定位**：P2.5 / Sprint 3 **总线、数据流、信令与粗略性能**验证；**不是** shipped AR App 的完整启动与画质门控。**无对错之分**：Editor **XR Simulation** 与 **真机 ARCore** 不等价，分行记录即可。

| 概念 | 本阶段（测试） | Sprint 4 / AR 工作区（产品与设计） |
|:-----|:---------------|:-------------------------------------|
| **Editor XR Sim / 模拟器 AR 相机画面** | **补充通道 / 按需**：进 LiveKit 的轨可作连通、tier/mute、**截图/短片段/粗性能**烟测；**报告措辞上勿写成「产品主视频流」**（语义上按补充视觉探针记，与 shipped AR 采集分离）。 | 门控、采集策略、启动编排、**高质量主视频**来源与 **Identify / burst** 合同在此收口。 |
| **WebCam / Editor 强制 fallback** | 仅 harness 替身，避免零轨。 | 产品是否允许、何时切换，由 App 设计决定，**不得**从本阶段结果外推。 |
| **LiveKit RPC + DataChannel** | **补充 / 控制面**：场景、tier、工具 RPC 等；与「相机轨」分列写结论。 | Sprint 4 可扩展「测试菜单切流」等 — 宜避免长期把 **整屏渲染 GameView** 当高码率主源（性能差）；与 **ARVideoPublisher** 类注释一致。 |

**写报告时**：结论请标注 **环境（Editor Sim / Editor WebCam / 真机）**；**不要**用 Editor 结果替代「Sprint 4 AR 工作区最终验收」或 **AR app 启动设计**的签字依据。

---

## 5. 已知限制（写进结果里避免误判）

1. **RTT 数字**含 LiveKit 调度 + Python asyncio，**不等于**「用户说话→鹦鹉回答」延迟。  
2. **`onSceneReady`** 会触发 `generate_reply`，**不要**把它当作 RTT 探针。  
3. **Editor XR Simulation** 与 **真机 ARCore** 在相机与 IMU 上 **不等价** — 分行填结果。  
4. **产品级启动流程**仍未单独设计 — `[产品]` 行失败可能是 **流程缺口** 而非后端 bug（见留档 §10.5）。  
5. **`T-RPC-01` 复用 `onGosloPlaced` 语义**：探针载荷带 `rtt_probe`，与真机「点击放置」共用同一 RPC 名 — Brain 端若只按「次数」统计会 **与真实放置混淆**；对表时请读 **payload / 时间窗** 或依赖 Unity 侧 `[RpcRtt]` 锚点。若未来要完全分离语义，再考虑专用 `echo` RPC（需 Brain 合同）。

---

*填表约定：`状态` 用 ⬜ 待测 / ✅ 通过 / ❌ 失败 / ⚠️ 不稳定；每次运行记 **Git SHA + Build 类型 + 设备型号**。*