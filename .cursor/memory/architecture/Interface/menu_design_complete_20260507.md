---
status: ratified-design / pending-implementation
category: menu-design
status_note: "完整菜单设计 SSOT — 三层架构（启动页/HUD/工具柜/节点画布）+ 4 类块定义（Model/Persona/Mode/Scene）+ 预设系统 + 默认 fallback + 海盗换肤 + 像素画素材清单按菜单细分 + 与 8 场景关联 + 实施推荐顺序 Phase A-E。【2026-05-07 增量 v0.1】§4 节点画布加 2 占位（过滤器块 + 有效期预测模块 + §4.7 占位说明）+ §8 关联表 + §7.5 素材 2 条；具体设计延后到 NEED-P3-FILTER / NEED-P3-VALIDITY。Sub-Chat A 用户视角主输入；AR 工作区独立菜单 UI chat 主输入。"
last_reviewed: 2026-05-07
ai_priority: high
ai_audience: "Sub-Chat A 用户视角 + AR 工作区独立菜单 UI chat + Sonnet 4.6 抄码 baseline"
parent_doc: "../app_completion_master_audit_20260507.md"
related:
  - "../ar_app_flow_ui_design.md (UI 基线)"
  - "../../lore/ideas.md (海盗主题 / 猫爪 / 望远镜)"
  - "interface_design_and_how_todo_v0_20260507.md (§5.0 启动 + §5.6 4 类块 + §5.9 HUD)"
  - "interface_design_supplement_20260507.md (§1.4 2 Scene baseline + §1.7 海盗换肤)"
  - "concept_dictionary_20260507.md (§3.2 Persona/Mode/Model/Scene 区分 + §6 用户主题)"
  - "legacy_issues_split_20260507.md (NEED-P3-B/C/D/E + NEED-P2.5-A)"
---

---
status: ratified-design / pending-implementation
category: menu-design
status_note: "完整菜单设计 — 启动页 + HUD + 工具柜 + 4 类块 + 节点画布 + 默认 fallback + 海盗换肤 + 像素画素材清单 + 与 8 场景关联 + 实施推荐顺序。基于 ar_app_flow_ui_design + lore/ideas + concept_dictionary 综合设计。本文是 user-visible 菜单的 SSOT；Sub-Chat A 用户视角主输入；菜单 UI chat 主输入。"
last_reviewed: 2026-05-07
authoritative_for: "user-visible 菜单层（启动页 / 主菜单 / 节点画布 / 默认 fallback / 海盗换肤）的设计 SSOT"
parent_doc: "../app_completion_master_audit_20260507.md"
related:
  - "../ar_app_flow_ui_design.md"
  - "../../lore/ideas.md"
  - "interface_design_and_how_todo_v0_20260507.md (§5.0 启动 + §5.6 4 类块 + §5.9 HUD)"
  - "interface_design_supplement_20260507.md (§1.4 2 Scene baseline + §1.7 海盗换肤 + §1.8 多设备)"
  - "concept_dictionary_20260507.md (§3.2 Persona/Mode/Model/Scene 区分 + §6 用户主题)"
  - "legacy_issues_split_20260507.md (NEED-P3-B/C/D/E + NEED-P2.5-A 修复路径)"
---

# ParrotCarriers — 完整菜单设计（user-visible UI SSOT）

> **本文用途**：把"启动页 / HUD / 工具柜 / 4 类块 / 节点画布 / 默认 fallback / 海盗换肤"7 层 UI 一次性设计完整。Sub-Chat A 用户视角实施 + AR 工作区独立菜单 UI chat 主输入 + Sonnet 4.6 抄码 baseline。
>
> **设计依据**：
> - `ar_app_flow_ui_design.md` 当前 baseline（启动页 / HUD / 工具柜 / 道具）
> - `lore/ideas.md` 2026-04-27（海盗主题 / 猫爪 / 望远镜 / 羊皮纸 / Last Report 风格）
> - `dsg_decisions_master §3.2`（Obsidian 3 子类 → Roleplay 模式）
> - `goslo_modularization_residual_debt §4.3`（4 类块 + 预设 + 节点画布构想）
>
> **实施约束**：
> - 占位优先 + 美术后期补（master_audit §6 像素画清单）
> - 不动 wire（Phase 4 §8 锁）
> - Plan UI / body_state 升级走 P3 wire ADR；本文场景 5 用占位 stub UI

---

## §0 三层菜单架构总览

```
┌──────────────────────────────────────────────────┐
│ 第 1 层：启动页菜单（Boot Menu）                 │
│  - Stardew Valley 风                             │
│  - 6 项主菜单（开始 AR / 房间 / 管线 / 人设 /     │
│    场景 / 权限连接测试）                          │
│  - 调试折叠（隐藏给开发期）                        │
└──────────┬───────────────────────────────────────┘
           │ user 点"开始 AR"
           ▼
┌──────────────────────────────────────────────────┐
│ 第 2 层：主菜单（运行时 HUD + 工具柜）           │
│  - HUD（屏幕一角，2D 像素羊皮纸）                  │
│  - 工具柜（HUD 对角，2D 像素）                    │
│  - 用户偏好持久化（横/竖向 / 开关）                 │
└──────────┬───────────────────────────────────────┘
           │ user 点工具柜某按钮（如"放大镜"）
           ▼
┌──────────────────────────────────────────────────┐
│ 第 3 层：节点画布（Canvas Menu，NEED-P3-D）      │
│  - 高级用户向 4 类块 拖拽 + 连线                  │
│  - 模型 / 设定 / 模式 / 场景 块                  │
│  - 保存预设 + 恢复默认                            │
│  - 默认 fallback（NEED-P3-E）= 列表选 + 保存      │
└──────────────────────────────────────────────────┘

跨层换肤：
  ScriptableObject swap → 大小姐宅邸 ↔ 海盗主题
  （不重启 app；ar_feature_vision §3.4 + lore §海盗主题）
```

---

## §1 第 1 层 — 启动页菜单（Boot Menu）

### §1.1 风格基线

- **参考**：Stardew Valley 启动页（lore §2026-04-27 user 钦定）
- **背景**：大小姐宅邸（默认）/ 维多利亚 / 蕾丝 / 暖色调；微动效（窗帘飘动 / 烛光闪）
- **像素分辨率**：320×240 px logical → 上采样到 1080×1920 / 1920×1080
- **音效**：可选；柔和翻页声 / 选择 click 声

### §1.2 6 项主菜单（baseline）

| # | 菜单项 | 用途 | 默认值 / 选项 | 关联模块 / NEED |
|:--|:--|:--|:--|:--|
| 1 | **开始 AR 主场景** | 进入大小姐宅邸主流程 | — | 全场景 |
| 2 | **初始房间 / LiveKit room** | 选择或显示当前 room_id | 默认 `parrot-main`；可手动输入或下拉 | A1 LiveKit |
| 3 | **BrainAgent 管线** | LineA Gemini Realtime（默认）/ LineB STT-LLM-TTS | env-gate `PARROT_LLM_PIPELINE` | `lineb_implementation_completion` |
| 4 | **人设 / 场景**（4 类块预设入口）| 选择预设（默认 GOSLO_default + companion + main_scene + parrot_default）/ 进入节点画布 / 默认 fallback | NEED-P3-B/C/D/E | 第 3 层菜单入口 |
| 5 | **场景 baseline** | DESKTOP_WEBCAM（Editor / 无 AR）/ AR_HANDHELD（Android 真机 AR） | 默认 AR_HANDHELD | NEED-P2.5-SCENE-2BASELINE / `ar_feature_vision §3.4` |
| 6 | **权限 + 连接测试** | Camera / Mic / 网络 / Token Mint / LiveKit / Brain presence | 必交付；可折叠 | A1 / token_mint / S0 |

### §1.3 调试折叠（开发期；正式版本默认隐藏）

| # | 项 | 用途 |
|:--|:--|:--|
| D.1 | 日志级别 | DEBUG / INFO / WARNING / ERROR |
| D.2 | HUD 强制开启 | runtime debug 用 |
| D.3 | 自检按钮（SelfTest）| 跑 Sprint 3 测试束（**仅开发期**） |
| D.4 | Force Shutdown | livekit-unity-lifecycle/IMPL_REF §2 |
| D.5 | Simulate Pause | 模拟 OnApplicationPause（M2）|
| D.6 | 多设备 input 选择（P3.5）| DroidCam / OBS / 副摄（lore §P3.5）|

### §1.4 启动序

```
1. 启动 Logo + 加载动画
2. 启动页菜单展示
3. user 在 #1 #2 #3 #4 #5 选好 → 点"开始 AR"
4. 权限请求（如未授）
5. Token Mint POST `/mint`
6. LiveKit room.connect()
7. AR session start（视 #5 选择 DESKTOP_WEBCAM 或 AR_HANDHELD）
8. onSceneReady → Brain 单次问候（去重）
9. 进入主菜单（HUD + 工具柜）
```

### §1.5 用户偏好持久化（PlayerPrefs）

| key | 默认 | 持久度 |
|:--|:--|:--|
| `parrot.boot.last_room_id` | `parrot-main` | 永久 |
| `parrot.boot.last_pipeline` | `line_a` | 永久 |
| `parrot.boot.last_preset_id` | `default` | 永久 |
| `parrot.boot.last_scene_baseline` | `ar_handheld` | 永久 |
| `parrot.boot.show_debug_panel` | `false` | 永久 |

---

## §2 第 2 层 — 主菜单（HUD + 工具柜）

### §2.1 HUD（屏幕一角）

#### 风格

- **2D 像素羊皮纸**（白底 / 暖金边）— Last Report / Paper Please 风
- **位置**：屏幕角（user 可选 4 corner 之一）
- **可开关 + 收纳 + 横/竖向展开**（user 选；不自动横竖屏）

#### 显示内容

| 元素 | 用途 | 数据源 |
|:--|:--|:--|
| 时间钟 | 现在时间 | OS time |
| 天气 icon | 晴 / 阴 / 雨 / 雪 | 配置 / API |
| 连接 icon | LiveKit 连接 4 态（healthy/degraded/lost/recovering） | BB `session/connection_health` |
| 音频 icon | 麦克风 ON/OFF/muted | BB `session/audio_route_policy` |
| 视频 icon | 视频档位（VIDEO_OFF/GEMINI_ONLY/FULL/BURST） | BB `session/video_tier` |
| Brain 在房 icon | brain.agent 在 / 不在 | BB `session/connection_health.brain_presence` |
| 视觉自我感知 icon | 4 级（active/degraded/paused/blocked）| BB `session/visual_state`（NEED-P2.5-VISUAL-SELF-AWARE） |

### §2.2 工具柜（HUD 对角）

#### 风格

- **2D 像素 Meta UI**；同 HUD 风格
- **位置**：HUD 对角（4 corner 之另一）
- **横/竖向展开**

#### 道具列表（P0 + P1 + P2）

| # | 道具 | 优先级 | 状态 | 触发动作 | 依据 |
|:--|:--|:--|:--|:--|:--|
| 1 | **设置** | P0 | 待做 | 进入设置子菜单 | `ar_app_flow_ui_design §7` |
| 2 | **相机模式**（视频档位）| P0 | 待做 | set_video_tier | NEED-P2.5-B 一部分 |
| 3 | **拍照按钮 📷** | P0 | 待做 | PhotoController.CapturePhoto() | S3 子任务 |
| 4 | **放大镜** | P0 | 待做 | 圆形 alpha 蒙版 + 拖动 + 倍率调节 | `ar_app_flow_ui_design §7` |
| 5 | **注意力框（BBox）**| P0 | 待做 | 拖动框；EcpEvent `bbox.placed` | Phase 4 W6-7 |
| 6 | **常用任务按钮**（4-6 个）| P0 | 待做 | fly_to / animate / dispatch_task / set_mode 等 | parrot_behavior_rules §4.3 |
| 7 | **2D 工作区入口** | P1 | 待做 | 进入 2D 报告 / 行程 / 反馈 工作区 | `ar_app_flow_ui_design §7` |
| 8 | **简易行程单** | P1 | 待做 | 待办列表 + 打勾 | 同上 |
| 9 | **2D 贴图箱** | P2 | 待做 | 拖贴纸到画面 | 同上 |
| 10 | **节点画布入口** | P1 | 待做 | 进入第 3 层菜单 | NEED-P3-D |

### §2.3 折叠 / 展开 / 持久化

| 操作 | 触发 | 持久化 |
|:--|:--|:--|
| 点 HUD icon | 展开 / 收纳 | `parrot.hud.expanded` / `parrot.hud.direction`（horizontal/vertical）|
| 点工具柜 icon | 同上 | `parrot.toolbar.expanded` / `parrot.toolbar.direction` |
| 长按某按钮 | 拖出到画面（如放大镜） | runtime |

### §2.4 海盗主题换肤（P3）

| 元素 | 大小姐宅邸 | 海盗 |
|:--|:--|:--|
| HUD 板纹理 | 像素羊皮纸（白底暖金边）| 老海图 / 卷边 / 黄铜钉 |
| 工具柜板 | 同 | 同 |
| 放大镜 | 圆形玻璃 | 海盗望远镜 |
| AR 视野滤镜 | 无 | 半边模糊黑色（眼罩 / lore 钦定）/ 脏镜片 |
| 字体 | 像素中文 baseline | 海盗装饰字体（**字体可读性挑战**）|
| 切换方式 | ScriptableObject swap（不重启 app）| 同 |

---

## §3 4 类块定义（核心 — NEED-P3-B 主线）

> 每个块 = ① ID 命名空间 ② 数据格式 ③ 加载器 ④ active BB key ⑤ 切换事件

### §3.1 Model 块（已落 GOSLO mod）

| 维度 | 内容 |
|:--|:--|
| ID | `model_id`（如 `GOSLO_default` / `qfufu_v1`） |
| 数据格式 | `ModelManifest` Pydantic（`shared/model_manifest.py`）|
| 文件位置 | `unity/ArSpike/Assets/Resources/parrot_models/<model_id>.json` |
| 加载器 | `ModelDriver.cs` 反射实例化 + auto-scale |
| active BB key | `global/active_model_id` |
| 切换事件 | `EcpCommand.meta["model_id"]` 透传 |
| 当前默认 | `GOSLO_default`（goslo_default.json 8 reserved capability_id） |
| Sub-Chat 范围 | Sub-Chat B 后端模块视角（已 ratified） |

### §3.2 Persona 块（NEED-P2.5-A 待外置）

| 维度 | 内容（设计） |
|:--|:--|
| ID | `persona_id`（如 `goslo_parrot_default` / `goslo_pirate_first_mate`） |
| 数据格式 | `.md` 或 `.toml`（含 core_instructions + 各 mode 段 + 4 级视觉自我感知段 + 8 条强制话术） |
| 文件位置 | `src/parrot/brain/personas/<persona_id>.md` |
| 加载器 | `parrot.brain.persona_loader.load(persona_id)` |
| active BB key | `global/active_persona_id` |
| 切换事件 | persona_loader 监听 BB key 变化 |
| 当前默认 | `goslo_parrot_default`（旧文本原样搬，0 漂移） |
| 配套 | NEED-P2.5-VISUAL-SELF-AWARE / NEED-P2.5-OBSIDIAN-3SUB / NEED-P3-MODE-ROLEPLAY |
| Sub-Chat 范围 | DSG 协议升级 chat（与 NEED-P3-B/C 一锅端） |

### §3.3 Mode 块（已落 + Roleplay 扩展）

| 维度 | 内容 |
|:--|:--|
| ID | `mode_flags`（list[str]：BASE/COMPANION/BUTLER/RESEARCHER/PLAYFUL/FULL）+ ROLEPLAY flag（NEED-P3-MODE-ROLEPLAY） |
| 数据格式 | BehaviorMode Flag enum；BB 存 list |
| 文件位置 | `src/parrot/shared/parrot_actions.py:BehaviorMode` |
| 加载器 | `mode_watcher`（Phase 1） |
| active BB key | `global/active_mode`（list） |
| 切换事件 | `set_mode` tool / Redis Pub-Sub `set_mode_request` |
| Roleplay 联动 | 开 ROLEPLAY → Persona 子类切 / Obsidian-设定-Roleplay 桶激活 / 海盗换肤 ScriptableObject swap |
| Sub-Chat 范围 | DSG 协议升级 chat |

### §3.4 Scene 块（部分落 + 2 baseline 待升）

| 维度 | 内容 |
|:--|:--|
| ID | `scene_type`（SceneType enum）+ `location_tag`（scalar） |
| 数据格式 | `SceneProfile` dataclass（`l1_5/scene_snapshot.py`） |
| 文件位置 | 注册在 `SceneRegistry`（in-memory；P3 可外置 JSON） |
| 加载器 | `SceneRegistry.switch(scene_type)` → `SceneSwitchOutcome` |
| active BB key | `global/active_scene_id` |
| 切换事件 | `IntentEventBoundaryHandler.switch_scene` |
| 当前 | DESKTOP only；2 baseline 待升（DESKTOP_WEBCAM + AR_HANDHELD） |
| 配套 | NEED-P2.5-SCENE-2BASELINE / TODO(P3-multi-scene) |
| Sub-Chat 范围 | DSG 协议升级 chat |

---

## §4 第 3 层 — 节点画布（NEED-P3-D 高级用户向）

### §4.1 风格 + 灵感

- **参考**：ComfyUI / n8n / Unreal Blueprint
- **场景**：进入第 2 层 → 工具柜 → "节点画布入口" 按钮
- **目的**：让 user 自定义"模型 + 设定 + 模式 + 场景"组合并保存为预设

### §4.2 节点类型（4 色区分）

| 节点 | 颜色 | 接口 ScriptableObject |
|:--|:--|:--|
| **Model 块** | 蓝 | `ModelBlockSO`（含 model_id 列表）|
| **Persona 块** | 粉 | `PersonaBlockSO`（含 persona_id 列表）|
| **Mode 块** | 黄 | `ModeBlockSO`（含 mode flags）|
| **Scene 块** | 绿 | `SceneBlockSO`（含 scene_type）|
| **过滤器块**（占位）| 灰 | `FilterBlockSO`（placeholder；NEED-P3-FILTER；多实例可连入同一目标模块；具体过滤器子类待用户后续设计 / 调研）|
| **有效期预测模块**（占位）| 橙 | `MemoryValidityModuleSO`（placeholder；NEED-P3-VALIDITY；引 `module_map_p2 §11.2` MemoryValidity 过滤器 PLANNED；具体规则 / Ebbinghaus 衰减 / 阈值 / 与 Graphiti 写入路径关系待用户独立设计 chat 调研）|

### §4.3 边（连接）

| 边类型 | 含义 |
|:--|:--|
| Model ←→ Persona | 模型与设定的绑定关系（任意组合）|
| Persona ←→ Mode | 设定与模式的覆盖关系 |
| Model/Persona/Mode ←→ Scene | 场景内激活的组合 |
| 过滤器 → 有效期预测模块 | 过滤器对模块生效（多对一：一个模块可被多个过滤器连入；具体过滤规则待后续设计）|

### §4.4 操作

| 操作 | 行为 |
|:--|:--|
| 拖入新节点 | 从节点 palette 拖入画布 |
| 连线 | 节点 port → port 拖动 |
| 选中节点 | 显示属性（如 `model_id` dropdown）|
| 保存预设 | "保存当前组合"按钮 → 输入 preset_id → 写 `data/presets/<preset_id>.json` |
| 加载预设 | "加载预设"按钮 → 选 preset_id → 应用到画布 |

### §4.5 预设 JSON schema（NEED-P3-C）

```json
{
  "preset_id": "default",
  "version": 1,
  "active_model_id": "GOSLO_default",
  "active_persona_id": "goslo_parrot_default",
  "active_mode": ["BASE", "COMPANION"],
  "active_scene_id": "ar_handheld",
  "metadata": {
    "created_at": "2026-05-07T12:00:00Z",
    "user_label": "我的默认配置"
  }
}
```

### §4.6 加载预设 → 应用到 4 active BB key

```python
# src/parrot/brain/preset_loader.py (NEW; deferred to DSG 协议升级 chat)
def apply_preset(preset: Preset) -> None:
    """加载预设 → 写 4 active BB key → 触发各加载器"""
    bb.set("global/active_model_id", preset.active_model_id)
    bb.set("global/active_persona_id", preset.active_persona_id)
    bb.set("global/active_mode", preset.active_mode)  # list[str]
    bb.set("global/active_scene_id", preset.active_scene_id)

    # 触发各加载器
    persona_loader.load(preset.active_persona_id)
    mode_watcher 检测 BB 变化自动切
    SceneRegistry.switch(SceneType(preset.active_scene_id))
    ParrotRegistry / ModelDriver 检测 model_id 变化自动切
    # 注：MemoryValidityModule 节点（NEED-P3-VALIDITY）对应的 preset 字段尚未定义；
    #     待用户独立设计 chat 决定接口后再补入本函数。
```

---

### §4.7 占位说明（NEED-P3-FILTER / NEED-P3-VALIDITY）

> 本小节登记 user-visible 菜单层 placeholder，**不做具体设计**。

- **有效期预测模块**：源自 `module_map_p2 §11.2`（Graphiti 之前的有效期侦测 + Ebbinghaus 衰减，PLANNED）。canvas 上以单一节点呈现；具体内部规则、参数、衰减曲线、与 Graphiti / 对话混合层的关系**待用户独立设计 chat 调研后填充**。
- **过滤器块**：通用过滤器节点抽象。可同时存在多个实例（"一堆"）连接到同一目标模块；每个实例的具体过滤逻辑（text_source / tool_result / cv_track / user_tag / 其它）待用户后续选型。
- **不做的事**：本占位**不**实现 SO 字段、不引 `dsg/ingest/` 现成 5 filter 命名（避免把 backend ingest filter 与 canvas filter block 提前对绑——前者属于 DSG L1.5 入口数据流，后者属于 user-visible 配置层，是否合并由后续设计决定）。
- **后续 chat 出口**：见 `cross_chat_pending_registry §4.I`（过滤器块）/ `§4.J`（有效期预测模块）。

---

## §5 默认 fallback 菜单（NEED-P3-E）

> **目的**：节点画布是高级用户向；普通用户用列表菜单 fallback。

### §5.1 列表选择 UI

```
┌─────────────────────────────┐
│  人设 / 场景配置（默认菜单）  │
├─────────────────────────────┤
│  模型块: [GOSLO_default  ▼] │
│  设定块: [parrot_default ▼] │
│  模式块: [☑ BASE            │
│            ☑ COMPANION      │
│            ☐ BUTLER         │
│            ☐ RESEARCHER     │
│            ☐ PLAYFUL        │
│            ☐ ROLEPLAY ]     │
│  场景块: [ar_handheld     ▼] │
├─────────────────────────────┤
│ [保存为预设]  [恢复默认]    │
│ [应用]                       │
└─────────────────────────────┘
```

### §5.2 操作

| 操作 | 行为 |
|:--|:--|
| 下拉选择 | 直接修改 active 项 |
| 复选 mode | 多选 mode flag |
| 保存为预设 | 输入 preset_id → 写 `data/presets/<id>.json` |
| 恢复默认 | 重置 4 active 为 baseline |
| 应用 | 写 4 active BB key → 触发加载器 |

---

## §6 海盗主题换肤（P3 — NEED-P3-PIRATE-SKIN）

### §6.1 切换方式

- **触发**：启动页第 4 项"人设/场景" → 选海盗预设；或 4 类块菜单切到海盗组合
- **实施**：ScriptableObject swap；不重启 app
- **预设示例**（user 可保存）：

```json
{
  "preset_id": "pirate_demo",
  "active_model_id": "GOSLO_default",
  "active_persona_id": "goslo_pirate_first_mate",
  "active_mode": ["BASE", "COMPANION", "ROLEPLAY"],
  "active_scene_id": "ar_handheld",
  "metadata": {
    "theme_skin": "pirate"
  }
}
```

### §6.2 资产对照表（master_audit §6 + supplement §1.7 合并）

| 元素 | 大小姐宅邸 sprite | 海盗 sprite |
|:--|:--|:--|
| 启动页背景 | 维多利亚 / 蕾丝 / 暖色调 | 深蓝 / 木质 / 黄铜 / 海图 |
| HUD 板 | 像素羊皮纸 | 老海图 / 卷边 / 黄铜钉 |
| 工具柜板 | 同上 | 同上海盗 |
| 放大镜 / 望远镜 | 圆形玻璃 | 海盗望远镜（lore §海盗主题）|
| AR 视野滤镜 | 无 | 半边模糊黑色（眼罩 / lore 钦定）+ 脏镜片可选 |
| 角色头像（HUD）| GOSLO 大小姐 | GOSLO 戴眼罩（大副 skin）|
| 纸条 | 现代邮件 | 卷羊皮纸 + 火漆封 |
| 字体 | 可读像素中文 | 海盗装饰字体（注意可读性挑战，lore §设计挑战）|

### §6.3 字体可读性挑战（lore §设计挑战）

- **问题**：在像素羊皮纸 UI 上显示大量现代文本（如 Google 日程）时，纯像素字体会很模糊
- **方向**：参考 Last Report / Paper Please / Stardew Valley 的字体策略
- **决策**（推 P3 调研 chat）：双字体 — 标题用像素装饰字体（不可读但好看）+ 正文用现代抗锯齿字体（可读但稍违和）

### §6.4 互动表现（lore §互动表现）

- **猫爪伸出递交纸条**（默认主题）：从屏幕底部伸出 2D 像素猫爪 → 抓住纸条 → 摇晃 → 放下
- **海盗手套递交纸条**（海盗主题）：粗糙手 + 卷羊皮纸 + 火漆封
- **音效**：信封纸沙沙 / 火漆封"啪嗒"

---

## §7 像素画素材清单（按菜单细分）

> 与 `master_audit §6` 对应；本节按菜单层细化到具体 sprite 文件。

### §7.1 启动页（Class 1，master_audit §6.1）

| # | sprite | 规格 | 优先级 | 海盗换肤 |
|:--|:--|:--|:--|:--|
| 1.1 | logo_default.png | 320×240 / 24-32 色 | P0 | logo_pirate.png |
| 1.2 | loading_dots_anim/01-08.png | 64×64 ×8 帧 | P0 | — |
| 1.3 | boot_transition_anim/01-24.png | 320×240 ×24 帧 | P0 | — |
| 1.4 | boot_bg_default.png + boot_bg_default_anim/* | 1080×1920（竖）+ 1920×1080（横） | P0 | boot_bg_pirate.png |
| 1.5 | menu_button_normal/hover/pressed.png | 240×48 ×3 | P0 | — |

### §7.2 HUD（Class 2，master_audit §6.2）

| # | sprite | 规格 | 优先级 |
|:--|:--|:--|:--|
| 2.1 | hud_collapsed_icon.png | 48×48 | P0 |
| 2.2 | hud_horizontal_bg.png | 480×96 9-slice | P0 |
| 2.3 | hud_vertical_bg.png | 96×480 9-slice | P0 |
| 2.4 | hud_status_icons/{connect,audio,video,brain,visual_state}.png | 24×24 ×5 ×4 态 | P0 |
| 2.5 | hud_clock_pixel_font.png | 像素字体 | P0 |
| 2.6 | hud_weather_icons/{sunny,cloudy,rainy,snowy}.png | 24×24 ×4 | P1 |

### §7.3 工具柜（Class 3-4，master_audit §6.3-§6.4）

| # | sprite | 规格 | 优先级 |
|:--|:--|:--|:--|
| 3.1 | toolbar_collapsed_icon.png | 48×48 | P0 |
| 3.2 | toolbar_horizontal_bg.png + toolbar_vertical_bg.png | 9-slice | P0 |
| 4.1 | tool_magnifier_default.png + tool_magnifier_pirate.png | 64×64 ×3 态 | P0 |
| 4.2 | tool_attention_box_corners/{tl,tr,bl,br}.png + edges 9-slice | 16×16 + edge | P0 |
| 4.3 | tool_photo_button.png | 64×64 ×3 态 | P0 |
| 4.4 | tool_settings.png + tool_camera_mode.png + tool_workspace_entry.png + tool_node_canvas_entry.png | 64×64 each | P0-P1 |
| 4.5 | tool_calendar.png + tool_task_buttons/{fly,animate,dance,...}.png | 64×64 ×6 | P0-P1 |

### §7.4 反馈消息（Class 5，master_audit §6.5）

| # | sprite | 规格 | 优先级 |
|:--|:--|:--|:--|
| 5.1 | cat_paw_anim_in/01-08.png + cat_paw_anim_out/01-08.png | 96×128 ×8 ×2 | P1 |
| 5.1b | pirate_hand_anim_in/out（海盗换肤） | 同上 | P3 |
| 5.2 | paper_note_folded.png + paper_note_expanded.png + paper_note_shredding/01-04.png | 240×96 + 480×320 | P1 |
| 5.2b | scroll_paper_pirate_*.png（海盗换肤） | 同上 | P3 |
| 5.3 | desk_accept.png + trash_reject.png | 128×128 ×3 态 | P1 |

### §7.5 节点画布（Class 7，master_audit §6.7）

| # | sprite | 规格 | 优先级 |
|:--|:--|:--|:--|
| 7.1 | canvas_bg.png | 全屏 9-slice | P2 |
| 7.2 | block_model_blue.png + block_persona_pink.png + block_mode_yellow.png + block_scene_green.png | 192×96 ×4 | P2 |
| 7.3 | connection_port.png + connection_line.png | 16×16 + 9-slice | P2 |
| 7.4 | block_filter_gray.png（过滤器块，占位）| 192×96（占位）| P3 |
| 7.5 | block_memory_validity_orange.png（有效期预测模块，占位）| 192×96（占位）| P3 |

### §7.6 海盗换肤独立资产

| # | sprite | 规格 | 优先级 |
|:--|:--|:--|:--|
| 6.1 | pirate_eyepatch_overlay.png（半边黑色遮挡） | 全屏 alpha | P3 |
| 6.2 | pirate_dirty_lens_filter.png（脏镜片） | 全屏 alpha | P3 |
| 6.3 | pirate_treasure_map_hud.png（海图 HUD 板） | 同 HUD bg | P3 |
| 6.4 | goslo_eyepatch_avatar.png（GOSLO 戴眼罩头像） | 96×96 | P3 |
| 6.5 | sailor_avatar.png（水手头像，Nanobot） | 96×96 | P3 |

### §7.7 字体

| # | 字体 | 用途 | 优先级 |
|:--|:--|:--|:--|
| 9.1 | pixel_cn_8px.ttf + pixel_cn_12px.ttf + pixel_cn_16px.ttf | 中文像素字体 3 套 | P0 |
| 9.2 | pirate_decorative.ttf（海盗装饰字体）| P3 换肤 | P3 |

---

## §7.6 ChatA LiveKit 启动切片补丁（2026-05-09）

本节是 Sub-Chat A 当前实现约束。画布菜单只做最小实现，是因为它与 LiveKit 稳定连接、启动顺序、切屏生命周期互相阻塞；LiveKit 连接机制本身不按占位处理，按 `client-sdk-unity`、`livekit-unity-lifecycle`、已有问题表和官方 LiveKit 安全资料落最终路径。

### §7.6.1 5 类块：新增 2DWorkspace

| 维度 | 内容 |
|:--|:--|
| ID | `workspace_id`，如 `mansion_hub` / `workdesk` / `report_desk` |
| 数据格式 | `WorkspaceSummary`，只存 UI/canvas surface 摘要和轻量 metadata |
| 加载器 | `parrot.brain.workspace_registry.WorkspaceRegistry` |
| active BB key | `global/active_workspace_id` |
| 切换事件 | `applyWorkspace` RPC 或 `applyMenuSelection` 里的 `workspace_id` |
| 当前默认 | `mansion_hub` |

`2DWorkspace` 与 `IntentWorkspace` 必须区分：

- `2DWorkspace` 是用户看见的 2D App / Canvas / 报告桌 / 工作台表面，负责“当前在看哪个 2D 工具或页面”。
- `IntentWorkspace` 是 Brain 内部资源暂存和生命周期管理层，负责 staged photo、event、note、plan ref、owner scope、磁盘恢复等。
- 两者有交互：2DWorkspace 的 metadata 未来可以保存 IntentWorkspace ref id，用于在报告桌打开某个 staged result；但 2DWorkspace 不持有大 payload，也不替代 IntentWorkspace 的回收/pressure 逻辑。

### §7.6.2 启动与问候策略

当前启动流改为：

```
1. 启动页收集 room / scene / workspace / capability_mode
2. 权限检查；Mic 和 Camera 均按 capability mode 决定是否请求或发布
3. POST `/mint` 获取短期 LiveKit join token
4. RoomManager.Connect(livekit_url, join_token)
5. setAppCapabilityMode RPC 对齐 Brain 侧 session policy
6. onSceneReady 只登记 ready，不主动问候
7. onGosloPlaced 后才允许首次问候，并且必须通过 session_policy.should_generate_reply
8. 进入 HUD + 工具柜；切 workspace 不断 LiveKit room
```

### §7.6.3 静默保活与对话关闭

| 模式 | LiveKit room | Mic publish | Video publish | Brain speech | 用途 |
|:--|:--|:--|:--|:--|:--|
| `SessionOnlySilent` | 保持连接 | 禁止 publish intent，并 unpublish 已有 mic track | 关闭 | 阻断 proactive `generate_reply` | App 保活、等待用户下一步，不让 GOSLO 说话 |
| `VoiceOnlyNoVideo` | 保持连接 | 允许 | 关闭 | 允许 | 仅语音低带宽模式 |
| `VoiceVideoNoActionMonitor` | 保持连接 | 允许 | Gemini only | 允许 | 观察/对话，但不进入全 AR companion |
| `FullARCompanion` | 保持连接 | 允许 | 动态档位 | 允许 | 正常 AR companion |
| 对话关闭且不保活 | 走 graceful shutdown | 先禁用并 unpublish | 关闭 | 阻断 | 结束会话或退后台 |

结论：Session 保活不对话不能只靠堵麦克风。麦克风 publish gate 用来阻断输入，Brain 的 `session_policy.should_generate_reply` 用来阻断输出；两边同时存在，才能保证 GOSLO 不说话。对话不保活则不是“只阻断麦克风”，而是走 `LifecycleShutdownService` 的统一关闭路径。

### §7.6.4 蓝牙与麦克风通道切换

- 麦克风是 LiveKit `TrackSource.SourceMicrophone` 的输入 publish 轨道，受 `MicrophonePublisher.PublishIntentEnabled` 控制。
- 蓝牙主要是设备/系统音频路由问题，不等价于 LiveKit room 生命周期。有蓝牙输入路由时 Unity 默认优先使用蓝牙设备；蓝牙 / 手机麦克风切换通过串行 mic unpublish → rebuild source/sample-rate → publish 完成，不能触发 room 重连。
- 静默模式下路由变化只更新本地 route cache，不会重新发布 mic。
- 未来若要做正式蓝牙选择 UI，应落在 `AudioRoutePolicy` producer 上，写入 `session/audio_route_policy`，而不是在启动流里复制 ParrotDev 的连通性脚本。

### §7.6.5 LiveKit 安全策略

- Unity 不持有 LiveKit API secret，只请求后端 mint 的短期 join token。
- `/mint` 默认短 TTL；自托管环境无法即时撤销旧 token 时，短 TTL 是必要防线。
- Unity 客户端 token 只授予 room join、publish、subscribe、data，不授予 room admin/list/create/record。
- 生产环境必须使用 HTTPS/WSS 和可信证书；TURN/TLS 后续作为弱网/企业网络覆盖项处理。

---

## §8 与 8 场景的关联（菜单 → 场景路径）

> 每个菜单交互对应触发哪些 v0 §5 场景。

| 菜单交互 | 触发场景 | 备注 |
|:--|:--|:--|
| 启动页 #1 "开始 AR" | S0 启动流程 | baseline |
| 启动页 #3 "BrainAgent 管线" | S7 LineA↔LineB 切换 | env-gate |
| 启动页 #5 "场景 baseline" | S8 场景切换 + S0 启动序 | NEED-P2.5-SCENE-2BASELINE |
| 启动页 #4 "人设/场景" → 节点画布 | S6 4 类块菜单 | NEED-P3-D |
| 启动页 #4 → 默认 fallback | S6 4 类块菜单 | NEED-P3-E |
| 工具柜 "拍照按钮" | S3 拍照 → 评论 | Phase 4 W8 |
| 工具柜 "放大镜" + "注意力框" | S1 GOSLO 对话（视觉门控）+ S2 主动好奇（注意力扩散）| Phase 4 W6-7 |
| 工具柜 "相机模式" | S10 视频档位运行时调节 | set_video_tier |
| 工具柜 "任务按钮" | S1 fly_to / animate / dance / S4 dispatch_task | parrot_behavior_rules |
| 工具柜 "2D 工作区入口" | S4 富文本批改 / 汇报展示 | NEED-P3-D 配套 |
| 工具柜 "节点画布入口" | S6 4 类块菜单（高级用户向）| NEED-P3-D |
| 海盗主题切换 | 跨场景换肤；触发 Mode 块 ROLEPLAY + Persona 块切 | NEED-P3-PIRATE-SKIN + NEED-P3-MODE-ROLEPLAY |
| 手势 perch_to_finger | S1.5（不通过菜单触发）| Reflex 层；不打扰菜单 |
| 节点画布 §4.7 占位（过滤器块 + 有效期预测模块）| 后续 NEED-P3 设计 chat | NEED-P3-FILTER + NEED-P3-VALIDITY |

---

## §9 实施推荐顺序

> Phase 编号与 v0 §7 推荐执行顺序对齐。

| Phase | 内容 | 状态 |
|:--|:--|:--|
| **A1** 启动页 baseline | 6 项主菜单 + 默认占位 sprite + 持久化 PlayerPrefs | Sub-Chat A 用户视角主任务（S0）|
| **A2** HUD baseline | 4 corner 选 + 横/竖向 + 6 状态 icon + 持久化 | S9 |
| **A3** 工具柜 baseline | P0 道具 6 个（设置 / 相机模式 / 拍照 / 放大镜 / 注意力框 / 任务按钮）| S9 + S3 + S10 |
| **B1** Persona 外置 | NEED-P2.5-A → DSG 协议升级 chat | 4 类块前置 |
| **B2** 4 类块统一注册表 | NEED-P3-B（Persona 块 + 4 active BB key） | DSG 协议升级 chat |
| **B3** 预设 schema | NEED-P3-C（data/presets/<id>.json）| 同上 |
| **C1** 默认 fallback 菜单 | NEED-P3-E（列表选 + 保存 + 恢复默认） | AR 工作区独立 chat |
| **C2** 节点画布 | NEED-P3-D（高级用户向）| AR 工作区独立 chat |
| **D** 海盗主题换肤 | NEED-P3-PIRATE-SKIN（ScriptableObject swap） | AR 工作区独立 chat / P3 |
| **E** 字体可读性优化 | lore §设计挑战 / 调研 P3 | P3 |

---

## §10 不在本文范围（推到对应 chat）

| 项 | 推到哪 |
|:--|:--|
| Plan UI wire（场景 5）| P3 wire 升级 ADR chat（占位 stub UI 即可）|
| body_state 解锁 | P3 wire 升级 ADR chat |
| Plan UI 上 menu | P3 wire ADR chat / AR 工作区独立 chat |
| 多设备 input 选择（P3.5）| P3.5 玩法扩展 chat |
| 群聊 / 多 user / 光遇式（NEED-P3-MULTIPLAYER）| 远期 |
| Web 控制台 | NEED-P3-WEB-CONSOLE / 子项目 |

---

## §11 引用源

- AR App Flow / UI baseline：`ar_app_flow_ui_design.md`
- 海盗 / 猫爪 / 望远镜 / 字体可读性灵感：`lore/ideas.md` 2026-04-27
- 4 类块结构 + 预设 schema 构想：`goslo_modularization_residual_debt §4.3`
- 接口设计 v0 + 补丁：`Interface/interface_design_and_how_todo_v0_20260507.md` + `interface_design_supplement_20260507.md`
- 概念词典：`Interface/concept_dictionary_20260507.md`
- 遗留问题：`Interface/legacy_issues_split_20260507.md`
- 像素画素材清单 baseline：`app_completion_master_audit_20260507.md §6`
- Phase 4 §8 锁：`sprint4_phase4_entry_20260430.md §8`
- Roleplay 联动：`dsg/dsg_decisions_master.md §3.2`

---

## §12 变更日志

- **2026-05-09 ChatA**：补充 LiveKit 启动切片。菜单从 4 类块运行态扩为 5 类块（新增 2DWorkspace），明确 2DWorkspace 与 IntentWorkspace 边界；启动问候延后到 `onGosloPlaced`；新增 `SessionOnlySilent` 静默保活、对话关闭、蓝牙/麦克风路由、安全 token 策略说明。画布菜单本轮保持最小实现，LiveKit 生命周期按最终路径实现。
- **2026-05-07**：本文创建。三层菜单架构（启动页 + HUD/工具柜 + 节点画布）+ 4 类块定义（Model/Persona/Mode/Scene）+ 预设系统（NEED-P3-B/C）+ 默认 fallback（NEED-P3-E）+ 海盗主题换肤（P3）+ 像素画素材按菜单细分清单 + 与 8 场景关联表 + 实施推荐顺序 Phase A-E。
- **2026-05-07 v0.1（增量）**：§4 加 2 占位节点类型（过滤器块灰 / 有效期预测模块橙）+ §4.3 边追加"过滤器 → 模块"+ §4.7 占位说明小节 + §7.5 素材 2 条（block_filter_gray / block_memory_validity_orange）+ §8 关联表 1 行；具体设计延后到 NEED-P3-FILTER / NEED-P3-VALIDITY；与 backend `memory/MemoryValidity 过滤器` PLANNED（`module_map_p2 §11.2`）对接，但 canvas 占位**不**强行绑定 backend schema。
