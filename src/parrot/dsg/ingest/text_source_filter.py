"""text_source_filter — Gemini oral + user messages → Observations.

Sprint 2 T6. Consumes free-form text from two upstreams:

    1. Gemini transcript (role=assistant speech)    → GEMINI_ORAL, TENTATIVE
    2. Gemini user transcript (role=user speech)    → USER_EXPLICIT, TENTATIVE
    3. Explicit user text (chat / Obsidian freeform) → USER_EXPLICIT, CONFIRMED

The filter extracts **noun phrases with optional locative prepositions**
using a deliberately small regex-based extractor — no spaCy dep in V1.
Precision over recall: we'd rather miss a phrase than fabricate one, because
a false positive writes a ghost SemanticNode to L2-B that `identify_object`
would then latch onto.

Sprint 2 confidence policy (plan §5.1):
    - GEMINI_ORAL    → TENTATIVE, confidence=0.4
    - USER_EXPLICIT  → CONFIRMED, confidence=0.85
    - USER_TAG_OBSIDIAN → CONFIRMED, confidence=1.0 (that filter is separate)

Time-window "same label twice in 30s → promote to CONFIRMED" is runner-side
state, not filter-side; filters stay pure. Runner receives these Observations
and consults its own counter.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from parrot.dsg.ingest.base import (
    IngestFilter,
    IngestOutcome,
    Observation,
    ObservationSource,
)
from parrot.dsg.l1_5_protocol import SensorFrame
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

logger = logging.getLogger(__name__)

# Chinese + English noun phrase extractor. Matches sequences like:
#   - "一个 红色的 杯子"  "the red cup"  "桌子上的 笔"
# Keep it tiny on purpose — over-engineering regex produces noisier results
# than a small curated one.
_CN_NOUN_PHRASE_RE = re.compile(
    r"(?:[一两三四五六七八九十]+\s*(?:个|只|张|把|支|杯|瓶|本)\s*)?"
    r"(?:(?:红|黄|蓝|绿|黑|白|灰|紫|粉|橙)色\s*的\s*)?"
    r"([\u4e00-\u9fff]{1,6}(?:[\u4e00-\u9fff]{1,4})?)"
)

_LOCATIVE_PATTERNS = [
    re.compile(r"(在|靠近|旁边|上面|下面|里面|后面|前面)\s*([\u4e00-\u9fff]{1,8})"),
    re.compile(r"(on|near|inside|behind|in front of|next to)\s+(?:the\s+)?([a-zA-Z]{2,20})", re.IGNORECASE),
]

_MIN_LABEL_LEN = 2
_MAX_LABEL_LEN = 20

# Pronouns / meta words we refuse to treat as labels — they would create
# garbage nodes like "这" / "那" / "东西".
_LABEL_BLOCKLIST = frozenset(
    {
        "这", "那", "它", "他", "她", "你", "我", "东西", "什么", "一下",
        "现在", "一会儿", "这里", "那里", "this", "that", "thing", "stuff",
    }
)


class TextSourceFilter(IngestFilter):
    """Extracts object-like noun phrases from speech/chat text."""

    name = "text_source_filter"

    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        # Not a frame filter.
        return IngestOutcome(filter_name=self.name)

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        if not text or not text.strip():
            return IngestOutcome(filter_name=self.name)

        cleaned = text.strip()
        labels = self._extract_labels(cleaned)
        if not labels:
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="no_extractable_np"
            )

        confirmation, confidence = self._score(source)

        observations: list[Observation] = []
        for label in labels:
            obs = Observation(
                source=source,
                provenance_stream_id=provenance_stream_id,
                label=label,
                kind=NodeKind.OBJECT,
                description=cleaned[:180],
                confidence=confidence,
                confirmation=confirmation,
                meta={**(meta or {}), "raw_text": cleaned[:400]},
            )
            observations.append(obs)

        return IngestOutcome(
            filter_name=self.name,
            accepted=len(observations),
            observations=tuple(observations),
        )

    def _extract_labels(self, text: str) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()

        for m in _CN_NOUN_PHRASE_RE.finditer(text):
            candidate = m.group(1).strip()
            if self._label_ok(candidate) and candidate not in seen:
                found.append(candidate)
                seen.add(candidate)

        for pattern in _LOCATIVE_PATTERNS:
            for m in pattern.finditer(text):
                candidate = m.group(2).strip()
                if self._label_ok(candidate) and candidate not in seen:
                    found.append(candidate)
                    seen.add(candidate)

        return found[:8]

    @staticmethod
    def _label_ok(label: str) -> bool:
        if not label:
            return False
        if label in _LABEL_BLOCKLIST:
            return False
        n = len(label)
        return _MIN_LABEL_LEN <= n <= _MAX_LABEL_LEN

    @staticmethod
    def _score(source: ObservationSource) -> tuple[ConfirmationStatus, float]:
        if source == ObservationSource.USER_EXPLICIT:
            return ConfirmationStatus.CONFIRMED, 0.85
        if source == ObservationSource.GEMINI_ORAL:
            return ConfirmationStatus.TENTATIVE, 0.4
        return ConfirmationStatus.TENTATIVE, 0.3


__all__ = ["TextSourceFilter"]
