from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
BASE_DIR = ROOT / "docs" / "defense" / "ppt_skill_workspace" / "final_export"
DECK_NAME = "ar_defense_clean_v1"
DECK_DIR = BASE_DIR / DECK_NAME
ORIGIN_DIR = DECK_DIR / "origin_image"

W, H = 2560, 1440

BG = "#F8FAFC"
WHITE = "#FFFFFF"
INK = "#111827"
TEXT = "#273449"
MUTED = "#64748B"
LINE = "#D7DEE8"
SOFT = "#EFF6FF"
BLUE = "#2563EB"
CYAN = "#0891B2"
GREEN = "#16A34A"
ORANGE = "#D97706"
RED = "#DC2626"
PALE_CYAN = "#E8F7FA"
PALE_GREEN = "#ECFDF3"
PALE_ORANGE = "#FFF7ED"

FONT_REG = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/simhei.ttf")
FONT_EN = Path("C:/Windows/Fonts/arial.ttf")


def font(size: int, bold: bool = False, en: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_EN if en else (FONT_BOLD if bold else FONT_REG)
    return ImageFont.truetype(str(path), size=size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    if not text:
        return 0, 0
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        line = ""
        for ch in raw:
            candidate = line + ch
            if text_bbox(draw, candidate, fnt)[0] <= max_width or not line:
                line = candidate
            else:
                lines.append(line)
                line = ch
        lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 14,
    anchor: str = "la",
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    cursor = y
    for line in lines:
        if anchor == "mm":
            draw.text((x, cursor), line, font=fnt, fill=fill, anchor="mm")
        else:
            draw.text((x, cursor), line, font=fnt, fill=fill)
        cursor += fnt.size + line_gap
    return cursor


def arrow(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], fill: str = BLUE, width: int = 6) -> None:
    draw.line([a, b], fill=fill, width=width)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    length = 22
    spread = math.pi / 7
    p1 = (b[0] - length * math.cos(ang - spread), b[1] - length * math.sin(ang - spread))
    p2 = (b[0] - length * math.cos(ang + spread), b[1] - length * math.sin(ang + spread))
    draw.polygon([b, p1, p2], fill=fill)


def line_arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: str = BLUE, width: int = 6) -> None:
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=fill, width=width)
    if len(points) > 1:
        arrow(draw, points[-2], points[-1], fill=fill, width=width)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = WHITE, outline: str = LINE, radius: int = 6) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def pill(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, fill: str, outline: str, text_fill: str = INK, size: int = 34) -> None:
    draw.rounded_rectangle(box, radius=6, fill=fill, outline=outline, width=2)
    draw.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2 - 2), label, font=font(size, bold=True), fill=text_fill, anchor="mm")


def header(draw: ImageDraw.ImageDraw, idx: int, section: str, title: str, subtitle: str | None = None) -> None:
    draw.rectangle((124, 112, 130, 170), fill=BLUE)
    draw.text((150, 108), section.upper(), font=font(22, en=True), fill=BLUE)
    draw.text((150, 148), title, font=font(76, bold=True), fill=INK)
    if subtitle:
        draw_wrapped(draw, (152, 250), subtitle, font(34), MUTED, 1220, line_gap=10)
    draw.text((2360, 1320), f"{idx:02d}", font=font(24, en=True), fill="#A3AAB6")
    draw.line((150, 1280, 2410, 1280), fill="#E2E8F0", width=2)


def new_slide() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def save(img: Image.Image, idx: int) -> None:
    ORIGIN_DIR.mkdir(parents=True, exist_ok=True)
    img.save(ORIGIN_DIR / f"slide_{idx:02d}.png", quality=96)


def s1() -> None:
    img, d = new_slide()
    d.rectangle((0, 0, W, H), fill=BG)
    d.rectangle((128, 118, 134, 184), fill=BLUE)
    d.text((158, 112), "GRADUATION DEFENSE", font=font(24, en=True), fill=BLUE)
    d.text((158, 166), "AR 生活助手与智能提醒系统", font=font(86, bold=True), fill=INK)
    d.text((162, 300), "从实时交互到场景记忆", font=font(38), fill=MUTED)
    d.line((166, 492, 760, 492), fill=LINE, width=4)
    d.text((166, 560), "实时交互", font=font(42, bold=True), fill=INK)
    d.text((166, 640), "场景记忆", font=font(42, bold=True), fill=INK)
    d.text((166, 720), "后台协作", font=font(42, bold=True), fill=INK)
    cx, cy = 1740, 660
    d.ellipse((cx - 135, cy - 135, cx + 135, cy + 135), outline=BLUE, width=8, fill=SOFT)
    d.text((cx, cy - 18), "GOSLO", font=font(44, bold=True), fill=INK, anchor="mm")
    d.text((cx, cy + 34), "Scene Agent", font=font(28, en=True), fill=MUTED, anchor="mm")
    labels = [("User", 1350, 360, BLUE), ("LiveKit", 2030, 380, CYAN), ("DSG", 1320, 945, GREEN), ("Task", 2100, 930, ORANGE)]
    for label, x, y, color in labels:
        d.ellipse((x - 68, y - 68, x + 68, y + 68), outline=color, width=6, fill=WHITE)
        d.text((x, y), label, font=font(28, bold=True, en=True), fill=INK, anchor="mm")
        arrow(d, (cx + int((x - cx) * 0.58), cy + int((y - cy) * 0.58)), (x - int((x - cx) * 0.11), y - int((y - cy) * 0.11)), fill=color, width=5)
    d.text((158, 1300), "软件工程答辩 | 2026", font=font(24), fill="#A3AAB6")
    save(img, 1)


def s2() -> None:
    img, d = new_slide()
    header(d, 2, "goal", "项目目标", "让助手理解当前场景，并在合适时机协助用户。")
    words = [("感知", "语音、视频、照片", BLUE), ("记忆", "日程、笔记、历史情景", GREEN), ("行动", "前台动作与后台任务", ORANGE)]
    y = 560
    for i, (big, small, color) in enumerate(words):
        x = 360 + i * 720
        d.text((x, y), big, font=font(76, bold=True), fill=INK, anchor="mm")
        d.line((x - 120, y + 76, x + 120, y + 76), fill=color, width=8)
        d.text((x, y + 156), small, font=font(32), fill=MUTED, anchor="mm")
    d.text((W // 2, 1040), "核心产物：一条可追踪的数据流", font=font(52, bold=True), fill=INK, anchor="mm")
    d.text((W // 2, 1115), "Observation / Ref / Intent / Task / Episode", font=font(34, en=True), fill=BLUE, anchor="mm")
    save(img, 2)


def s3() -> None:
    img, d = new_slide()
    header(d, 3, "input", "场景输入", "语音、视频、照片、日程和笔记先变成可追踪信号。")
    sources = [("LiveKit / SVA", "实时音视频"), ("nanobot", "后台任务"), ("Calendar", "时间上下文"), ("Obsidian", "长期知识"), ("CV 扩展", "对象与关系")]
    start_y = 440
    for i, (name, desc) in enumerate(sources):
        y = start_y + i * 130
        d.text((210, y), name, font=font(40, bold=True), fill=INK)
        d.text((210, y + 54), desc, font=font(28), fill=MUTED)
        d.line((560, y + 22, 910, y + 22), fill=LINE, width=4)
    d.line((910, 462, 1040, 980), fill=LINE, width=6)
    panel(d, (1120, 500, 1960, 840), fill=WHITE)
    d.text((1540, 610), "统一入口", font=font(58, bold=True), fill=INK, anchor="mm")
    d.text((1540, 706), "Observation / Ref / Task", font=font(38, en=True), fill=BLUE, anchor="mm")
    arrow(d, (1960, 670), (2240, 670), fill=BLUE, width=8)
    d.text((2300, 670), "DSG\nGraphiti\nScheduler", font=font(38, bold=True), fill=INK, anchor="lm", spacing=18)
    save(img, 3)


def s4() -> None:
    img, d = new_slide()
    header(d, 4, "architecture", "总体架构", "前端、实时通信、Agent、记忆和后台任务分层协作。")
    y = 680
    xs = [250, 690, 1130, 1570, 2010]
    nodes = [
        ("Unity AR", "相机 / 麦克风 / UI", BLUE),
        ("LiveKit", "Track / Data / RPC", CYAN),
        ("Brain Agent", "Intent / Tool / Context", INK),
        ("DSG / Graphiti", "工作记忆 / 长期记忆", GREEN),
        ("Scheduler", "Redis / nanobot", ORANGE),
    ]
    for i, (title, desc, color) in enumerate(nodes):
        panel(d, (xs[i], y - 120, xs[i] + 320, y + 120), fill=WHITE, outline=color)
        d.text((xs[i] + 160, y - 28), title, font=font(38, bold=True, en=i < 2), fill=INK, anchor="mm")
        d.text((xs[i] + 160, y + 40), desc, font=font(25), fill=MUTED, anchor="mm")
        if i < len(nodes) - 1:
            arrow(d, (xs[i] + 330, y), (xs[i + 1] - 22, y), fill=LINE, width=6)
    d.text((W // 2, 1045), "nanobot 位于后台任务侧，经 Scheduler / Redis 派发", font=font(40, bold=True), fill=INK, anchor="mm")
    save(img, 4)


def s5() -> None:
    img, d = new_slide()
    header(d, 5, "livekit", "实时音视频通道", "Room 组织参与者和轨道，数据通道承载状态与事件。")
    d.line((360, 720, 2200, 720), fill=BLUE, width=10)
    d.text((1280, 650), "LiveKit Room", font=font(50, bold=True, en=True), fill=INK, anchor="mm")
    channels = [("Audio Track", "语音输入", 520, 500), ("Video Track", "画面输入", 1000, 930), ("DataChannel", "事件与状态", 1520, 500), ("RPC", "前台动作", 2000, 930)]
    for name, desc, x, y in channels:
        d.ellipse((x - 18, 720 - 18, x + 18, 720 + 18), fill=BLUE)
        d.line((x, 720, x, y + (70 if y < 720 else -70)), fill=LINE, width=5)
        d.text((x, y), name, font=font(38, bold=True, en=True), fill=INK, anchor="mm")
        d.text((x, y + 58), desc, font=font(30), fill=MUTED, anchor="mm")
    save(img, 5)


def s6() -> None:
    img, d = new_slide()
    header(d, 6, "sva", "SVA 与 Context 注入", "视频流按受控频率处理，形成可审计的观察结果。")
    xs = [340, 850, 1360, 1870]
    labels = [("Video Track", "实时画面", BLUE), ("Processor", "抽帧 / 识别", CYAN), ("Observation", "结构化结果", GREEN), ("LLM / DSG", "上下文注入", INK)]
    y = 700
    for i, (title, desc, color) in enumerate(labels):
        panel(d, (xs[i], y - 115, xs[i] + 340, y + 115), fill=WHITE, outline=color)
        d.text((xs[i] + 170, y - 26), title, font=font(36, bold=True, en=i in [0, 1, 2]), fill=INK, anchor="mm")
        d.text((xs[i] + 170, y + 42), desc, font=font(28), fill=MUTED, anchor="mm")
        if i < len(labels) - 1:
            arrow(d, (xs[i] + 360, y), (xs[i + 1] - 28, y), fill=BLUE if i == 0 else LINE, width=6)
    d.text((1280, 1010), "处理结果可以进入提示词，也可以进入 DSG 作为证据", font=font(38, bold=True), fill=INK, anchor="mm")
    save(img, 6)


def s7() -> None:
    img, d = new_slide()
    header(d, 7, "ecp", "前台动作闭环", "语音动作要有回执，状态写入共享黑板。")
    top_y = 610
    bottom_y = 885
    xs = [360, 820, 1280, 1740]
    top = [("用户语音", BLUE), ("Brain 工具", INK), ("LiveKit RPC", CYAN), ("Unity 动作", GREEN)]
    for i, (label, color) in enumerate(top):
        panel(d, (xs[i] - 155, top_y - 70, xs[i] + 155, top_y + 70), fill=WHITE, outline=color)
        d.text((xs[i], top_y), label, font=font(32, bold=True, en=label in ["LiveKit RPC"]), fill=INK, anchor="mm")
        if i < len(top) - 1:
            arrow(d, (xs[i] + 175, top_y), (xs[i + 1] - 175, top_y), fill=LINE, width=6)

    bottom = [("ACK", 1740, BLUE), ("Blackboard", 1280, INK), ("后续回复", 820, GREEN)]
    for label, x, color in bottom:
        panel(d, (x - 155, bottom_y - 70, x + 155, bottom_y + 70), fill=WHITE, outline=color)
        d.text((x, bottom_y), label, font=font(32, bold=True, en=label in ["ACK", "Blackboard"]), fill=INK, anchor="mm")

    arrow(d, (1740, top_y + 82), (1740, bottom_y - 82), fill=BLUE, width=6)
    arrow(d, (1580, bottom_y), (1440, bottom_y), fill=LINE, width=6)
    arrow(d, (1120, bottom_y), (980, bottom_y), fill=LINE, width=6)
    d.text((1280, 1100), "执行结果进入状态面，后续语言反馈和系统状态保持一致。", font=font(40, bold=True), fill=INK, anchor="mm")
    save(img, 7)


def s8() -> None:
    img, d = new_slide()
    header(d, 8, "behavior", "行为分层", "本地反应、前台意图、后台任务分别处理。")
    bars = [
        ("Reflex", "本地低延迟动作", BLUE, 470),
        ("Intent", "前台语音 / UI / RPC", GREEN, 690),
        ("Task", "耗时外部执行", ORANGE, 910),
    ]
    for name, desc, color, y in bars:
        d.rounded_rectangle((420, y - 58, 2120, y + 58), radius=6, fill=WHITE, outline=color, width=4)
        d.rectangle((420, y - 58, 690, y + 58), fill=color)
        d.text((555, y), name, font=font(36, bold=True, en=True), fill=WHITE, anchor="mm")
        d.text((760, y), desc, font=font(38, bold=True), fill=INK, anchor="lm")
    d.text((1280, 1110), "该立即反应的留在本地，需要回执的进入 Intent，耗时任务交给后台。", font=font(34), fill=MUTED, anchor="mm")
    save(img, 8)


def s9() -> None:
    img, d = new_slide()
    header(d, 9, "task", "后台任务协作", "改日程任务用于说明 Task 的派发链路。")
    y = 720
    steps = ["日程草稿", "用户确认", "Scheduler", "Redis Stream", "nanobot Worker", "结果回流"]
    colors = [BLUE, BLUE, INK, CYAN, ORANGE, GREEN]
    xs = [230, 590, 950, 1350, 1760, 2170]
    for i, step in enumerate(steps):
        d.ellipse((xs[i] - 46, y - 46, xs[i] + 46, y + 46), fill=colors[i])
        d.text((xs[i], y + 104), step, font=font(30, bold=True, en=i in [2, 3]), fill=INK, anchor="mm")
        if i < len(steps) - 1:
            arrow(d, (xs[i] + 64, y), (xs[i + 1] - 64, y), fill=LINE, width=7)
    d.text((1280, 1030), "前台对话保留确认权，后台执行保留结果回流。", font=font(42, bold=True), fill=INK, anchor="mm")
    save(img, 9)


def s10() -> None:
    img, d = new_slide()
    header(d, 10, "memory", "工作记忆与长期记忆", "运行时信息进入 DSG，需要长期保存的内容归档到 Graphiti。")
    panel(d, (300, 510, 1120, 940), fill=WHITE, outline=BLUE)
    panel(d, (1440, 510, 2260, 940), fill=WHITE, outline=GREEN)
    d.text((710, 610), "DSG", font=font(66, bold=True, en=True), fill=INK, anchor="mm")
    d.text((710, 706), "运行时工作记忆", font=font(38, bold=True), fill=INK, anchor="mm")
    d.text((710, 790), "Observation / Ref / L1.5 / L2-B", font=font(30, en=True), fill=BLUE, anchor="mm")
    d.text((1850, 610), "Graphiti", font=font(66, bold=True, en=True), fill=INK, anchor="mm")
    d.text((1850, 706), "长期图记忆", font=font(38, bold=True), fill=INK, anchor="mm")
    d.text((1850, 790), "Episode / Entity / Fact", font=font(30, en=True), fill=GREEN, anchor="mm")
    arrow(d, (1130, 725), (1425, 725), fill=BLUE, width=8)
    d.text((1280, 660), "归档", font=font(30, bold=True), fill=INK, anchor="mm")
    arrow(d, (1425, 830), (1135, 830), fill=GREEN, width=8)
    d.text((1280, 892), "回灌", font=font(30, bold=True), fill=INK, anchor="mm")
    save(img, 10)


def s11() -> None:
    img, d = new_slide()
    header(d, 11, "trigger", "触发器协议", "事件发生后，系统按统一输出处理后续动作。")
    cx, cy = 1280, 720
    d.ellipse((cx - 160, cy - 160, cx + 160, cy + 160), fill=SOFT, outline=BLUE, width=6)
    d.text((cx, cy - 20), "Trigger", font=font(48, bold=True, en=True), fill=INK, anchor="mm")
    d.text((cx, cy + 40), "Kind → Outcome", font=font(28, en=True), fill=BLUE, anchor="mm")
    outs = [
        ("Observation", 250, 470, BLUE),
        ("Staged Ref", 700, 1040, CYAN),
        ("Archive", 1280, 1130, GREEN),
        ("Plan", 1860, 1040, ORANGE),
        ("Task", 2310, 470, ORANGE),
        ("Notify", 1280, 325, INK),
    ]
    for label, x, y, color in outs:
        arrow(d, (cx + int((x - cx) * 0.18), cy + int((y - cy) * 0.18)), (x - int((x - cx) * 0.08), y - int((y - cy) * 0.08)), fill=LINE, width=5)
        d.text((x, y), label, font=font(34, bold=True, en=True), fill=color, anchor="mm")
    save(img, 11)


def s12() -> None:
    img, d = new_slide()
    header(d, 12, "photo", "拍照数据流", "照片先成为证据入口，再进入识别、检索和归档。")
    steps = ["快门", "预览事件", "图片上传", "PhotoNode", "PHOTO Ref", "UUID 绑定"]
    xs = [280, 650, 1020, 1390, 1760, 2130]
    y = 710
    for i, step in enumerate(steps):
        d.ellipse((xs[i] - 30, y - 30, xs[i] + 30, y + 30), fill=BLUE if i < 3 else GREEN)
        d.line((xs[i], y + 30, xs[i], y + 145), fill=LINE, width=4)
        d.text((xs[i], y + 190), step, font=font(32, bold=True, en=step in ["PhotoNode", "PHOTO Ref", "UUID 绑定"]), fill=INK, anchor="mm")
        if i < len(steps) - 1:
            arrow(d, (xs[i] + 48, y), (xs[i + 1] - 48, y), fill=LINE, width=7)
    d.text((1280, 1010), "预览负责及时感知，完整图片负责后续证据。", font=font(42, bold=True), fill=INK, anchor="mm")
    save(img, 12)


def s13() -> None:
    img, d = new_slide()
    header(d, 13, "demo", "Demo 路线", "用两分钟展示交互、主动提醒和后台状态。")
    d.rounded_rectangle((360, 445, 2200, 920), radius=6, outline=LINE, width=4, fill=WHITE)
    d.text((1280, 570), "Demo Video", font=font(64, bold=True, en=True), fill=INK, anchor="mm")
    d.text((1280, 650), "2 min", font=font(40, en=True), fill=MUTED, anchor="mm")
    steps = [("前台交互", BLUE), ("主动提醒 / 邮件", CYAN), ("后台状态与日记", GREEN)]
    for i, (label, color) in enumerate(steps):
        x = 590 + i * 520
        d.line((x - 140, 1030, x + 140, 1030), fill=color, width=8)
        d.text((x, 1095), label, font=font(38, bold=True), fill=INK, anchor="mm")
        if i < 2:
            arrow(d, (x + 180, 1030), (x + 340, 1030), fill=LINE, width=5)
    save(img, 13)


def s14() -> None:
    img, d = new_slide()
    header(d, 14, "result", "完成情况", "把多源输入、状态闭环、记忆和后台任务串成原型链路。")
    items = [
        ("多源输入链路", "语音、视频、拍照、日程、笔记进入统一上下文", BLUE),
        ("前台状态闭环", "RPC 执行动作，ACK 回写 Blackboard", CYAN),
        ("记忆与任务协作", "DSG / Graphiti / Scheduler / nanobot 分工运行", GREEN),
    ]
    for i, (title, desc, color) in enumerate(items):
        y = 480 + i * 220
        d.rectangle((350, y, 370, y + 120), fill=color)
        d.text((420, y + 8), title, font=font(44, bold=True), fill=INK)
        d.text((420, y + 72), desc, font=font(32), fill=MUTED)
    d.text((1280, 1160), "答辩重点：架构设计、数据流和核心流程。", font=font(40, bold=True), fill=INK, anchor="mm")
    save(img, 14)


def s15() -> None:
    img, d = new_slide()
    header(d, 15, "next", "后续完善", "视觉稳定性、记忆治理和外部模块接入仍可继续加强。")
    words = [("视觉稳定性", BLUE), ("记忆治理", GREEN), ("外部模块接入", ORANGE)]
    for i, (word, color) in enumerate(words):
        x = 500 + i * 770
        d.text((x, 650), word, font=font(64, bold=True), fill=INK, anchor="mm")
        d.line((x - 150, 735, x + 150, 735), fill=color, width=10)
    d.text((1280, 1040), "谢谢各位老师", font=font(62, bold=True), fill=INK, anchor="mm")
    save(img, 15)


SLIDES = [
    ("项目题目", ["AR 生活助手与智能提醒系统", "从实时交互到场景记忆"], "cover"),
    ("项目目标", ["理解当前场景", "在合适时机协助用户", "形成可追踪数据流"], "goal"),
    ("场景输入", ["语音、视频、照片、日程、笔记", "统一为 Observation / Ref / Task"], "input map"),
    ("总体架构", ["Unity AR 前端", "LiveKit 实时通信", "Brain / DSG / Graphiti / Scheduler / nanobot"], "architecture"),
    ("实时音视频通道", ["Room", "Track", "DataChannel", "RPC"], "concept"),
    ("SVA 与 Context 注入", ["Video Track", "Processor", "Observation", "LLM / DSG"], "workflow"),
    ("前台动作闭环", ["语音 Intent", "LiveKit RPC", "Unity 动作", "ACK / Blackboard"], "workflow"),
    ("行为分层", ["Reflex", "Intent", "Task"], "layering"),
    ("后台任务协作", ["日程草稿", "用户确认", "Scheduler", "Redis Stream", "nanobot Worker"], "workflow"),
    ("工作记忆与长期记忆", ["DSG", "Graphiti", "Episode / Ref"], "memory"),
    ("触发器协议", ["TriggerKind", "TriggerOutcome", "Observation / Ref / Archive / Plan / Task / Notify"], "protocol"),
    ("拍照数据流", ["快门", "预览事件", "图片上传", "PhotoNode", "PHOTO Ref", "UUID"], "timeline"),
    ("Demo 路线", ["前台交互", "主动提醒 / 邮件", "后台状态与日记"], "demo"),
    ("完成情况", ["多源输入链路", "前台状态闭环", "记忆与任务协作"], "summary"),
    ("后续完善", ["视觉稳定性", "记忆治理", "外部模块接入"], "closing"),
]


SPEECH = {
    1: "各位老师好，我汇报的项目是 AR 生活助手与智能提醒系统。它面向真实 AR 场景，把用户当前的交互、场景信息、记忆和后台任务组织到一条清楚的数据流里。",
    2: "项目目标可以概括成三个词：感知、记忆、行动。系统需要理解用户当前看到什么、正在做什么，再结合日程和历史信息，在合适时机协助用户。",
    3: "场景输入包括实时音视频、后台任务、日程、Obsidian 笔记和后续 CV 扩展。它们进入系统后会先变成 Observation、Ref 或 Task，方便追踪来源和后续处理。",
    4: "总体架构分成五层：Unity AR 前端负责交互和展示，LiveKit 负责实时通信，Brain Agent 负责理解和工具调用，DSG 与 Graphiti 负责记忆，Scheduler 和 nanobot 负责后台任务。",
    5: "LiveKit 在这里承载 Room、音视频 Track、DataChannel 和 RPC。音视频用于感知，DataChannel 用于事件和状态，RPC 用于后端触发前端动作。",
    6: "SVA 在本项目中作为 Processor 思路使用。视频流可以按受控频率处理，得到结构化 Observation，再注入大模型上下文或 DSG 工作记忆。",
    7: "前台动作需要闭环。用户发出语音指令后，Brain 调用工具，通过 LiveKit RPC 下发给 Unity；Unity 执行后返回 ACK，后端把结果写入 Blackboard。",
    8: "行为调度分成 Reflex、Intent 和 Task。Reflex 处理低延迟动作，Intent 处理需要前台回执的用户意图，Task 处理耗时的外部执行。",
    9: "以改日程为例，系统先生成日程草稿并等待确认；确认后进入 Scheduler，通过 Redis Stream 派发给 nanobot Worker 或 gateway，完成后结果回流。",
    10: "DSG 是运行时工作记忆，保存当前场景里的 Observation 和 Ref。Graphiti 负责长期图记忆，适合归档 Episode、实体和事实，并在后续场景中回灌。",
    11: "触发器协议用于统一处理事件。触发器输出可以是观察、暂存引用、归档请求、计划、后台任务或前台通知，主动提醒和记忆回灌都可以接入这个机制。",
    12: "拍照流程说明多源 Ref 的价值。快门触发后先产生预览事件，完整图片再上传；系统创建 PhotoNode，暂存 PHOTO Ref，并用 UUID 绑定来源。",
    13: "Demo 部分建议控制在两分钟，展示前台交互、主动提醒或邮件，以及后台状态和 Obsidian 日记，让架构设计落到可见流程上。",
    14: "当前完成的重点是三条链路：多源输入进入统一上下文，前台动作形成状态闭环，记忆与后台任务可以协同运行。",
    15: "后续还可以加强视觉稳定性、长期记忆治理和更多外部模块接入。我的汇报到这里，谢谢各位老师。",
}


SOURCES = """# Sources

- LiveKit Rooms / Participants / Tracks: https://docs.livekit.io/intro/basics/rooms-participants-tracks
- LiveKit Data packets and RPC: https://docs.livekit.io/home/client/data/packets/
- Vision Agents by Stream: https://github.com/GetStream/Vision-Agents
- Google Calendar: https://workspace.google.com/products/calendar/
- Obsidian data storage: https://obsidian.md/help/data-storage
- Graphiti documentation: https://help.getzep.com/graphiti/getting-started/welcome
- Meta SAM 2: https://ai.meta.com/sam2/
- ConceptGraphs: https://concept-graphs.github.io/
- Local project research notes: docs/defense/workbench/round_02_research_notes.md
- Local flow audit: docs/defense/workbench/round_01_flow_example_audit.md
"""


def write_text_artifacts() -> None:
    lines = ["# PPT 大纲：简约答辩版", ""]
    for i, (title, points, role) in enumerate(SLIDES, 1):
        lines.append(f"## Slide {i}: {title}")
        lines.append(f"- Layout role: {role}")
        for p in points:
            lines.append(f"- {p}")
        lines.append("")
    (DECK_DIR / "outline.md").write_text("\n".join(lines), encoding="utf-8")

    speech_lines: list[str] = ["# 演讲备注", ""]
    for i, (title, _, _) in enumerate(SLIDES, 1):
        speech_lines.append(f"## Slide {i}: {title}")
        speech_lines.append("")
        speech_lines.append(SPEECH[i])
        speech_lines.append("")
    (DECK_DIR / "speech.md").write_text("\n".join(speech_lines), encoding="utf-8")

    spec = {
        "deck_name": DECK_NAME,
        "style": "white minimal defense deck; short Chinese titles; sparse diagrams; project UI screenshots excluded",
        "slides": [
            {"slide_number": i, "title": title, "key_points": points, "layout_role": role}
            for i, (title, points, role) in enumerate(SLIDES, 1)
        ],
    }
    (DECK_DIR / "deck_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    (DECK_DIR / "sources.md").write_text(SOURCES, encoding="utf-8")


def contact_sheet() -> None:
    thumbs = []
    for i in range(1, len(SLIDES) + 1):
        img = Image.open(ORIGIN_DIR / f"slide_{i:02d}.png").resize((512, 288), Image.Resampling.LANCZOS)
        thumbs.append(img)
    cols, rows = 3, math.ceil(len(thumbs) / 3)
    sheet = Image.new("RGB", (cols * 548 + 40, rows * 332 + 60), "#EEF2F7")
    d = ImageDraw.Draw(sheet)
    for idx, img in enumerate(thumbs):
        col, row = idx % cols, idx // cols
        x, y = 24 + col * 548, 24 + row * 332
        sheet.paste(img, (x, y))
        d.text((x, y + 296), f"Slide {idx + 1:02d}", font=font(18, en=True), fill=MUTED)
    sheet.save(DECK_DIR / "contact_sheet.png", quality=92)


def validate_text() -> None:
    banned = ["不是", "而是", "启动页", "startup", "AR 提醒助手"]
    files = [DECK_DIR / "outline.md", DECK_DIR / "speech.md", DECK_DIR / "deck_spec.json"]
    problems: list[str] = []
    for p in files:
        content = p.read_text(encoding="utf-8")
        for word in banned:
            if word in content:
                problems.append(f"{p.name}: {word}")
    if problems:
        raise SystemExit("Banned text found:\n" + "\n".join(problems))


def main() -> None:
    if DECK_DIR.exists():
        shutil.rmtree(DECK_DIR)
    ORIGIN_DIR.mkdir(parents=True, exist_ok=True)
    for fn in [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15]:
        fn()
    write_text_artifacts()
    validate_text()
    contact_sheet()


if __name__ == "__main__":
    main()
