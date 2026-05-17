from __future__ import annotations

import asyncio

from parrot.brain.tools.calendar_context import do_calendar_context, format_calendar_context


def test_calendar_context_formats_t1_preview() -> None:
    receipt = {
        "success": True,
        "data": {
            "count": 1,
            "read_model": "Google Calendar API events.list via OAuth2",
            "normalized_events": [
                {
                    "id": "evt_1",
                    "title": "Tea planning",
                    "start_time": "2026-05-18T09:00:00+08:00",
                    "end_time": "2026-05-18T09:30:00+08:00",
                    "location": "Library",
                    "status": "confirmed",
                }
            ],
            "mapping_rows": [
                {
                    "l15_bucket": "google_calendar",
                    "l2b_kind": "event",
                    "l2b_action": "upsert_event",
                }
            ],
        },
    }

    text = format_calendar_context(
        receipt,
        intent="decide whether there is time before lunch",
        requested_date="2026-05-18",
        resolved_date="2026-05-18",
        fetch_source="api",
        tried_sources=["api"],
        sync_policy="import",
    )

    assert "T1 Intent/Thinking" in text
    assert "Tea planning" in text
    assert "1 L1.5 observation candidate" in text
    assert "requested_import_downgraded_to_preview" in text
    assert "No Google Calendar write" in text
    assert "no L2-B mutation" in text


def test_do_calendar_context_uses_api_fetcher_and_returns_compact_context() -> None:
    seen_payloads: list[dict] = []

    async def fake_api(payload: dict) -> dict:
        seen_payloads.append(payload)
        return {
            "success": True,
            "data": {
                "count": 0,
                "read_model": "fake api",
                "normalized_events": [],
                "mapping_rows": [],
            },
        }

    text = asyncio.run(
        do_calendar_context(
            intent="check today",
            date="2026-05-18",
            calendar_id="primary",
            timezone="Asia/Shanghai",
            limit=40,
            fetch_source="api",
            api_fetcher=fake_api,
        )
    )

    assert seen_payloads == [
        {
            "date": "2026-05-18",
            "calendar_id": "primary",
            "timezone": "Asia/Shanghai",
            "limit": 12,
        }
    ]
    assert "No events found" in text
    assert "fake api" in text
    assert "No Google Calendar write" in text


def test_do_calendar_context_falls_back_to_task_when_t1_fetch_times_out() -> None:
    dispatched: list[tuple[str, dict | None, str]] = []

    async def slow_api(payload: dict) -> dict:
        await asyncio.sleep(0.2)
        return {"success": True, "data": {"count": 0, "normalized_events": []}}

    async def fake_dispatch(task_type: str, params: dict | None, priority: str) -> str:
        dispatched.append((task_type, params, priority))
        return "task1234"

    text = asyncio.run(
        do_calendar_context(
            intent="check if we can schedule writing",
            date="2026-05-18",
            calendar_id="primary",
            timezone="Asia/Shanghai",
            fetch_source="api",
            api_fetcher=slow_api,
            task_dispatcher=fake_dispatch,
            thinking_budget_s=0.05,
        )
    )

    assert "T1 Intent/Thinking -> T3 calendar_fetch" in text
    assert "timeout" in text
    assert "task1234" in text
    assert dispatched
    task_type, params, priority = dispatched[0]
    assert task_type == "calendar_fetch"
    assert priority == "high"
    assert params is not None
    assert params["source"] == "calendar_context_t1_fallback"
    assert params["date"] == "2026-05-18"
    assert params["sync_policy"] == "preview"
    assert "No Google Calendar write" in text
