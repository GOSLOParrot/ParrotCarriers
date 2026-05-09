"""App V1 developer-console test harness.

These helpers exercise the same EcpEvent observer path that Unity uses for
Focus, BBox, and Photo preview events. They are intentionally small and
side-effect explicit: every helper returns metrics so the Web console can show
what changed, and no helper writes Graphiti or external calendars.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import EcpEventIngest
from parrot.brain.observer.event_bus import register_phase4_observers
from parrot.shared.ecp_event import TOPIC_ECP_EVENT, EcpEvent, EcpEventSource, EcpEventType


@dataclass(frozen=True)
class AppHarnessResult:
    """Serializable result for Web console tool-flow tests."""

    action: str
    success: bool
    event_type: str
    event_id: str = ""
    message: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "success": self.success,
            "event_type": self.event_type,
            "event_id": self.event_id,
            "message": self.message,
            "metrics": dict(self.metrics),
            "payload": dict(self.payload),
        }


def simulate_focus_event(
    *,
    focus_id: str = "fc_web_console",
    action: str = "anchored",
    label: str = "web console focus",
) -> AppHarnessResult:
    """Simulate Focus tool anchoring/release through the EcpEvent ingest path."""
    selected = action.strip().lower()
    if selected not in {"anchored", "released"}:
        return AppHarnessResult(
            action="simulate_focus_event",
            success=False,
            event_type="focus.invalid",
            message=f"unsupported focus action: {action}",
        )

    event_type = (
        EcpEventType.FOCUS_ANCHORED
        if selected == "anchored"
        else EcpEventType.FOCUS_RELEASED
    )
    payload: dict[str, Any] = {"focus_id": focus_id}
    if selected == "anchored":
        payload.update({
            "center": [0.5, 0.5],
            "radius": 0.16,
            "pose": _default_pose(),
            "label": label,
        })
    return _dispatch_once(
        action="simulate_focus_event",
        event_type=event_type,
        payload=payload,
    )


def simulate_bbox_event(
    *,
    bbox_id: str = "bb_web_console",
    action: str = "placed",
    label: str = "web console bbox",
) -> AppHarnessResult:
    """Simulate BoundaryBox placement/removal through the EcpEvent ingest path."""
    selected = action.strip().lower()
    if selected not in {"placed", "removed"}:
        return AppHarnessResult(
            action="simulate_bbox_event",
            success=False,
            event_type="bbox.invalid",
            message=f"unsupported bbox action: {action}",
        )

    event_type = EcpEventType.BBOX_PLACED if selected == "placed" else EcpEventType.BBOX_REMOVED
    payload: dict[str, Any] = {"bbox_id": bbox_id}
    if selected == "placed":
        payload.update({
            "corners": [[0.25, 0.25], [0.75, 0.75]],
            "pose": _default_pose(),
            "label": label,
        })
    return _dispatch_once(
        action="simulate_bbox_event",
        event_type=event_type,
        payload=payload,
    )


def simulate_photo_preview(
    *,
    photo_id: str = "ph_web_console",
    candidate_subject_uuid: str = "",
) -> AppHarnessResult:
    """Simulate Unity's photo.taken_preview event without sending an asset."""
    tiny_preview = base64.b64encode(b"APP_V1_PREVIEW").decode("ascii")
    payload = {
        "schema_version": 1,
        "photo_id": photo_id,
        "stage": "preview",
        "pose": {"px": 0, "py": 1, "pz": 0, "qx": 0, "qy": 0, "qz": 0, "qw": 1},
        "episode_ref": "",
        "focus_refs": [],
        "bbox_refs": [],
        "candidate_subject_uuid": candidate_subject_uuid,
        "preview_jpeg_b64": tiny_preview,
        "asset_ref": "",
        "asset_bytes": 0,
        "ts_ms": 0,
    }
    return _dispatch_once(
        action="simulate_photo_preview",
        event_type=EcpEventType.PHOTO_TAKEN_PREVIEW,
        payload=payload,
    )


def _dispatch_once(
    *,
    action: str,
    event_type: EcpEventType,
    payload: dict[str, Any],
) -> AppHarnessResult:
    ingest = EcpEventIngest()
    register_phase4_observers(ingest)
    event = EcpEvent.build(
        event_type=event_type,
        source=EcpEventSource.UNITY,
        payload=payload,
        unity_identity="web-console",
        room_id="app-v1-console",
    )
    accepted = ingest.handle_raw(TOPIC_ECP_EVENT, event.to_wire_json().encode("utf-8"))
    metrics = {
        "ingest": ingest.metrics_snapshot(),
        "refs": refs_registry.metrics_snapshot(),
    }
    return AppHarnessResult(
        action=action,
        success=accepted is not None,
        event_type=event_type.value,
        event_id=event.event_id,
        message="dispatched" if accepted is not None else "rejected",
        metrics=metrics,
        payload=payload,
    )


def _default_pose() -> dict[str, list[float]]:
    return {
        "position": [0.0, 1.0, 0.5],
        "rotation": [0.0, 0.0, 0.0, 1.0],
    }


__all__ = [
    "AppHarnessResult",
    "simulate_bbox_event",
    "simulate_focus_event",
    "simulate_photo_preview",
]
