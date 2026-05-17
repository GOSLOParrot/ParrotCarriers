from __future__ import annotations

import asyncio
import json

import pytest

from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
from parrot.brain.tools import tools_for_active_model
from parrot.brain.tools.calendar_change_request import calendar_change_request
from parrot.brain.tools.calendar_change_request import do_calendar_change_request
from parrot.brain.tools.calendar_task_status import calendar_task_status
from parrot.brain.tools.calendar_task_status import do_calendar_task_status
from parrot.shared.constants import STREAM_NANOBOT_DISPATCH, STREAM_TRIGGER_RESULTS


@pytest.fixture(autouse=True)
def _reset_intent_workspace():
    set_intent_workspace_for_test(IntentWorkspace())
    yield
    set_intent_workspace_for_test(None)


def test_calendar_change_request_stages_hitl_draft_without_dispatch() -> None:
    text = asyncio.run(
        do_calendar_change_request(
            action="create",
            title="Tea planning",
            time_range="2026-05-18 15:00-15:30",
            calendar_id="primary",
            reason="User asked GOSLO to reserve focus time",
            details_json=json.dumps({"location": "Library"}),
        )
    )

    assert "Calendar change draft staged" in text
    assert "create -> calendar_create" in text
    assert "No Google Calendar write" in text

    from parrot.brain.intent_workspace import get_intent_workspace

    drafts = get_intent_workspace().list_active(role="calendar_draft")
    assert len(drafts) == 1
    payload = json.loads(get_intent_workspace().fetch_payload(drafts[0].ref_id))
    draft_payload = payload["payload"]
    assert draft_payload["schema"] == "goslo_calendar_change_request_v1"
    assert draft_payload["requires_hitl"] is True
    assert draft_payload["task_type_after_approval"] == "calendar_create"
    assert draft_payload["details"]["location"] == "Library"


def test_calendar_collaboration_tools_are_registered_for_goslo() -> None:
    tools = tools_for_active_model()

    assert calendar_change_request in tools
    assert calendar_task_status in tools


def test_calendar_change_request_rejects_patch_without_event_id() -> None:
    text = asyncio.run(
        do_calendar_change_request(
            action="patch",
            title="Move event",
            time_range="2026-05-18 16:00-16:30",
        )
    )

    assert "missing event_id" in text
    assert "No write occurred" in text


def test_calendar_task_status_reads_completed_result() -> None:
    async def fake_reader(stream: str, count: int):
        if stream == STREAM_TRIGGER_RESULTS:
            return [
                (
                    "1-0",
                    {
                        "payload": json.dumps(
                            {
                                "type": "calendar_result",
                                "task_id": "task-1",
                                "original_type": "calendar_fetch",
                                "status": "completed",
                                "result": {
                                    "events": [
                                        {
                                            "id": "evt-1",
                                            "title": "Tea planning",
                                        }
                                    ]
                                },
                            }
                        ),
                        "created_at": "1",
                    },
                )
            ]
        if stream == STREAM_NANOBOT_DISPATCH:
            return []
        return []

    text = asyncio.run(
        do_calendar_task_status(
            task_id="task-1",
            stream_reader=fake_reader,
        )
    )

    assert "result available" in text
    assert "task-1" in text
    assert "Events: 1" in text
    assert "Tea planning" in text
    assert "did not write Calendar" in text


def test_calendar_task_status_reads_pending_dispatch() -> None:
    async def fake_reader(stream: str, count: int):
        if stream == STREAM_TRIGGER_RESULTS:
            return []
        if stream == STREAM_NANOBOT_DISPATCH:
            return [
                (
                    "2-0",
                    {
                        "payload": json.dumps(
                            {
                                "task_id": "task-2",
                                "type": "calendar_fetch",
                                "priority": "high",
                                "params": {
                                    "result_channel": "calendar_result",
                                    "intent": "check today's schedule",
                                },
                            }
                        )
                    },
                )
            ]
        return []

    text = asyncio.run(
        do_calendar_task_status(
            task_id="task-2",
            stream_reader=fake_reader,
        )
    )

    assert "dispatched or pending" in text
    assert "task-2" in text
    assert "calendar_fetch" in text
    assert "GOSLO can continue" in text
