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
