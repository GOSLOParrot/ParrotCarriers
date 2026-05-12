"""Castle ECS Orchestrator (Phase 2).

Plan reference:
``.cursor/memory/architecture/Interface/app_v1_brain_cold_start_line_lifecycle_audit_20260511.md``
§Phase 2.

The orchestrator is the **single business-level entry point** for:

* Inspecting which components are running on ECS (containers + Python
  processes), what the live Brain resolved, and whether a config drift
  exists.
* Writing ``data/runtime_config.json`` to flip Line / LineProfile /
  RoomProfile for the next LiveKit room job (Tier 1 setting changes).
* Restarting Python components via systemd (Tier 2 changes).

It deliberately does **not** mint LiveKit tokens, fan out media, or
parse business RPC payloads. ``token_mint`` keeps that role; this
service is purely a control plane.

Public surface (HTTP, default port 7890; see ``server.py``):

* ``GET /health``                      — liveness probe (no auth)
* ``GET /status``                      — full ECS status snapshot
* ``POST /set_active_line``            — Tier 1 line switch
* ``POST /apply_room_profile``         — write room_profile_id (Tier 1)
* ``POST /restart_component``          — Tier 2 process restart
* ``POST /clear_runtime_config``       — drop runtime_config.json

All non-``/health`` endpoints require ``Authorization: Bearer
$PARROT_ORCH_SECRET`` when the env var is set. When unset, requests
are accepted (dev/local mode) but a warning is logged.
"""

from parrot.castle.orchestrator.server import build_app

__all__ = ["build_app"]
