import { S, rect, rule, text, label, subtitle, footer, iconBox, arrowText } from "./common.mjs";

export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, 1280, 720, S.bg, S.bg, 0);

  rule(slide, ctx, 70, 70, 5, S.blue, 58);
  label(slide, ctx, "GRADUATION DEFENSE", 92, 72, 240, S.blue);
  text(slide, ctx, "软件工程 / AR Agent 原型", 92, 96, 320, 24, { size: 15, color: S.muted });

  text(slide, ctx, "AR+生活助手与\n智能提醒系统设计与实现", 70, 176, 690, 150, {
    size: 50,
    bold: true,
    color: S.ink,
    face: "Microsoft YaHei UI",
  });
  subtitle(slide, ctx, "从实时交互到场景记忆，让助手理解当前环境并主动协助。", 74, 356, 600, 64);

  const rails = [
    ["实时交互", "LiveKit / RPC / ACK"],
    ["场景记忆", "DSG / Ref / UUID"],
    ["后台协作", "Scheduler / nanobot"],
  ];
  rails.forEach((item, i) => {
    const x = 74 + i * 190;
    rule(slide, ctx, x, 498, 34, i === 0 ? S.blue : i === 1 ? S.cyan : S.ink, 3);
    text(slide, ctx, item[0], x, 518, 150, 28, { size: 20, bold: true, color: S.ink });
    text(slide, ctx, item[1], x, 552, 160, 24, { size: 12.5, color: S.muted, face: "Aptos" });
  });

  rect(slide, ctx, 780, 118, 360, 420, S.white, S.line, 1);
  text(slide, ctx, "系统主线", 812, 150, 160, 28, { size: 20, bold: true, color: S.ink });
  text(slide, ctx, "不是功能堆叠，而是一条可追踪的数据流", 812, 184, 270, 42, { size: 16, color: S.muted });

  const nodes = [
    ["用户场景", "Mic / Camera / UI", "Camera", S.paleBlue, S.blue],
    ["实时通信", "Track / Data / RPC", "Radio", S.paleCyan, S.cyan],
    ["Brain Agent", "Intent / Tool / Context", "BrainCircuit", S.paleBlue, S.blue2],
    ["记忆与任务", "DSG / Graphiti / Task", "Network", S.paleGray, S.ink],
  ];
  nodes.forEach((node, i) => {
    const y = 250 + i * 68;
    iconBox(slide, ctx, node[2], 812, y, node[3], node[4]);
    text(slide, ctx, node[0], 874, y + 3, 180, 24, { size: 18, bold: true, color: S.ink });
    text(slide, ctx, node[1], 874, y + 30, 210, 22, { size: 12.5, color: S.muted, face: "Aptos" });
    if (i < nodes.length - 1) arrowText(slide, ctx, 828, y + 48, S.soft);
  });

  text(slide, ctx, "样张 01", 1044, 568, 96, 22, { size: 12, color: S.soft, align: "right", face: "Aptos" });
  footer(slide, ctx, 1);
  return slide;
}
