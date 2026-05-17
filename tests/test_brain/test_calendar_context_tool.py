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
