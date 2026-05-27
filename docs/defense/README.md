# 答辩工作包

这个目录作为答辩准备的工作区。当前阶段只建立结构，不提前定死正文、PPT 图稿或最终表达。

## 工作流

1. `00_user_original_requirements.md`：记录原话需求、注意点、选用例子和大纲入口。
2. `drafts/01_outline.md`：大纲稿，先按“时间 / 内容 / 说什么”组织。
3. `drafts/02_speech_script.md`：演讲稿，后续负责把研究内容讲顺。
4. `drafts/03_ppt_script.md`：PPT 稿，后续负责把内容转换成直观展示。
5. `ppt_skill_workspace/`：给 `codex-ppt` skill 使用的 PPT 工作区，先只放确认阶段材料。
6. `workbench/`：放判断过程、流程例子、内容取舍，不直接作为最终稿。
7. `refs/`：放 Index、样式 Ref、skill 判断等暂存材料，后续再决定是否进入正式稿。

## 当前原则

- 先判断内容适合“口头讲清楚”，还是适合“PPT 直观展示”。
- 保留技术名词，但解释要服务于软件工程答辩。
- 先用实现中能确认的流程做例子，再逐步写进大纲和演讲稿。
- `nanobot` 后台 Worker 不作为 LiveKit 挂载模块来讲。
- `codex-ppt` 已安装到全局 skill 目录；重启 Codex 后可正式触发。
- 使用 `codex-ppt` 时不跳过确认门：先确认大纲，再确认视觉风格，再确认图片后端和样张。

## PPT Skill 工作区

- `ppt_skill_workspace/assets/`：后续放必须进入 PPT 的图片、截图、参考图。
- `ppt_skill_workspace/outline_review/`：后续放待确认的 PPT 大纲。
- `ppt_skill_workspace/style_review/`：后续放风格方向与样式选择。
- `ppt_skill_workspace/sample_review/`：后续放一页样张和修改意见。
- `ppt_skill_workspace/final_export/`：后续放最终 PPTX、导出图片或检查结果。
