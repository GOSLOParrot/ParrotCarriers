"""dsg/mode_controller — gates Ingest filter dispatch by DsgMode.

Sprint 2 T9. Given the current `session/dsg_mode` BB value, exposes an
`is_enabled(filter_name)` predicate that `GeminiTranscriptExtractor`,
`ssot_enrichment_trigger`, and any future A10 dispatcher consult before
calling a filter. The policy table lives here (sprint2_plan §5.4) so a
single file answers "which filters run in DSG_FULL".

Not a py-trees node. Not a BB writer. Pure read-side. Starts a 1 Hz BB
poll to cache the current DsgMode so the extractor's tight loop doesn't
hit py-trees lookups on every spoken word.

Lifecycle:
    attach_mode_controller()    — once on agent.py startup, after Supervisor
    is_enabled(filter_name)     — hot path, called per Observation source
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.tiers import DsgMode

if TYPE_CHECKING:
    import py_trees

logger = logging.getLogger(__name__)

# Filter enablement per DsgMode (sprint2_plan §5.4). Filter names match the
# `IngestFilter.name` class attribute on each concrete filter.
FILTER_SETS: dict[DsgMode, frozenset[str]] = {
    DsgMode.DSG_TEXT_ONLY: frozenset(
        {"tool_result_filter", "user_tag_filter"}
    ),
    DsgMode.DSG_GEMINI_VISION: frozenset(
        {"text_source_filter", "tool_result_filter", "user_tag_filter"}
    ),
    DsgMode.DSG_FULL: frozenset(
        {
            "text_source_filter",
            "tool_result_filter",
            "user_tag_filter",
            "cv_track_filter",
        }
    ),
    DsgMode.DSG_SENTINEL_AUX: frozenset(
        {"text_source_filter", "tool_result_filter", "user_tag_filter"}
    ),
}

# Fallback when BB has no value yet (e.g. agent booting, before Supervisor
# has written anything). We default to the same set as DSG_GEMINI_VISION —
# safer to let text_source run and discard than to miss the first minute.
_FALLBACK_SET = FILTER_SETS[DsgMode.DSG_GEMINI_VISION]

_POLL_INTERVAL_S = 1.0


class ModeController:
    """Caches the active DsgMode filter-set for hot-path lookup."""

    def __init__(self) -> None:
        self._bb: "py_trees.blackboard.Client" = open_bb_client(
            name="mode_controller", writer=None
        )
        self._current_set: frozenset[str] = _FALLBACK_SET
        self._current_mode: DsgMode | None = None
        self._task: asyncio.Task | None = None

    def is_enabled(self, filter_name: str) -> bool:
        return filter_name in self._current_set

    def current_mode(self) -> DsgMode | None:
        return self._current_mode

    def _refresh(self) -> None:
        try:
            mode = self._bb.get("session/dsg_mode")
        except KeyError:
            mode = None

        if not isinstance(mode, DsgMode):
            self._current_set = _FALLBACK_SET
            return

        new_set = FILTER_SETS.get(mode, _FALLBACK_SET)
        if mode != self._current_mode:
            logger.info(
                "mode_controller: dsg_mode → %s (filters=%s)",
                mode.value, sorted(new_set),
            )
            self._current_mode = mode
            self._current_set = new_set

    async def _poll_loop(self) -> None:
        while True:
            try:
                self._refresh()
            except Exception:
                logger.debug("mode_controller: poll error", exc_info=True)
            await asyncio.sleep(_POLL_INTERVAL_S)

    def start_background(self) -> None:
        if self._task and not self._task.done():
            return
        # Prime the cache so the first is_enabled call doesn't race the loop.
        self._refresh()
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


_instance: ModeController | None = None


def attach_mode_controller() -> ModeController:
    """Create the ModeController singleton and start its BB poll loop."""
    global _instance
    if _instance is None:
        _instance = ModeController()
    _instance.start_background()
    logger.info("mode_controller: attached (poll %.1fs)", _POLL_INTERVAL_S)
    return _instance


def get_mode_controller() -> ModeController | None:
    return _instance


__all__ = [
    "FILTER_SETS",
    "ModeController",
    "attach_mode_controller",
    "get_mode_controller",
]
