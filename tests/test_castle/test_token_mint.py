from __future__ import annotations

import importlib
from pathlib import Path

import jwt
from fastapi.testclient import TestClient


def _reload_token_mint(
    monkeypatch,
    *,
    mode: str = "unity",
    agent_name: str = "",
    active_dispatch: str = "1",
    internal_url: str | None = None,
):
    monkeypatch.setenv("LIVEKIT_URL", "ws://example.test:7880")
    if internal_url is None:
        monkeypatch.delenv("PARROT_MINT_LIVEKIT_INTERNAL_URL", raising=False)
        monkeypatch.delenv("LIVEKIT_INTERNAL_URL", raising=False)
    else:
        monkeypatch.setenv("PARROT_MINT_LIVEKIT_INTERNAL_URL", internal_url)
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey")
    monkeypatch.setenv(
        "LIVEKIT_API_SECRET",
        "parrot_test_livekit_secret_at_least_32_bytes",
    )
    monkeypatch.delenv("PARROT_MINT_SECRET", raising=False)
    monkeypatch.setenv("PARROT_MINT_AGENT_DISPATCH", mode)
    monkeypatch.setenv("PARROT_MINT_ACTIVE_AGENT_DISPATCH", active_dispatch)
    monkeypatch.setenv("PARROT_MINT_AGENT_NAME", agent_name)

    import parrot.castle.token_mint as token_mint

    return importlib.reload(token_mint)


def _claims(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False})


def test_unity_mint_token_requests_unnamed_brain_dispatch(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch)

    token = token_mint._generate_token("parrot-main", "unity-app")
    claims = _claims(token)

    assert claims["video"]["room"] == "parrot-main"
    assert claims["video"]["roomJoin"] is True
    assert claims["roomConfig"]["agents"] == [{}]


def test_non_unity_mint_token_does_not_dispatch_by_default(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch)

    token = token_mint._generate_token("parrot-main", "observer")
    claims = _claims(token)

    assert claims["video"]["room"] == "parrot-main"
    assert "roomConfig" not in claims


def test_mint_agent_dispatch_can_be_disabled(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch, mode="off")

    token = token_mint._generate_token("parrot-main", "unity-app")
    claims = _claims(token)

    assert "roomConfig" not in claims


def test_livekit_internal_url_is_used_only_for_server_api(monkeypatch) -> None:
    token_mint = _reload_token_mint(
        monkeypatch,
        internal_url="ws://livekit:7880",
    )

    assert token_mint._LIVEKIT_URL == "ws://example.test:7880"
    assert token_mint._livekit_http_url() == "http://livekit:7880"


def test_mint_endpoint_actively_dispatches_for_unity_identity(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch)
    calls: list[str] = []

    async def fake_ensure_agent_dispatch(room: str) -> dict:
        calls.append(room)
        return {
            "attempted": True,
            "created": True,
            "already_present": False,
            "error": "",
        }

    monkeypatch.setattr(
        token_mint,
        "_ensure_agent_dispatch",
        fake_ensure_agent_dispatch,
    )

    response = TestClient(token_mint.app).post(
        "/mint",
        json={"room": "parrot-main", "identity": "unity-phone"},
    )

    assert response.status_code == 200
    assert calls == ["parrot-main"]
    body = response.json()
    assert body["agent_dispatch_requested"] is True
    assert body["agent_dispatch_active_attempted"] is True
    assert body["agent_dispatch_active_created"] is True
    assert body["agent_dispatch_active_already_present"] is False
    assert body["agent_dispatch_active_error"] == ""
    assert "roomConfig" not in _claims(body["token"])


def test_mint_endpoint_skips_active_dispatch_for_observer(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch)
    calls: list[str] = []

    async def fake_ensure_agent_dispatch(room: str) -> dict:
        calls.append(room)
        return {
            "attempted": True,
            "created": True,
            "already_present": False,
            "error": "",
        }

    monkeypatch.setattr(
        token_mint,
        "_ensure_agent_dispatch",
        fake_ensure_agent_dispatch,
    )

    response = TestClient(token_mint.app).post(
        "/mint",
        json={"room": "parrot-main", "identity": "observer"},
    )

    assert response.status_code == 200
    assert calls == []
    body = response.json()
    assert body["agent_dispatch_requested"] is False
    assert body["agent_dispatch_active_attempted"] is False


def test_mint_endpoint_can_disable_active_dispatch(monkeypatch) -> None:
    token_mint = _reload_token_mint(monkeypatch, active_dispatch="off")
    calls: list[str] = []

    async def fake_ensure_agent_dispatch(room: str) -> dict:
        calls.append(room)
        return {
            "attempted": True,
            "created": True,
            "already_present": False,
            "error": "",
        }

    monkeypatch.setattr(
        token_mint,
        "_ensure_agent_dispatch",
        fake_ensure_agent_dispatch,
    )

    response = TestClient(token_mint.app).post(
        "/mint",
        json={"room": "parrot-main", "identity": "unity-phone"},
    )

    assert response.status_code == 200
    assert calls == []
    body = response.json()
    assert body["agent_dispatch_requested"] is True
    assert body["agent_dispatch_active_attempted"] is False
    assert _claims(body["token"])["roomConfig"]["agents"] == [{}]


def test_active_dispatch_path_reuses_existing_room_dispatch() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "src" / "parrot" / "castle" / "token_mint.py").read_text(
        encoding="utf-8"
    )

    assert "lk.agent_dispatch.list_dispatch(room)" in text
    assert "Brain dispatch already present" in text
    assert "JRP_NEVER" in text
