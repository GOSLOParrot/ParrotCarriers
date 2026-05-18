"""Sanitized Web Console environment profile helpers.

The browser should know which lab it is talking to, but it must not receive
bearer secrets, token mint secrets, or raw OAuth credentials.
"""

from __future__ import annotations

import os
from typing import Any


def build_console_environment(
    *,
    service_name: str,
    orchestrator_base_url: str = "",
    orchestrator_auth_mode: str = "",
) -> dict[str, Any]:
    """Return a browser-safe snapshot of the active Console target profile."""

    profile = _profile_name()
    laptop_host = _env("PARROT_LAPTOP_HOST") or "127.0.0.1"
    ecs_host = _env("PARROT_ECS_HOST") or "8.216.45.45"

    active = {
        "profile": profile,
        "api_path": "/api",
        "api_origin": "same-origin",
        "dev_proxy_target": _clean_url(
            _env("PARROT_WEB_CONSOLE_API_TARGET")
            or _env("VITE_PARROT_WEB_CONSOLE_API_TARGET")
        ),
        "app_api_base_url": _clean_url(
            _env("PARROT_WEB_CONSOLE_APP_API_URL")
            or _env("PARROT_WEB_CONSOLE_L2B_URL")
            or _env("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        ),
        "graphiti_proxy_url": _clean_url(
            _env("PARROT_WEB_CONSOLE_GRAPHITI_URL")
            or _env("PARROT_WEB_CONSOLE_L2B_URL")
        ),
        "orchestrator_base_url": _clean_url(orchestrator_base_url),
        "orchestrator_auth_mode": orchestrator_auth_mode,
        "livekit_url": _env("LIVEKIT_URL"),
        "room": _env("LIVEKIT_ROOM"),
        "runtime_data_root": _env("PARROT_RUNTIME_DATA_ROOT") or _env("PARROT_DATA_ROOT"),
        "restart_control": _restart_control(profile),
    }

    return {
        "schema_version": 1,
        "service": service_name,
        "profile": profile,
        "active": active,
        "profiles": [
            {
                "id": "ecs",
                "label": "public ECS",
                "app_api_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_ECS_APP_API_URL")
                    or f"http://{ecs_host}:8790"
                ),
                "orchestrator_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_ECS_ORCH_URL")
                    or f"http://{ecs_host}:7890"
                ),
                "token_mint_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_ECS_TOKEN_MINT_URL")
                    or f"http://{ecs_host}:7888"
                ),
                "livekit_url": _env("PARROT_WEB_CONSOLE_ECS_LIVEKIT_URL")
                or f"ws://{ecs_host}:7880",
                "room": _env("PARROT_WEB_CONSOLE_ECS_ROOM") or "parrot-main",
                "runtime_scope": "ecs:/opt/parrot/ParrotCarriers",
            },
            {
                "id": "laptop",
                "label": "laptop Castle",
                "app_api_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_LAPTOP_APP_API_URL")
                    or f"http://{laptop_host}:18790"
                ),
                "orchestrator_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_LAPTOP_ORCH_URL")
                    or f"http://{laptop_host}:17890"
                ),
                "token_mint_base_url": _clean_url(
                    _env("PARROT_WEB_CONSOLE_LAPTOP_TOKEN_MINT_URL")
                    or f"http://{laptop_host}:17888"
                ),
                "livekit_url": _env("PARROT_WEB_CONSOLE_LAPTOP_LIVEKIT_URL")
                or f"ws://{laptop_host}:17880",
                "room": _env("PARROT_WEB_CONSOLE_LAPTOP_ROOM")
                or "parrot-laptop-main",
                "runtime_scope": "codex_workspace/local_runtime/castle_laptop",
            },
        ],
        "secrets": {
            "orchestrator_secret_configured": _has_env("PARROT_ORCH_SECRET"),
            "app_monitor_secret_configured": _has_env("PARROT_APP_MONITOR_SECRET"),
            "token_mint_secret_configured": _has_env("PARROT_MINT_SECRET"),
            "google_credentials_configured": _has_env(
                "PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH"
            )
            or _has_env("GOOGLE_WORKSPACE_CREDENTIALS_PATH"),
        },
        "warnings": _profile_warnings(profile, active),
    }


def apply_console_environment_profile(profile_id: str) -> dict[str, Any]:
    """Switch this Web Console process to a known upstream profile.

    This is intentionally process-local: it changes where the running BFF
    proxies Graphiti/L2-B/app-monitor/orchestrator requests, without writing a
    config file or persisting the selection into the browser.
    """

    profile = str(profile_id or "").strip().lower()
    if profile not in {"laptop", "ecs"}:
        raise ValueError("profile must be 'laptop' or 'ecs'")

    if profile == "laptop":
        app_url = _clean_url(
            _env("PARROT_WEB_CONSOLE_LAPTOP_BFF_APP_API_URL")
            or _env("PARROT_WEB_CONSOLE_LAPTOP_APP_API_URL")
            or "http://127.0.0.1:18790"
        )
        orch_url = _clean_url(
            _env("PARROT_WEB_CONSOLE_LAPTOP_BFF_ORCH_URL")
            or _env("PARROT_WEB_CONSOLE_LAPTOP_ORCH_URL")
            or "http://127.0.0.1:17890"
        )
        livekit_url = (
            _env("PARROT_WEB_CONSOLE_LAPTOP_LIVEKIT_URL")
            or "ws://127.0.0.1:17880"
        )
        room = _env("PARROT_WEB_CONSOLE_LAPTOP_ROOM") or "parrot-laptop-main"
    else:
        ecs_host = _env("PARROT_ECS_HOST") or "8.216.45.45"
        app_url = _clean_url(
            _env("PARROT_WEB_CONSOLE_ECS_APP_API_URL")
            or f"http://{ecs_host}:8790"
        )
        orch_url = _clean_url(
            _env("PARROT_WEB_CONSOLE_ECS_ORCH_URL")
            or f"http://{ecs_host}:7890"
        )
        livekit_url = (
            _env("PARROT_WEB_CONSOLE_ECS_LIVEKIT_URL")
            or f"ws://{ecs_host}:7880"
        )
        room = _env("PARROT_WEB_CONSOLE_ECS_ROOM") or "parrot-main"

    os.environ["PARROT_WEB_CONSOLE_PROFILE"] = profile
    os.environ["PARROT_WEB_CONSOLE_APP_API_URL"] = app_url
    os.environ["PARROT_WEB_CONSOLE_GRAPHITI_URL"] = app_url
    os.environ["PARROT_WEB_CONSOLE_L2B_URL"] = app_url
    os.environ["PARROT_WEB_CONSOLE_NANOBOT_API_URL"] = app_url
    os.environ["PARROT_WEB_CONSOLE_ORCH_URL"] = orch_url
    os.environ["LIVEKIT_URL"] = livekit_url
    os.environ["LIVEKIT_ROOM"] = room
    return build_console_environment(
        service_name="web-console",
        orchestrator_base_url=orch_url,
        orchestrator_auth_mode="bearer" if _has_env("PARROT_ORCH_SECRET") else "none",
    )


def _profile_name() -> str:
    explicit = (
        _env("PARROT_WEB_CONSOLE_PROFILE")
        or _env("VITE_PARROT_WEB_CONSOLE_PROFILE")
        or _env("PARROT_ENV_PROFILE")
    )
    if explicit:
        return explicit
    room = _env("LIVEKIT_ROOM").lower()
    target = " ".join(
        [
            _env("PARROT_WEB_CONSOLE_API_TARGET"),
            _env("PARROT_WEB_CONSOLE_GRAPHITI_URL"),
            _env("PARROT_WEB_CONSOLE_APP_API_URL"),
            _env("PARROT_WEB_CONSOLE_ORCH_URL"),
        ]
    )
    if "laptop" in room or ":18790" in target or ":17890" in target:
        return "laptop"
    if ":8790" in target or ":7890" in target or "8.216.45.45" in target:
        return "ecs"
    return "local-bff"


def _profile_warnings(profile: str, active: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if profile == "laptop" and "8.216.45.45" in str(active):
        warnings.append("laptop profile references public ECS endpoints")
    if profile == "ecs" and "127.0.0.1" in str(active.get("app_api_base_url", "")):
        warnings.append("ecs profile app API still points at localhost")
    if active.get("runtime_data_root") and profile == "ecs":
        warnings.append("runtime data root is local; verify this is not a laptop path")
    restart_control = active.get("restart_control")
    if isinstance(restart_control, dict) and restart_control.get("mode") == "external_operator":
        warnings.append("process restarts are managed by the local operator shell")
    return warnings


def _restart_control(profile: str) -> dict[str, Any]:
    mode = (
        _env("PARROT_ORCH_RESTART_MODE")
        or ("external_operator" if profile == "laptop" else "systemd")
    )
    command = (
        _env("PARROT_ORCH_RESTART_OPERATOR_COMMAND")
        or "powershell -ExecutionPolicy Bypass -File infra\\laptop-castle.ps1 "
        "-Action restart -Service {component}"
    )
    return {
        "mode": mode,
        "operator_command": command if mode == "external_operator" else "",
        "restart_route": "/restart_component",
        "components": ["brain", "scheduler", "nanobot-worker", "orchestrator"],
    }


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _has_env(name: str) -> bool:
    return bool(_env(name))


def _clean_url(value: str) -> str:
    cleaned = value.strip()
    return cleaned[:-1] if cleaned.endswith("/") else cleaned
