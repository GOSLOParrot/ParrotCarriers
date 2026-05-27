from __future__ import annotations

import json
from pathlib import Path

import pytest

from parrot.bus import nanobot_consumer
from parrot.bus.nanobot_consumer import NanobotConsumer
from parrot.shared.constants import CH_NANOBOT_RESULTS, STREAM_NANOBOT_DISPATCH


class FakeRedis:
    def __init__(self) -> None:
        self.hsets: list[tuple[str, dict[str, str]]] = []
        self.acks: list[tuple[str, str, str]] = []
        self.published: list[tuple[str, str]] = []

    async def hset(self, key: str, *, mapping: dict[str, str]) -> None:
        self.hsets.append((key, mapping))

    async def xack(self, stream: str, group: str, msg_id: str) -> None:
        self.acks.append((stream, group, msg_id))

    async def publish(self, channel: str, payload: str) -> None:
        self.published.append((channel, payload))


class FakeResponse:
    def __init__(self, *, status: int = 200, body: bytes = b"", headers: dict[str, str] | None = None) -> None:
        self.status = status
        self._body = body
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def getcode(self) -> int:
        return self.status

    def read(self, _limit: int = -1) -> bytes:
        return self._body


def published_body(redis: FakeRedis) -> dict[str, object]:
    published = json.loads(redis.published[0][1])
    return json.loads(published["result"])


@pytest.mark.asyncio
async def test_fallback_nanobot_diary_query_reads_daily_markdown(tmp_path) -> None:
    diary_root = tmp_path / "Diary" / "2026"
    diary_root.mkdir(parents=True)
    note = diary_root / "2026-05-18.md"
    note.write_text(
        "---\nprofile: daily\ntitle: Diary 2026-05-18\ndate: 2026-05-18\n---\n"
        "Practiced guitar chords, watched anime, drank water, took medicine.",
        encoding="utf-8",
    )
    redis = FakeRedis()
    task = {
        "task_id": "task-diary",
        "type": "diary_query",
        "params": {
            "diary_root": str(tmp_path / "Diary"),
            "date_from": "2026-05-12",
            "date_to": "2026-05-18",
            "result_channel": "diary_result",
            "query": "guitar water medicine",
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-0",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "diary_query"
    assert published["result_channel"] == "diary_result"
    assert published["result_summary"].startswith("Diary query found 1 entry")
    assert body["entries"][0]["date"] == "2026-05-18"
    assert body["entries"][0]["path"] == str(note)
    assert "profile=daily" in body["profile_policy"]


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_fetch_reads_demo_fixture(tmp_path) -> None:
    fixture = tmp_path / "calendar.json"
    fixture.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "id": "evt_future",
                        "summary": "Demo future event",
                        "start": {"dateTime": "2026-05-21T10:00:00+08:00"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar",
        "type": "calendar_fetch",
        "params": {
            "demo_events_path": str(fixture),
            "time_min": "2026-05-20T00:00:00+08:00",
            "time_max": "2026-05-22T00:00:00+08:00",
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-1",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_fetch"
    assert published["result_channel"] == "calendar_result"
    assert published["result_summary"].startswith("Calendar query found 1 event")
    assert body["events"][0]["id"] == "evt_future"
    assert body["events"][0]["title"] == "Demo future event"


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_create_calls_google_api(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_calendar_api_request(**kwargs):
        calls.append(kwargs)
        event_body = kwargs["body"]
        assert isinstance(event_body, dict)
        return (
            {
                "id": "evt_created",
                "summary": event_body["summary"],
                "start": event_body["start"],
                "end": event_body["end"],
                "status": "confirmed",
                "htmlLink": "https://calendar.google.com/event?eid=created",
            },
            200,
            "unit_oauth",
        )

    monkeypatch.setattr(nanobot_consumer, "_calendar_google_api_request", fake_calendar_api_request)
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-create",
        "type": "calendar_create",
        "params": {
            "calendar_write_approved": True,
            "calendar_id": "primary",
            "title": "Tea planning",
            "time_range": "2026-05-18 15:00-15:30",
            "details": {"location": "Library"},
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-10", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_create"
    assert published["status"] == "completed"
    assert published["result_channel"] == "calendar_result"
    assert published["result_summary"].startswith("Calendar create completed")
    assert body["event_id"] == "evt_created"
    assert body["events"][0]["title"] == "Tea planning"
    assert calls[0]["method"] == "POST"
    assert calls[0]["calendar_id"] == "primary"
    assert calls[0]["event_id"] == ""
    assert calls[0]["body"]["location"] == "Library"
    assert calls[0]["body"]["start"]["dateTime"].startswith("2026-05-18T15:00:00")
    assert calls[0]["body"]["end"]["dateTime"].startswith("2026-05-18T15:30:00")
    assert calls[0]["query"]["sendUpdates"] == "none"


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_patch_calls_google_api(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_calendar_api_request(**kwargs):
        calls.append(kwargs)
        event_body = kwargs["body"]
        assert isinstance(event_body, dict)
        return (
            {
                "id": "evt_patch",
                "summary": event_body["summary"],
                "start": {"dateTime": "2026-05-18T16:00:00+08:00"},
                "end": {"dateTime": "2026-05-18T16:30:00+08:00"},
                "location": event_body["location"],
                "status": "confirmed",
            },
            200,
            "unit_oauth",
        )

    monkeypatch.setattr(nanobot_consumer, "_calendar_google_api_request", fake_calendar_api_request)
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-patch",
        "type": "calendar_patch",
        "params": {
            "hitl_approved": True,
            "calendar_id": "primary",
            "event_id": "evt_patch",
            "title": "Moved tea planning",
            "details": {"location": "Study"},
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-11", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_patch"
    assert published["status"] == "completed"
    assert body["event_id"] == "evt_patch"
    assert body["events"][0]["location"] == "Study"
    assert calls[0]["method"] == "PATCH"
    assert calls[0]["event_id"] == "evt_patch"
    assert calls[0]["body"] == {"location": "Study", "summary": "Moved tea planning"}


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_delete_calls_google_api(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_calendar_api_request(**kwargs):
        calls.append(kwargs)
        return {}, 204, "unit_oauth"

    monkeypatch.setattr(nanobot_consumer, "_calendar_google_api_request", fake_calendar_api_request)
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-delete",
        "type": "calendar_delete",
        "params": {
            "operator_mode": True,
            "calendar_id": "primary",
            "event_id": "evt_delete",
            "title": "Cancelled tea planning",
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-12", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_delete"
    assert published["status"] == "completed"
    assert body["event_id"] == "evt_delete"
    assert body["events"][0]["status"] == "cancelled"
    assert calls[0]["method"] == "DELETE"
    assert calls[0]["event_id"] == "evt_delete"
    assert calls[0]["body"] is None


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_write_requires_approval(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_calendar_api_request(**kwargs):
        calls.append(kwargs)
        return {}, 200, "unit_oauth"

    monkeypatch.setattr(nanobot_consumer, "_calendar_google_api_request", fake_calendar_api_request)
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-unapproved",
        "type": "calendar_delete",
        "params": {
            "calendar_id": "primary",
            "event_id": "evt_delete",
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-13", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_delete"
    assert published["status"] == "failed"
    assert "calendar_write_not_approved" in body["error"]
    assert calls == []


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_mission_reports_decision_options(tmp_path) -> None:
    fixture = tmp_path / "calendar.json"
    fixture.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "id": "evt_busy",
                        "summary": "Existing meeting",
                        "start": {"dateTime": "2026-05-18T15:00:00+08:00"},
                        "end": {"dateTime": "2026-05-18T15:30:00+08:00"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-mission",
        "type": "calendar_mission",
        "params": {
            "goal": "Find a safe time for tea planning",
            "mode": "guided_workflow",
            "workflow": {"steps": ["inspect_calendar", "detect_conflicts", "wait_for_approval"]},
            "authority": "draft_only",
            "demo_events_path": str(fixture),
            "time_min": "2026-05-18T14:00:00+08:00",
            "time_max": "2026-05-18T17:00:00+08:00",
            "title": "Tea planning",
            "time_range": "2026-05-18 15:00-15:30",
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-14", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_mission"
    assert published["status"] == "needs_user_decision"
    assert published["result_channel"] == "calendar_result"
    assert body["schema"] == "nanobot_mission_result_v1"
    assert body["mode"] == "guided_workflow"
    assert body["nanobot_capabilities"]["workflow_guided"] is True
    assert body["investigation_trace"][0]["phase"] == "understand_goal"
    assert body["workflow_phase_results"][1]["id"] == "detect_conflicts"
    assert body["decision_strategy"]["next_action"] == "ask_user_to_resolve_conflict"
    assert body["authority"] == "draft_only"
    assert body["requires_approval"] is True
    assert body["conflicts"][0]["event_id"] == "evt_busy"
    assert body["options"][0]["id"] == "proceed_with_proposed_write"
    assert body["proposed_write"]["event_body"]["summary"] == "Tea planning"


@pytest.mark.asyncio
async def test_fallback_nanobot_calendar_mission_executes_approved_write(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_calendar_api_request(**kwargs):
        calls.append(kwargs)
        return {
            "id": "evt_created",
            "summary": "Tea planning",
            "start": {"dateTime": "2026-05-18T16:00:00+08:00"},
            "end": {"dateTime": "2026-05-18T16:30:00+08:00"},
            "htmlLink": "https://calendar.google.com/event?eid=evt_created",
        }, 200, "unit_oauth"

    monkeypatch.setattr(nanobot_consumer, "_calendar_google_api_request", fake_calendar_api_request)
    redis = FakeRedis()
    task = {
        "task_id": "task-calendar-mission-write",
        "type": "calendar_mission",
        "params": {
            "goal": "Create tea planning if there are no conflicts",
            "authority": "approved_write",
            "calendar_write_approved": True,
            "hitl_approved": True,
            "calendar_id": "primary",
            "title": "Tea planning",
            "time_range": "2026-05-18 16:00-16:30",
            "result_channel": "calendar_result",
        },
    }

    await NanobotConsumer()._handle_task(redis, "1710000000-15", {"payload": json.dumps(task)})

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "calendar_mission"
    assert published["status"] == "completed"
    assert published["result_channel"] == "calendar_result"
    assert body["schema"] == "nanobot_mission_result_v1"
    assert body["status"] == "completed"
    assert body["execution_policy"] == "approved_calendar_write_performed"
    assert body["write_task_type"] == "calendar_create"
    assert body["nanobot_capabilities"]["calendar_write_actuator_available"] is True
    assert body["decision_strategy"]["next_action"] == "report_write_receipt"
    assert body["investigation_trace"][-1]["phase"] == "approved_execution"
    assert body["write_result"]["action"] == "create"
    assert body["event_id"] == "evt_created"
    assert calls[0]["method"] == "POST"
    assert calls[0]["calendar_id"] == "primary"
    assert calls[0]["body"]["summary"] == "Tea planning"


@pytest.mark.asyncio
async def test_fallback_nanobot_message_check_returns_demo_important_mail() -> None:
    redis = FakeRedis()
    task = {
        "task_id": "task-message",
        "type": "message_check",
        "params": {
            "query": "important unread mail",
            "result_channel": "message_result",
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-2",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "message_check"
    assert published["result_channel"] == "message_result"
    assert published["result_summary"].startswith("Google 刚收到 1 封重要邮件")
    assert body["messages"][0]["importance"] == "high"
    assert body["messages"][0]["subject"] == "GOSLO 演示准备确认"


@pytest.mark.asyncio
async def test_fallback_nanobot_remind_returns_due_summary() -> None:
    redis = FakeRedis()
    task = {
        "task_id": "task-remind",
        "type": "remind",
        "params": {
            "reminder_text": "吃药",
            "when": "2026-05-19T08:00:00+08:00",
            "result_channel": "reminder_result",
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-3",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["type"] == "remind"
    assert published["result_channel"] == "reminder_result"
    assert published["result_summary"].startswith("提醒时间到了：吃药")
    assert body["reminder_text"] == "吃药"


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_reports_local_file_hash(tmp_path) -> None:
    local_ref = tmp_path / "Amiya.md"
    local_ref.write_text("Amiya", encoding="utf-8")
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_unit",
            "result_channel": "memory_ref_scan_result",
            "allow_mutation": False,
            "refs": [
                {
                    "ref_id": "ref-local",
                    "canonical_uuid": "canon-local",
                    "kind": "obsidian_doc",
                    "locators": [str(local_ref)],
                    "manifest_action": "compare_git_manifest_and_ref_record",
                }
            ],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-0",
        {"payload": json.dumps(task)},
    )

    assert redis.acks == [(STREAM_NANOBOT_DISPATCH, "nanobot-workers", "1710000000-0")]
    assert redis.published[0][0] == CH_NANOBOT_RESULTS
    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    ref_result = body["ref_results"][0]
    locator_result = ref_result["locator_results"][0]
    assert published["task_id"] == "task-ref-scan"
    assert published["type"] == "ref_scan"
    assert published["result_channel"] == "memory_ref_scan_result"
    assert body["scan_id"] == "refscan_unit"
    assert body["allow_mutation"] is False
    assert ref_result["ref_id"] == "ref-local"
    assert ref_result["health"] == "ok"
    assert ref_result["content_hash"].startswith("sha256:")
    assert locator_result["health"] == "ok"
    assert locator_result["reason"] == "local_path_exists"
    assert body["manifest_delta"][0]["action"] == "propose_health_update"


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_keeps_remote_refs_unknown() -> None:
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan-remote",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_remote_unit",
            "result_channel": "memory_ref_scan_result",
            "allow_mutation": False,
            "refs": [
                {
                    "ref_id": "ref-ecs",
                    "canonical_uuid": "canon-ecs",
                    "kind": "ecs_path",
                    "locators": ["ecs://castle/root/photos/amiya.jpg"],
                },
                {
                    "ref_id": "ref-graphiti",
                    "canonical_uuid": "canon-graphiti",
                    "kind": "graphiti_entity",
                    "locators": ["graphiti://arknights/entity/graphiti-node"],
                },
            ],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-1",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    by_ref = {row["ref_id"]: row for row in body["ref_results"]}
    assert by_ref["ref-ecs"]["health"] == "unknown"
    assert by_ref["ref-ecs"]["locator_results"][0]["reason"] == "ecs_path_not_checked_by_fallback"
    assert by_ref["ref-graphiti"]["health"] == "unknown"
    assert by_ref["ref-graphiti"]["locator_results"][0]["reason"] == "graphiti_pointer_not_checked_by_fallback"
    assert body["manifest_delta"] == []


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_runs_enabled_url_head(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        assert request.get_method() == "HEAD"
        assert timeout == 3.0
        return FakeResponse(
            status=204,
            headers={"Content-Type": "text/plain", "Content-Length": "0"},
        )

    monkeypatch.setattr(nanobot_consumer.urllib.request, "urlopen", fake_urlopen)
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan-url",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_url_unit",
            "allow_mutation": False,
            "enable_url_check": True,
            "refs": [
                {
                    "ref_id": "ref-url",
                    "canonical_uuid": "canon-url",
                    "kind": "external_url",
                    "locators": ["https://example.test/amiya"],
                }
            ],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-3",
        {"payload": json.dumps(task)},
    )

    body = published_body(redis)
    ref_result = body["ref_results"][0]
    locator_result = ref_result["locator_results"][0]
    assert ref_result["health"] == "ok"
    assert locator_result["health"] == "ok"
    assert locator_result["reason"] == "url_head_ok"
    assert locator_result["status_code"] == 204
    assert body["checker_policy"]["remote_checks_enabled"] == ["url_head"]


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_runs_enabled_ecs_local_probe(monkeypatch, tmp_path) -> None:
    ecs_file = tmp_path / "amiya.jpg"
    ecs_file.write_bytes(b"amiya-photo")

    def fake_locator_to_local_path(locator: str, *, options: dict[str, object]) -> tuple[Path, str]:
        assert locator == "ecs://castle/root/photos/amiya.jpg"
        return ecs_file, ""

    monkeypatch.setattr(nanobot_consumer, "_ecs_locator_to_local_path", fake_locator_to_local_path)
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan-ecs",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_ecs_unit",
            "allow_mutation": False,
            "enable_ecs_local_check": True,
            "ecs_local_check_confirmed": True,
            "refs": [
                {
                    "ref_id": "ref-ecs",
                    "canonical_uuid": "canon-ecs",
                    "kind": "ecs_path",
                    "locators": ["ecs://castle/root/photos/amiya.jpg"],
                }
            ],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-4",
        {"payload": json.dumps(task)},
    )

    body = published_body(redis)
    ref_result = body["ref_results"][0]
    locator_result = ref_result["locator_results"][0]
    assert ref_result["health"] == "ok"
    assert ref_result["content_hash"].startswith("sha256:")
    assert locator_result["target_type"] == "ecs_path"
    assert locator_result["reason"] == "ecs_local_path_exists"
    assert locator_result["local_probe_path"] == str(ecs_file)


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_runs_enabled_graphiti_probe(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        assert request.full_url == "http://graphiti.local/api/graphiti/search"
        payload = json.loads(request.data.decode("utf-8"))
        assert payload == {"query": "graphiti-node", "partition": "arknights", "limit": 10}
        assert timeout == 3.0
        return FakeResponse(
            status=200,
            body=json.dumps(
                {
                    "success": True,
                    "data": {"results": [{"uuid": "graphiti-node", "name": "Amiya"}]},
                }
            ).encode("utf-8"),
        )

    monkeypatch.setattr(nanobot_consumer.urllib.request, "urlopen", fake_urlopen)
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan-graphiti",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_graphiti_unit",
            "allow_mutation": False,
            "enable_graphiti_probe": True,
            "graphiti_base_url": "http://graphiti.local",
            "refs": [
                {
                    "ref_id": "ref-graphiti",
                    "canonical_uuid": "canon-graphiti",
                    "kind": "graphiti_entity",
                    "locators": ["graphiti://arknights/entity/graphiti-node"],
                }
            ],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-5",
        {"payload": json.dumps(task)},
    )

    body = published_body(redis)
    ref_result = body["ref_results"][0]
    locator_result = ref_result["locator_results"][0]
    assert ref_result["health"] == "ok"
    assert locator_result["health"] == "ok"
    assert locator_result["reason"] == "graphiti_uuid_found_by_search_probe"
    assert locator_result["result_count"] == 1


@pytest.mark.asyncio
async def test_fallback_nanobot_ref_scan_refuses_mutation_request() -> None:
    redis = FakeRedis()
    task = {
        "task_id": "task-ref-scan-mutate",
        "type": "ref_scan",
        "params": {
            "scan_id": "refscan_mutate_unit",
            "result_channel": "memory_ref_scan_result",
            "allow_mutation": True,
            "refs": [],
        },
    }

    await NanobotConsumer()._handle_task(
        redis,
        "1710000000-2",
        {"payload": json.dumps(task)},
    )

    published = json.loads(redis.published[0][1])
    body = json.loads(published["result"])
    assert published["status"] == "failed"
    assert body["error"] == "ref_scan_worker_refuses_mutation"
    assert body["warnings"] == ["mutation_request_rejected"]
