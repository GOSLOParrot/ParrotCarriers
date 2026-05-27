# PPT Skill 工作区

这个目录为 `codex-ppt` 准备。当前只建立阶段性工作区，不生成最终 PPT、图片或 prompt。

## 阶段

1. `assets/`：放源图、截图、风格参考图。
2. `outline_review/`：放待确认的 PPT 大纲。
3. `style_review/`：放风格选项和最终风格说明。
4. `sample_review/`：放一页样张和反馈记录。
5. `final_export/`：放最终 `.pptx` 和导出检查结果。

## 约束

- 大纲确认前，不生成最终 `deck_spec.json`、`speech.md`、prompt 文件、幻灯片图片或 `.pptx`。
- 视觉风格确认前，不进入图片生成。
- 图片后端确认前，不生成样张。
- 样张确认前，不批量生成整套幻灯片。
