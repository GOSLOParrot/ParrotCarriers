"""Tests for Sprint4 ECP alpha schemas and legacy RPC response parsing.

Coverage map (kept narrow on purpose — see `sprint4_ecp_minimal_audit_20260429.md`):
    - Envelope wrapping carries `command_id` to the wire.
    - `EcpAck.ok` follows the strict terminal-success band (intermediate
      statuses must NOT flip ok=True).
    - `_classify_response` distinguishes terminal success / intermediate /
      failure / malformed so `tick/last_rpc_ack.ok` keeps its felt-experience
      contract.
    - `EcpCommand.layer` round-trips through the shared `EventLayer` enum.
"""

from parrot.brain.tools._rpc_bridge import _classify_response
from parrot.shared.ecp import (
    ConnectionOverall,
    EcpAck,
    EcpAckStatus,
    EcpCommand,
    EcpCommandKind,
    EcpConnectionHealth,
    EcpFrontendState,
    EcpState,
    wrap_legacy_rpc_payload,
)
from parrot.shared.event_log import EventLayer


def test_wrap_legacy_rpc_payload_adds_ecp_envelope():
    payload, command = wrap_legacy_rpc_payload(
        {"x": 1.0, "y": 2.0, "z": 3.0},
        kind=EcpCommandKind.MOVE_TO,
        target={"position": {"x": 1.0, "y": 2.0, "z": 3.0}},
        actor="test",
        expires_in_s=5.0,
    )

    assert payload["x"] == 1.0
    assert payload["_ecp"]["schema_version"] == "ecp.v2.alpha"
    assert payload["_ecp"]["command_id"] == command.command_id
    assert payload["_ecp"]["expires_at"] > payload["_ecp"]["issued_at"]
    assert payload["_ecp"]["layer"] == "intent"


def test_wrap_legacy_rpc_payload_zero_expires_means_no_expiry():
    payload, _ = wrap_legacy_rpc_payload(
        {},
        kind=EcpCommandKind.ANIMATE,
        target={},
        actor="test",
        expires_in_s=0.0,
    )

    assert payload["_ecp"]["expires_at"] == 0.0


def test_wrap_legacy_rpc_payload_meta_kwarg_pass_through():
    """GOSLO model modularization (Step 1, 2026-05-06): tools may attach
    routing-hint metadata (today: ``model_id``; future: actor address /
    capability hint) via the ``meta`` kwarg. ``EcpCommand.meta`` is the
    existing free-form ``dict[str, Any]`` slot, so this is 0 wire change /
    0 schema_version bump / 0 cs_parity impact.
    """
    payload, command = wrap_legacy_rpc_payload(
        {"animation": "fly"},
        kind=EcpCommandKind.ANIMATE,
        target={"animation": "fly"},
        actor="test",
        meta={"model_id": "owl_v1"},
    )

    assert payload["_ecp"]["meta"] == {"model_id": "owl_v1"}
    assert command.meta == {"model_id": "owl_v1"}


def test_wrap_legacy_rpc_payload_default_meta_is_empty_dict():
    """Tools that don't use the ``meta`` kwarg get the existing wire shape
    (empty meta dict on the envelope) — guarantees we don't accidentally
    require meta at the consumer."""
    payload, command = wrap_legacy_rpc_payload(
        {},
        kind=EcpCommandKind.ANIMATE,
        target={},
        actor="test",
    )

    assert payload["_ecp"]["meta"] == {}
    assert command.meta == {}


def test_ecp_command_layer_round_trips_event_layer_enum():
    cmd = EcpCommand(kind=EcpCommandKind.PERCH_TO_FINGER, layer=EventLayer.REFLEX)

    dumped = cmd.model_dump(mode="json")

    assert dumped["layer"] == "reflex"


def test_ecp_ack_completed_is_ok():
    ack = EcpAck(status=EcpAckStatus.COMPLETED, command_id="cmd_1")

    assert ack.ok is True


def test_ecp_ack_intermediate_states_are_not_ok():
    """A `received`/`accepted`/`queued`/`running` ack is not a completion.

    This guards against the felt-experience regression flagged in
    `sprint4_ecp_minimal_audit_20260429.md` (audit finding A2): if the strict
    terminal band ever drifts back to including intermediates, Gemini will
    silently stop seeing pending work.
    """
    for status in (
        EcpAckStatus.RECEIVED,
        EcpAckStatus.ACCEPTED,
        EcpAckStatus.QUEUED,
        EcpAckStatus.RUNNING,
    ):
        assert EcpAck(status=status, command_id="cmd_1").ok is False, status


def test_rpc_bridge_accepts_ecp_completed_response():
    ok, reason, detail = _classify_response(
        '{"schema_version":"ecp.v2.alpha","command_id":"cmd_1",'
        '"status":"completed","reason":"applied"}'
    )

    assert ok is True
    assert reason == "applied"
    assert detail == ""


def test_rpc_bridge_intermediate_status_is_not_ok():
    ok, reason, _ = _classify_response(
        '{"schema_version":"ecp.v2.alpha","command_id":"cmd_1","status":"running"}'
    )

    assert ok is False
    assert reason == "running"


def test_rpc_bridge_rejects_ecp_rejected_response():
    ok, reason, detail = _classify_response(
        '{"schema_version":"ecp.v2.alpha","command_id":"cmd_1",'
        '"status":"rejected","reason":"micro_lock","detail":"body busy"}'
    )

    assert ok is False
    assert reason == "micro_lock"
    assert detail == "body busy"


def test_rpc_bridge_expired_status_is_failure():
    ok, reason, _ = _classify_response(
        '{"schema_version":"ecp.v2.alpha","command_id":"cmd_1","status":"expired"}'
    )

    assert ok is False
    assert reason == "expired"


def test_rpc_bridge_legacy_ok_response_still_classified():
    ok, reason, detail = _classify_response('{"status":"ok"}')

    assert ok is True
    assert reason == ""
    assert detail == ""


# ─── Sprint4 Phase 3: EcpState / ConnectionHealth ─────────────────────────


def test_ecp_frontend_state_carries_connection_overall():
    """Sprint4 Phase 3 INDEX_for_phase3 §1 #13: per-command ack carries the
    4-state aggregate, not the full ConnectionHealthState."""
    fs = EcpFrontendState(
        body_state="flying",
        connection_overall=ConnectionOverall.HEALTHY,
    )

    dumped = fs.model_dump(mode="json")

    assert dumped["connection_overall"] == "healthy"
    assert dumped["body_state"] == "flying"


def test_ecp_state_heartbeat_round_trips_health():
    health = EcpConnectionHealth(
        room_connected=True,
        brain_present=True,
        rpc_ready=True,
        video_first_frame=True,
        video_fresh_frame=True,
        audio_published=True,
        overall=ConnectionOverall.HEALTHY,
    )
    state = EcpState(
        unity_identity="unity-arspike",
        room_id="parrot-dev",
        app_lifecycle_state="running",
        connection_health=health,
        active_locks=("body",),
    )

    dumped = state.model_dump(mode="json")

    assert dumped["schema_version"] == "ecp.v2.alpha"
    assert dumped["connection_health"]["overall"] == "healthy"
    assert dumped["connection_health"]["video_fresh_frame"] is True
    assert dumped["app_lifecycle_state"] == "running"
    assert dumped["active_locks"] == ["body"]


def test_ecp_state_allows_missing_connection_health_during_cold_start():
    """Cold-start window: aggregator may be empty before any signal arrives."""
    state = EcpState(
        unity_identity="unity-arspike",
        app_lifecycle_state="cold_start",
    )

    dumped = state.model_dump(mode="json")

    assert dumped["connection_health"] is None
    assert dumped["app_lifecycle_state"] == "cold_start"


def test_connection_overall_enum_serialises_as_lowercase_string():
    """Wire format must be the lowercase string Unity sends, not the Enum repr."""
    health = EcpConnectionHealth(overall=ConnectionOverall.DEGRADED)

    assert health.model_dump(mode="json")["overall"] == "degraded"
