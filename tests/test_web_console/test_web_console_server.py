from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib import import_module
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from parrot.web_console.server import OrchestratorProxyConfig, _status_summary, build_app


def test_console_config_uses_env_without_leaking_secret(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_WEB_CONSOLE_ORCH_URL", "http://127.0.0.1:9876/")
    monkeypatch.setenv("PARROT_ORCH_SECRET", "secret-value")
    monkeypatch.setenv("PARROT_WEB_CONSOLE_REFRESH_S", "9")

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    body = client.get("/api/console/config").json()

    assert body["orchestrator_base_url"] == "http://127.0.0.1:9876"
    assert body["orchestrator_auth_mode"] == "bearer"
    assert body["refresh_interval_s"] == 9.0
    assert "secret-value" not in str(body)


def test_orchestrator_status_proxy_calls_fetcher(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_ORCH_PORT", "8123")
    monkeypatch.delenv("PARROT_WEB_CONSOLE_ORCH_URL", raising=False)
    monkeypatch.delenv("PARROT_ORCH_SECRET", raising=False)

    async def fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
        assert config.base_url == "http://127.0.0.1:8123"
        assert config.auth_mode == "dev-open"
        return {
            "ok": True,
            "state": "connected",
            "upstream": {
                "url": config.status_url,
                "status_code": 200,
                "auth_mode": config.auth_mode,
                "fetched_at": 1.0,
            },
            "summary": {"online_processes": 1, "offline_processes": 0},
            "status": {"schema_version": 1, "processes": []},
            "detail": {},
        }

    client = TestClient(build_app(status_fetcher=fetcher))
    body = client.get("/api/orchestrator/status").json()

    assert body["ok"] is True
    assert body["upstream"]["url"] == "http://127.0.0.1:8123/status"


def test_index_serves_static_console() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    response = client.get("/")

    assert response.status_code == 200
    assert "Parrot Web Console" in response.text
    app_asset_match = re.search(r'src="(?P<asset>/assets/app[^"]+\.js)"', response.text)
    assert app_asset_match is not None
    assert response.headers["Cache-Control"] == "no-store"

    asset = client.get(app_asset_match.group("asset"))
    assert asset.status_code == 200
    assert asset.headers["Cache-Control"] == "no-store"

    fallback = client.get("/memory")
    assert fallback.status_code == 200
    assert "Parrot Web Console" in fallback.text
    assert fallback.headers["Cache-Control"] == "no-store"


def test_app_canvas_and_lineb_facade_routes_are_exposed() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher, app_facade_factory=_FakeAppFacade))

    canvas = client.get("/api/app/canvas").json()
    modules = client.get("/api/app/modules").json()
    profiles = client.get("/api/app/line-profiles").json()
    route = client.post("/api/app/lineb/audio-route", json={}).json()
    mic = client.post(
        "/api/app/lineb/mic-input",
        json={"asr_text": "hello LineB", "echo_score": "0.1"},
    ).json()

    assert canvas["active_workspace_id"] == "workdesk"
    assert modules[0]["module_id"] == "voice_pipeline"
    assert profiles[0]["line_profile_id"] == "lineb_google_default"
    assert route["source"] == "web_console.lineb_voice"
    assert mic["turn_decision"] == "user_turn"


def test_livekit_web_token_mints_without_exposing_api_secret(monkeypatch) -> None:
    monkeypatch.setenv("LIVEKIT_URL", "ws://127.0.0.1:7880")
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "very-secret-livekit-api-secret-with-length")
    monkeypatch.setenv("PARROT_WEB_CONSOLE_LIVEKIT_TOKEN_TTL_S", "60")

    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    config = client.get("/api/livekit/config").json()
    token = client.post(
        "/api/livekit/web-token",
        json={"room": "parrot-test", "identity": "web-console-test"},
    ).json()

    assert config["url"] == "ws://127.0.0.1:7880"
    assert config["room"] == "parrot-main"
    assert "very-secret-livekit-api-secret" not in str(config)
    assert token["url"] == "ws://127.0.0.1:7880"
    assert token["room"] == "parrot-test"
    assert token["identity"] == "web-console-test"
    assert token["token"]
    assert "very-secret-livekit-api-secret" not in str(token)


def test_graphiti_status_search_and_dry_run_routes_are_exposed(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-status-secret")
    monkeypatch.setenv("GRAPHITI_LLM_PROVIDER", "deepseek")
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    status = client.get("/api/graphiti/status").json()
    blank_search = client.post("/api/graphiti/search", json={"query": ""}).json()
    missing_search = client.post(
        "/api/graphiti/search",
        json={"query": "blue mug", "partition": "scene"},
    ).json()
    draft = client.post(
        "/api/graphiti/episode/draft",
        json={"name": "web_test", "body": "hello memory", "partition": "maid"},
    ).json()
    dry_run = client.post(
        "/api/graphiti/episode",
        json={"name": "web_test", "body": "hello memory", "partition": "maid", "dry_run": True},
    ).json()

    assert status["action"] == "graphiti_status"
    assert status["success"] is True
    assert status["data"]["partitions"] == [
        "goslo",
        "maid",
        "scene",
        "user",
        "arknights_test",
    ]
    assert status["data"]["graphiti_llm"]["provider"] == "deepseek"
    assert status["data"]["graphiti_llm"]["model"] == "deepseek-v4-pro"
    assert status["data"]["graphiti_llm"]["secret_configured"] is True
    assert "deepseek-status-secret" not in str(status)
    assert blank_search["success"] is False
    assert blank_search["message"] == "query is required"
    assert missing_search["success"] is False
    assert missing_search["available"] is False
    assert missing_search["message"] == "graphiti-core optional extra not installed"
    assert "pip install" not in str(missing_search)
    assert draft["action"] == "draft_episode"
    assert draft["data"]["draft"]["group_id"] == "maid"
    assert dry_run["action"] == "add_episode"
    assert dry_run["success"] is True
    assert "dry_run=true" in dry_run["message"]


def test_graphiti_subgraph_export_routes_are_l15_dry_run_and_secret_safe(monkeypatch) -> None:
    from parrot.brain import graphiti_console

    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-export-secret")
    monkeypatch.setattr(graphiti_console, "_graphiti_core_installed", lambda: False)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    missing_search = client.post(
        "/api/graphiti/subgraph/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": 3},
    ).json()
    bad_limit_search = client.post(
        "/api/graphiti/subgraph/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": "bad"},
    ).json()
    bad_limit_plain_search = client.post(
        "/api/graphiti/search",
        json={"query": "Amiya Chernobog", "partition": "arknights_test", "limit": "bad"},
    ).json()
    hit = {
        "text": "Amiya's field role changes during the Chernobog crisis.",
        "uuid": "graphiti-hit-1",
        "source_node_uuid": "source-amiya",
        "target_node_uuid": "target-chernobog",
        "score": 0.91,
        "source_url": "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88",
        "source_description": "arknights_test:main_00_01",
    }
    draft = client.post(
        "/api/graphiti/subgraph/export-draft",
        json={"partition": "arknights_test", "query": "Amiya", "hits": [hit]},
    ).json()
    export = client.post(
        "/api/graphiti/subgraph/export",
        json={
            "partition": "arknights_test",
            "query": "Amiya",
            "hits": [hit],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()

    assert missing_search["action"] == "graphiti.subgraph.search"
    assert missing_search["success"] is False
    assert missing_search["data"]["subgraph"]["partition"] == "arknights_test"
    assert bad_limit_search["action"] == "graphiti.subgraph.search"
    assert bad_limit_search["data"]["subgraph"]["partition"] == "arknights_test"
    assert bad_limit_plain_search["action"] == "search_graphiti"
    assert bad_limit_plain_search["message"] == "graphiti-core optional extra not installed"
    assert draft["action"] == "graphiti.subgraph.export_draft"
    assert draft["success"] is True
    assert draft["data"]["write_path"] == "L15Pool.admit(Observation(source=USER_EXPLICIT))"
    observation = draft["data"]["observations"][0]
    assert observation["graphiti_uuid"] == "graphiti-hit-1"
    assert observation["meta"]["graphiti_partition"] == "arknights_test"
    assert observation["meta"]["graphiti_source_node_uuid"] == "source-amiya"
    assert observation["meta"]["source_description"] == "arknights_test:main_00_01"
    assert draft["data"]["subgraph"]["partition"] == "arknights_test"
    assert draft["data"]["edge_drafts"][0]["source_graphiti_uuid"] == "source-amiya"
    assert draft["data"]["edge_drafts"][0]["target_graphiti_uuid"] == "target-chernobog"
    assert draft["data"]["edge_drafts"][0]["write_policy"] == "requires_resolved_l2b_node_uuid"
    assert "resolved L2-B node UUIDs" in draft["data"]["edge_write_policy"]
    assert export["action"] == "graphiti.subgraph.export"
    assert export["data"]["would_apply"] is True
    assert export["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert export["audit"]["direct_falkordb_write"] is False
    assert "deepseek-export-secret" not in str(missing_search) + str(draft) + str(export)


def test_arknights_graphiti_fixture_script_dry_run() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "src/scripts/import_arknights_to_graphiti.py",
            "--dry-run",
            "--limit",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["dry_run"] is True
    assert payload["partition"] == "arknights_test"
    assert len(payload["episodes"]) == 2
    assert payload["episodes"][0]["story_order"] == "main_00_01"
    assert "copied" not in payload["episodes"][0]["episode_body"].lower()
    assert "source_url" in payload["episodes"][0]["episode_body"]


def test_obsidian_vault_scan_previews_three_profiles(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\ntags: daily,desk\n---\nKeep the desk clear.",
        encoding="utf-8-sig",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor scene pack\nkind: object\n---\nScene mood and props.",
        encoding="utf-8",
    )
    (vault / "ref.md").write_text(
        "---\nprofile: ref\nlabel: Blue mug ref\nobsidian_uuid: mug-ref-1\ntarget_node_uuid: node-1\n---\nReference binding.",
        encoding="utf-8",
    )
    (vault / "bad_ref.md").write_text(
        "---\nprofile: ref\nlabel: Missing target\n---\nThis ref is intentionally invalid.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.get(
        "/api/l15/obsidian-vault/scan",
        params={"vault_path": str(vault), "limit": 8},
    ).json()

    assert body["action"] == "l15.obsidian_vault.scan"
    assert body["success"] is True
    assert body["data"]["vault"]["status"] == "ingest_ready"
    profiles = {row["profile"] for row in body["data"]["notes"]}
    assert {"daily", "roleplay", "ref"} <= profiles
    roleplay = next(row for row in body["data"]["notes"] if row["profile"] == "roleplay")
    assert roleplay["uuid_free_allowed"] is True
    assert roleplay["target_bucket"] == "obsidian_setting_roleplay"
    ref = next(row for row in body["data"]["notes"] if row["profile"] == "ref")
    assert ref["payload"]["target_node_uuid"] == "node-1"
    assert body["data"]["invalid_notes"][0]["reason"] == "missing_frontmatter_or_ref_target"


def test_obsidian_vault_import_draft_uses_l15_observation_path(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor pack\nkind: object\n---\nRoleplay scene notes.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={"vault_path": str(vault), "paths": ["roleplay.md"], "limit": 8},
    ).json()
    dry_apply = client.post(
        "/api/l15/obsidian-vault/import",
        json={
            "vault_path": str(vault),
            "paths": ["roleplay.md"],
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()

    assert draft["action"] == "l15.obsidian_vault.import_draft"
    assert draft["success"] is True
    assert draft["data"]["selected_count"] == 1
    item = draft["data"]["items"][0]
    assert item["profile"] == "roleplay"
    assert item["target_bucket"] == "obsidian_setting_roleplay"
    assert item["observation"]["source"] == "user_tag_obsidian"
    assert item["observation"]["meta"]["profile"] == "roleplay"
    assert draft["data"]["write_path"] == "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)"
    assert dry_apply["action"] == "l15.obsidian_vault.import"
    assert dry_apply["data"]["would_apply"] is True
    assert dry_apply["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"


def test_obsidian_vault_import_draft_reports_selected_missing_or_invalid_paths(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "bad_ref.md").write_text(
        "---\nprofile: ref\nlabel: Missing target\n---\nThis ref is intentionally invalid.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md", "bad_ref.md", "missing.md"],
            "limit": 8,
        },
    ).json()

    assert draft["action"] == "l15.obsidian_vault.import_draft"
    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 1
    errors = {row["path"]: row["error"] for row in draft["data"]["errors"]}
    assert errors["bad_ref.md"] == "note_not_import_ready"
    assert errors["missing.md"] == "selected_path_not_found"


def test_obsidian_vault_import_draft_reports_profile_mismatch_for_selected_path(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    (vault / "roleplay.md").write_text(
        "---\nprofile: roleplay\nlabel: Harbor pack\nkind: object\n---\nRoleplay scene notes.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["daily.md", "roleplay.md"],
            "profiles": ["roleplay"],
            "limit": 8,
        },
    ).json()

    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 1
    assert draft["data"]["items"][0]["path"] == "roleplay.md"
    assert draft["data"]["errors"] == [
        {
            "path": "daily.md",
            "profile": "daily",
            "error": "selected_profile_mismatch",
            "expected_profiles": ["roleplay"],
        }
    ]


def test_obsidian_vault_import_draft_reports_selected_paths_over_limit(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    for name in ("a.md", "b.md", "c.md"):
        (vault / name).write_text(
            f"---\nprofile: daily\nlabel: {name}\nkind: object\n---\n{name}",
            encoding="utf-8",
        )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={
            "vault_path": str(vault),
            "paths": ["a.md", "b.md", "c.md"],
            "limit": 2,
        },
    ).json()

    assert draft["success"] is False
    assert draft["data"]["selected_count"] == 2
    assert [item["path"] for item in draft["data"]["items"]] == ["a.md", "b.md"]
    assert draft["data"]["errors"] == [
        {
            "path": "c.md",
            "profile": "daily",
            "error": "selected_path_over_limit",
            "limit": 2,
        }
    ]


def test_obsidian_vault_scan_and_import_draft_reject_invalid_limit(tmp_path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "daily.md").write_text(
        "---\nprofile: daily\nlabel: Daily desk rule\nkind: object\n---\nKeep the desk clear.",
        encoding="utf-8",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    scan = client.get(
        "/api/l15/obsidian-vault/scan",
        params={"vault_path": str(vault), "limit": "abc"},
    ).json()
    draft = client.post(
        "/api/l15/obsidian-vault/import-draft",
        json={"vault_path": str(vault), "paths": ["daily.md"], "limit": "abc"},
    ).json()

    assert scan["success"] is False
    assert scan["data"]["error"]["error"] == "invalid_limit"
    assert draft["success"] is False
    assert draft["data"]["errors"][0]["error"] == "invalid_limit"


def test_google_calendar_preview_preserves_mapping_fields() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/google/calendar/preview",
        json={
            "events": [
                {
                    "id": "evt_preview",
                    "calendar_id": "primary",
                    "summary": "Calendar preview",
                    "start": {"dateTime": "2026-05-15T10:00:00+08:00", "timeZone": "Asia/Shanghai"},
                    "end": {"dateTime": "2026-05-15T10:30:00+08:00", "timeZone": "Asia/Shanghai"},
                    "location": "Desk",
                    "htmlLink": "https://calendar.google.com/event?eid=test",
                    "etag": "etag-preview",
                    "status": "confirmed",
                    "iCalUID": "ical-preview",
                    "objects": ["blue mug"],
                }
            ]
        },
    ).json()

    assert body["action"] == "google.calendar.preview"
    assert body["success"] is True
    normalized = body["data"]["normalized_events"][0]
    assert normalized["id"] == "evt_preview"
    assert normalized["start_time"] == "2026-05-15T10:00:00+08:00"
    assert normalized["timezone"] == "Asia/Shanghai"
    assert normalized["html_link"].startswith("https://calendar.google.com/")
    observation = body["data"]["observations"][0]
    assert observation["source"] == "google_calendar"
    assert observation["kind"] == "event"
    assert observation["meta"]["calendar_event_id"] == "evt_preview"
    assert observation["meta"]["etag"] == "etag-preview"
    mapping = body["data"]["mapping_rows"][0]
    assert mapping["calendar_event_id"] == "evt_preview"
    assert mapping["l15_bucket"] == "google_calendar"
    assert mapping["l2b_kind"] == "event"
    assert mapping["l2b_action"] == "upsert_event"
    assert mapping["intent_workspace_policy"] == "not_used_for_read_sync"
    assert "operator_required_for_import" in body["data"]


def test_google_calendar_preview_accepts_raw_google_items_payload() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    raw = json.dumps(
        {
            "items": [
                {
                    "id": "evt_raw",
                    "calendar_id": "primary",
                    "summary": "Raw Google item",
                    "start": {
                        "dateTime": "2026-05-15T12:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {
                        "dateTime": "2026-05-15T12:30:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "htmlLink": "https://calendar.google.com/event?eid=raw",
                }
            ]
        }
    )

    body = client.post("/api/google/calendar/preview", json={"raw": raw}).json()

    assert body["success"] is True
    normalized = body["data"]["normalized_events"][0]
    assert normalized["id"] == "evt_raw"
    assert normalized["title"] == "Raw Google item"
    assert normalized["start_time"] == "2026-05-15T12:00:00+08:00"
    assert body["data"]["observations"][0]["meta"]["calendar_event_id"] == "evt_raw"
    assert body["data"]["mapping_rows"][0]["provider_ref"] == "google_calendar:primary:evt_raw"


def test_google_calendar_preview_marks_cancelled_as_historical_tombstone() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post(
        "/api/google/calendar/preview",
        json={
            "events": [
                {
                    "id": "evt_cancelled",
                    "calendar_id": "primary",
                    "summary": "Cancelled sync item",
                    "status": "cancelled",
                    "start": {"dateTime": "2026-05-15T13:00:00+08:00"},
                }
            ]
        },
    ).json()

    assert body["success"] is True
    mapping = body["data"]["mapping_rows"][0]
    observation = body["data"]["observations"][0]
    assert mapping["status"] == "cancelled"
    assert mapping["l2b_action"] == "mark_historical_tombstone"
    assert mapping["policy_note"] == "keep_google_identity_and_set_ghost_state"
    assert observation["confirmation"] == "ghost"
    assert observation["meta"]["is_tombstone"] is True
    assert observation["meta"]["tombstone_policy"] == "historical_event"


def test_google_calendar_fetch_dispatch_is_operator_gated() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.post("/api/google/calendar/fetch", json={}).json()

    assert body["action"] == "google.calendar.fetch.dispatch"
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["operator_mode"] is False
    assert body["data"]["task_type"] == "calendar_fetch"
    assert body["data"]["params"]["result_channel"] == "calendar_result"
    assert body["data"]["would_dispatch"] is True
    assert body["data"]["dispatch_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert "Google Workspace MCP" in body["data"]["result_flow"]
    assert "sk-" not in str(body).lower()


def test_google_calendar_fetch_can_dispatch_in_operator_mode(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    calls: list[dict[str, Any]] = []

    async def fake_do_dispatch_task(
        task_type: str,
        *,
        params: dict[str, Any] | None = None,
        priority: str = "normal",
    ) -> str:
        calls.append({"task_type": task_type, "params": params or {}, "priority": priority})
        return "task_calendar_real"

    dispatch_module = import_module("parrot.brain.tools.dispatch_task")
    monkeypatch.setattr(dispatch_module, "do_dispatch_task", fake_do_dispatch_task)

    body = client.post(
        "/api/google/calendar/fetch",
        json={"dry_run": False, "operator_mode": True, "priority": "normal"},
    ).json()

    assert body["action"] == "google.calendar.fetch.dispatch"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert body["data"]["dispatched"] is True
    assert body["data"]["task_id"] == "task_calendar_real"
    assert calls == [
        {
            "task_type": "calendar_fetch",
            "params": body["data"]["params"],
            "priority": "normal",
        }
    ]


def test_google_calendar_results_reads_scheduler_ledger(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    class FakeRedis:
        async def xrevrange(self, stream: str, count: int = 20):
            assert stream == "parrot.trigger.results.stream"
            assert count >= 6
            return [
                (
                    "1710000000000-0",
                    {
                        "payload": json.dumps(
                            {
                                "task_id": "task_calendar",
                                "type": "calendar_result",
                                "original_type": "calendar_fetch",
                                "status": "completed",
                                "api_key": "sk-should-redact",
                                "result": json.dumps(
                                    [
                                        {
                                            "id": "evt_history",
                                            "summary": "Ledger event",
                                            "start": {"dateTime": "2026-05-15T10:00:00+08:00"},
                                        }
                                    ]
                                ),
                            }
                        ),
                        "result_channel": "calendar_result",
                        "task_id": "task_calendar",
                        "created_at": "1710000000.0",
                    },
                )
            ]

    async def fake_get_redis():
        return FakeRedis()

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get("/api/google/calendar/results", params={"limit": 2}).json()

    assert body["action"] == "google.calendar.results"
    assert body["success"] is True
    assert body["data"]["available"] is True
    row = body["data"]["rows"][0]
    assert row["task_id"] == "task_calendar"
    assert row["result_channel"] == "calendar_result"
    assert row["original_type"] == "calendar_fetch"
    assert row["event_count"] == 1
    assert row["event_sample"][0]["id"] == "evt_history"
    assert row["payload"]["api_key"] == "<redacted>"
    assert "sk-should-redact" not in str(body)


def test_google_calendar_results_tolerates_missing_redis(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    async def fake_get_redis():
        raise RuntimeError("redis offline")

    monkeypatch.setattr("parrot.shared.redis_client.get_redis", fake_get_redis)

    body = client.get("/api/google/calendar/results").json()

    assert body["action"] == "google.calendar.results"
    assert body["success"] is True
    assert body["data"]["available"] is False
    assert body["data"]["rows"] == []


def test_google_calendar_import_routes_are_l15_operator_gated() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    payload = {
        "events": [
            {
                "id": "evt_import",
                "calendar_id": "primary",
                "summary": "Calendar import",
                "start": {"dateTime": "2026-05-15T11:00:00+08:00", "timeZone": "Asia/Shanghai"},
                "end": {"dateTime": "2026-05-15T11:30:00+08:00", "timeZone": "Asia/Shanghai"},
                "htmlLink": "https://calendar.google.com/event?eid=import",
                "etag": "etag-import",
                "status": "confirmed",
                "objects": ["blue mug"],
            }
        ]
    }

    draft = client.post("/api/google/calendar/import-draft", json=payload).json()
    apply_preview = client.post("/api/google/calendar/import", json=payload).json()

    assert draft["action"] == "google.calendar.import_draft"
    assert draft["success"] is True
    assert draft["dry_run"] is True
    assert draft["operator_mode"] is False
    assert draft["data"]["observation_count"] == 1
    assert draft["data"]["observations"][0]["source"] == "google_calendar"
    assert draft["data"]["observations"][0]["meta"]["calendar_event_id"] == "evt_import"
    assert draft["data"]["mapping_rows"][0]["merge_key"] == "primary:evt_import"
    assert "L15Pool.admit" in draft["data"]["write_path"]
    assert apply_preview["action"] == "google.calendar.import"
    assert apply_preview["success"] is True
    assert apply_preview["dry_run"] is True
    assert apply_preview["operator_mode"] is False
    assert apply_preview["data"]["would_apply"] is True
    assert apply_preview["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert "sk-" not in str(draft).lower()
    assert "PARROT_ORCH_SECRET" not in str(draft)


def test_google_calendar_operator_import_preserves_event_time(monkeypatch) -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))
    captured: list[Any] = []

    @dataclass(frozen=True)
    class FakeOutcome:
        rejected: tuple[Any, ...] = ()

    class FakePool:
        async def admit(self, observations):
            captured.extend(observations)
            return FakeOutcome()

    monkeypatch.setattr(
        "parrot.dsg.l1_5.pool.get_l1_5_pool",
        lambda: FakePool(),
    )

    body = client.post(
        "/api/google/calendar/import",
        json={
            "dry_run": False,
            "operator_mode": True,
            "events": [
                {
                    "id": "evt_import_time",
                    "calendar_id": "primary",
                    "summary": "Calendar import keeps time",
                    "start": {
                        "dateTime": "2026-05-15T11:00:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                    "end": {
                        "dateTime": "2026-05-15T11:30:00+08:00",
                        "timeZone": "Asia/Shanghai",
                    },
                }
            ],
        },
    ).json()

    assert body["action"] == "google.calendar.import"
    assert body["success"] is True
    assert body["dry_run"] is False
    assert body["operator_mode"] is True
    assert captured
    observation = captured[0]
    assert observation.meta["calendar_event_id"] == "evt_import_time"
    assert observation.time_span[0] == observation.observed_at
    assert observation.time_span[1] is not None
    assert observation.time_span[1] > observation.time_span[0]


def test_runtime_monitor_route_is_web_only_read_surface() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    body = client.get("/api/runtime/monitor").json()

    assert body["audit"]["read_only"] is True
    assert body["audit"]["web_only"] is True
    assert body["agent_team"]["agent_team_id"] == "catmaid-team-v1"
    assert body["scheduler"]["channels"]["commands"] == "parrot.scheduler.commands"
    assert "research" in body["scheduler"]["nanobot_task_types"]["all"]
    assert body["nanobot"]["dispatch_stream"] == "parrot.nanobot.dispatch"
    assert [stage["stage"] for stage in body["collaboration"]["channel_flow"]] == [
        "scheduler_commands",
        "nanobot_dispatch",
        "nanobot_worker",
        "nanobot_results",
        "brain_return",
    ]
    assert body["collaboration"]["channel_flow"][0]["channel"] == "parrot.scheduler.commands"
    assert "secret" not in str(body).lower()


def test_runtime_flow_typed_models_preserve_route_wire_shape() -> None:
    from parrot.web_console.runtime_flow_models import (
        RuntimeFlowChanges,
        RuntimeFlowEdge,
        RuntimeFlowEvent,
        RuntimeFlowNode,
        RuntimeFlowSnapshot,
        RuntimeHumanGate,
        RuntimeReceipt,
    )

    node = RuntimeFlowNode(
        id="plan:p1",
        lane="plan",
        entity_kind="plan",
        entity_id="p1",
        trace_id="plan:p1",
        label="Plan",
        status="awaiting_user_confirmation",
        summary="1 step",
        payload_ref="ref:p1",
    ).as_json()
    edge = RuntimeFlowEdge(
        id="plan:p1->gate:plan:p1:awaits_human",
        source="plan:p1",
        target="gate:plan:p1",
        kind="awaits_human",
        trace_id="plan:p1",
    ).as_json()
    event = RuntimeFlowEvent(
        sequence=7,
        trace_id="plan:p1",
        span_id="7:plan:p1:awaiting_user_confirmation",
        parent_span_id="",
        entity_kind="plan",
        entity_id="p1",
        op="awaiting_user_confirmation",
        status="awaiting_user_confirmation",
        event_source="web_console.runtime_flow",
        writer="read_model",
        summary="Plan",
        created_at=1.0,
        payload_ref="ref:p1",
    ).as_json()
    gate = RuntimeHumanGate(
        gate_id="plan:p1",
        target_kind="plan",
        target_id="p1",
        trace_id="plan:p1",
        state="pending",
        plan_state="awaiting_user_confirmation",
        prompt="Approve?",
        summary="Plan",
        options=["approve", "approve_and_start"],
        valid_actions_for_state=["approve", "approve_and_start"],
        payload_ref="ref:p1",
    ).as_json()
    audit = {
        "web_only": True,
        "read_model": True,
        "typed_schema": "parrot.web_console.runtime_flow_models",
    }
    snapshot = RuntimeFlowSnapshot(
        sequence=7,
        generated_at=1.0,
        lanes=[{"id": "plan", "label": "Plan"}],
        nodes=[node],
        edges=[edge],
        events=[event],
        pending_human_gates=[gate],
        source_sequences={"live_state": 1},
        audit=audit,
    ).as_json()
    changes = RuntimeFlowChanges(
        since=6,
        sequence=7,
        changed=True,
        events=[event],
        snapshot=snapshot,
        audit=audit,
    ).as_json()
    receipt = RuntimeReceipt(
        action="runtime.hitl.draft_decision",
        success=True,
        dry_run=True,
        operator_mode=False,
        receipt_id="web-test",
        data={"gate_id": "plan:p1"},
        audit={"web_only": True, "core_candidate": "CORE-011"},
    ).as_json()

    assert node["id"] == "plan:p1"
    assert edge["source"] == "plan:p1"
    assert edge["target"] == "gate:plan:p1"
    assert event["source"] == "web_console.runtime_flow"
    assert "event_source" not in event
    assert gate["options"] == gate["valid_actions_for_state"]
    assert snapshot["action"] == "runtime.flow.snapshot"
    assert snapshot["pending_human_gates"][0]["target_kind"] == "plan"
    assert changes["snapshot"]["sequence"] == 7
    assert receipt["core_candidate"] == "CORE-011"


def test_runtime_flow_and_hitl_routes_are_web_only_receipt_surfaces(monkeypatch) -> None:
    import asyncio

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.plan import (
        PlanProposal,
        PlanRegistry,
        PlanStepProposal,
        set_plan_registry_for_test,
    )

    monkeypatch.setenv("PARROT_ORCH_SECRET", "runtime-flow-secret")
    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Runtime HITL test plan",
            suggested_steps=(
                PlanStepProposal(
                    step_id="s1",
                    title="Check messages",
                    expected_tool="message_check",
                ),
                PlanStepProposal(
                    step_id="s2",
                    title="Summarize messages",
                    expected_tool="summarize",
                    depends_on=("s1", "s1"),
                ),
            ),
        )))
        asyncio.run(registry.submit_for_confirmation(plan.plan_id))

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        flow = client.get("/api/runtime/flow").json()
        changes = client.get("/api/runtime/flow/changes?since=0").json()
        no_change = client.get(f"/api/runtime/flow/changes?since={flow['sequence']}").json()
        pending = client.get("/api/runtime/hitl/pending").json()
        draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve"},
        ).json()
        missing_plan_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": "plan:missing", "decision": "approve"},
        ).json()
        unsupported_target_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": "trigger:manual_llm_push", "decision": "approve"},
        ).json()
        dry_apply = client.post(
            "/api/runtime/hitl/apply-decision",
            json={
                "gate_id": f"plan:{plan.plan_id}",
                "decision": "approve_and_start",
                "dry_run": True,
                "operator_mode": False,
            },
        ).json()

        assert flow["success"] is True
        assert flow["audit"]["web_only"] is True
        assert "CORE-010" in flow["audit"]["shared_core_candidates"]
        assert any(lane["id"] == "human_gate" for lane in flow["lanes"])
        assert any(gate["target_id"] == plan.plan_id for gate in flow["pending_human_gates"])
        node_ids = {node["id"] for node in flow["nodes"]}
        edge_ids = [edge["id"] for edge in flow["edges"]]
        assert len(edge_ids) == len(set(edge_ids))
        assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in flow["edges"])
        assert any(node.get("trace_id") == f"plan:{plan.plan_id}" for node in flow["nodes"])
        assert flow["audit"]["typed_schema"] == "parrot.web_console.runtime_flow_models"
        assert changes["changed"] is True
        assert no_change["changed"] is False
        assert no_change["snapshot"] is None
        assert pending["gates"][0]["gate_id"] == f"plan:{plan.plan_id}"
        assert pending["gates"][0]["plan_state"] == "awaiting_user_confirmation"
        assert pending["gates"][0]["options"] == pending["gates"][0]["valid_actions_for_state"]
        assert pending["gates"][0]["operator_required_for_execute"] is True
        assert draft["success"] is True
        assert draft["core_candidate"] == "CORE-011"
        assert draft["data"]["operator_required_for_execute"] is True
        assert missing_plan_draft["success"] is False
        assert missing_plan_draft["data"]["error"] == "plan_not_found"
        assert unsupported_target_draft["success"] is False
        assert unsupported_target_draft["data"]["error"] == "unsupported_hitl_target"
        assert unsupported_target_draft["data"]["target_kind"] == "trigger"
        assert unsupported_target_draft["data"]["valid_actions"] == []
        assert unsupported_target_draft["data"]["valid_actions_for_state"] == []
        assert unsupported_target_draft["data"]["valid_target_kinds"] == ["plan"]
        assert dry_apply["data"]["would_apply"] is True
        assert dry_apply["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
        assert "runtime-flow-secret" not in str(flow) + str(changes) + str(pending)
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_memory_live_state_changes_uses_stable_web_sequence(monkeypatch) -> None:
    import parrot.brain.app_live_state as app_live_state_module
    import parrot.dsg.l2b_graph as l2b_graph_module
    import parrot.web_console.memory_live_state as memory_live_state_module
    from parrot.dsg.l2b_graph import L2BGraph
    from parrot.dsg.l2b_types import NodeKind, SemanticNode

    graph = L2BGraph()
    l2b_graph_module._instance = graph
    app_live_state_module._sequence = 0
    monkeypatch.setattr(memory_live_state_module, "_memory_sequence", 0)
    monkeypatch.setattr(memory_live_state_module, "_memory_signature", "")

    try:
        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        first = client.get("/api/memory/live-state/changes", params={"since": 0}).json()
        second = client.get(
            "/api/memory/live-state/changes",
            params={"since": first["sequence"]},
        ).json()

        graph.upsert_node(SemanticNode(
            uuid="memory_change_node",
            kind=NodeKind.OBJECT,
            label="Memory changed",
        ))
        third = client.get(
            "/api/memory/live-state/changes",
            params={"since": first["sequence"]},
        ).json()

        assert first["action"] == "memory.live_state.changes"
        assert first["changed"] is True
        assert first["snapshot"]["l2b"]["node_count"] == 0
        assert first["audit"]["web_only"] is True
        assert first["audit"]["app_dto_pollution"] is False
        assert second["sequence"] == first["sequence"]
        assert second["changed"] is False
        assert second["snapshot"] is None
        assert third["sequence"] > first["sequence"]
        assert third["changed"] is True
        assert third["snapshot"]["l2b"]["node_count"] == 1
        assert any(event["entity_kind"] == "l2b_node" for event in third["events"])
    finally:
        l2b_graph_module._instance = None
        app_live_state_module._sequence = 0
        memory_live_state_module._memory_sequence = 0
        memory_live_state_module._memory_signature = ""


def test_runtime_hitl_draft_validates_plan_state() -> None:
    import asyncio

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.plan import (
        PlanProposal,
        PlanRegistry,
        PlanStepProposal,
        set_plan_registry_for_test,
    )

    set_intent_workspace_for_test(IntentWorkspace())
    registry = PlanRegistry(dispatch_task=_fake_plan_dispatch)
    set_plan_registry_for_test(registry)
    try:
        plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Approved plan",
            suggested_steps=(PlanStepProposal(
                step_id="s1",
                title="Check messages",
                expected_tool="message_check",
            ),),
        )))
        asyncio.run(registry.submit_for_confirmation(plan.plan_id))
        asyncio.run(registry.approve(plan.plan_id))

        empty_plan = asyncio.run(registry.draft(PlanProposal(
            proposed_by="test",
            title="Empty complete plan",
            suggested_steps=(),
        )))
        asyncio.run(registry.submit_for_confirmation(empty_plan.plan_id))
        asyncio.run(registry.approve(empty_plan.plan_id))
        asyncio.run(registry.start_executing(empty_plan.plan_id))

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        stale_approve = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve"},
        ).json()
        start_draft = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{plan.plan_id}", "decision": "approve_and_start"},
        ).json()
        completed_cancel = client.post(
            "/api/runtime/hitl/draft-decision",
            json={"gate_id": f"plan:{empty_plan.plan_id}", "decision": "cancel"},
        ).json()

        assert stale_approve["success"] is False
        assert stale_approve["data"]["error"] == "invalid_plan_state"
        assert stale_approve["data"]["plan_state"] == "approved"
        assert "approve_and_start" in stale_approve["data"]["valid_actions_for_state"]
        assert start_draft["success"] is True
        assert completed_cancel["success"] is False
        assert completed_cancel["data"]["error"] == "invalid_plan_state"
        assert completed_cancel["data"]["plan_state"] == "complete"
    finally:
        set_plan_registry_for_test(None)
        set_intent_workspace_for_test(None)


def test_blackboard_activity_route_returns_bounded_summaries() -> None:
    import py_trees

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    py_trees.blackboard.Blackboard.activity_stream = None
    try:
        py_trees.blackboard.Blackboard.enable_activity_stream()
        bb = py_trees.blackboard.Client(name="web_activity_test")
        bb.register_key(key="global/web_activity_test", access=py_trees.common.Access.WRITE)
        bb.set("global/web_activity_test", {"status": "ok", "secret": "summary-only"})

        client = TestClient(build_app(status_fetcher=_fake_fetcher))
        body = client.get("/api/memory/blackboard/activity?limit=5").json()

        assert body["success"] is True
        assert body["action"] == "blackboard.activity"
        assert body["audit"]["web_only"] is True
        assert body["audit"]["values"] == "summaries_only"
        assert body["data"]["limit"] == 5
        assert body["data"]["activities"]
        row = body["data"]["activities"][-1]
        assert row["key"] == "global/web_activity_test"
        assert row["scope"] == "global"
        assert row["client_name"] == "web_activity_test"
        assert row["current_summary"].startswith("dict(")
        assert "summary-only" not in str(body)
        assert "secret" not in str(body).lower()
    finally:
        py_trees.blackboard.Blackboard.storage = {}
        py_trees.blackboard.Blackboard.metadata = {}
        py_trees.blackboard.Blackboard.activity_stream = None


def test_runtime_monitor_plan_rows_include_dag_edges() -> None:
    from parrot.web_console.runtime_monitor import _plan_row

    plan = SimpleNamespace(
        plan_id="plan_a",
        title="Test Plan",
        state="executing",
        intent_event_id="intent_a",
        episode_id="episode_a",
        related_node_uuids=("node_a",),
        related_staged_ref_ids=("ref_a",),
        staged_ref_id="plan_ref",
        blackboard_namespace="plan/plan_a",
        blocks_conversation=False,
        drafted_at=10.0,
        approved_at=11.0,
        started_executing_at=12.0,
        completed_at=0.0,
        supersedes="",
        superseded_by="",
        steps=[
            SimpleNamespace(
                step_id="step_a",
                title="Fetch mail",
                description="",
                expected_tool="message_check",
                state="done",
                depends_on=(),
                nanobot_task_id="task_a",
                started_at=12.0,
                completed_at=13.0,
                result_summary="ok",
                result_ref_id="result_a",
                error="",
            ),
            SimpleNamespace(
                step_id="step_b",
                title="Summarize",
                description="",
                expected_tool="summarize",
                state="pending",
                depends_on=("step_a",),
                nanobot_task_id="",
                started_at=0.0,
                completed_at=0.0,
                result_summary="",
                result_ref_id="",
                error="",
            ),
        ],
    )

    row = _plan_row(plan)

    assert row["related_node_uuids"] == ["node_a"]
    assert row["steps"][1]["depends_on"] == ["step_a"]
    assert row["steps"][0]["result_ref_id"] == "result_a"
    assert row["dag"]["edges"] == [
        {"source": "step_a", "target": "step_b", "kind": "depends_on"}
    ]
    assert row["dag"]["ready_step_ids"] == ["step_b"]
    assert row["dag"]["blocked_step_ids"] == []
    assert row["dag"]["critical_step_ids"] == ["step_a", "step_b"]


def test_dsg_trigger_management_routes_are_dry_run_and_secret_safe(monkeypatch) -> None:
    monkeypatch.setenv("PARROT_ORCH_SECRET", "route-secret")
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    catalog = client.get("/api/dsg/triggers/catalog").json()
    draft = client.post(
        "/api/dsg/triggers/draft-event",
        json={
            "trigger_name": "message_notification",
            "event": {"type": "message_push", "subject": "hello"},
        },
    ).json()
    dry_fire = client.post(
        "/api/dsg/triggers/fire-event",
        json={
            "trigger_name": "message_notification",
            "event": {"type": "message_push", "subject": "hello"},
            "dry_run": True,
            "operator_mode": False,
        },
    ).json()
    on_demand_draft = client.post(
        "/api/dsg/triggers/draft-event",
        json={"event": {"kind": "scene_switch", "new_scene_type": "desktop_webcam"}},
    ).json()

    assert catalog["success"] is True
    assert "message_notification" in {item["name"] for item in catalog["triggers"]}
    assert draft["dry_run"] is True
    assert draft["data"]["matched_triggers"] == ["message_notification"]
    assert dry_fire["data"]["would_publish"] is True
    assert dry_fire["data"]["publish_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert on_demand_draft["data"]["matched_triggers"] == ["scene_switch"]
    assert "route-secret" not in str(catalog) + str(draft) + str(dry_fire)


def test_l15_pool_route_and_operator_drafts_are_exposed() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    pool = client.get("/api/l15/pool").json()
    bucket_draft = client.post(
        "/api/l15/bucket-op/draft",
        json={"op": "freeze", "kind": "main"},
    ).json()
    bucket_apply_dry_run = client.post(
        "/api/l15/bucket-op",
        json={"op": "clear", "kind": "main", "dry_run": True, "operator_mode": False},
    ).json()
    daily_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={
            "profile": "daily",
            "label": "UUID free setting",
            "description": "No Obsidian UUID is required for daily settings.",
        },
    ).json()
    ref_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={"profile": "ref", "label": "Missing UUID ref"},
    ).json()
    blank_label_obsidian = client.post(
        "/api/l15/obsidian-node/draft",
        json={"profile": "daily", "label": "   "},
    ).json()

    assert pool["success"] is True
    assert "main" in {item["kind"] for item in pool["buckets"]}
    assert pool["audit"]["web_only"] is True
    assert bucket_draft["data"]["bucket_op"]["op"] == "freeze"
    assert bucket_apply_dry_run["action"] == "l15.bucket_op.apply"
    assert bucket_apply_dry_run["data"]["would_apply"] is True
    assert bucket_apply_dry_run["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert daily_obsidian["success"] is True
    assert daily_obsidian["data"]["uuid_free_allowed"] is True
    blank_payload = blank_label_obsidian["data"]["event"]["payload"]
    assert blank_payload["label"] == "Web Console setting"
    assert blank_payload["obsidian_note_key"] == "web-console/daily/Web Console setting"
    assert ref_obsidian["success"] is False
    assert ref_obsidian["data"]["error"] == "ref_profile_requires_obsidian_uuid"


def test_l2b_node_and_edge_routes_stay_dry_run_by_default() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    node = client.post(
        "/api/l2b/node",
        json={"label": "Web Test Node", "kind": "object", "description": "draft only"},
    ).json()
    update = client.post(
        "/api/l2b/node",
        json={
            "node_uuid": "node_a",
            "label": "Updated Web Test Node",
            "kind": "object",
            "description": "update draft only",
        },
    ).json()
    delete = client.post("/api/l2b/node/delete", json={"node_uuid": "node_a"}).json()
    edge = client.post(
        "/api/l2b/edge",
        json={
            "from_uuid": "node_a",
            "to_uuid": "node_b",
            "kind": "associated_with",
            "strength": 0.7,
            "meta": {"tag": "web_test"},
        },
    ).json()
    edge_update = client.post(
        "/api/l2b/edge/update",
        json={
            "from_uuid": "node_a",
            "to_uuid": "node_b",
            "kind": "reminds_of",
            "match_kind": "associated_with",
            "strength": 0.9,
            "meta": {"reason": "operator_preview"},
        },
    ).json()
    edge_delete = client.post(
        "/api/l2b/edge/delete",
        json={"from_uuid": "node_a", "to_uuid": "node_b", "match_kind": "associated_with"},
    ).json()
    self_edge = client.post(
        "/api/l2b/edge/draft",
        json={"from_uuid": "node_a", "to_uuid": "node_a", "kind": "associated_with"},
    ).json()

    assert node["success"] is True
    assert node["dry_run"] is True
    assert node["data"]["would_apply"] is True
    assert node["data"]["write_path"] == "L15Pool.admit(Observation(source=USER_EXPLICIT))"
    assert update["data"]["would_apply"] is True
    assert update["data"]["observation"]["meta"]["target_node_uuid"] == "node_a"
    assert delete["data"]["would_evict"] is True
    assert edge["data"]["would_apply"] is True
    assert edge["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert edge["data"]["operator_required_for_execute"] is True
    assert edge["data"]["edge"]["kind"] == "associated_with"
    assert edge["data"]["edge"]["strength"] == 0.7
    assert edge["data"]["edge"]["meta"]["tag"] == "web_test"
    assert edge_update["data"]["would_apply"] is True
    assert edge_update["data"]["edge"]["kind"] == "reminds_of"
    assert edge_update["data"]["match_kind"] == "associated_with"
    assert edge_delete["data"]["would_delete"] is True
    assert edge_delete["data"]["match_kind"] == "associated_with"
    assert self_edge["success"] is False
    assert self_edge["data"]["error"] == "self_edge_not_allowed"


def test_google_message_routes_use_nanobot_and_trigger_drafts() -> None:
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    check = client.post("/api/google/messages/check", json={}).json()
    push = client.post(
        "/api/google/messages/push-test",
        json={"subject": "mail test", "dry_run": True},
    ).json()

    assert check["action"] == "google.message_check.dispatch"
    assert check["data"]["task_type"] == "message_check"
    assert check["data"]["would_dispatch"] is True
    assert push["action"] == "dsg.trigger.fire_event"
    assert push["data"]["event"]["type"] == "message_push"
    assert push["data"]["would_publish"] is True


def test_ref_binding_draft_is_core_candidate_and_draft_only() -> None:
    from parrot.brain import refs as refs_registry

    refs_registry.reset_refs_for_tests()
    try:
        ref = refs_registry.bind_focus(
            focus_id="focus-web-ref",
            source_event_id="evt-web-ref",
            label="Focus web ref",
        )
        client = TestClient(build_app(status_fetcher=_fake_fetcher))

        draft = client.post(
            "/api/refs/binding/draft",
            json={
                "ref_id": ref.ref_id,
                "target_kind": "l2b_node",
                "target_id": "node-web-ref",
                "dry_run": True,
                "operator_mode": False,
            },
        ).json()
        missing = client.post(
            "/api/refs/binding/draft",
            json={"ref_id": ref.ref_id, "target_kind": "l2b_node"},
        ).json()
        unresolved = client.post(
            "/api/refs/binding/draft",
            json={"ref_id": ref.ref_id, "target_kind": "unresolved"},
        ).json()

        assert draft["action"] == "refs.binding.draft"
        assert draft["success"] is True
        assert draft["data"]["core_candidate"] == "CORE-006"
        assert draft["data"]["apply_route"] == ""
        assert draft["data"]["current_ref"]["ref_id"] == ref.ref_id
        assert draft["data"]["draft_target"] == {
            "target_kind": "l2b_node",
            "target_id": "node-web-ref",
        }
        assert "Unity/App DTOs" in draft["data"]["policy"]
        assert missing["success"] is False
        assert missing["data"]["error"] == "missing_target_id"
        assert unresolved["success"] is True
        assert unresolved["data"]["operation"] == "unresolve_ref"
        assert unresolved["data"]["would_resolve"] is False
        assert unresolved["data"]["would_unresolve"] is True
        assert unresolved["data"]["draft_target"] == {
            "target_kind": "unresolved",
            "target_id": "",
        }
    finally:
        refs_registry.reset_refs_for_tests()


def test_photo_asset_route_serves_only_cache_root(monkeypatch, tmp_path) -> None:
    day = "2026-05-15"
    photo_id = "web_photo_asset"
    photo_dir = tmp_path / day
    photo_dir.mkdir()
    photo_bytes = b"\xff\xd8web-console-photo\xff\xd9"
    (photo_dir / f"{photo_id}.jpg").write_bytes(photo_bytes)
    monkeypatch.setenv("PARROT_PHOTO_CACHE_ROOT", str(tmp_path))

    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    direct = client.get(f"/api/photos/asset/{day}/{photo_id}")
    with_extension = client.get(f"/api/photos/asset/{day}/{photo_id}.jpg")
    missing = client.get(f"/api/photos/asset/{day}/missing_photo")
    bad_day = client.get(f"/api/photos/asset/not-a-day/{photo_id}")
    bad_id = client.get(f"/api/photos/asset/{day}/bad..photo")

    assert direct.status_code == 200
    assert direct.content == photo_bytes
    assert direct.headers["content-type"].startswith("image/jpeg")
    assert direct.headers["Cache-Control"] == "no-store"
    assert with_extension.status_code == 200
    assert with_extension.content == photo_bytes
    assert missing.status_code == 404
    assert bad_day.status_code == 400
    assert bad_id.status_code == 400


def test_status_summary_marks_degraded_for_offline_process() -> None:
    summary = _status_summary(
        {
            "schema_version": 1,
            "host": "host-a",
            "processes": [
                {"module_id": "brain", "online": True},
                {"module_id": "nanobot-worker", "online": False},
            ],
            "warnings": [],
            "selection_drift": {"is_drift": False},
            "containers": [],
        }
    )

    assert summary["state"] == "degraded"
    assert summary["online_processes"] == 1
    assert summary["offline_processes"] == 1


def test_vision_evidence_routes_are_secret_safe_and_record_timeline(tmp_path, monkeypatch) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import reset_frame_cache_for_tests

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests()
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    status = client.get("/api/vision/evidence/status").json()
    request = client.post(
        "/api/vision/evidence/request",
        json={"description": "what is in the highlighted region", "target_time_ms": 1},
    ).json()
    attention = client.post(
        "/api/app/test/visual-attention",
        json={
            "kind": "bbox",
            "subject_id": "bb_test_web",
            "label": "test bbox",
            "dispatch_harness": False,
            "timebase": {
                "clock_domain": "web",
                "wall_time_ms": 1_700_000_000_000,
                "source_id": "pytest",
            },
        },
    ).json()
    timeline = client.get("/api/vision/evidence/timeline?kind=bbox_focus").json()
    detail = client.get(
        f"/api/vision/evidence/{attention['evidence']['evidence_id']}"
    ).json()

    assert status["action"] == "vision.evidence.status"
    assert status["livekit_sampler"]["message"] == "status_file_missing"
    assert request["action"] == "vision.evidence.request"
    assert request["message"] == "evidence_request_recorded"
    assert attention["action"] == "app.test.visual_attention"
    assert attention["evidence"]["kind"] == "bbox_focus"
    assert timeline["items"][0]["evidence_id"] == attention["evidence"]["evidence_id"]
    assert detail["success"] is True


def test_vision_frame_cache_upload_records_video_frame(tmp_path) -> None:
    from parrot.brain.vision.evidence import get_evidence_ledger
    from parrot.brain.vision.frame_cache import reset_frame_cache_for_tests

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    dry = client.post(
        "/api/vision/evidence/frame-cache/upload",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
            "mime_type": "image/png",
            "track_sid": "track-web-test",
        },
    ).json()
    applied = client.post(
        "/api/vision/evidence/frame-cache/upload",
        json={
            "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
            "mime_type": "image/png",
            "room_id": "parrot-test",
            "track_sid": "track-web-test",
            "source_id": "track-web-test",
            "wall_time_ms": 1_700_000_020_000,
            "media_time_us": 55_000,
            "sequence": 3,
            "dry_run": False,
            "operator_mode": True,
        },
    ).json()
    request = client.post(
        "/api/vision/evidence/request",
        json={"target_time_ms": 1_700_000_020_001, "require_asset": True},
    ).json()
    timeline = client.get("/api/vision/evidence/timeline?kind=video_frame").json()

    assert dry["success"] is True
    assert dry["data"]["apply_skipped_reason"] == "dry_run_or_operator_mode_missing"
    assert applied["action"] == "vision.evidence.frame_cache.upload"
    assert applied["success"] is True
    assert applied["evidence"]["kind"] == "video_frame"
    assert applied["evidence"]["asset_exists"] is True
    assert applied["frame_cache"]["frame_count"] == 1
    assert request["message"] == "nearest_evidence_found"
    assert request["evidence"]["evidence_id"] == applied["evidence"]["evidence_id"]
    assert timeline["items"][0]["evidence_id"] == applied["evidence"]["evidence_id"]
    assert "sk-" not in str(applied).lower()


def test_vision_evidence_stage_hint_writes_intent_workspace_notice(tmp_path, monkeypatch) -> None:
    import py_trees

    from parrot.brain.intent_workspace import IntentWorkspace, set_intent_workspace_for_test
    from parrot.brain.vision.evidence import (
        ClockDomain,
        EvidenceKind,
        EvidenceStatus,
        TimebaseStamp,
        get_evidence_ledger,
    )

    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "missing-sampler-status.json"),
    )
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    sample = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(clock_domain=ClockDomain.WEB, wall_time_ms=1_700_000_020_000),
        description="staged red mug",
    )
    client = TestClient(build_app(status_fetcher=_fake_fetcher))

    try:
        staged = client.post(
            "/api/vision/evidence/stage-hint",
            json={"evidence_id": sample.evidence_id, "description": "staged red mug"},
        ).json()
        status = client.get("/api/vision/evidence/status").json()

        assert staged["action"] == "vision.evidence.stage_hint"
        assert staged["success"] is True
        assert staged["decision"]["staged_ref_id"]
        assert status["evidence_awareness"]["staged_ref_id"] == staged["decision"]["staged_ref_id"]
        assert "sk-" not in str(staged).lower()
    finally:
        set_intent_workspace_for_test(None)


async def _fake_fetcher(config: OrchestratorProxyConfig) -> dict[str, Any]:
    return {
        "ok": False,
        "state": "offline",
        "upstream": {
            "url": config.status_url,
            "status_code": None,
            "auth_mode": config.auth_mode,
            "fetched_at": 1.0,
        },
        "summary": {},
        "status": None,
        "detail": {"message": "fake"},
    }


async def _fake_plan_dispatch(task_type: str, params: dict, priority: str) -> str:
    return f"task-{task_type}-{params.get('step_id', 'step')}-{priority}"


class _FakeSnapshot:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def as_json(self) -> dict[str, Any]:
        return self._payload


class _FakeStatus:
    def as_json(self) -> dict[str, Any]:
        return {
            "module_id": "voice_pipeline",
            "state": "ready",
            "summary": "fake",
            "metrics": {},
            "refs": {},
        }


class _FakeActionResult:
    def as_json(self) -> dict[str, Any]:
        return {"status": "ok", "workspace_id": "workdesk"}


class _FakeAppFacade:
    def canvas_snapshot(self) -> _FakeSnapshot:
        return _FakeSnapshot(
            {
                "active_workspace_id": "workdesk",
                "module_statuses": [_FakeStatus().as_json()],
                "workspaces": [{"workspace_id": "workdesk", "display_name": "Workdesk"}],
                "paper_notes": [],
                "photo_refs": [],
                "tool_cabinet": [],
            }
        )

    def list_module_statuses(self) -> list[_FakeStatus]:
        return [_FakeStatus()]

    def list_line_profiles(self) -> list[dict[str, Any]]:
        return [{"line_profile_id": "lineb_google_default"}]

    def apply_line_profile(self, draft_or_id: dict[str, Any] | str) -> dict[str, Any]:
        return {"line_profile": draft_or_id}

    def apply_workspace(self, workspace_id: str) -> _FakeActionResult:
        return _FakeActionResult()

    def set_lineb_audio_route_policy(self, **kwargs: Any) -> dict[str, Any]:
        return kwargs

    def register_lineb_tts_segment(self, **kwargs: Any) -> dict[str, Any]:
        return {"segment_id": "seg_fake", **kwargs}

    def classify_lineb_mic_input(self, **kwargs: Any) -> dict[str, Any]:
        return {"turn_decision": "user_turn", **kwargs}
