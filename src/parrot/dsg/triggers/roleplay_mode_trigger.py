"""RoleplayModeTrigger (ON_DEMAND).

DSG-TRIGGER-V2 § 5.3.

Open roleplay → register OBSIDIAN_SETTING_ROLEPLAY + import items.
Close roleplay → clear ROLEPLAY_TEMP + unregister OBSIDIAN_SETTING_ROLEPLAY +
serialize a snapshot for留档.
"""

from __future__ import annotations

from typing import Any

from parrot.dsg.archive import (
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
)
from parrot.dsg.l1_5.buckets import (
    BucketKind,
    BucketOp,
    BucketOpKind,
    BucketSpec,
)
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome


class RoleplayModeTrigger(BaseTrigger):
    name = "roleplay_mode_trigger"
    kinds = [TriggerKind.ON_DEMAND]
    interval_seconds = 0

    async def on_startup(self) -> TriggerOutcome | None:
        return None

    async def on_tick(self) -> TriggerOutcome | None:
        return None

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if not isinstance(event, dict):
            return None
        if event.get("kind") != "roleplay_mode":
            return None
        action = event.get("action", "open")  # "open" | "close"

        if action == "open":
            items = tuple(event.get("items", ()) or ())
            spec = BucketSpec(
                kind=BucketKind.ROLEPLAY_TEMP,
                is_authority=True,
                preserved_across_scene_switch=True,
            )
            bucket_ops = (
                BucketOp(
                    op=BucketOpKind.REGISTER,
                    kind=BucketKind.ROLEPLAY_TEMP,
                    payload={"spec": spec},
                ),
            )
            if items:
                bucket_ops = bucket_ops + (
                    BucketOp(
                        op=BucketOpKind.IMPORT,
                        kind=BucketKind.ROLEPLAY_TEMP,
                        payload={"items": items},
                    ),
                )
            return TriggerOutcome(
                trigger_name=self.name,
                summary="roleplay mode opened",
                bucket_ops=bucket_ops,
                notify_gemini=True,
                notification_text="进入 Roleplay 模式",
            )

        # close
        archive_req = ArchiveRequest(
            kind=ArchiveRequestKind.SERIALIZE_NOW,
            target=ArchiveTarget.SCENE_SNAPSHOT,
            target_id="roleplay_temp",
        )
        bucket_ops = (
            BucketOp(op=BucketOpKind.CLEAR, kind=BucketKind.ROLEPLAY_TEMP),
            BucketOp(op=BucketOpKind.UNREGISTER, kind=BucketKind.ROLEPLAY_TEMP),
        )
        return TriggerOutcome(
            trigger_name=self.name,
            summary="roleplay mode closed",
            bucket_ops=bucket_ops,
            archive_request=archive_req,
            notify_gemini=True,
            notification_text="退出 Roleplay 模式",
        )


__all__ = ["RoleplayModeTrigger"]
