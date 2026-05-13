"""Web Console BFF helpers for DSG memory/operator workflows.

This module is intentionally Web-only. It returns operator receipts and draft
payloads for the console without changing App-facing DTOs. Dangerous writes
default to dry-run and require an explicit operator flag.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any


_TRIGGER_EVENT_HINTS: dict[str, list[dict[str, Any]]] = {
    "obsidian_ingest": [
        {
            "type": "obsidian_note",
            "payload": {
                "profile": "daily",
                "label": "Web setting note",
                "kind": "object",
                "description": "UUID-free daily/roleplay setting note.",
                "obsidian_note_key": "web-console/sample-setting",
            },
        }
    ],
    "message_notification": [
        {
            "type": "message_push",
            "message_id": "web_test_message",
            "sender": "test@example.com",
            "subject": "Web Console message push test",
            "snippet": "Synthetic Gmail notification for trigger testing.",
            "importance": "high",
        },
        {
            "type": "message_result",
            "result": json.dumps(
                [
                    {
                        "id": "web_result_message",
                        "sender": "test@example.com",
                        "subject": "Web Console message result",
                        "snippet": "Synthetic Gmail result payload.",
                        "importance": "normal",
                    }
                ]
            ),
        },
    ],
    "intent_event_boundary": [
        {
            "type": "intent_boundary",
            "kind": "intent_explicit",
            "actor": "web_console",
            "summary": "Synthetic boundary event.",
        }
    ],
    "calendar": [
        {
            "type": "calendar_result",
            "result": json.dumps(
                [
                    {
                        "id": "web_calendar_event",
                        "summary": "Web Console calendar trigger test",
                        "start": {"dateTime": "2026-05-13T10:00:00+08:00"},
                    }
                ]
            ),
        }
    ],
    "scene_switch": [
        {
            "kind": "scene_switch",
            "old_scene_type": "previous",
            "new_scene_type": "desktop_webcam",
            "source": "web_console",
        }
    ],
    "roleplay_mode": [
        {"kind": "roleplay_mode", "action": "open", "source": "web_console"}
    ],
}


def trigger_catalog() -> dict[str, Any]:
    """Return trigger metadata for the Runtime Monitor lab."""
    from parrot.dsg.triggers import ALL_TRIGGERS

    triggers: list[dict[str, Any]] = []
    for trigger_cls in ALL_TRIGGERS:
        name = str(getattr(trigger_cls, "name", trigger_cls.__name__))
        triggers.append(
            {
                "name": name,
                "class": f"{trigger_cls.__module__}.{trigger_cls.__name__}",
                "kinds": [_enum_value(kind) for kind in getattr(trigger_cls, "kinds", [])],
                "interval_seconds": float(getattr(trigger_cls, "interval_seconds", 0) or 0),
                "event_hints": _event_hints_for(name),
            }
        )
    return {
        "success": True,
        "action": "trigger_catalog",
        "triggers": triggers,
        "audit": {
            "web_only": True,
            "default_mode": "dry_run",
            "fire_channel": "CH_DSG_EVENTS",
        },
    }


def draft_trigger_event(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a Redis DSG event without publishing it."""
    body = payload or {}
    event = _extract_event(body)
    trigger_name = str(body.get("trigger_name") or "").strip()
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    matched = _matched_trigger_names(event, trigger_name)

    return _receipt(
        action="dsg.trigger.draft_event",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "channel": "parrot.dsg.events",
            "event": event,
            "matched_triggers": matched,
            "would_publish": False,
            "operator_required_for_execute": True,
        },
    )


async def fire_trigger_event(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Publish a DSG event only when operator mode is explicit."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_trigger_event({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    if dry_run or not operator_mode:
        draft["action"] = "dsg.trigger.fire_event"
        draft["data"]["would_publish"] = True
        draft["data"]["publish_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    try:
        from parrot.shared.constants import CH_DSG_EVENTS
        from parrot.shared.redis_client import get_redis

        redis = await get_redis()
        event = draft["data"]["event"]
        await redis.publish(CH_DSG_EVENTS, json.dumps(event, ensure_ascii=False))
        return _receipt(
            action="dsg.trigger.fire_event",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={
                "channel": CH_DSG_EVENTS,
                "event": event,
                "matched_triggers": draft["data"]["matched_triggers"],
                "published": True,
            },
        )
    except Exception as exc:
        return _receipt(
            action="dsg.trigger.fire_event",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={
                "event": draft["data"]["event"],
                "matched_triggers": draft["data"]["matched_triggers"],
                "published": False,
                "error": f"{type(exc).__name__}: {exc}",
            },
        )


async def build_l15_pool_snapshot() -> dict[str, Any]:
    """Return L1.5 pool health, buckets, refs, timeline, and scene."""
    from parrot.dsg.l1_5.pool import get_l1_5_pool

    pool = get_l1_5_pool()
    health = pool.health()
    ref_report = await pool.ref_health_report()
    refs_health_distribution: dict[str, int] = {}
    refs: list[dict[str, Any]] = []
    for item in ref_report:
        status = _enum_value(item.status)
        refs_health_distribution[status] = refs_health_distribution.get(status, 0) + 1
        refs.append(_jsonable(item))

    timeline = pool.get_timeline()[-32:]
    return {
        "success": True,
        "action": "l15.pool.snapshot",
        "health": {
            "total_nodes": health.total_nodes,
            "nodes_per_bucket": {
                _enum_value(kind): count for kind, count in health.nodes_per_bucket.items()
            },
            "refs_total": health.refs_total,
            "refs_health_distribution": refs_health_distribution,
            "timeline_marker_count": health.timeline_marker_count,
            "current_scene": health.current_scene,
            "capacity_pressure": _enum_value(health.capacity_pressure),
        },
        "buckets": [_bucket_handle_as_dict(handle) for handle in pool.list_buckets()],
        "refs": refs[:80],
        "timeline": [_jsonable(marker) for marker in timeline],
        "scene": _jsonable(pool.current_scene()),
        "audit": {
            "web_only": True,
            "writes_default_to": "draft_receipt",
        },
    }


def draft_l15_bucket_op(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a bucket operation receipt."""
    from parrot.dsg.l1_5.buckets import BucketKind, BucketOpKind

    body = payload or {}
    op_raw = str(body.get("op") or "freeze").strip().lower()
    kind_raw = str(body.get("kind") or BucketKind.MAIN.value).strip().lower()
    op = _parse_enum(BucketOpKind, op_raw)
    kind = _parse_enum(BucketKind, kind_raw)
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    if op is None or kind is None:
        return _receipt(
            action="l15.bucket_op.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "invalid_bucket_op_or_kind",
                "op": op_raw,
                "kind": kind_raw,
                "valid_ops": [item.value for item in BucketOpKind],
                "valid_kinds": [item.value for item in BucketKind],
            },
        )
    return _receipt(
        action="l15.bucket_op.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "bucket_op": {
                "op": op.value,
                "kind": kind.value,
                "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
            },
            "would_apply": False,
            "operator_required_for_execute": True,
        },
    )


async def apply_l15_bucket_op(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply a bucket op only when operator mode is explicit."""
    from parrot.dsg.l1_5.buckets import BucketKind, BucketOp, BucketOpKind
    from parrot.dsg.l1_5.pool import get_l1_5_pool

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_l15_bucket_op({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    draft["action"] = "l15.bucket_op.apply"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    op_data = draft["data"]["bucket_op"]
    op = BucketOp(
        op=BucketOpKind(op_data["op"]),
        kind=BucketKind(op_data["kind"]),
        payload=dict(op_data.get("payload") or {}),
    )
    result = await get_l1_5_pool().apply_bucket_op(op)
    return _receipt(
        action="l15.bucket_op.apply",
        success=bool(result.success),
        dry_run=False,
        operator_mode=True,
        data={"result": _jsonable(result), "bucket_op": op_data},
    )


def draft_obsidian_setting_node(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft an Obsidian three-profile setting/ref event."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    node_payload = _obsidian_node_payload(body)
    if node_payload.get("profile") == "ref" and not node_payload.get("obsidian_uuid"):
        return _receipt(
            action="l15.obsidian_node.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "ref_profile_requires_obsidian_uuid",
                "payload": node_payload,
            },
        )
    event = _obsidian_event(node_payload)
    return _receipt(
        action="l15.obsidian_node.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "event": event,
            "profile": node_payload["profile"],
            "uuid_free_allowed": node_payload["profile"] in {"daily", "roleplay"},
            "operator_required_for_execute": True,
        },
    )


async def apply_obsidian_setting_node(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Publish an Obsidian event only under operator execution."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_obsidian_setting_node(
        {**body, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    draft["action"] = "l15.obsidian_node.apply"
    if not draft.get("success"):
        return draft
    return await fire_trigger_event(
        {
            "event": draft["data"]["event"],
            "dry_run": dry_run,
            "operator_mode": operator_mode,
            "trigger_name": "obsidian_ingest",
        }
    )


def draft_l2b_node(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft an L2-B node create/update through L1.5 Observation."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    label = str(body.get("label") or "").strip()
    if not label:
        return _receipt(
            action="l2b.node.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={"error": "missing_label"},
        )

    observation = _l2b_observation_draft(body)
    return _receipt(
        action="l2b.node.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "observation": observation,
            "write_path": "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            "operator_required_for_execute": True,
        },
    )


async def apply_l2b_node(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create/update a node through L1.5 only under operator execution."""
    from parrot.dsg.ingest.base import Observation, ObservationSource
    from parrot.dsg.l1_5.pool import get_l1_5_pool
    from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_l2b_node({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    draft["action"] = "l2b.node.apply"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    obs_data = draft["data"]["observation"]
    obs = Observation(
        source=ObservationSource.USER_EXPLICIT,
        provenance_stream_id=str(obs_data.get("provenance_stream_id") or ""),
        obsidian_uuid=str(obs_data.get("obsidian_uuid") or ""),
        graphiti_uuid=str(obs_data.get("graphiti_uuid") or ""),
        label=str(obs_data["label"]),
        kind=NodeKind(obs_data["kind"]),
        description=str(obs_data.get("description") or ""),
        confidence=float(obs_data.get("confidence") or 0.85),
        confirmation=ConfirmationStatus(obs_data.get("confirmation") or "confirmed"),
        meta=dict(obs_data.get("meta") or {}),
    )
    outcome = await get_l1_5_pool().admit((obs,))
    return _receipt(
        action="l2b.node.apply",
        success=not outcome.rejected,
        dry_run=False,
        operator_mode=True,
        data={"admit_outcome": _jsonable(outcome)},
    )


async def delete_l2b_node(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Evict a node through L1.5, defaulting to dry-run."""
    from parrot.dsg.l1_5.pool import EvictReason, get_l1_5_pool

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    node_uuid = str(body.get("node_uuid") or body.get("uuid") or "").strip()
    if not node_uuid:
        return _receipt(
            action="l2b.node.delete",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={"error": "missing_node_uuid"},
        )
    if dry_run or not operator_mode:
        return _receipt(
            action="l2b.node.delete",
            success=True,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "node_uuid": node_uuid,
                "would_evict": True,
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
            },
        )
    ok = await get_l1_5_pool().evict(node_uuid, EvictReason.EXPLICIT)
    return _receipt(
        action="l2b.node.delete",
        success=ok,
        dry_run=False,
        operator_mode=True,
        data={"node_uuid": node_uuid, "evicted": ok},
    )


def draft_l2b_edge(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft an L2-B edge using the SemanticEdge shape."""
    from parrot.dsg.l2b_types import EdgeKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    from_uuid = str(body.get("from_uuid") or body.get("source_uuid") or "").strip()
    to_uuid = str(body.get("to_uuid") or body.get("target_uuid") or "").strip()
    kind = _parse_enum(EdgeKind, str(body.get("kind") or EdgeKind.ASSOCIATED_WITH.value))
    if not from_uuid or not to_uuid or kind is None:
        return _receipt(
            action="l2b.edge.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_or_invalid_edge_fields",
                "valid_kinds": [item.value for item in EdgeKind],
            },
        )
    if from_uuid == to_uuid:
        return _receipt(
            action="l2b.edge.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "self_edge_not_allowed",
                "from_uuid": from_uuid,
                "to_uuid": to_uuid,
            },
        )
    edge = {
        "from_uuid": from_uuid,
        "to_uuid": to_uuid,
        "edge": {
            "kind": kind.value,
            "strength": _body_float(body.get("strength"), 0.5),
            "source": str(body.get("source") or "web_console"),
            "meta": body.get("meta") if isinstance(body.get("meta"), dict) else {},
        },
        "operator_required_for_execute": True,
    }
    return _receipt(
        action="l2b.edge.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data=edge,
    )


async def apply_l2b_edge(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Connect two existing nodes only under operator execution."""
    from parrot.dsg.l1_5.pool import get_l1_5_pool
    from parrot.dsg.l1_5.timeline import TimelineMarkerKind
    from parrot.dsg.l2b_graph import get_l2b_graph
    from parrot.dsg.l2b_types import EdgeKind, SemanticEdge

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_l2b_edge({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    draft["action"] = "l2b.edge.apply"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    edge_data = draft["data"]["edge"]
    ok = get_l2b_graph().connect(
        str(draft["data"]["from_uuid"]),
        str(draft["data"]["to_uuid"]),
        SemanticEdge(
            kind=EdgeKind(edge_data["kind"]),
            strength=float(edge_data["strength"]),
            source=str(edge_data["source"]),
            meta=dict(edge_data.get("meta") or {}),
        ),
    )
    if ok:
        get_l1_5_pool().mark(
            TimelineMarkerKind.BUCKET_OP,
            payload={
                "op": "l2b_edge_connect",
                "kind": edge_data["kind"],
                "source": edge_data["source"],
            },
            related_node_uuids=(
                str(draft["data"]["from_uuid"]),
                str(draft["data"]["to_uuid"]),
            ),
        )
    return _receipt(
        action="l2b.edge.apply",
        success=ok,
        dry_run=False,
        operator_mode=True,
        data={**draft["data"], "connected": ok},
    )


def draft_message_check(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a Nanobot Gmail/message_check dispatch."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    params = {
        "query": str(body.get("query") or "Check Gmail for unread important messages"),
        "instructions": str(
            body.get("instructions")
            or (
                "Use the Gmail API or MCP tool to fetch unread messages that are "
                "starred, important, or from known contacts. Skip marketing and "
                "automated notifications. Return JSON with id, sender, subject, "
                "snippet, timestamp, is_reply, and importance."
            )
        ),
        "result_channel": str(body.get("result_channel") or "message_result"),
    }
    return _receipt(
        action="google.message_check.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "task_type": "message_check",
            "priority": str(body.get("priority") or "normal"),
            "params": params,
            "operator_required_for_execute": True,
        },
    )


async def dispatch_message_check(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dispatch message_check through Scheduler only under operator execution."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_message_check({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    draft["action"] = "google.message_check.dispatch"
    if dry_run or not operator_mode:
        draft["data"]["would_dispatch"] = True
        draft["data"]["dispatch_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    try:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        task_id = await do_dispatch_task(
            "message_check",
            params=draft["data"]["params"],
            priority=draft["data"]["priority"],
        )
        return _receipt(
            action="google.message_check.dispatch",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "task_id": task_id, "dispatched": True},
        )
    except Exception as exc:
        return _receipt(
            action="google.message_check.dispatch",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "error": f"{type(exc).__name__}: {exc}"},
        )


async def push_test_message(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft/publish a synthetic message_push event through the trigger bus."""
    body = payload or {}
    event = {
        "type": "message_push",
        "message_id": str(body.get("message_id") or f"web_msg_{uuid.uuid4().hex[:8]}"),
        "sender": str(body.get("sender") or "web-console@example.com"),
        "subject": str(body.get("subject") or "Web Console message push test"),
        "snippet": str(body.get("snippet") or "Synthetic push event from Web Console."),
        "importance": str(body.get("importance") or "high"),
        "source": "web_console",
    }
    return await fire_trigger_event(
        {
            "event": event,
            "trigger_name": "message_notification",
            "dry_run": _body_bool(body.get("dry_run"), True),
            "operator_mode": _body_bool(body.get("operator_mode"), False),
        }
    )


def _event_hints_for(trigger_name: str) -> list[dict[str, Any]]:
    for key, value in _TRIGGER_EVENT_HINTS.items():
        if key in trigger_name:
            return value
    return []


def _matched_trigger_names(event: dict[str, Any], trigger_name: str = "") -> list[str]:
    explicit = trigger_name.strip()
    if explicit:
        return [explicit]
    matched: list[str] = []
    for name, hints in _TRIGGER_EVENT_HINTS.items():
        for hint in hints:
            if _event_matches_hint(event, hint):
                matched.append(name)
                break
    return matched


def _event_matches_hint(event: dict[str, Any], hint: dict[str, Any]) -> bool:
    """Return True when a draft event follows a catalog sample shape.

    Trigger events are intentionally mixed while we migrate: legacy push events
    use ``type`` and newer on-demand trigger events use ``kind``. The matcher
    checks both keys so operator receipts do not imply an old-only protocol.
    """
    event_type = str(event.get("type") or "").strip()
    hint_type = str(hint.get("type") or "").strip()
    if event_type and hint_type and event_type == hint_type:
        return True
    event_kind = str(event.get("kind") or "").strip()
    hint_kind = str(hint.get("kind") or "").strip()
    return bool(event_kind and hint_kind and event_kind == hint_kind)


def _extract_event(body: dict[str, Any]) -> dict[str, Any]:
    event = body.get("event")
    if isinstance(event, dict):
        return dict(event)
    raw = body.get("event_json")
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"type": "invalid_json", "raw": raw}
    return {
        "type": str(body.get("type") or "web_console_test"),
        "source": "web_console",
        "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
        "timestamp": time.time(),
    }


def _obsidian_node_payload(body: dict[str, Any]) -> dict[str, Any]:
    profile = str(body.get("profile") or "daily").strip().lower().replace("-", "_")
    if profile in {"setting", "setting_daily", "daily_setting"}:
        profile = "daily"
    if profile in {"setting_roleplay", "roleplay_setting", "rp"}:
        profile = "roleplay"
    if profile in {"reference", "ref_reinforce"}:
        profile = "ref"
    if profile not in {"daily", "roleplay", "ref"}:
        profile = "daily"
    label = str(body.get("label") or "").strip()[:128] or "Web Console setting"
    tags = body.get("tags")
    if isinstance(tags, str):
        tags = [item.strip() for item in tags.split(",") if item.strip()]
    if not isinstance(tags, list):
        tags = ["web_console", profile]
    return {
        "profile": profile,
        "label": label,
        "kind": str(body.get("kind") or "object").strip().lower(),
        "description": str(body.get("description") or "").strip()[:400],
        "obsidian_uuid": str(body.get("obsidian_uuid") or "").strip(),
        "obsidian_note_key": str(
            body.get("obsidian_note_key")
            or body.get("path")
            or f"web-console/{profile}/{label}"
        ),
        "obsidian_path": str(body.get("obsidian_path") or body.get("path") or ""),
        "target_node_uuid": str(body.get("target_node_uuid") or "").strip(),
        "graphiti_uuid": str(body.get("graphiti_uuid") or "").strip(),
        "tags": [str(tag) for tag in tags[:10]],
    }


def _obsidian_event(node_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "obsidian_note",
        "source": "web_console.obsidian_node",
        "provenance_stream_id": f"web:obsidian:{uuid.uuid4().hex[:12]}",
        "payload": node_payload,
        "timestamp": time.time(),
    }


def _l2b_observation_draft(body: dict[str, Any]) -> dict[str, Any]:
    kind = str(body.get("kind") or "object").strip().lower()
    if kind not in {"object", "surface", "zone", "person", "event", "photo"}:
        kind = "object"
    return {
        "source": "user_explicit",
        "provenance_stream_id": str(body.get("provenance_stream_id") or "web:l2b:manual"),
        "obsidian_uuid": str(body.get("obsidian_uuid") or ""),
        "graphiti_uuid": str(body.get("graphiti_uuid") or ""),
        "label": str(body.get("label") or "").strip()[:128],
        "kind": kind,
        "description": str(body.get("description") or "").strip()[:400],
        "confidence": max(0.0, min(_body_float(body.get("confidence"), 0.85), 1.0)),
        "confirmation": str(body.get("confirmation") or "confirmed"),
        "meta": {
            "source_tool": "web_console",
            "target_node_uuid": str(body.get("node_uuid") or ""),
            "audit_note": str(body.get("audit_note") or ""),
        },
    }


def _bucket_handle_as_dict(handle: Any) -> dict[str, Any]:
    node_uuids = sorted(str(item) for item in getattr(handle, "node_uuids", set()))
    spec = getattr(handle, "spec", None)
    return {
        "kind": _enum_value(getattr(spec, "kind", "")),
        "frozen": bool(getattr(handle, "frozen", False)),
        "created_at": float(getattr(handle, "created_at", 0) or 0),
        "last_modified_at": float(getattr(handle, "last_modified_at", 0) or 0),
        "node_count": len(node_uuids),
        "node_uuids": node_uuids[:80],
        "spec": _jsonable(spec),
    }


def _receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "success": success,
        "action": action,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "receipt": {
            "receipt_id": f"web_{uuid.uuid4().hex[:12]}",
            "created_at": time.time(),
            "audit_level": "operator" if operator_mode else "draft",
            "secret_redacted": True,
        },
        "data": _jsonable(data),
    }


def _parse_enum(enum_cls: Any, raw: Any) -> Any | None:
    value = str(raw or "").strip().lower()
    try:
        return enum_cls(value)
    except Exception:
        return None


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _body_float(value: Any, default: float) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in fields(value)
            if not field.name.startswith("_")
        }
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump())
    return value
