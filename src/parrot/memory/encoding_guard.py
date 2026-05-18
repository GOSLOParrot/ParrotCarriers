"""Text encoding sanity checks for Graphiti episode writes.

Graphiti should preserve raw source text. That makes it important to reject
obviously corrupted text before it becomes provenance data.
"""

from __future__ import annotations

import re
from typing import Any

_C1_CONTROL_RE = re.compile(r"[\u0080-\u009f]")

_LATIN1_UTF8_MARKERS = (
    "Ã",
    "Â",
    "â€",
    "â€™",
    "â€œ",
    "â€\x9d",
    "æ",
    "è",
    "ç",
    "å",
)

_GBK_UTF8_MARKERS = (
    "鐢ㄦ",
    "绗",
    "銆",
    "锛",
    "涓€",
    "鎴",
    "鍙",
    "榧",
    "鑱",
    "鏉",
    "濡傛",
)


def detect_text_mojibake(text: str, *, sample_size: int = 160) -> dict[str, Any]:
    """Return a serializable report for likely mojibake.

    The detector is intentionally conservative. C1 control characters are a
    strong signal for UTF-8 decoded as latin-1/Windows-1252. The GBK markers are
    treated as suspicious only when multiple tokens appear, because any one CJK
    character can be legitimate in normal Chinese prose.
    """

    value = text or ""
    signals: list[str] = []
    if "\ufffd" in value:
        signals.append("replacement_character")

    c1_count = len(_C1_CONTROL_RE.findall(value))
    if c1_count:
        signals.append(f"c1_control_chars:{c1_count}")

    latin_hits = [token for token in _LATIN1_UTF8_MARKERS if token and token in value]
    if c1_count and latin_hits:
        signals.append("latin1_utf8_mojibake:" + ",".join(latin_hits[:6]))

    gbk_hits = [token for token in _GBK_UTF8_MARKERS if token in value]
    if len(gbk_hits) >= 2:
        signals.append("gbk_utf8_mojibake:" + ",".join(gbk_hits[:6]))

    return {
        "suspicious": bool(signals),
        "signals": signals,
        "sample": value[:sample_size],
    }


def text_has_mojibake(text: str) -> bool:
    """Return True when ``text`` looks corrupted enough to block writes."""

    return bool(detect_text_mojibake(text).get("suspicious"))


__all__ = ["detect_text_mojibake", "text_has_mojibake"]
