# 当前进度与下一步

> 最后更新: 2026-04-24 (Sprint 3 代码全落地，进入真机测试阶段)
> **当前阶段**: **Sprint 3 真机测试中** — Dev.unity 是集成测试舞台（非最终 AR App 场景），AC1-AC8 验收用例待用户跑完反馈
>
> **Dev.unity 定位说明**: Dev.unity = Editor + 真机 **集成测试场景**，用来验证 Bus/Brain/LiveKit/AR Foundation 各层接缝。不是最终要上线的 AR App 场景；AR App 前端（Launcher.unity + AR 主场景）在 P2.5 测试完成后独立搭建。
>
> **Sprint 3 完成报告 (in_testing)**: `.cursor/memory/architecture/sprint3_completion_report_20260423.md` — 测试中持续更新 AC 验收栏
> **Sprint 3 开工提示词**: `.cursor/memory/architecture/sprint3_kickoff_prompt.md`
> **Sprint 2 完成报告 (ratified)**: `.cursor/memory/architecture/sprint2_completion_report_20260423.md`
>
> **最新 commit**: `3254d2b` — gitignore mint secrets + Resources config examples + TokenService fallback path fix
>
> ---
>
> ## 整体计划路径（一张图）
>
> ```
> 现在
>  │
>  ├─ [Sprint 3 测试] Dev.unity 真机验收 AC1-AC8
>  │    目标: 确认 Token Mint / AR 平面 / GOSLO 放置 / 两轴模式 / Brain RPC 全通
>  │    工具: adb logcat + python src/scripts/tail_obs_log.py --stream both
>  │    反馈: 用户测试 → 补 Bug → 更新 sprint3_completion_report AC 栏 → ratified
>  │
>  ├─ [Sprint 4] captureSnapshot + 相机模式补充通道 + identify_object Path1 + 便签 UI + 食指 perching
>  │    前提: Sprint 3 AC1-AC5 通过
>  │    完成标志: P2.5 全部功能验收通过
>  │
>  ├─ [P2.5 收口] 全量功能测试完成 → 写 P2.5 completion report
>  │    标志: Sprint 0-4 全部 ratified，identify_object 三路全通，相机模式完整
>  │
>  ├─ [AR 工作区搭建] 基于已验证的各层接缝，独立构建 AR App 前端
>  │    内容: Launcher.unity 正式场景 + AR 主场景 + UI 完善 + GOSLO.glb 真模型
>  │    参考: ar_app_plan.md + ar_camera_interaction_survey.md
>  │    注意: 不重建后端！只是前端工程，所有 Brain/Bus/DSG 接口复用 Sprint 3-4 已验证的版本
>  │
>  └─ [各模块独立开发] AR 工作区稳定后，按模块边界拆分独立迭代
>       Brain Tools 扩展 → DSG 语义层深化 → Nanobot 任务调度 → Obsidian 双链 → 记忆蒸馏 …
>       （每个模块有独立的 skill/rule 文件，不再需要全局上下文对齐）
> ```
>
> ---
>
> **Sprint 4 核心目标**: captureSnapshot + 相机模式补充通道 + identify_object Path 1 (A10 CV) + 便签 UI + 食指 perching
>
> **Sprint 3 决策收口 (D1-D6)**:
>   D1: set_video_tier hold_seconds=300 (PARROT_OVERRIDE_HOLD_SECONDS 可配置)
>   D2: A10 heartbeat via Redis SETEX parrot:a10_heartbeat + asyncio task (src/parrot/a10/heartbeat.py)
>   D3: Token Mint Bearer secret, Unity 存 Resources/parrot_config.json（gitignored，见 parrot_config.json.example）
>   D4: 新增 TRACK_REBUILDING reason, 映射 PAUSED 跳过 Supervisor 降档计时
>   D5: Gemini 继续看纯摄像头画面, Sprint 4 再接合成帧
>   D6: GOSLO.glb 换上真模型 (Assets/Models/GOSLO.glb 29KB), AnimationDriver 用 Transform.Find() 查节点
>
> 部署快照: `.cursor/memory/deploy_snapshot_p2_20260412.md`
> **P2 里程碑**: `.cursor/memory/milestone_p2.md` (P2 已完成, 历史归档)
> 同步工具: `.cursor/memory/commit_guidelines.md` + `infra/sync-castle.ps1`
>
> **Sprint 3 验收用例 (用户测试中，反馈后更新下方栏)**:
>   AC1 ⬜ IQOO NEO9 → Launcher 权限弹窗 → 全部允许 → 就绪
>   AC2 ⬜ 点连接 → Token Mint 成功 → 房间连接 → "连接成功"
>   AC3 ⬜ AR 场景加载 → Brain onSceneReady → GOSLO 问候语播放
>   AC4 ⬜ 点 AR 平面 → GOSLO 放置 → onGosloPlaced RPC 上报
>   AC5 ⬜ 说"视频全开" → set_video_tier → BB=VIDEO_FULL → Unity track 重建
>   AC6 ⬜ 说"视频关闭" → VIDEO_OFF → track mute → DSG 切 PASSIVE
>   AC7 ⬜ 断网 30s → Supervisor 降级 → 恢复自动升档
>   AC8 ⬜ SceneProfileManager 切换 → setScene RPC → Injector C3/C4 更新

---

## 版本锁定表 (2026-04-20 已验证)

| 依赖 | pyproject.toml 约束 | Castle 已安装 | 说明 |
|:-----|:--------------------|:-------------|:-----|
| `livekit-agents[google]` | `>=1.5,<2.0` | 1.5.2 | 1.x 主版本内兼容 |
| `graphiti-core[falkordb,google-genai]` | `>=0.28,<0.29` | 0.28.2 | 紧锁 0.28.x，API 已验证 |
| `redis` | `>=7.1,<9.0` | **7.4.0** | **⚠️ 从 5.3.1 升级**，falkordb 1.6.0 要求 >=7.1 |
| `python-dotenv` | `>=1.0,<2.0` | 1.2.2 | — |
| `py-trees` | `>=2.4,<3.0` | 2.4.0 | — |
| `rustworkx` | `>=0.15,<1.0` | 0.17.1 | — |
| LiveKit Unity SDK | `#2a7c57d7bcad2305a75bc75218e8064ccd5d10bf` | 同上 | manifest.json 已锁 commit hash |

**Gemini 模型（.env 可覆盖，无需改代码）：**
```
GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
GEMINI_LIVE_VOICE=Puck
GEMINI_RERANKER_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

---

## 当前阶段: Sprint 0 前置规划 (进 Sprint 0 代码前的流程约束)

### 基础设施状态 (已验证, 无待办)
- Castle Brain Agent: 运行中 (tmux `brain`, worker `AW_Y3QgXUuvtFKD`)
- FalkorDB + Redis + LiveKit: 运行中
- GitHub master: `0d0a2ea`
- Unity 编译: 通过
- 麦克风 / 视频推流: **Unity + Brain + Gemini 三端已验通** (详见 `Test/p2/connectivity_report_p2.md`)

### 历史待办 (Sprint 4 统一处理, 不单独跑)
- ~~Gemini 听到声音~~ → 已验通
- ~~重新生成 token~~ → 已跑过, Token Mint 方案在 Sprint 3
- **[Sprint 4] identify_object 按需发现链路** → `audit_identify_object_no_screenshot_20260420.md` (S4.A-B 统一做)

### P2 实现状态 (2026-04-13)
**已完成 — Graphiti 记忆共享 (P2-Alpha):**
- FalkorDB 替代 Neo4j (Docker 容器, 512MB, 端口 6380)
- Graphiti 客户端单例 + FalkorDB driver + Gemini LLM/Embedder + 4 分区 (goslo/maid/scene/user)
- Brain 记忆工具: `remember` / `query_memory` / `query_scene` / `set_mode`
- 对话自动归档: Brain→goslo 分区, Nanobot→maid 分区

**已完成 — Scheduler 增强 (P2-Beta):**
- BehaviorMode 动态切换: Redis Pub/Sub → mode_watcher → session.update_instructions()
- Context Injector: 记忆注入 + 场景注入 + 主动通知 + 周期轮询

**已完成 — DSG 耦合层 (P2-Gamma):**
- DSG↔Graphiti 接口层 + ExpectationChecker + L1 模拟脚本 + Obsidian SSOT 同步 + Trigger Listener

**已完成 — P2.5 审计修复 + 增强 (Phase 5):**
- TriggerRunner 真正启动 + L2-B 预加载集成到 agent.py
- identify_object ↔ L2-B 双向接入 + 触发事件发射
- Nanobot result_channel 路由协议 + CH_TRIGGER_RESULTS 新通道
- CalendarTrigger 三层提醒 (digest/prep/imminent) + quiet hours + cooldown
- MessageNotificationTrigger (Gmail 重要消息) 新增
- episode_id 防冲突 + 自动归档 + Salience.ALERT + ConfirmationStatus.TENTATIVE
- Agent disconnect 时 TriggerRunner 清理

**待完成 (2026-04-20 核对):**
- [ ] **[P0] git push 4 个未推 commit** → 通过 GitHub Desktop (commit_guidelines §1)
- [ ] **[P0] Castle 拉取 + FalkorDB 首次拉起** → `sync-castle.ps1` 拉代码 + SSH 上 `docker compose up -d`
- [ ] **[P1] Graphiti 线上链路验证** → FalkorDB ping + `remember/query_memory/query_scene` 真实调用
- [ ] **[P1] 创建 Unity AR 项目 (ParrotAR)** 并把 `ARVideoPublisher` 端到端跑通到 Gemini Live
- [ ] **[P1] identify_object 按需发现链路首测** ⚠ 设计未落地 (缺截图+错派Nanobot), 见 `audit_identify_object_no_screenshot_20260420.md`; 需 B1-B2 视频采样基建先就绪
- [ ] **[P2] Google OAuth 真实联调** (CalendarTrigger/MessageTrigger)
- [ ] **[P2] 用户制作 fly/dance/idle 动画 (Minecraft 风格)**
- [ ] **[P2] 像素画小纸条** (lore/ideas.md P3 条目，可能提前到 P2 做 MVP)

> 详见: `.cursor/memory/milestone_p2.md`

### V1 部署基础 (2026-04-12 已验证)
- Castle (ECS) 部署成功: LiveKit Server, Redis, Brain Agent, Nanobot Worker, GOSLO Chat
- GOSLO 双身体上线: Live (Gemini 语音) + Chat (Telegram nanobot)
- Bus V1 全链路验证通过: 语音 + RPC + Nanobot 后台链路
- 信息共享: P2 已通过 Graphiti + FalkorDB 打通记忆互通

### 当前真实状态

**L2 层三条核心链路已真实跑通（有集成测试证明）：**

1. **Path A 挂载**: Brain Agent + Scheduler 通过阶段式 pipeline 挂载到 Bus（L1+L2）
2. **Path B 挂载**: Nanobot Consumer 作为 L2-only Worker 挂载到 Bus
3. **dispatch → consume → result**: Brain dispatch_task → Scheduler 路由 → Redis Stream → Nanobot 消费 → 结果发布

**L1 层 Brain Agent 端到端验证通过（2026-04-11 笔记本模拟）：**

4. **Console 模式**: Bus mount 全流水线 → Gemini Realtime API 连接 → READY
5. **Dev 模式**: Worker 注册 → Agent Dispatch API → Job 分配 → Bus mount 全链路 → Gemini 音频连接 → READY
6. **sim_unity_client**: 连接同一房间 → 收到 Agent 音频 track → RPC handlers 就绪（flyTo/animate）
7. **关键修复**: LiveKit SDK `with_ttl` 改用 `timedelta`；显式 dispatch 需要 `RoomAgentDispatch` 或 API

**Unity 客户端 C# 代码 + Editor 脚本就绪：**

8. **RoomManager**: LiveKit Room 连接 + 远端音频自动播放 + 单例
9. **ParrotRpcHandler**: 注册 flyTo / animate RPC → 转发给 ParrotController
10. **ParrotController**: 方块移动 + 颜色反馈（Phase 1 dev mode）
11. **UnityMainThread**: 线程调度器，LiveKit 回调 → Unity 主线程
12. **DevSceneSetup.cs**: Editor 菜单一键搭建 Dev 场景 (Parrot > Setup Dev Scene)

**Castle 部署配置已创建：**

13. **docker-compose.yml**: Redis 绑定 127.0.0.1
14. **env-castle.template**: Castle 环境变量模板
15. **deploy-castle.sh**: rsync + pip + docker compose + 健康检查

**GitHub 仓库已推送：**

16. **https://github.com/GOSLOParrot/ParrotCarriers** — 2 commits on master
17. **https://github.com/GOSLOParrot/nanobot** — Fork 自 HKUDS/nanobot，`parrot_bus.py` adapter **已完成且已验证**

### 验证矩阵进度

| # | 链路 | 状态 | 验证方式 |
|:--|:-----|:-----|:---------|
| V1 | Brain ↔ Unity (语音) | **✅ 笔记本模拟通过** | sim_unity_client 收到 Agent 音频 track |
| V2 | Brain → Unity (指令) | **RPC 就绪** | sim_unity_client flyTo/animate handlers 注册成功；待真实语音触发 |
| V3 | Brain → Scheduler → Nanobot | **✅ 已验证** | 集成测试 5/5 通过 (含 ParrotBusChannel) |
| V4 | 模块注册与心跳 | **✅ 已验证** | Console + Dev 模式日志确认 register + heartbeat |
| V5 | Nanobot → Bus (结果回写) | **✅ 已验证** | stub + ParrotBusChannel 双路径验证 |
| V6 | ParrotBusChannel 连通 | **✅ 已验证** | test_nanobot_channel.py 2/2 通过 |
| V7 | 猫娘微信 Bot | **✅ 已验证** | QR 登录成功 + gateway 双 channel 并行运行 + Gemini API 200 OK + 微信 sendmessage 200 OK |
| V8 | GOSLO 模式信号 | **已实现** | constants.py HASH_GOSLO_MODE + brain/agent.py mount→live, disconnect→chat |
| V9 | GOSLO Chat bot | **代码就绪** | goslo_config.json + ParrotSoul workspace + start_goslo_chat.py + mode hook；待 TELEGRAM_BOT_TOKEN 配置 |
| V10 | 双 bot 并行 | **部署脚本就绪** | deploy-castle.sh 支持 3 tmux session (brain + maid + goslo-chat)；待 Castle 上验证 |

### 已完成

- [x] 需求清单 v2 + 模块划分 + 目录结构
- [x] Bus 骨架代码（manifest/registry/heartbeat/mounting/processor_hook）
- [x] 审计通过 → ModuleManifest 精简 → mounting 重构
- [x] Brain Agent 入口 + Scheduler 服务 + Nanobot Consumer
- [x] dispatch_task Tool：Brain → Scheduler → Nanobot 完整链路
- [x] 集成测试 2/2 + 单元测试 5/5 + ruff lint 全通过
- [x] Brain Agent 接入 Gemini RealtimeModel（AgentServer + AgentSession）
- [x] ParrotAssistant(Agent) 人格 + function tools (fly_to, animate, dispatch_task)
- [x] RPC 桥接 (`_rpc_bridge.py`): Unity RPC 转发
- [x] docker-compose.dev.yml LiveKit Server + Redis 开发栈
- [x] Console 模式验证: Bus mount → Gemini 连接 → READY ✅
- [x] Dev 模式验证: Worker 注册 → 参与者触发 → 完整入房 → READY ✅
- [x] **Unity C# 客户端**: RoomManager + ParrotRpcHandler + ParrotController + UnityMainThread
- [x] **Token 生成脚本**: `src/scripts/generate_token.py`（已修复 timedelta + agent dispatch）
- [x] **Castle 部署配置**: docker-compose.yml + env-castle.template + deploy-castle.sh
- [x] **项目 README.md + Unity README.md**
- [x] **.gitignore 更新**: ParrotDev + ParrotAR 通配
- [x] **笔记本模拟验证**: sim_unity_client + Brain Agent 端到端 Gemini 语音 ✅
- [x] **DevSceneSetup.cs**: Unity Editor 一键搭建 Dev 场景
- [x] **GOSLO 鹦鹉模型**: Assets/Models/GOSLO.glb (29KB)
- [x] **LiveKit SDK 适配规则**: .cursor/rules/livekit-unity-sdk.mdc
- [x] **GitHub Push**: https://github.com/GOSLOParrot/ParrotCarriers (2 commits)
- [x] **Nanobot ParrotBusChannel**: nanobot/channels/parrot_bus.py — Redis Stream 消费 + agent 回复 → Pub/Sub 结果发布
- [x] **parrot_config.json**: nanobot fork 专用配置 (OpenRouter + Gemini Flash + parrot_bus + weixin channels)
- [x] **start_nanobot_worker.py**: 一键启动真实 nanobot gateway (--stub 可回退到 echo consumer)
- [x] **ParrotBusChannel 连通测试**: test_nanobot_channel.py 2/2 — ParrotBusChannel → 结果发布 + 全链路到 Brain
- [x] **Scheduler 超时检测**: 120s 任务超时 → 通知 Brain
- [x] **NANOBOT_TASK_TYPES 扩展**: +summarize, +remind (对齐 parrot_bus._build_prompt)
- [x] **Brain 结果反馈优化**: timeout/completed/其他状态区分处理
- [x] **Stub consumer 修复**: 增加 result 字段 (解决 result_summary 空白)
- [x] **集成测试修复**: Pub/Sub 按 task_id 过滤 (消除跨测试串扰)
- [x] **全量测试**: 27/27 通过 (22 单元 + 5 集成)
- [x] **猫娘女仆微信 Bot**: parrot_config.json 启用 weixin channel + SOUL.md 人格 + USER.md 用户画像
- [x] **start_nanobot_worker.py 升级**: 支持 --no-weixin 参数，默认启用 weixin + parrot_bus 双 channel
- [x] **P2 多角色协作架构设计**: 副协作模块定位 + 不引入外部协作框架 + 外挂 Obsidian/LobeChat 做主工作区
- [x] **GOSLO 模式信号**: HASH_GOSLO_MODE (Redis Hash) + Brain Agent 连接/断开时写入 active_body=live/chat
- [x] **GOSLO Chat bot 配置**: goslo_config.json (Telegram channel) + ParrotSoul SOUL.md/AGENTS.md + start_goslo_chat.py
- [x] **Protocol Snapshot v1.1**: 新增 Section 10 — 角色工作模式 + 多实例架构 + 信息共享策略 + 决策 D12-D17
- [x] **Scene.md 更新**: GOSLO 双身体(Live+Chat) 拆分为独立角色行项
- [x] **GOSLO 模式感知 pre-hook**: BaseChannel.pre_handle_hook + goslo_mode.py 中间件 (查 Redis → live 转发/chat 正常)
- [x] **start_goslo_chat.py 升级**: in-process gateway 启动 + 自动注入 mode hook (--no-mode-hook 可禁用)
- [x] **deploy-castle.sh 升级**: 双仓库同步 + nanobot pip install + GOSLO workspace setup + 3 tmux session 说明
- [x] **env-castle.template 更新**: 新增 GEMINI_API_KEY + TELEGRAM_BOT_TOKEN + REDIS_URL

### 当前不做 (P2/P2.5 阶段)

- [ ] 不做 DSG 真实视觉管线（需 A10 GPU，P3/P4）
- [ ] 不做 MemoryValidity 衰减层（P3）
- [ ] 不做 Skill Distillation 技能提炼（P3）
- [ ] 不做群聊（Telegram 群 + LobeChat，P3）
- [ ] 不加 VAD/Silero（Gemini 自带 turn detection）
- [x] ~~不做 XR Hands~~ → P2.5 已完成 Unity 端骨架 (XRHandTracker + PerchOnHand)

### 下一步

**本周关键路径 (按顺序, 每步完成再进下一步):**

1. **用户确认** `ar_feature_vision.md` §六 + §八 + §3.5 三合一 (不反对即通过)
2. **执行** `sprint0_preflight.md` 的 14 项 S0.A-S0.N 任务 (四层时间轴 + Cursor 合约 + ADR + 三闸门 + 版本锁 + tentative/ratified 两态机)
3. **执行** `ar_feature_implementation_plan.md` Sprint 0 的 S0.1-S0.7 (基建修缮) → 打 tag `v-s0`
4. **执行** Sprint 1 自知底座 (Blackboard 扩域 + 三层调度收口 S1.A-G) → 打 tag `v-s1`
5. **顺序执行** Sprint 2 两轴 → Sprint 3 AR 桌面 MVP → Sprint 4 玩法糖衣 + identify_object 升级
6. 每 Sprint 严格按**三闸门验收** (`sprint0_preflight.md` §4), 不追求完美, 不做 P3 的事

**Sprint 过程中按需补 skill/rule** (不提前):
- Sprint 2 末: `rules/scheduler-three-layer.mdc` — E2/E5 与三层意识收口约束
- Sprint 4 中 (S4.A3 后): `skills/unity-snapshot-service/SKILL.md` — AsyncGPUReadback 坑
- Sprint 4 中 (S4.B2 后): `skills/gemini-visual-match/SKILL.md` — Flash 多图比对约束
- Sprint 4 末: `rules/soul-constraints.mdc` + `rules/consciousness-dispatch.mdc` — 实测后固化

**P2 收尾延期项** (Sprint 之外, 不阻塞):
- GitHub Desktop push 4 个未推 commit → `sync-castle.ps1` → SSH `docker compose up -d`
- SSH 上跑 FalkorDB 健康检查 + Graphiti 集成测试

**P2 剩余 (随顺序推进):**
- [ ] Brain 优雅退出: AgentSession cleanup + 心跳停止 + Bus deregister
- [ ] `Scheduler._connect_livekit` 补完 (P1 遗留 stub，Castle 调试时做)
- [ ] 用户完成 fly/dance/idle/thinking 动画 (Minecraft 风格) → Unity 替换 Cube
- [ ] 像素画小纸条 (lore/ideas.md) MVP: Unity UI Canvas + 2D 像素风 Sprite + RPC 触发

**P2.5 准备:**
- [x] AR App 工程计划: `.cursor/memory/architecture/ar_app_plan.md` (硬事实+调研索引+问卷)
- [x] 视频流采样 skill: `.cursor/skills/livekit-unity-video-publish/SKILL.md` (5段接缝: Unity推流端+Gemini消费端+DSG预留接口+identify_object截帧路径)
- [x] AR Foundation 规则: `.cursor/rules/ar-foundation.mdc` (版本约束+5条已知坑)
- [ ] Cursor 工作区规则: .cursor/rules/ 模块隔离策略（按官方推荐）
- [ ] 新 skill 收集: XR Interaction Toolkit, Unity Sentis (本地推理)
- [ ] 猫娘 cron 任务: Obsidian vault 变更 → Gemini Flash 三元组补充
- [x] Google 生态 MCP 配置就位
  - 架构设计: `.cursor/memory/architecture/gemini_drive_bridge.md`
  - 验证计划: `.cursor/memory/architecture/verification_plan_google.md`
  - ⚠️ **真实 OAuth 联调未做** (Calendar/Gmail Trigger 需要用户账号授权)
- [ ] 三级调度 Priority 子树 (reflex > intent > task)
- [ ] ResourceLockManager 骨架 (body 通道互斥)

**lore/ideas.md 待回流到 requirements:**
- [ ] "发现 vs 未发现的不对称性" → 影响 `ExpectationChecker` 的 MISSING 判定和 `ConfirmationStatus` 状态机

**P3 前瞻:**
- [ ] MemoryValidity (信息有效期 + Ebbinghaus 衰减)
- [ ] Skill Distillation (工作流 → skill 自动提炼)
- [ ] DSG 真实视觉管线 (A10 GPU)
- [ ] Obsidian MCP 双向交互
- [ ] 群聊 (Telegram 群 + LobeChat)
- [ ] XR Hands 手势反射 (C8, C9)
- [ ] Unity ARFoundation 前端升级

### 新增重大讨论项与潜在风险 (2026-04-13)

- 🔶 **多工作区环境配置与双仓代码推送策略**: 当前部署是通过简单的 SSH 脚本强推。用户提出：后续开发在 PC 上的 Cursor 环境进行，但是在 ECS 和 `nanobot` 项目进行部署或者模式配置补充时，可能需要在 ECS 远程环境利用 `Remote SSH` 工作。这种工作模式的割裂可能会带来双仓代码同步、Git 冲突等问题。如何组织推代码（Push 策略）和切换 Agent 的关注点，是后续在进行 ECS 操作时必须先讨论清晰的痛点。未来请通过 `.cursor/rules/workspace.mdc` 定义隔离策略，但本期暂不急着改规则。
- 🔶 **LiveKit 的密钥错位问题**: 在本地进行开发，而服务端部署在云端时，由于 `.env` 与云端部署脚本中的 `livekit.yaml` 可能会错配（如云端 `secret` 与本地长字符串冲突导致 401），以后要保证 ECS 工作环境与本地 `.env` 永远严格对齐。
- 🔶 **网络 VPN 引发的 UDP 大丢包**: 测试证明使用科学上网代理（Clash/Mihomo）连接阿里云 ECS 7880 UDP 端口，会造成 3~5 秒极大延迟与丢包。测试 LiveKit 时必须为该 IP 配置直连（DIRECT）或直接关闭代理。

### 关于 Tool 阻塞（已确认）

- `fly_to` / `animate`: 等待 Unity RPC 响应（<10s），不阻塞 Agent 事件循环
- `dispatch_task`: 火即忘（publish → return），不等 Nanobot 结果

### P1.5 完成项（2026-04-12）

- **Scheduler**: SimpleRouter if-else → py-trees BT (Selector + HandleReflex/DispatchToNanobot/HandleBrainDirect)
- **Blackboard**: 自写空壳删除 → py-trees Blackboard V2 Client + namespace /scheduler/*
- **结果汇总**: Brain 不再直听 CH_NANOBOT_RESULTS → Scheduler 汇总后走 CH_SCHEDULER_TO_BRAIN
- **DataChannel**: TelemetryFrame(pose+timestamp+behavior_state) + TelemetryEvent 定义 + Python 接收回调
- **BehaviorMode**: Flag enum (BASE|COMPANION) + Blackboard 存储 + ParrotSoul 按模式拼接 instructions
- **协议快照**: protocol_snapshot_p1.md — 已验证/候选标注完整
- **共享枚举**: ParrotAnimation(8种) + ParrotBodyState(5种) + BehaviorMode(5种) 统一在 shared/parrot_actions.py
- **新增通道**: CH_SCHEDULER_TO_BRAIN = "parrot.scheduler.to_brain"
- **测试**: 22 passed (9 BT router + 4 parrot_actions + 4 telemetry + 5 bus registry)
- **审计修复 (2026-04-12 补)**: dispatch_task 任务类型与 BT 路由表对齐 + animate 强校验 + 正式链路集成测试 + docstring 更新 + 协议快照口径修正

### P1 审计发现（2026-04-11，P1.5 已修复的标 ✅）

- ✅ Blackboard 类已写但全仓库无调用方 → py-trees Blackboard V2 替换，BT 节点和 BTRouter 都使用
- ✅ Brain 直听 CH_NANOBOT_RESULTS 跳过 Scheduler 汇总 → 改走 CH_SCHEDULER_TO_BRAIN
- ✅ DataChannel 遥测（A6）完全空白 → telemetry.py + telemetry_receiver.py 骨架
- ✅ BehaviorMode 有调研设计但未实现 → Flag enum + Blackboard + ParrotSoul 集成
- 🔶 Scheduler._connect_livekit 仍是空壳（P1.5-B Castle 部署时补）
- 🔶 SimpleRouter 的 reflex_direct 和 brain_direct 无下游执行器（P2 接入 DataChannel/XR Hands）
- ✅ animate tool 已接入 ParrotAnimation enum 强校验（不在枚举内返回错误提示）
- 🔶 15 个 Redis 常量中仍有 10 个无消费代码（候选，P2 按需激活）
- 🔶 **多端 RPC 路由风险**: 当前 `_rpc_bridge.py` 寻找 `unity-*` 客户端的逻辑是找到房间里的“第一个”。如果是 `sim_unity_client` + `Unity Editor` 都在房间内且身份均以 `unity-` 开头，会导致 RPC 随机打给其中一个。P1 是单端 demo 此设计无伤大雅，P2/P3 多端多设备协作时需升级（广播 / 靶向）。

### 已确认事实（防翻案）

- Phase 1 = Bus-first（模块化基础设施，非 demo）
- Nanobot 直接适配（fork + parrot_bus.py），不做"最小部署"过渡
- A10 非前置条件：Phase 1 只为 DSG 留 Processor 挂载接口
- 调度器统一叫 Scheduler；查旧稿时注意历史名称 Dispatcher
- 双仓库架构：ParrotCarriers（主）+ nanobot（fork 已完成：GOSLOParrot/nanobot）
- 2C8G 够用: P2 已用 FalkorDB 替代 Neo4j (D-P2-1)，内存压力解除
- 协议由代码驱动，不在纸上空转，V1 定版可迭代
- GOSLOParrot = 主项目（家族全景）；ParrotCarriers = Bus 基建子项目
- GOSLO = 鹦鹉大小姐 desuwa；Nanobot = 猫娘女仆（Agents Team，默认 3 并发）
- 猫娘女仆微信 Bot = nanobot 内置 weixin channel，纯配置启用，零代码改造
- nanobot 一个实例可同时运行多个 channel（parrot_bus + weixin），共享 AgentLoop，独立 session
- GOSLO Chat bot = 第二个 nanobot 实例（goslo_config.json + goslo-workspace/ + ParrotSoul），P2 已创建配置
- GOSLO 双身体通过 Redis HASH_GOSLO_MODE 协调：Brain 连接时 active_body=live，断开时 =chat
- ParrotCarriers 定位 = 副协作模块 + 信息提供商，不膨胀为 one-for-all 工作区
- 不引入 AutoGen/CrewAI 等外部协作框架——Agent 是多进程独立实例，Redis Bus 已够用
- 群聊 = P3（Telegram 群 + LobeChat），P2 聚焦各角色 1对1 bot 稳定运行
- Graphiti 信息共享策略: group_id 分区隔离 (goslo/maid)，scene/user 分区共享只读
- ModuleManifest = 轻量挂载声明，不是 God Contract
- Brain Agent 使用 `agents.cli.run_app(server)` 作为入口点
- Agent dispatch 需显式调用 `agent_dispatch.create_dispatch()`
- Console 模式可以在无 LiveKit Server 时测试
- Unity 客户端 identity 必须以 "unity" 前缀开头（_rpc_bridge.py 检测）
- LiveKit Unity SDK v1.3.5 通过 UPM git URL 安装
- LiveKit Python SDK `with_ttl()` 需要 `timedelta` 而非 `int`
- `@server.rtc_session(agent_name=...)` 启用显式 dispatch，需通过 API 或 token room_config 触发
- sim_unity_client.py 内置 auto-dispatch 逻辑（检测房间无 agent 时自动调用 dispatch API）
- GitHub 仓库: https://github.com/GOSLOParrot/ParrotCarriers
- FalkorDB 替代 Neo4j (D-P2-1): 2C8G 下必选，~100-500MB vs ~2.7GB
- DSG 是耦合子系统，不是独立模块 (D-P2-2): 通过触发器/预加载/直写和 Graphiti/Brain 紧密耦合
- Gemini 4 条通信通道 (D-P2-3): 语音 / generate_reply / update_instructions / tools 返回值
- Obsidian 是人写 SSOT (D-P2-4): .md + UUID 绑定 Graphiti scene 分区，文件组织随意
- Graphiti 4 分区 (D-P2-5): goslo / maid / scene / user
- P2 里程碑详情: `.cursor/memory/milestone_p2.md`

---

## 关键上下文

- **项目**: `ParrotCarriers` — GOSLOParrot 通信总线子项目
- **GitHub**: `GOSLOParrot/ParrotCarriers` + `GOSLOParrot/nanobot`
- **服务器**: 东京 `ecs.g9i.large`（常驻）+ 东京 `A10`（按需），同 VPC
- **全局索引**: `.cursor/memory/INDEX.md`
- **需求清单**: `.cursor/memory/requirements.md` v2
- **模块划分**: `.cursor/memory/architecture/module_division.md`
- **总线架构**: `.cursor/memory/architecture/bus_v4.md` v4.2
- **审计报告**: `docs/report/2026-04-08_p1_bus_architecture_manifest_trace_report.md`
- **设计护栏**: `.cursor/memory/BigIssue.md`
- **P2 里程碑**: `.cursor/memory/milestone_p2.md` — 记忆共享 + Scheduler 增强 + DSG 耦合层
- **协议快照**: `.cursor/memory/architecture/protocol_snapshot_p1.md`
- **部署快照**: `.cursor/memory/deploy_snapshot_p2_20260412.md`

### 运行命令速查

```bash
# ===== 快速启动（推荐）=====

# 终端 1: 一键启动开发栈 + 生成 token
python src/scripts/run_dev.py

# 终端 1 (继续): 启动 Brain Agent
.venv\Scripts\python.exe -m parrot.brain.agent dev

# 终端 2: 模拟客户端 + 麦克风 + 全栈（Scheduler + Nanobot）
.venv\Scripts\python.exe src/scripts/sim_unity_client.py --mic --full

# ===== 手动分步 =====

# 开发栈
docker compose -f infra/docker-compose.dev.yml up -d   # Redis + LiveKit Server

# Brain Agent
python -m parrot.brain.agent console                    # 终端模式（无需 LiveKit）
python -m parrot.brain.agent dev                        # 开发模式（需 LiveKit）

# 模拟客户端（替代 Unity）
python src/scripts/sim_unity_client.py --mic            # 麦克风语音对话
python src/scripts/sim_unity_client.py --mic --full     # 语音 + Scheduler + Nanobot
python src/scripts/sim_unity_client.py                  # 仅监听（不发语音）

# Scheduler（单独启动，不用 --full 时需要）
python src/scripts/start_scheduler.py

# Nanobot Worker（stub 版，不用 --full 时需要）
python -m parrot.bus.nanobot_consumer

# 猫娘微信 Bot
D:\GOSLOParrot\ParrotCarriers\.venv\Scripts\nanobot.exe channels login weixin -c D:\GOSLOParrot\nanobot\config\parrot_config.json  # 首次扫码
python src/scripts/start_nanobot_worker.py              # 启动 parrot_bus + weixin
python src/scripts/start_nanobot_worker.py --no-weixin  # 只启动 parrot_bus

# Unity Token
python src/scripts/generate_token.py                    # 生成 → 保存到文件 + 复制到剪贴板
python src/scripts/generate_token.py --identity unity-phone  # 手机用

# 测试
pytest tests/test_bus/ -v                               # 单元测试
pytest tests/integration/ -v                            # 集成测试（需 Redis）
pytest tests/integration/test_graphiti_chain.py -v      # Graphiti 链路（需 FalkorDB）

# Castle 同步（日常）—— 详见 commit_guidelines.md §2
.\infra\sync-castle.ps1               # 只拉代码
.\infra\sync-castle.ps1 -Workspace    # 代码 + nanobot persona
.\infra\sync-castle.ps1 -Env          # 代码 + .env
.\infra\sync-castle.ps1 -All          # 全量

# Castle 首次部署或重置（用 Git Bash 跑）
bash infra/deploy-castle.sh 8.216.45.45

# ===== P2 新增 =====

# DSG 桌面模拟
python src/scripts/sim_dsg_desktop.py                   # 全场景模拟
python src/scripts/sim_dsg_desktop.py --scenario new    # 物体出现
python src/scripts/sim_dsg_desktop.py --scenario missing # 物体消失

# Obsidian 同步到 Graphiti
python src/scripts/sync_obsidian_to_graphiti.py --vault /path/to/obsidian/objects

# Graphiti 集成测试
pytest tests/integration/test_graphiti_chain.py -v      # 需要 FalkorDB 运行
```

### 手动验证场景

| 场景 | 你说什么 | 期望结果 |
|:-----|:---------|:---------|
| 语音对话 | "Hello Parrot" | Gemini 用 Parrot 人格语音回复 |
| 跳舞指令 | "Dance for me" | sim client 打印 `RPC animate: dance` |
| 飞行指令 | "Fly to 1 2 3" | sim client 打印 `RPC flyTo: {x:1,y:2,z:3}` |
| 后台任务 | "Search for IPoAC" | Scheduler 路由 → Nanobot 处理 → Gemini 语音反馈结果 |
| 记忆写入 | "记住我喜欢咖啡" | Graphiti goslo 分区写入 → 下次启动能搜到 |
| 记忆查询 | "我之前说过什么" | query_memory 从 Graphiti 搜索 → 返回结果 |
| 场景查询 | "桌上有什么" | query_scene 从 Graphiti scene 分区搜索 |
| 模式切换 | "切换到研究模式" | set_mode → Redis → mode_watcher → instructions 更新 |
| 物体发现 | "这是什么东西？" | identify_object(match) → Graphiti 搜索 → L2-B 更新 → 自然回复 |
| 保存新物体 | "记住这个杯子" | identify_object(save_new) → Graphiti 写入 + L2-B 节点 + SSOT 触发器 |
| 深度搜索 | "帮我查一下这个" | identify_object(deep_search) → Nanobot research → 结果回写 |
| Episode 管理 | "开始新任务：找包裹" | manage_episode(start) → L2-B Episode 创建 |
| 日程提醒 | (自动) | CalendarTrigger → Nanobot → 三层提醒 → Gemini 自然播报 |
