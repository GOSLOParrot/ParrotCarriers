"""IntentEventBoundaryTrigger (EVENT_DRIVEN).

DSG-TRIGGER-V2 § 5.2 + DSG-INTENT-EVENT-V1.

Fires when a cognitive boundary signal arrives (tool call / nanobot
result / long idle / explicit). Calls
``IntentEventBoundaryHandler.open()`` to roll the IntentEvent forward,
which in turn closes the previous event (decay + fold strategies) and
tags the next batch of active nodes.

Outcome carries no upload-channel side effects — the handler does the
work directly. We only emit ``notify_gemini=False`` (subconscious
boundary; not user-facing).
"""

from __future__ import annotations

from typing import Any

from parrot.dsg.l2b.intent_event_boundary import (
    IntentEventReason,
    get_intent_event_handler,
)
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome


_EVENT_KIND_TO_REASON: dict[str, IntentEventReason] = {
    "tool_call_start": IntentEventReason.TOOL_CALL_BOUNDARY,
    "nanobot_result": IntentEventReason.NANOBOT_RESULT_RETURN,
    "long_idle": IntentEventReason.LONG_IDLE,
    "intent_explicit": IntentEventReason.EXPLICIT,
    "plan_phase_change": IntentEventReason.PLAN_PHASE_CHANGE,
}


class IntentEventBoundaryTrigger(BaseTrigger):
    name = "intent_event_boundary_trigger"
    kinds = [TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if not isinstance(event, dict):
            return None
        kind = event.get("kind", "")
        reason = _EVENT_KIND_TO_REASON.get(kind)
        if reason is None:
            return None

        handler = get_intent_event_handler()
        actor = str(event.get("actor", ""))
        related_plan_id = str(event.get("plan_id", ""))
        related_episode_id = str(event.get("episode_id", ""))
        node_uuids = tuple(event.get("node_uuids", ()) or ())

        state = handler.open(
            reason=reason,
            triggering_actor=actor,
            related_plan_id=related_plan_id,
            related_episode_id=related_episode_id,
            related_node_uuids=node_uuids,
        )

        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"intent_event {state.event_id} opened ({reason.value})",
            nodes_affected=list(state.member_node_uuids),
            notify_gemini=False,
        )


__all__ = ["IntentEventBoundaryTrigger"]
