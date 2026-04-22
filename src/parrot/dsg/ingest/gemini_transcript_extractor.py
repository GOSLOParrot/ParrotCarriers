"""gemini_transcript_extractor — LiveKit Session events → TextSourceFilter.

Sprint 2 T7 adapter. NOT an IngestFilter; it's the **bridge** between
LiveKit's `AgentSession` event stream and the text_source_filter + runner
pipeline.

Wiring (inside `brain.agent._attach_gemini_transcript_to_terminal`):

    session.on("user_input_transcribed")   user speech         → feed(text, "user")
    session.on("conversation_item_added")  assistant response  → feed(text, "assistant")

Anti-loop guard (sprint2_plan §9.N3):
    Injector's C3/C4 posts `[状态] ...` role=user messages into the chat
    context. Gemini may echo those back as "transcribed user input" in some
    builds. We drop any text beginning with `[状态]` or `[Gemini·` before
    touching the filter so we never ingest our own nudges.

Runner injection:
    The extractor calls into `dsg.ingest.runner.commit_observation` for
    every Observation produced. The runner is imported lazily inside the
    coroutine so `agent.py` can import this module at module load without
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

_SKIP_PREFIXES = ("[状态]", "[Gemini·", "[MEMORY CONTEXT]", "[SCENE CONTEXT]")


class GeminiTranscriptExtractor:
    """LiveKit-session → text_source_filter → ingest runner bridge."""

    def __init__(self) -> None:
        self._filter = TextSourceFilter()

    def feed_transcript(self, text: str, role: Role) -> None:
        """Entry point — safe to call from a sync LiveKit `@session.on(...)`
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


_instance: GeminiTranscriptExtractor | None = None


def get_gemini_transcript_extractor() -> GeminiTranscriptExtractor:
    global _instance
    if _instance is None:
        _instance = GeminiTranscriptExtractor()
    return _instance


__all__ = ["GeminiTranscriptExtractor", "get_gemini_transcript_extractor"]
