from __future__ import annotations

import importlib

import jwt


def _reload_token_mint(monkeypatch, *, mode: str = "unity", agent_name: str = ""):
    monkeypatch.setenv("LIVEKIT_URL", "ws://example.test:7880")
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey")
    monkeypatch.setenv(
        "LIVEKIT_API_SECRET",
        "parrot_test_livekit_secret_at_least_32_bytes",
    )
    monkeypatch.setenv("PARROT_MINT_AGENT_DISPATCH", mode)
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

