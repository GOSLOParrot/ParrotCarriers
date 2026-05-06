"""SceneSwitchTrigger (ON_DEMAND).

DSG-TRIGGER-V2 § 5.1 + DSG-SCENE-V1 § 3.

Fires when ``set_scene`` Brain tool is invoked. Output:
    bucket_ops:
        FREEZE OBSIDIAN_SETTING_DAILY (preserved across SceneType)
        FREEZE OBSIDIAN_SETTING_ROLEPLAY (preserved if active)
        CLEAR  GOOGLE_CALENDAR (fresh on switch)
        CLEAR  AUTONOMOUS_CURIOSITY (fresh on switch)
    archive_request:
        SERIALIZE_NOW(SCENE_SNAPSHOT, scene_id=old)
    notify_gemini:
        "切换到 {new_scene_type} 场景了"
"""

from __future__ import annotations

from typing import Any

from parrot.dsg.archive import (
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
)
from parrot.dsg.l1_5.buckets import BucketKind, BucketOp, BucketOpKind
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome


class SceneSwitchTrigger(BaseTrigger):
    name = "scene_switch_trigger"
    kinds = [TriggerKind.ON_DEMAND]
    interval_seconds = 0

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if not isinstance(event, dict):
            return None
        if event.get("kind") != "scene_switch":
            return None

        old_scene = str(event.get("old_scene_type", ""))
        new_scene = str(event.get("new_scene_type", ""))

        bucket_ops = (
            BucketOp(op=BucketOpKind.FREEZE, kind=BucketKind.OBSIDIAN_SETTING_DAILY),
            BucketOp(op=BucketOpKind.FREEZE, kind=BucketKind.OBSIDIAN_SETTING_ROLEPLAY),
            BucketOp(op=BucketOpKind.CLEAR, kind=BucketKind.GOOGLE_CALENDAR),
            BucketOp(op=BucketOpKind.CLEAR, kind=BucketKind.AUTONOMOUS_CURIOSITY),
        )
        archive_req = ArchiveRequest(
            kind=ArchiveRequestKind.SERIALIZE_NOW,
            target=ArchiveTarget.SCENE_SNAPSHOT,
            target_id=old_scene or "previous",
        )
        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"scene switched {old_scene} → {new_scene}",
            bucket_ops=bucket_ops,
            archive_request=archive_req,
            notify_gemini=True,
            notification_text=f"切换到 {new_scene or 'unknown'} 场景了",
        )


__all__ = ["SceneSwitchTrigger"]
