export const S = {
  bg: "#F7F8FA",
  white: "#FFFFFF",
  ink: "#111827",
  text: "#334155",
  muted: "#64748B",
  soft: "#94A3B8",
  line: "#D8DEE8",
  blue: "#2563EB",
  blue2: "#1D4ED8",
  cyan: "#0891B2",
  paleBlue: "#EAF2FF",
  paleCyan: "#E8F7FA",
  paleGray: "#EEF2F7",
  dangerSoft: "#FFF1F2",
  successSoft: "#ECFDF5",
};

export function rect(slide, ctx, x, y, w, h, fill = S.white, line = S.line, width = 1, name) {
  return ctx.addShape(slide, {
    x, y, w, h,
    geometry: "rect",
    fill,
    line: ctx.line(line, width),
    name,
  });
}

export function pill(slide, ctx, x, y, w, h, fill, line, name) {
  return rect(slide, ctx, x, y, w, h, fill, line, 1, name);
}

export function rule(slide, ctx, x, y, w, color = S.line, h = 1) {
  return ctx.addShape(slide, {
    x, y, w, h,
    geometry: "rect",
    fill: color,
    line: ctx.line(color, 0),
  });
}

export function text(slide, ctx, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: value,
    x, y, w, h,
    size: opts.size ?? 24,
    color: opts.color ?? S.ink,
    bold: opts.bold ?? false,
    face: opts.face ?? "Microsoft YaHei UI",
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "#00000000",
    line: ctx.line("#00000000", 0),
    insets: opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
    name: opts.name,
  });
}

export function label(slide, ctx, value, x, y, w, color = S.blue) {
  return text(slide, ctx, value, x, y, w, 22, {
    size: 12,
    bold: true,
    color,
    face: "Aptos",
  });
}

export function title(slide, ctx, value, x = 70, y = 88, w = 850, size = 42) {
  return text(slide, ctx, value, x, y, w, 108, {
    size,
    bold: true,
    color: S.ink,
    face: "Microsoft YaHei UI",
  });
}

export function subtitle(slide, ctx, value, x, y, w, h = 64) {
  return text(slide, ctx, value, x, y, w, h, {
    size: 22,
    color: S.text,
    face: "Microsoft YaHei UI",
  });
}

export function footer(slide, ctx, n, note = "AR+生活助手与智能提醒 | 毕业答辩样张") {
  rule(slide, ctx, 70, 674, 1040, S.line, 1);
  text(slide, ctx, note, 70, 688, 760, 18, { size: 10.5, color: S.soft, face: "Aptos" });
  text(slide, ctx, String(n).padStart(2, "0"), 1150, 684, 60, 22, {
    size: 12,
    color: S.soft,
    align: "right",
    face: "Aptos",
    bold: true,
  });
}

export async function iconBox(slide, ctx, icon, x, y, fill, color = S.blue) {
  rect(slide, ctx, x, y, 46, 46, fill, fill, 0);
  await ctx.addLucideIcon(slide, {
    icon,
    x: x + 11,
    y: y + 11,
    w: 24,
    h: 24,
    color,
    strokeWidth: 2,
  });
}

export function arrowText(slide, ctx, x, y, color = S.muted) {
  return text(slide, ctx, "→", x, y, 32, 30, {
    size: 24,
    color,
    align: "center",
    face: "Aptos",
  });
}
