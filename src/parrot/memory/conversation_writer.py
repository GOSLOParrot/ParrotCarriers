"""Auto-archive conversation turns to Graphiti.

Two integration points:
  1. Brain Agent (GOSLO Live): attach_conversation_writer(session) hooks into
     AgentSession events to capture user+assistant turns.
  2. Nanobot (GOSLO Chat / Maid): write_nanobot_turn() called from channel hooks.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque

logger = logging.getLogger(__name__)

_BATCH_INTERVAL_S = 30.0
_MAX_BATCH_SIZE = 10


class ConversationWriter:
    """Batches conversation turns and writes them to Graphiti periodically."""

    def __init__(self, group_id: str, source: str):
        self._group_id = group_id
        self._source = source
        self._buffer: deque[str] = deque(maxlen=100)
        self._task: asyncio.Task | None = None

    async def add_turn(self, role: str, text: str) -> None:
        if not text or not text.strip():
            return
        self._buffer.append(f"{role}: {text}")

    async def flush(self) -> int:
        """Write buffered turns to Graphiti. Returns number of turns written."""
        if not self._buffer:
            return 0

        batch = []
        while self._buffer and len(batch) < _MAX_BATCH_SIZE:
            batch.append(self._buffer.popleft())

        if not batch:
            return 0

        text = "\n".join(batch)
        try:
            from graphiti_core.graphiti_types import EpisodeType

            from parrot.memory.graphiti_client import get_graphiti

            g = await get_graphiti()
            await g.add_episode(
                text=text,
                episode_type=EpisodeType.text,
                group_id=self._group_id,
                source=self._source,
            )
            logger.info(
                "conversation_writer: archived %d turns to %s",
                len(batch), self._group_id,
            )
            return len(batch)
        except Exception:
            logger.exception("conversation_writer: failed to archive")
            for turn in reversed(batch):
                self._buffer.appendleft(turn)
            return 0

    async def _periodic_flush(self) -> None:
        while True:
            await asyncio.sleep(_BATCH_INTERVAL_S)
            try:
                await self.flush()
            except Exception:
                logger.exception("conversation_writer: periodic flush error")

    def start_background(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._periodic_flush())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.flush()


_brain_writer: ConversationWriter | None = None


def attach_conversation_writer(session) -> ConversationWriter:
    """Hook into an AgentSession to auto-archive GOSLO Live conversations.

    Call this in brain_entrypoint after session.start().
    """
    from parrot.memory.graphiti_client import PARTITIONS

    global _brain_writer
    writer = ConversationWriter(
        group_id=PARTITIONS.GOSLO,
        source="brain_live",
    )
    _brain_writer = writer

    from livekit.agents.voice.events import (
        ConversationItemAddedEvent,
        UserInputTranscribedEvent,
    )

    @session.on("user_input_transcribed")
    def _on_user(ev: UserInputTranscribedEvent) -> None:
        if ev.is_final and ev.transcript:
            asyncio.create_task(writer.add_turn("user", ev.transcript))

    @session.on("conversation_item_added")
    def _on_assistant(ev: ConversationItemAddedEvent) -> None:
        from livekit.agents.llm import ChatMessage

        item = ev.item
        if isinstance(item, ChatMessage) and item.role == "assistant":
            text = item.text_content
            if text:
                asyncio.create_task(writer.add_turn("assistant", text))

    writer.start_background()
    logger.info("conversation_writer: attached to Brain AgentSession")
    return writer


async def write_nanobot_turn(
    role: str, text: str, group_id: str, source: str = "nanobot",
) -> None:
    """Write a single nanobot conversation turn to Graphiti immediately.

    Lighter-weight than the batching writer — nanobot conversations are
    lower-frequency than real-time voice.
    """
    if not text or not text.strip():
        return
    try:
        from graphiti_core.graphiti_types import EpisodeType

        from parrot.memory.graphiti_client import get_graphiti

        g = await get_graphiti()
        await g.add_episode(
            text=f"{role}: {text}",
            episode_type=EpisodeType.text,
            group_id=group_id,
            source=source,
        )
    except Exception:
        logger.exception("write_nanobot_turn: failed for %s/%s", group_id, source)
