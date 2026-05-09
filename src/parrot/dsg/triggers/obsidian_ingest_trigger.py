"""Obsidian note ingest trigger.

Runtime Obsidian bridge scripts publish ``obsidian_note`` events to
CH_DSG_EVENTS. This trigger converts those note events through UserTagFilter
and returns Observations to the normal TriggerOutcome commit path.

Write boundaries:
    * Filter: pure payload -> Observation conversion.
    * L1.5 Pool: bucket/ref routing, including profile=ref lightweight bind.
    * L2-B: only written by IngestRunner through L1.5 Pool.
"""

from __future__ import annotations

from typing import Any

from parrot.dsg.ingest.user_tag_filter import UserTagFilter
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

_EVENT_TYPES = frozenset({
    "obsidian_note",
    "obsidian.note",
    "obsidian.sync.note",
})


class ObsidianIngestTrigger(BaseTrigger):
    """Bridge Obsidian note events into L1.5 without direct graph writes."""

    name = "obsidian_ingest"
    kinds = [TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0

    def __init__(self, graph):
        super().__init__(graph)
        self._filter = UserTagFilter()

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if event.get("type") not in _EVENT_TYPES:
            return None

        payload = event.get("payload")
        if not isinstance(payload, dict):
            payload = event

        outcome = self._filter.process_tag(
            payload,
            provenance_stream_id=str(event.get("provenance_stream_id", "")),
        )
        if outcome.rejected:
            return TriggerOutcome(
                trigger_name=self.name,
                summary=f"Rejected Obsidian note: {outcome.reason}",
            )
        if not outcome.observations:
            return None

        profile = (outcome.observations[0].meta or {}).get("profile", "daily")
        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"Accepted Obsidian {profile} note",
            commit_observations=outcome.observations,
        )


__all__ = ["ObsidianIngestTrigger"]
