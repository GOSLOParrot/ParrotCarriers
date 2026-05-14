from __future__ import annotations

from pathlib import Path


def test_castle_livekit_server_key_matches_token_mint_default() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "livekit" / "livekit.yaml").read_text(encoding="utf-8")

    assert "devkey: secret" not in text
    assert "devkey: parrot_carriers_local_dev_livekit_secret_key_v1" in text
