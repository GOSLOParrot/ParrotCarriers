from __future__ import annotations

import json

import py_trees
import pytest

from parrot.brain import refs as refs_registry
from parrot.brain.event_ingest import EcpEventIngest
from parrot.brain.intent_workspace import IntentWorkspace, get_intent_workspace, set_intent_workspace_for_test
from parrot.brain.observer import visual_tool as visual_tool_observer
from parrot.brain.vision.evidence import get_evidence_ledger
from parrot.brain.vision.evidence_awareness import latest_evidence_awareness_notice
from parrot.brain.vision.tool_lifecycle import (
    handle_visual_tool_lifecycle,
    latest_visual_tool_lifecycle_receipt,
    reset_visual_tool_lifecycle_for_tests,
)
from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType, TOPIC_ECP_EVENT


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    refs_registry.reset_refs_for_tests()
    get_evidence_ledger().reset_for_tests()
    reset_visual_tool_lifecycle_for_tests()
    visual_tool_observer.reset_metrics_for_tests()
    set_intent_workspace_for_test(IntentWorkspace())
    yield
    refs_registry.reset_refs_for_tests()
    get_evidence_ledger().reset_for_tests()
    reset_visual_tool_lifecycle_for_tests()
    set_intent_workspace_for_test(None)


@pytest.mark.asyncio
async def test_bbox_confirm_records_evidence_and_c3_notice() -> None:
    receipt = await handle_visual_tool_lifecycle(
        {
            "tool_id": "bbox_app_1",
            "tool_kind": "bbox",
            "interaction_phase": "confirm",
            "region": {
                "x": 0.1,
                "y": 0.2,
                "width": 0.3,
                "height": 0.4,
                "coordinate_space": "normalized",
            },
            "timebase": {
                "clock_domain": "unity",
                "wall_time_ms": 1_777_000_000_000,
                "source_id": "app-camera",
            },
            "subject_hint": "blue mug",
        },
        source="unit_test",
    )

    assert receipt["success"] is True
    assert receipt["ref_kind"] == "bbox"
    assert receipt["delivery"]["resolved_channel"] == "c3_context_notice"
    assert receipt["delivery"]["notify_goslo"] is True
    assert receipt["delivery"]["allow_interrupt"] is False
    assert receipt["salience"]["scope"] == "visual_tool_evidence_salience_not_dsg_l3_attention"
    assert refs_registry.get_ref_by_bbox("bbox_app_1") is not None
    assert receipt["evidence"]["kind"] == "bbox_focus"
    assert receipt["evidence"]["region"]["width"] == 0.3
    assert get_intent_workspace().list_active()

    notice = latest_evidence_awareness_notice()
    assert notice["notify_goslo"] is True
    assert notice["allow_interrupt"] is False
    assert notice["evidence_id"] == receipt["evidence"]["evidence_id"]


@pytest.mark.asyncio
async def test_mag_confirm_is_intent_only_but_explicit_send_notifies() -> None:
    confirm = await handle_visual_tool_lifecycle(
        {
            "tool_id": "mag_app_1",
            "tool_kind": "mag",
            "interaction_phase": "confirm",
            "region": {"x": 0.4, "y": 0.4, "width": 0.2, "height": 0.2},
            "asset_path": "data/photos/2026-05-16/mag_crop.jpg",
            "mime_type": "image/jpeg",
        },
        source="unit_test",
    )

    assert confirm["success"] is True
    assert confirm["ref_kind"] == "focus"
    assert confirm["evidence"]["kind"] == "image_asset"
    assert confirm["delivery"]["resolved_channel"] == "intent_workspace"
    assert confirm["delivery"]["notify_goslo"] is False
    assert latest_evidence_awareness_notice()["notify_goslo"] is False

    explicit = await handle_visual_tool_lifecycle(
        {
            "tool_id": "mag_app_1",
            "tool_kind": "mag",
            "interaction_phase": "explicit_send",
            "delivery_preference": "c3",
            "asset_path": "data/photos/2026-05-16/mag_crop.jpg",
            "mime_type": "image/jpeg",
        },
        source="unit_test",
    )

    assert explicit["delivery"]["resolved_channel"] == "c3_context_notice"
    assert explicit["delivery"]["notify_goslo"] is True
    assert latest_evidence_awareness_notice()["notify_goslo"] is True


@pytest.mark.asyncio
async def test_cancel_releases_ref_without_c3_notice() -> None:
    await handle_visual_tool_lifecycle(
        {"tool_id": "bbox_cancel", "tool_kind": "bbox", "interaction_phase": "lock"},
        source="unit_test",
    )
    assert refs_registry.get_ref_by_bbox("bbox_cancel") is not None

    cancel = await handle_visual_tool_lifecycle(
        {
            "tool_id": "bbox_cancel",
            "tool_kind": "bbox",
            "interaction_phase": "cancel",
            "delivery_preference": "silent",
        },
        source="unit_test",
    )

    assert cancel["success"] is True
    assert cancel["delivery"]["notify_goslo"] is False
    assert refs_registry.get_ref_by_bbox("bbox_cancel") is None


def test_visual_tool_lifecycle_ecp_observer_bridges_to_same_receipt() -> None:
    ingest = EcpEventIngest()
    visual_tool_observer.register(ingest)
    event = EcpEvent.build(
        event_type=EcpEventType.VISUAL_TOOL_LIFECYCLE,
        source=EcpEventSource.UNITY,
        payload={
            "tool_id": "bbox_ecp",
            "tool_kind": "bbox",
            "interaction_phase": "confirm",
            "region": {"x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5},
            "timebase": {"clock_domain": "unity", "wall_time_ms": 1_777_000_001_000},
        },
    )

    handled = ingest.handle_raw(TOPIC_ECP_EVENT, event.to_wire_json().encode("utf-8"))

    assert handled is not None
    assert visual_tool_observer.get_metrics_snapshot()["lifecycle_bridged"] == 1
    assert refs_registry.get_ref_by_bbox("bbox_ecp") is not None
    receipt = latest_visual_tool_lifecycle_receipt()
    assert receipt["success"] is True
    assert receipt["packet"]["tool_id"] == "bbox_ecp"
    assert receipt["delivery"]["resolved_channel"] == "c3_context_notice"
    assert json.loads(event.to_wire_json())["payload"]["tool_kind"] == "bbox"
