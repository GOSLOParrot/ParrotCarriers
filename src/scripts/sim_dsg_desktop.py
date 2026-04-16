"""Simulate L1 vision pipeline output for Desktop Scene testing.

This script simulates what L1 would *output* (detected objects, positions),
NOT how L1 internally works. The simulated detections flow through the real
DSG interface layer → Graphiti preload → update_last_seen → triggers.

Usage:
  python src/scripts/sim_dsg_desktop.py                  # run full scenario
  python src/scripts/sim_dsg_desktop.py --scenario new   # only NEW events
  python src/scripts/sim_dsg_desktop.py --obsidian ~/vault/goslo/objects  # load from Obsidian

Scenarios:
  full     — objects appear, some disappear, one moves (default)
  new      — only new object detections
  missing  — objects disappear from scene
  displaced — objects move to new positions
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import time

from parrot.dsg.interfaces import (
    emit_trigger,
    preload_object_semantics,
    publish_scene_update,
    update_last_seen,
)
from parrot.dsg.types import L1DetectionResult, ObjectInfo, SceneTrigger, TriggerType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger("sim_dsg")

DESKTOP_OBJECTS = [
    ObjectInfo(
        object_id="obj-001", label="蓝色马克杯", surface="桌面", zone="工作区",
        position=(0.3, 0.75, -0.2),
    ),
    ObjectInfo(
        object_id="obj-002", label="MacBook Pro", surface="桌面", zone="工作区",
        position=(0.0, 0.76, 0.0),
    ),
    ObjectInfo(
        object_id="obj-003", label="iPhone", surface="桌面", zone="工作区",
        position=(-0.25, 0.75, 0.1),
    ),
    ObjectInfo(
        object_id="obj-004", label="键盘", surface="桌面", zone="工作区",
        position=(0.0, 0.76, -0.15),
    ),
    ObjectInfo(
        object_id="obj-005", label="耳机", surface="桌面", zone="工作区",
        position=(0.4, 0.75, 0.05),
    ),
]


async def sim_new_objects(objects: list[ObjectInfo]) -> None:
    """Simulate objects appearing in scene → preload + update + trigger."""
    logger.info("=== Simulating %d objects appearing ===", len(objects))
    for obj in objects:
        known = await preload_object_semantics(obj.object_id, obj.label)
        if known:
            logger.info("  %s: known (%d facts)", obj.label, len(known.get("known_facts", [])))
        else:
            logger.info("  %s: NEW (unknown object)", obj.label)

        await update_last_seen(
            obj.object_id, obj.label, obj.position,
            zone=obj.zone, surface=obj.surface,
        )

        await emit_trigger(SceneTrigger(
            trigger_type=TriggerType.NEW,
            object_info=obj,
            description=f"'{obj.label}' detected on {obj.surface}",
            timestamp=time.time(),
        ))

        await asyncio.sleep(0.5)


async def sim_missing_objects(objects: list[ObjectInfo]) -> None:
    """Simulate objects disappearing from scene."""
    logger.info("=== Simulating %d objects disappearing ===", len(objects))
    for obj in objects:
        await emit_trigger(SceneTrigger(
            trigger_type=TriggerType.MISSING,
            object_info=obj,
            description=f"'{obj.label}' no longer visible on {obj.surface}",
            timestamp=time.time(),
        ))
        await asyncio.sleep(0.5)


async def sim_displaced_objects(objects: list[ObjectInfo], offsets: list[tuple]) -> None:
    """Simulate objects moving to new positions."""
    logger.info("=== Simulating %d objects displaced ===", len(objects))
    for obj, offset in zip(objects, offsets):
        new_pos = (
            obj.position[0] + offset[0],
            obj.position[1] + offset[1],
            obj.position[2] + offset[2],
        )
        moved_obj = ObjectInfo(
            object_id=obj.object_id,
            label=obj.label,
            position=new_pos,
            surface=obj.surface,
            zone=obj.zone,
        )
        await update_last_seen(
            obj.object_id, obj.label, new_pos,
            zone=obj.zone, surface=obj.surface,
        )
        await emit_trigger(SceneTrigger(
            trigger_type=TriggerType.DISPLACED,
            object_info=moved_obj,
            description=f"'{obj.label}' moved from {obj.position} to {new_pos}",
            timestamp=time.time(),
        ))
        await asyncio.sleep(0.5)


async def run_full_scenario() -> None:
    """Full desktop scenario: objects appear, one disappears, one moves."""
    await sim_new_objects(DESKTOP_OBJECTS)
    await asyncio.sleep(2.0)

    scene = "Desktop scene: " + ", ".join(o.label for o in DESKTOP_OBJECTS)
    await publish_scene_update(scene)

    await sim_missing_objects([DESKTOP_OBJECTS[4]])
    await asyncio.sleep(1.0)

    await sim_displaced_objects(
        [DESKTOP_OBJECTS[0]],
        [(0.15, 0.0, 0.1)],
    )

    remaining = [o for o in DESKTOP_OBJECTS if o.object_id != "obj-005"]
    scene = "Desktop scene: " + ", ".join(o.label for o in remaining) + " (耳机 missing)"
    await publish_scene_update(scene)
    logger.info("=== Full scenario complete ===")


async def main():
    parser = argparse.ArgumentParser(description="Simulate L1 output for Desktop Scene")
    parser.add_argument(
        "--scenario", choices=["full", "new", "missing", "displaced"],
        default="full",
    )
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if args.scenario == "full":
        await run_full_scenario()
    elif args.scenario == "new":
        await sim_new_objects(DESKTOP_OBJECTS)
    elif args.scenario == "missing":
        await sim_missing_objects(DESKTOP_OBJECTS[:2])
    elif args.scenario == "displaced":
        await sim_displaced_objects(DESKTOP_OBJECTS[:2], [(0.1, 0, 0), (-0.1, 0, 0.1)])


if __name__ == "__main__":
    asyncio.run(main())
