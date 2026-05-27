import { S, rect, rule, text, label, title, subtitle, footer, iconBox, arrowText } from "./common.mjs";

export async function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, 1280, 720, S.bg, S.bg, 0);
  label(slide, ctx, "PROBLEM FRAMING", 70, 56, 220, S.blue);
  title(slide, ctx, "传统助手缺少的不是回答能力，\n而是场景上下文。", 70, 88, 900, 45);
  subtitle(slide, ctx, "AR 场景里的助手需要知道用户正在看什么、做什么，以及哪些外部信息值得进入当前判断。", 72, 208, 860, 60);

  rect(slide, ctx, 84, 312, 430, 238, S.white, S.line, 1);
  rect(slide, ctx, 766, 312, 430, 238, S.white, S.line, 1);
  text(slide, ctx, "传统助手", 118, 344, 170, 34, { size: 26, bold: true, color: S.ink });
  text(slide, ctx, "主要依赖文本、固定时间和单次对话", 118, 386, 330, 30, { size: 18, color: S.muted });
  await iconBox(slide, ctx, "MessageSquare", 118, 442, S.paleGray, S.muted);
  await iconBox(slide, ctx, "Calendar", 180, 442, S.paleGray, S.muted);
  text(slide, ctx, "知道“你说了什么”\n但不一定知道“你现在处在什么场景”", 260, 438, 220, 66, {
    size: 18,
    color: S.text,
  });

  text(slide, ctx, "AR 场景 Agent", 800, 344, 220, 34, { size: 26, bold: true, color: S.ink });
  text(slide, ctx, "把实时感知、记忆和后台任务组织起来", 800, 386, 340, 30, { size: 18, color: S.muted });
  await iconBox(slide, ctx, "Video", 800, 442, S.paleBlue, S.blue);
  await iconBox(slide, ctx, "Network", 862, 442, S.paleCyan, S.cyan);
  await iconBox(slide, ctx, "Database", 924, 442, S.paleGray, S.ink);
  text(slide, ctx, "理解当前环境\n再决定是否主动协助", 1004, 438, 150, 66, {
    size: 18,
    color: S.text,
  });

  rule(slide, ctx, 548, 424, 156, S.line, 2);
  arrowText(slide, ctx, 616, 404, S.blue);
  text(slide, ctx, "从被动问答\n到场景协助", 552, 456, 152, 60, {
    size: 20,
    bold: true,
    color: S.blue,
    align: "center",
  });

  rect(slide, ctx, 84, 586, 1112, 42, S.paleBlue, "#BBD3FF", 1);
  text(slide, ctx, "本项目的目标：让语音、视频、照片、日程、笔记和历史记忆进入同一条可追踪的数据流。", 112, 596, 1040, 24, {
    size: 20,
    color: S.ink,
    bold: true,
  });

  footer(slide, ctx, 2);
  return slide;
}
