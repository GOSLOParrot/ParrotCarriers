# P2.5 / Sprint 3 — 人手测试文档（Git 跟踪）

> **为何在此目录**：仓库根 **`Test/`** 在 `.gitignore` 中整目录忽略，**不会进入远程**；本目录 **`docs/test/p2_5/`** 与 **`tests/`**（pytest）区分，**可 commit / push**，Castle 上 `git pull` 即可与 Unity 侧对齐同一套 **阶段顺序 + 矩阵**。

| 文件 | 用途 |
|:-----|:-----|
| `pipeline_test_matrix_sprint3.md` | **主操作表**：P0→P1→P2、§C/§D 步骤、§3 矩阵、`[SEQ]` 与日志对表 |
| `remote_cursor_test_monitor_boot_prompt.md` | Remote SSH Cursor **启动提示词**（引用区整段粘贴） |
| `HANDOFF_ACTIVE_CONTEXT_FOR_ECS.md` | 真 **`active_context.md`** 被 ignore 时的 **脱敏交接模板** |
| `ECS_RUN_REPORTS/README.md` | ECS / 远端 **独立跑报告** 命名规则（防与主矩阵冲突） |

**勿提交**：JWT、Mint secret、完整 `parrot_config.json`（真文件仍 gitignore，见仓库根 `.gitignore`）。
