# 菜单画布外部模块业务接口流

> 对应设计：`../unity_ar_app/menu_canvas_external_modules_20260509.md`  
> 写法：遵循 `.cursor/memory/architecture/Interface/INDEX.md` 的 A-D 纪律，只写业务切片，不复制核心接口大全。

## A. 模块职责回读

必读事实源：

- `.cursor/memory/architecture/Interface/obsidian_true_connection_guide_20260509.md`
- `.cursor/memory/architecture/Interface/google_calendar_nanobot_true_connection_guide_20260509.md`
- `.cursor/memory/architecture/Interface/photo_memory_awareness_true_connection_guide_20260509.md`

业务设计源：

- `codex_workspace/design_workspace/unity_ar_app/menu_canvas_mvp_2dworkspace_20260509.md`
- `codex_workspace/design_workspace/unity_ar_app/menu_canvas_external_modules_20260509.md`
- `codex_workspace/design_workspace/app_2d_workspace/INDEX.md`

## B. 现有核心接口能否组合实现？

**部分 yes。**

已足够设计和做第一版只读/草稿流：

- `MenuRegistry.list_blocks()` 已能提供核心块和 workspace。
- `PresetLoader` / `WorkspaceRegistry` 已能保存 `active_workspace_id`。
- Obsidian ingest、Google read path、Photo asset path / staged ref、Nanobot result routing 都已有基础。
- IntentWorkspace 可承载 calendar draft、photo staged ref、report payload。

仍缺的核心表面见 C。

## C. 缺什么核心表面？

| 候选命名 | 落点模块 | 是否进协议 SSOT | 是否需要 Unity DTO 镜像 |
|:--|:--|:--|:--|
| `list_external_module_status()` | Brain / Menu | 是，作为 App menu RPC DTO | 是 |
| `refresh_external_module(module_id)` | Brain -> Scheduler / DSG | 是，动作类型需要稳定 | 是 |
| `create_intent_draft(kind, payload_ref)` | Brain / IntentWorkspace | 可能已有概念，需确认公开 DTO | 是 |
| `set_goslo_policy(policy_patch)` | Brain / SessionPolicy | 是，不能直接写 BB | 是 |
| `check_obsidian_vault(vault_path)` | Script / later Brain adapter | 否，先本地工具；进入 App 时再 DTO | 可选 |
| `photo_awareness_enabled` / policy RPC | Brain / Photo Awareness | 是 | 是 |

当前设计阶段不直接改协议；这些是后续实现菜单画布模块时要补的公开表面。

## D. 完成判据

### 正向

- 用户打开菜单画布，看到核心五块和外部模块 dock。
- Google 模块能显示授权/同步/草稿状态，写操作只生成 draft。
- Obsidian 模块能显示本地 vault 是否可达、有效 note 数、当前 profile。
- Obsidian 模块能区分“设定源 note”和“Ref 强化 note”：daily / roleplay 不要求 UUID，ref 才要求 UUID / Graphiti / L2-B 绑定线索。
- GOSLO Module 能显示 silent keepalive、Photo Awareness、语音/相机状态。
- Nanobot 模块能显示 idle/busy/result/error，并把结果变成报告纸条。
- Photo 模块能显示最近照片、上传状态、IntentWorkspace ref、Awareness decision。

### 失败态

- Google 未授权：显示 `needs_auth`，不阻塞 App 启动。
- Obsidian vault 未配置：显示 `local_missing`，提供本地配置入口。
- Obsidian vault 可达但无合法 note：显示 `no_valid_notes`，提示 frontmatter 模板；不要误提示 daily / roleplay 必须填写 UUID。
- Nanobot disconnected：显示 disconnected，不吞掉 Scheduler 错误。
- Photo preview/asset 丢失：显示 partial 状态，并进入恢复/重试提示。
- IntentWorkspace 压力过高：模块只显示 ref 过期，不持有 payload。
