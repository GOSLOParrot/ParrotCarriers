from __future__ import annotations

from pathlib import Path


def test_castle_livekit_server_key_matches_token_mint_default() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "livekit" / "livekit.yaml").read_text(encoding="utf-8")

    assert "devkey: secret" not in text
    assert "devkey: parrot_carriers_local_dev_livekit_secret_key_v1" in text


def test_laptop_livekit_template_is_lan_node_configured() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (
        root / "infra" / "livekit" / "livekit-laptop.template.yaml"
    ).read_text(encoding="utf-8")

    assert "node_ip: __PARROT_LAPTOP_HOST__" in text
    assert "use_external_ip: false" in text
    assert "port_range_start: 51000" in text
    assert "port_range_end: 51200" in text


def test_laptop_compose_does_not_use_ecs_env_or_shared_data() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "docker-compose.laptop.yml").read_text(
        encoding="utf-8"
    )

    assert "../.env" not in text
    assert "./laptop.env.local" in text
    assert "../data:/app/data" not in text
    assert "../codex_workspace/local_runtime/castle_laptop/data:/app/data" in text
    assert "17880:7880" in text
    assert "18790:8790" in text
    assert "python -m parrot.brain.agent dev --no-reload" in text
    assert "PARROT_MINT_AGENT_NAME=parrot-brain" in text
    assert "PARROT_BRAIN_AGENT_NAME=parrot-brain" in text
    assert "PARROT_PRESETS_DIR=/app/data/presets" in text
    assert "PARROT_LINE_PROFILES_DIR=/app/data/line_profiles" in text


def test_laptop_init_rewrites_seed_room_profiles_to_local_room() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "laptop-castle.ps1").read_text(encoding="utf-8")

    assert "function Update-LocalRoomProfiles" in text
    assert "metadata.livekit_room_id" in text
    assert "Update-LocalRoomProfiles -RoomId $envMap[\"LIVEKIT_ROOM\"]" in text


def test_unity_config_switcher_is_gitignored_and_secret_safe() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "switch-unity-app-config.ps1").read_text(
        encoding="utf-8"
    )
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "Resources\\parrot_config.json" in text
    assert "parrot_config.laptop.generated.json" in text
    assert "parrot_config.ecs.local.json" in text
    assert "hasMintSecret" in text
    assert "hasOrchestratorSecret" in text
    assert "Copy-Item -LiteralPath $LaptopConfig -Destination $ActiveConfig" in text
    assert "/codex_workspace/local_runtime/" in gitignore
    assert "mintSecret =" not in text
    assert "orchestratorSecret =" not in text


def test_brain_dockerfile_does_not_downgrade_livekit_agents() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "infra" / "Dockerfile.brain").read_text(encoding="utf-8")

    assert "livekit-agents>=0.10,<1.0" not in text
    assert "livekit-plugins-google>=0.6,<1.0" not in text
    assert '-e ".[memory,line_b,line_b_cartesia]"' in text


def test_brain_runtime_dependencies_include_image_helpers() -> None:
    root = Path(__file__).resolve().parents[2]
    text = (root / "pyproject.toml").read_text(encoding="utf-8").lower()

    assert '"pillow>=10.0,<12.0"' in text
