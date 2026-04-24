# ECS / 远端 — 单次测试跑报告（独立文件，防冲突）

## 规则

1. **不要**直接改 `../pipeline_test_matrix_sprint3.md` 里的「状态」列来记临时跑表（易与多人/多机冲突）；主矩阵仍由 **负责人**在 Git 里维护。  
2. 每次陪跑 / 真机联调，在此目录 **新建一个文件**，命名：

   `report-YYYYMMDDThhmmZ-{你的缩写或hostname}.md`

   例：`report-20260423T0830Z-castle.md`

3. 文件内容建议结构：

   - **时间轴**：按 **UTC** 列 Unity 行 → Brain 行 → docker 行（只摘要）。  
   - **阶段**：写明当时处于 **P0 / P1 / P2** 哪一步（与 `pipeline_test_matrix_sprint3.md` §0 对齐）。  
   - **结论**：pass / fail / blocked + 一条原因。  
   - **回填**：提醒主仓 **`sprint3_completion_report` §7** 与矩阵 **§3** 由谁更新。

4. 若希望报告 **也进 Git**：在 ECS clone 里 `git add` 本文件 → commit → push（与日常流程一致）；若仅本地留档可不放 Git。

## 与 Gemini / 对话时间轴

- 远端陪跑 Cursor **可把本文件路径**写进对话，便于会话内对齐；**不要**把整份日志贴进 Gemini（体积与 secret 风险）。  
- Unity 侧仍以 **`parrot_diagnostics.log`** 与 **`[SEQ]`** 为硬锚点。
