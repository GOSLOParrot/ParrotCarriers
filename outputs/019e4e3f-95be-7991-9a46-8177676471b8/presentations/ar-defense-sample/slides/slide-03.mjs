import { S, rect, rule, text, label, title, subtitle, footer, iconBox, arrowText } from "./common.mjs";

async function sourceCard(slide, ctx, { x, y, icon, name, desc, tag, fill, color }) {
  rect(slide, ctx, x, y, 204, 176, S.white, S.line, 1);
  await iconBox(slide, ctx, icon, x + 20, y + 20, fill, color);
  text(slide, ctx, name, x + 20, y + 78, 166, 28, { size: 20, bold: true, color: S.ink });
  text(slide, ctx, desc, x + 20, y + 111, 166, 38, { size: 14.5, color: S.text });
  text(slide, ctx, tag, x + 20, y + 148, 166, 18, { size: 10.5, color: S.muted, face: "Aptos" });
}

export async function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, 1280, 720, S.bg, S.bg, 0);
  label(slide, ctx, "INPUT SOURCES", 70, 56, 220, S.blue);
  title(slide, ctx, "场景 Agent 的输入不是一条文本，\n而是一组可追踪信号。", 70, 88, 900, 43);
  subtitle(slide, ctx, "先让老师认识输入源，再进入总体架构。这里不堆技术栈，只说明每类输入进入系统后的作用。", 72, 198, 880, 52);

  const y = 300;
  const cards = [
    { x: 70, y, icon: "Radio", name: "LiveKit / SVA", desc: "实时音视频与视频结构化处理", tag: "Track / Processor", fill: S.paleBlue, color: S.blue },
    { x: 300, y, icon: "Bot", name: "nanobot", desc: "后台任务 Agent / Worker 模式", tag: "Task / gateway", fill: S.paleCyan, color: S.cyan },
    { x: 530, y, icon: "Calendar", name: "Calendar", desc: "日程、提醒与时间上下文", tag: "Time context", fill: S.paleGray, color: S.ink },
    { x: 760, y, icon: "BookOpen", name: "Obsidian", desc: "本地笔记、日记和个人知识", tag: "Local knowledge", fill: S.paleBlue, color: S.blue2 },
    { x: 990, y, icon: "ScanSearch", name: "CV 扩展", desc: "检测、分割、特征和场景图方向", tag: "YOLO / SAM2 / DINOv2", fill: S.paleCyan, color: S.cyan },
  ];
  for (const card of cards) await sourceCard(slide, ctx, card);

  rule(slide, ctx, 136, 520, 1008, S.line, 2);
  [240, 470, 700, 930].forEach((x) => arrowText(slide, ctx, x, 506, S.soft));

  rect(slide, ctx, 332, 566, 616, 54, S.paleBlue, "#BBD3FF", 1);
  text(slide, ctx, "统一落点：Observation / Ref / Intent / Task / Episode", 372, 580, 536, 24, {
    size: 22,
    bold: true,
    color: S.ink,
    align: "center",
  });

  text(slide, ctx, "注意：CV 扩展页只讲能力方向，不讲成完整落地的视觉流水线。", 70, 632, 850, 22, {
    size: 14.5,
    color: S.muted,
  });

  footer(slide, ctx, 3);
  return slide;
}
