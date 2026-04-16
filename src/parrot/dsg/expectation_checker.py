"""ExpectationChecker — compares expected vs observed objects in scene.

Produces SceneTriggers for:
  - MISSING: object expected but not seen
  - DISPLACED: object seen but at different position
  - NEW: object seen but not expected
"""

from __future__ import annotations

import logging
import math
import time

from parrot.dsg.interfaces import emit_trigger, get_expected_objects, update_last_seen
from parrot.dsg.types import ObjectInfo, SceneTrigger, TriggerType

logger = logging.getLogger(__name__)

DISPLACEMENT_THRESHOLD_M = 0.15


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


async def check_expectations(
    observed: list[ObjectInfo],
    zone: str = "",
) -> list[SceneTrigger]:
    """Compare observed objects against Graphiti expectations.

    Returns list of triggers for any differences found.
    """
    expected = await get_expected_objects(zone)
    expected_map = {e.object_id: e for e in expected if e.object_id}
    observed_map = {o.object_id: o for o in observed}

    triggers: list[SceneTrigger] = []
    now = time.time()

    for obj_id, exp in expected_map.items():
        if obj_id not in observed_map:
            triggers.append(SceneTrigger(
                trigger_type=TriggerType.MISSING,
                object_info=exp,
                description=f"'{exp.label}' expected but not seen",
                timestamp=now,
            ))

    for obj_id, obs in observed_map.items():
        if obj_id not in expected_map:
            triggers.append(SceneTrigger(
                trigger_type=TriggerType.NEW,
                object_info=obs,
                description=f"'{obs.label}' detected (not previously known)",
                timestamp=now,
            ))
        else:
            exp = expected_map[obj_id]
            if (
                exp.position != (0.0, 0.0, 0.0)
                and obs.position != (0.0, 0.0, 0.0)
                and _distance(exp.position, obs.position) > DISPLACEMENT_THRESHOLD_M
            ):
                triggers.append(SceneTrigger(
                    trigger_type=TriggerType.DISPLACED,
                    object_info=obs,
                    description=(
                        f"'{obs.label}' moved from "
                        f"{exp.position} to {obs.position}"
                    ),
                    timestamp=now,
                ))

    for trigger in triggers:
        await emit_trigger(trigger)

        if trigger.trigger_type == TriggerType.NEW:
            await update_last_seen(
                trigger.object_info.object_id,
                trigger.object_info.label,
                trigger.object_info.position,
                zone=trigger.object_info.zone,
                surface=trigger.object_info.surface,
            )

    if triggers:
        logger.info(
            "expectation_checker: %d triggers (zone=%s)", len(triggers), zone or "all"
        )
    return triggers
