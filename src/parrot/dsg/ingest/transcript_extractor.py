"""transcript_extractor — LiveKit Session events → TextSourceFilter.

Sprint 2 T7 adapter (Sprint 4 Phase 5+ Line B rename, 2026-05-04).

NOT an IngestFilter; it's the **bridge** between LiveKit's `AgentSession` event
stream and the text_source_filter + runner pipeline. Works with any LLM
pipeline mode that emits ``user_input_transcribed`` and
``conversation_item_added`` events:

    Line A — Gemini Live (google.realtime.RealtimeModel)
    Line B — STT-LLM-TTS pipeline (e.g. google.STT + google.LLM + google.TTS)

Both pipelines fire the same ``AgentSession`` events; the extractor is
SoT-agnostic.

Wiring (inside ``brain.agent._attach_transcript_listener_to_session``):

    session.on("user_input_transcribed")   user speech         → feed(text, "user")
    session.on("conversation_item_added")  assistant response  → feed(text, "assistant")

Anti-loop guard (sprint2_plan §9.N3):
    Injector's C3/C4 posts ``[状态] ...`` role=user messages into the chat
    context. The active LLM pipeline may echo those back as "transcribed user
    input" in some builds. We drop any text beginning with ``[状态]`` /
    ``[Gemini·`` / ``[Brain·`` / ``[MEMORY CONTEXT]`` / ``[SCENE CONTEXT]``
    before touching the filter so we never ingest our own nudges.

Source dispatch (ADR-L1.5-001 + Phase 4 entry §8 lock):
    Assistant utterances from any LLM helper map to
    ``ObservationSource.GEMINI_ORAL``. The enum value is preserved verbatim
    (Phase 4 source dispatch lock — see ``adr_l1_5_source_dispatch_extension_space_20260504.md``
    §1.1 + §4.1) even though Line B may not literally be "Gemini" Realtime.
    The semantic class is "any LLM-produced oral utterance"; the enum's
    string identity stays GEMINI_ORAL to keep 11 source-dispatch tests +
    L1.5 ingest contract intact.

Runner injection:
    The extractor calls into ``dsg.ingest.runner.commit_observation`` for
    every Observation produced. The runner is imported lazily inside the
    coroutine so ``agent.py`` can import this module at module load without
    forcing the runner's eager Graphiti / rustworkx cost.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

from parrot.dsg.ingest.base import IngestOutcome, ObservationSource
from parrot.dsg.ingest.text_source_filter import TextSourceFilter

logger = logging.getLogger(__name__)

Role = Literal["user", "assistant"]

_SKIP_PREFIXES = (
    "[状态]",
    "[Gemini·",
    "[Brain·",
    "[MEMORY CONTEXT]",
    "[SCENE CONTEXT]",
)


class TranscriptExtractor:
    """LiveKit-session → text_source_filter → ingest runner bridge.

    Pipeline-agnostic. Works equally for Line A (Gemini Live) and Line B
    (STT-LLM-TTS). The class name is intentionally generic; ``GeminiTranscriptExtractor``
    is preserved as an alias in this module + the legacy
    ``gemini_transcript_extractor.py`` shim for backward import compatibility.
    """

    def __init__(self) -> None:
        self._filter = TextSourceFilter()

    def feed_transcript(self, text: str, role: Role) -> None:
        """Entry point — safe to call from a sync LiveKit ``@session.on(...)``
        handler. Does its own filtering + dispatch on the event loop.
        """
        if not text:
            return
        stripped = text.strip()
        if not stripped:
            return
        if any(stripped.startswith(p) for p in _SKIP_PREFIXES):
            logger.debug("transcript_extractor: dropped own nudge: %s", stripped[:40])
            return

        source = (
            ObservationSource.USER_EXPLICIT if role == "user"
            else ObservationSource.GEMINI_ORAL
        )
        outcome = self._filter.process_text(
            stripped,
            source=source,
            meta={"role": role},
        )

        if not outcome.observations:
            logger.debug(
                "transcript_extractor: %s yielded no observations (%s)",
                role, outcome.reason or "no match",
            )
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug(
                "transcript_extractor: no running loop — dropping %d observations",
                len(outcome.observations),
            )
            return

        loop.create_task(self._commit(outcome))

    async def _commit(self, outcome: IngestOutcome) -> None:
        try:
            from parrot.dsg.ingest.runner import get_ingest_runner

            runner = get_ingest_runner()
            await runner.commit_outcome(outcome)
        except Exception:
            logger.exception("transcript_extractor: runner commit failed")


_instance: TranscriptExtractor | None = None


def get_transcript_extractor() -> TranscriptExtractor:
    global _instance
    if _instance is None:
        _instance = TranscriptExtractor()
    return _instance


# Backward-compatible aliases (Sprint 4 Phase 5+ Line B rename, 2026-05-04).
# Keep so any in-flight chat / external script that imported the old names
# from this module continues to work; the legacy
# ``gemini_transcript_extractor`` module also re-exports these aliases.
GeminiTranscriptExtractor = TranscriptExtractor
get_gemini_transcript_extractor = get_transcript_extractor


__all__ = [
    "GeminiTranscriptExtractor",
    "TranscriptExtractor",
    "get_gemini_transcript_extractor",
    "get_transcript_extractor",
]
