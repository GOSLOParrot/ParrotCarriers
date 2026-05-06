"""GosloCuriosityTrigger (EVENT_DRIVEN).

DSG-TRIGGER-V2 § 5.4.

Fires when ``dsg/attention/threshold.py`` (or upstream Brain logic)
flags an unknown salient object. Output:
    commit_observations: GOSLO_AUTONOMOUS Observation × 1
    staged_refs:         stage(PHOTO) of the current frame
    plan_request:        optional PlanProposal if research is non-trivial
    notify_gemini:       short hint
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from parrot.brain.intent_workspace import (
    PayloadSource,
    StagedRefKind,
    StagedRefMetadata,
    StagedRefRequest,
)
from parrot.brain.plan import PlanProposal, PlanStepProposal
from parrot.dsg.ingest.base import Observation, ObservationSource
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome


class GosloCuriosityTrigger(BaseTrigger):
    name = "goslo_curiosity_trigger"
    kinds = [TriggerKind.EVENT_DRIVEN]
    interval_seconds = 0

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if not isinstance(event, dict):
            return None
        if event.get("kind") != "curiosity":
            return None

        label = str(event.get("label", "")).strip()
        if not label:
            return None
        photo_path = event.get("photo_path", "")
        confidence = float(event.get("confidence", 0.5))
        related_node_uuid = str(event.get("related_node_uuid", ""))

        observations = (
            Observation(
                source=ObservationSource.GOSLO_AUTONOMOUS,
                label=label,
                kind=NodeKind.OBJECT,
                description=str(event.get("description", "")),
                confidence=confidence,
                confirmation=ConfirmationStatus.TENTATIVE,
                provenance_stream_id=str(event.get("provenance_stream_id", "")),
                meta={
                    "triggered_by": "goslo_curiosity",
                    "discovered_at": time.time(),
                },
            ),
        )

        staged_refs: tuple[StagedRefRequest, ...] = ()
        if photo_path:
            staged_refs = (
                StagedRefRequest(
                    kind=StagedRefKind.PHOTO,
                    payload_source=PayloadSource.DISK_PATH,
                    payload_value=Path(photo_path),
                    metadata=StagedRefMetadata(
                        origin=f"trigger:{self.name}",
                        kind=StagedRefKind.PHOTO,
                        payload_source=PayloadSource.DISK_PATH,
                        related_node_uuid=related_node_uuid,
                        related_intent_event_id=str(event.get("intent_event_id", "")),
                        auto_evict_on_intent_close=True,
                    ),
                ),
            )

        # Optionally propose a Plan if the curiosity is "non-trivial"
        plan_request: PlanProposal | None = None
        if event.get("propose_plan", False):
            plan_request = PlanProposal(
                proposed_by=self.name,
                title=f"investigate {label}",
                rationale=f"GOSLO autonomous curiosity about {label}",
                suggested_steps=(
                    PlanStepProposal(
                        step_id="curiosity_step_1",
                        title=f"identify_object({label})",
                        expected_tool="identify_object",
                        inputs={"label": label, "photo_path": photo_path},
                    ),
                ),
                blocks_conversation=False,
            )

        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"curiosity: {label}",
            commit_observations=observations,
            staged_refs=staged_refs,
            plan_request=plan_request,
            notify_gemini=False,  # subconscious — let Context Injector decide
        )


__all__ = ["GosloCuriosityTrigger"]
