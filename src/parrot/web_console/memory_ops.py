"""Web Console BFF helpers for DSG memory/operator workflows.

This module is intentionally Web-only. It returns operator receipts and draft
payloads for the console without changing App-facing DTOs. Dangerous writes
default to dry-run and require an explicit operator flag.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


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

_TRIGGER_CHANNEL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "external_inbox": {
        "label": "External inbox",
        "description": "Calendar, message, Obsidian, or provider payloads rise into memory.",
    },
    "scheduled_poll": {
        "label": "Scheduled poll",
        "description": "Periodic checks lift background state into the trigger runner.",
    },
    "perception_scene": {
        "label": "Perception / scene",
        "description": "Scene, object, and curiosity signals rise from perception into context.",
    },
    "operator_mode": {
        "label": "Operator / mode",
        "description": "Web, Gemini, or operator actions change runtime mode or bucket state.",
    },
    "intent_boundary": {
        "label": "Intent boundary",
        "description": "Tool, plan, idle, and nanobot boundaries shape IntentEvent state.",
    },
    "memory_maintenance": {
        "label": "Memory maintenance",
        "description": "Archive, enrichment, and ref/context repair jobs maintain long memory.",
    },
}

_TRIGGER_MODULE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "google_calendar": {"label": "Google Calendar"},
    "google_message": {"label": "Google Message"},
    "obsidian": {"label": "Obsidian"},
    "graphiti": {"label": "Graphiti"},
    "l1_5_pool": {"label": "L1.5 Pool"},
    "l2_b_graph": {"label": "L2-B Graph"},
    "intent_workspace": {"label": "IntentWorkspace"},
    "plan_registry": {"label": "Plan Registry"},
    "archive_pipeline": {"label": "Archive Pipeline"},
    "scheduler_nanobot": {"label": "Scheduler / Nanobot"},
    "runtime_operator": {"label": "Runtime Operator"},
}

_TRIGGER_INFORMATION_DEFINITIONS: dict[str, dict[str, Any]] = {
    "calendar_event": {"label": "calendar_event"},
    "google_message": {"label": "google_message"},
    "obsidian_note": {"label": "obsidian_note"},
    "graphiti_context": {"label": "graphiti_context"},
    "scene_context": {"label": "scene_context"},
    "scene_state": {"label": "scene_state"},
    "curiosity_signal": {"label": "curiosity_signal"},
    "intent_boundary": {"label": "intent_boundary"},
    "mode_profile": {"label": "mode_profile"},
    "bucket_operation": {"label": "bucket_operation"},
    "l15_observation": {"label": "l15_observation"},
    "staged_ref": {"label": "staged_ref"},
    "plan_request": {"label": "plan_request"},
    "archive_request": {"label": "archive_request"},
    "nanobot_task": {"label": "nanobot_task"},
    "status_notice": {"label": "status_notice"},
    "provider_identity": {"label": "provider_identity"},
}

_TRIGGER_TAXONOMY_BY_KEY: dict[str, dict[str, list[str]]] = {
    "calendar": {
        "ascending_channels": ["external_inbox", "scheduled_poll"],
        "interaction_modules": ["google_calendar", "scheduler_nanobot", "l1_5_pool", "l2_b_graph"],
        "information_tags": ["calendar_event", "provider_identity", "l15_observation", "status_notice"],
    },
    "message": {
        "ascending_channels": ["external_inbox", "scheduled_poll"],
        "interaction_modules": ["google_message", "scheduler_nanobot", "l1_5_pool", "l2_b_graph"],
        "information_tags": ["google_message", "provider_identity", "l15_observation", "status_notice"],
    },
    "obsidian": {
        "ascending_channels": ["external_inbox", "memory_maintenance"],
        "interaction_modules": ["obsidian", "l1_5_pool", "l2_b_graph"],
        "information_tags": ["obsidian_note", "provider_identity", "l15_observation"],
    },
    "ssot": {
        "ascending_channels": ["memory_maintenance", "perception_scene"],
        "interaction_modules": ["graphiti", "l2_b_graph"],
        "information_tags": ["graphiti_context", "provider_identity", "scene_context"],
    },
    "scene_context": {
        "ascending_channels": ["perception_scene", "memory_maintenance"],
        "interaction_modules": ["graphiti", "l2_b_graph"],
        "information_tags": ["scene_context", "graphiti_context"],
    },
    "scene_switch": {
        "ascending_channels": ["operator_mode", "perception_scene"],
        "interaction_modules": ["runtime_operator", "l1_5_pool", "l2_b_graph"],
        "information_tags": ["scene_state", "bucket_operation"],
    },
    "roleplay": {
        "ascending_channels": ["operator_mode"],
        "interaction_modules": ["runtime_operator", "l1_5_pool"],
        "information_tags": ["mode_profile", "bucket_operation"],
    },
    "intent_event_boundary": {
        "ascending_channels": ["intent_boundary"],
        "interaction_modules": ["intent_workspace", "plan_registry"],
        "information_tags": ["intent_boundary", "scene_state"],
    },
    "goslo_curiosity": {
        "ascending_channels": ["perception_scene", "intent_boundary"],
        "interaction_modules": ["l1_5_pool", "intent_workspace", "plan_registry"],
        "information_tags": ["curiosity_signal", "l15_observation", "staged_ref", "plan_request"],
    },
    "idle_archive": {
        "ascending_channels": ["memory_maintenance", "scheduled_poll"],
        "interaction_modules": ["archive_pipeline", "scheduler_nanobot", "graphiti"],
        "information_tags": ["archive_request", "nanobot_task", "graphiti_context"],
    },
}


def trigger_catalog() -> dict[str, Any]:
    """Return trigger metadata for the Runtime Monitor lab."""
    from parrot.dsg.triggers import ALL_TRIGGERS

    triggers: list[dict[str, Any]] = []
    for trigger_cls in ALL_TRIGGERS:
        name = str(getattr(trigger_cls, "name", trigger_cls.__name__))
        taxonomy = _trigger_taxonomy_for(name)
        triggers.append(
            {
                "name": name,
                "class": f"{trigger_cls.__module__}.{trigger_cls.__name__}",
                "kinds": [_enum_value(kind) for kind in getattr(trigger_cls, "kinds", [])],
                "interval_seconds": float(getattr(trigger_cls, "interval_seconds", 0) or 0),
                "event_hints": _event_hints_for(name),
                **taxonomy,
            }
        )
    return {
        "success": True,
        "action": "trigger_catalog",
        "taxonomy": _trigger_taxonomy_catalog(),
        "groups": {
            "ascending_channel": _trigger_catalog_groups(
                triggers,
                field="ascending_channels",
                definitions=_TRIGGER_CHANNEL_DEFINITIONS,
            ),
            "interaction_module": _trigger_catalog_groups(
                triggers,
                field="interaction_modules",
                definitions=_TRIGGER_MODULE_DEFINITIONS,
            ),
            "information_tag": _trigger_catalog_groups(
                triggers,
                field="information_tags",
                definitions=_TRIGGER_INFORMATION_DEFINITIONS,
            ),
        },
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


def draft_ref_binding(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a RefBinding retarget/bind operation for the Web Source Board.

    This is intentionally draft-only in the current Web Console. ``RefBinding``
    is the emerging shared boundary for UI artifacts, photos, documents, L2-B,
    Graphiti, and board renderers, but CORE-006 is not ratified yet. Returning
    a typed receipt lets operators see the exact target and write path without
    silently mutating the Brain session registry or leaking Web-only repair
    actions into Unity/App DTOs.
    """

    from parrot.brain import refs as refs_registry
    from parrot.shared.ref_binding import RefTargetKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    ref_id = str(body.get("ref_id") or "").strip()
    target_kind_raw = str(body.get("target_kind") or RefTargetKind.L2B_NODE.value).strip()
    target_id = str(body.get("target_id") or body.get("target_uuid") or "").strip()
    valid_target_kinds = [item.value for item in RefTargetKind]
    target_kind = _parse_enum(RefTargetKind, target_kind_raw)

    if not ref_id:
        return _receipt(
            action="refs.binding.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_ref_id",
                "valid_target_kinds": valid_target_kinds,
                "core_candidate": "CORE-006",
            },
        )
    if target_kind is None:
        return _receipt(
            action="refs.binding.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "error": "invalid_target_kind",
                "target_kind": target_kind_raw,
                "valid_target_kinds": valid_target_kinds,
                "core_candidate": "CORE-006",
            },
        )
    if target_kind is not RefTargetKind.UNRESOLVED and not target_id:
        return _receipt(
            action="refs.binding.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "target_kind": target_kind.value,
                "error": "missing_target_id",
                "core_candidate": "CORE-006",
            },
        )

    current_ref = refs_registry.get_ref(ref_id)
    if current_ref is None:
        return _receipt(
            action="refs.binding.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "target_kind": target_kind.value,
                "target_id": target_id,
                "error": "ref_not_found",
                "write_path": "RefBindingRegistry.resolve_ref(ref_id, target_kind, target_id)",
                "operator_required_for_execute": True,
                "apply_route": "",
                "core_candidate": "CORE-006",
                "shared_status": "candidate_only",
            },
        )

    is_unresolved_target = target_kind is RefTargetKind.UNRESOLVED
    operation = "unresolve_ref" if is_unresolved_target else "resolve_ref"
    write_path = (
        "RefBinding.with_resolved_target(target_kind=unresolved, target_id='')"
        if is_unresolved_target
        else "RefBindingRegistry.resolve_ref(ref_id, target_kind, target_id)"
    )

    return _receipt(
        action="refs.binding.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "ref_id": ref_id,
            "current_ref": _jsonable(current_ref),
            "operation": operation,
            "draft_target": {
                "target_kind": target_kind.value,
                "target_id": target_id,
            },
            "would_resolve": not is_unresolved_target,
            "would_unresolve": is_unresolved_target,
            "write_path": write_path,
            "operator_required_for_execute": True,
            "apply_route": "/api/refs/binding/apply",
            "core_candidate": "CORE-006",
            "shared_status": "candidate_only",
            "policy": (
                "Web operator apply updates only the session RefBinding registry; "
                "it does not mutate L2-B, Graphiti, or Unity/App DTOs"
            ),
        },
    )


def apply_ref_binding(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply a RefBinding target update under explicit Web operator mode."""

    from parrot.brain import refs as refs_registry
    from parrot.shared.ref_binding import RefTargetKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    ref_id = str(body.get("ref_id") or "").strip()
    target_kind_raw = str(body.get("target_kind") or RefTargetKind.L2B_NODE.value).strip()
    target_id = str(body.get("target_id") or body.get("target_uuid") or "").strip()
    event_id = str(body.get("event_id") or "web_console.refs.binding.apply").strip()
    valid_target_kinds = [item.value for item in RefTargetKind]
    target_kind = _parse_enum(RefTargetKind, target_kind_raw)

    if not ref_id:
        return _receipt(
            action="refs.binding.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_ref_id",
                "valid_target_kinds": valid_target_kinds,
                "core_candidate": "CORE-006",
            },
        )
    if target_kind is None:
        return _receipt(
            action="refs.binding.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "error": "invalid_target_kind",
                "target_kind": target_kind_raw,
                "valid_target_kinds": valid_target_kinds,
                "core_candidate": "CORE-006",
            },
        )
    if target_kind is not RefTargetKind.UNRESOLVED and not target_id:
        return _receipt(
            action="refs.binding.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "target_kind": target_kind.value,
                "error": "missing_target_id",
                "core_candidate": "CORE-006",
            },
        )

    current_ref = refs_registry.get_ref(ref_id)
    if current_ref is None:
        return _receipt(
            action="refs.binding.apply",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "target_kind": target_kind.value,
                "target_id": target_id,
                "error": "ref_not_found",
                "write_path": "RefBindingRegistry.resolve_ref(ref_id, target_kind, target_id)",
                "operator_required_for_execute": True,
                "core_candidate": "CORE-006",
                "shared_status": "candidate_only",
            },
        )

    draft_target_id = "" if target_kind is RefTargetKind.UNRESOLVED else target_id
    write_path = (
        "RefBinding.with_resolved_target(target_kind=unresolved, target_id='')"
        if target_kind is RefTargetKind.UNRESOLVED
        else "RefBindingRegistry.resolve_ref(ref_id, target_kind, target_id)"
    )
    if dry_run or not operator_mode:
        return _receipt(
            action="refs.binding.apply",
            success=True,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "ref_id": ref_id,
                "current_ref": _jsonable(current_ref),
                "draft_target": {
                    "target_kind": target_kind.value,
                    "target_id": draft_target_id,
                },
                "would_apply": True,
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
                "write_path": write_path,
                "operator_required_for_execute": True,
                "core_candidate": "CORE-006",
                "shared_status": "candidate_only",
            },
        )

    updated = refs_registry.resolve_ref(
        ref_id,
        target_kind=target_kind,
        target_id=draft_target_id,
        new_event_id=event_id,
    )
    return _receipt(
        action="refs.binding.apply",
        success=updated is not None,
        dry_run=False,
        operator_mode=True,
        data={
            "ref_id": ref_id,
            "previous_ref": _jsonable(current_ref),
            "updated_ref": _jsonable(updated),
            "write_path": write_path,
            "core_candidate": "CORE-006",
            "shared_status": "candidate_only",
            "mutated": updated is not None,
            "mutation_scope": "session_ref_binding_registry_only",
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "app_dto": False,
        },
    )


def memory_identity_ref_index_snapshot(limit: int = 80) -> dict[str, Any]:
    """Read the Web-first CORE-015 IdentityMap/RefIndex candidate store."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    bounded = max(1, min(int(limit or 80), 300))
    index = MemoryIdentityRefIndex()
    return _receipt(
        action="memory.identity_ref_index.snapshot",
        success=True,
        dry_run=True,
        operator_mode=False,
        data={
            **index.snapshot(limit=bounded),
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "policy": (
                "Read-only Web review surface. IdentityMap owns UUID equivalence; "
                "RefIndex owns mutable locators; Graphiti Episodes remain provenance."
            ),
        },
    )


def draft_memory_identity_ref_index(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a durable IdentityMap/RefIndex upsert without writing the store."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    if not _identity_ref_payload_has_signal(body):
        return _receipt(
            action="memory.identity_ref_index.draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_identity_or_ref_signal",
                "required_any_of": [
                    "canonical_uuid",
                    "l2b_uuid",
                    "graphiti_uuid",
                    "graphiti_entity_uuid",
                    "graphiti_edge_uuid",
                    "graphiti_episode_uuid",
                    "obsidian_uuid",
                    "provider_key",
                    "ref_id",
                    "locator",
                    "path",
                    "url",
                ],
                "core_candidate": "CORE-015",
            },
        )

    index = MemoryIdentityRefIndex()
    identity, ref = index.upsert(body)
    return _receipt(
        action="memory.identity_ref_index.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "identity_draft": identity.to_dict(),
            "ref_draft": ref.to_dict() if ref is not None else None,
            "merge_report": index.last_upsert_report,
            "merge_policy": index.last_upsert_report.get("merge_policy", ""),
            "conflicts": index.last_upsert_report.get("conflicts", []),
            "conflict_count": index.last_upsert_report.get("conflict_count", 0),
            "would_save_path": str(index.path),
            "would_persist": False,
            "apply_route": "/api/memory/identity-ref-index/apply",
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "write_path": "MemoryIdentityRefIndex.upsert(payload).save()",
            "policy": (
                "Draft only. This does not mutate L2-B, Graphiti/FalkorDB, "
                "Obsidian, ECS files, or App DTOs."
            ),
        },
    )


def apply_memory_identity_ref_index(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply a CORE-015 IdentityMap/RefIndex upsert under Web operator mode."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_memory_identity_ref_index(
        {**body, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    draft["action"] = "memory.identity_ref_index.apply"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_persist"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    index = MemoryIdentityRefIndex()
    identity, ref = index.upsert(body)
    index.save()
    return _receipt(
        action="memory.identity_ref_index.apply",
        success=True,
        dry_run=False,
        operator_mode=True,
        data={
            "identity": identity.to_dict(),
            "ref": ref.to_dict() if ref is not None else None,
            "merge_report": index.last_upsert_report,
            "merge_policy": index.last_upsert_report.get("merge_policy", ""),
            "conflicts": index.last_upsert_report.get("conflicts", []),
            "conflict_count": index.last_upsert_report.get("conflict_count", 0),
            "snapshot": index.snapshot(limit=80),
            "mutated": True,
            "mutation_scope": "memory_identity_ref_index_json_only",
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "app_dto": False,
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
        },
    )


def draft_graphiti_ref_writeback(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft the M14 GraphitiRecordRef -> ExternalRefRecord binding plan."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    index = MemoryIdentityRefIndex()
    plan = index.upsert_graphiti_ref_writeback(body)
    if not plan.get("ok"):
        return _receipt(
            action="memory.identity_ref_index.graphiti_ref_writeback_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                **plan,
                "path": str(index.path),
                "core_candidate": "CORE-015",
                "shared_status": "candidate_only",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_file_move": False,
                "app_dto": False,
            },
        )
    return _receipt(
        action="memory.identity_ref_index.graphiti_ref_writeback_draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            **plan,
            "path": str(index.path),
            "would_persist": False,
            "apply_route": "/api/memory/identity-ref-index/graphiti-ref/apply",
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "mutated": False,
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "app_dto": False,
            "operator_required_for_execute": True,
            "policy": (
                "Draft only. GraphitiRecordRef and ExternalRefRecord are reviewed "
                "together; Graphiti audit Episode is returned as a draft."
            ),
        },
    )


async def apply_graphiti_ref_writeback(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Persist an M14 Graphiti/ref binding under Web operator mode.

    The default apply only writes the IdentityRefIndex JSON. Graphiti audit
    Episode writing is opt-in through ``write_graphiti_audit_episode`` so the
    operator can review the generated Episode body first.
    """

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    preview = draft_graphiti_ref_writeback(
        {**body, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    preview["action"] = "memory.identity_ref_index.graphiti_ref_writeback_apply"
    if not preview.get("success"):
        return preview
    preview_data = preview.get("data") if isinstance(preview.get("data"), dict) else {}
    if dry_run or not operator_mode:
        preview_data["would_persist"] = True
        preview_data["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        preview_data["mutated"] = False
        return preview

    index = MemoryIdentityRefIndex()
    plan = index.upsert_graphiti_ref_writeback(body)
    if not plan.get("ok"):
        return _receipt(
            action="memory.identity_ref_index.graphiti_ref_writeback_apply",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={
                **plan,
                "path": str(index.path),
                "core_candidate": "CORE-015",
                "shared_status": "candidate_only",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_file_move": False,
                "app_dto": False,
            },
        )
    index.save()
    graphiti_audit = await _maybe_write_graphiti_ref_audit_episode(body, plan)
    direct_graphiti_write = bool(graphiti_audit.get("written"))
    mutation_scope = (
        "memory_identity_ref_index_json_and_graphiti_audit_episode"
        if direct_graphiti_write
        else "memory_identity_ref_index_json_only"
    )
    return _receipt(
        action="memory.identity_ref_index.graphiti_ref_writeback_apply",
        success=True,
        dry_run=False,
        operator_mode=True,
        data={
            **plan,
            "path": str(index.path),
            "snapshot": index.snapshot(limit=80),
            "would_persist": True,
            "persisted": True,
            "mutated": True,
            "mutation_scope": mutation_scope,
            "graphiti_audit_episode": graphiti_audit,
            "graphiti_audit_episode_written": direct_graphiti_write,
            "direct_l2b_write": False,
            "direct_graphiti_write": direct_graphiti_write,
            "direct_file_move": False,
            "app_dto": False,
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "write_path": "MemoryIdentityRefIndex.upsert_graphiti_ref_writeback(payload).save()",
        },
    )


def verify_memory_identity_ref_index(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify IdentityRefIndex ref health without touching external systems."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    update_index = _body_bool(body.get("update_index"), False)
    should_update = bool(update_index and not dry_run and operator_mode)
    index = MemoryIdentityRefIndex()
    result = index.verify(
        graphiti_uuid_statuses=_bool_status_map(body.get("graphiti_uuid_statuses")),
        obsidian_uuid_statuses=_bool_status_map(body.get("obsidian_uuid_statuses")),
        update=should_update,
    )
    if should_update:
        index.save()
    return _receipt(
        action="memory.identity_ref_index.verify",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            **result,
            "path": str(index.path),
            "would_update_index": update_index,
            "updated_index": should_update,
            "apply_skipped_reason": (
                "" if should_update or not update_index else "dry_run_or_operator_mode_missing"
            ),
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "policy": (
                "Deterministic verifier: local paths are checked directly; URLs, ECS, "
                "and remote UUIDs are unknown unless an explicit status map is supplied."
            ),
        },
    )


def resolve_graphiti_identity_ref_index(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve Graphiti fact endpoints through CORE-015 without graph mutation."""

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    index = MemoryIdentityRefIndex()
    result = index.resolve_graphiti_subgraph(body)
    has_edges = bool(result.get("edge_count"))
    return _receipt(
        action="memory.identity_ref_index.resolve_graphiti",
        success=has_edges,
        dry_run=True,
        operator_mode=False,
        data={
            **result,
            "path": str(index.path),
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "mutated": False,
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "app_dto": False,
            "apply_route": "/api/memory/identity-ref-index/apply-graphiti-edge",
            "low_level_apply_route": "/api/l2b/edge",
            "apply_preconditions": {
                "dry_run": False,
                "operator_mode": True,
                "source": "resolved_l2b",
                "target": "resolved_l2b",
            },
            "error": "" if has_edges else "missing_graphiti_edge_signal",
            "policy": (
                "Read-only GraphitiResolver preview. It resolves endpoints "
                "through IdentityRefIndex and never materializes L2-B edges."
            ),
        },
    )


async def apply_graphiti_identity_ref_edge(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Materialize one resolved Graphiti fact edge into the L2-B graph.

    This is the operator path for the CORE-015 GraphitiResolver preview. It
    deliberately re-resolves the Graphiti endpoints before writing, then uses
    the existing ``apply_l2b_edge`` / ``L2BGraph.connect`` path so RustWorkX
    topology ownership stays in one place.
    """

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    index = MemoryIdentityRefIndex()
    resolver_result = index.resolve_graphiti_subgraph(body)
    selected_edge = _select_resolved_graphiti_edge(resolver_result, body)
    if selected_edge is None:
        error = (
            "selected_graphiti_edge_not_found"
            if resolver_result.get("edge_count") and _graphiti_edge_index_requested(body)
            else "missing_graphiti_edge_signal"
        )
        return _receipt(
            action="memory.identity_ref_index.apply_graphiti_edge",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                **resolver_result,
                "path": str(index.path),
                "error": error,
                "core_candidate": "CORE-015",
                "shared_status": "candidate_only",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_file_move": False,
                "app_dto": False,
            },
        )

    if selected_edge.get("can_materialize_l2b_edge") is not True:
        return _receipt(
            action="memory.identity_ref_index.apply_graphiti_edge",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "path": str(index.path),
                "resolver": resolver_result,
                "selected_edge": selected_edge,
                "selected_edge_index": selected_edge.get("index", 0),
                "error": "unresolved_graphiti_edge_endpoints",
                "blocked_reasons": selected_edge.get("blocked_reasons") or [],
                "would_apply": False,
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_file_move": False,
                "app_dto": False,
                "core_candidate": "CORE-015",
                "shared_status": "candidate_only",
                "policy": "L2-B edge materialization requires resolved_l2b source and target.",
            },
        )

    l2b_payload = _graphiti_l2b_edge_apply_payload(body, resolver_result, selected_edge)
    l2b_apply = await apply_l2b_edge(
        {**l2b_payload, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    l2b_data = l2b_apply.get("data") if isinstance(l2b_apply.get("data"), dict) else {}
    connected = bool(l2b_apply.get("success") and l2b_data.get("connected") is True)
    skipped_reason = str(l2b_data.get("apply_skipped_reason") or "")
    write_failed = bool(
        operator_mode
        and not dry_run
        and not connected
        and not l2b_data.get("would_apply")
    )
    return _receipt(
        action="memory.identity_ref_index.apply_graphiti_edge",
        success=bool(l2b_apply.get("success")),
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "path": str(index.path),
            "resolver": resolver_result,
            "selected_edge": selected_edge,
            "selected_edge_index": selected_edge.get("index", 0),
            "l2b_edge_payload": l2b_payload,
            "l2b_apply_receipt": l2b_apply,
            "would_apply": bool(l2b_data.get("would_apply")),
            "apply_skipped_reason": skipped_reason,
            "connected": connected,
            "mutated": connected,
            "mutation_scope": "l2b_rustworkx_graph_only" if connected else "none",
            "direct_l2b_write": connected,
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "app_dto": False,
            "error": "l2b_edge_connect_failed" if write_failed else "",
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "operator_required_for_execute": True,
            "write_path": (
                "MemoryIdentityRefIndex.resolve_graphiti_subgraph -> "
                "apply_l2b_edge -> L2BGraph.connect(SemanticEdge)"
            ),
        },
    )


def draft_memory_ref_scan_plan(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a Nanobot/MCP ref scan job for CORE-015 managed refs.

    The route is intentionally plan-only. It does not stat files, call remote
    ECS, query Graphiti, or write the proposed manifest. Nanobot can later run
    this contract through MCP tools and report results back for operator review.
    """

    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    body = payload or {}
    limit, limit_error = _body_int_limit(body.get("limit"), default=80, maximum=300)
    if limit_error:
        return _receipt(
            action="memory.identity_ref_index.ref_scan_plan",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": "invalid_limit",
                "limit_error": limit_error,
                "core_candidate": "CORE-015",
                "shared_status": "candidate_only",
                "mutated": False,
            },
        )

    index = MemoryIdentityRefIndex()
    manifest_path = _ref_scan_manifest_path(body.get("manifest_path"))
    git_root = _ref_scan_git_root(body.get("git_root"))
    result_channel = str(body.get("result_channel") or "memory_ref_scan_result")
    remote_checks = _ref_scan_remote_checks(body)
    ecs_local_check_confirmed = _body_bool(body.get("ecs_local_check_confirmed"), False)
    refs = sorted(
        index.refs.values(),
        key=lambda item: (str(getattr(item, "kind", "")), str(getattr(item, "ref_id", ""))),
    )[:limit]
    rows = [
        _ref_scan_plan_row(ref, index=index, manifest_path=manifest_path)
        for ref in refs
    ]
    counts = _ref_scan_counts(rows)
    scan_id = f"refscan_{uuid.uuid4().hex[:12]}"
    params = {
        "scan_id": scan_id,
        "schema_version": 1,
        "source": "web_console",
        "dry_run": True,
        "source_index_path": str(index.path),
        "manifest_path": str(manifest_path),
        "git_root": str(git_root),
        "limit": limit,
        "result_channel": result_channel,
        "scan_mode": "read_only",
        "allow_mutation": False,
        "remote_checks": remote_checks,
        "enable_url_check": "url" in remote_checks,
        "enable_ecs_local_check": "ecs" in remote_checks and ecs_local_check_confirmed,
        "ecs_local_check_confirmed": ecs_local_check_confirmed,
        "enable_graphiti_probe": "graphiti" in remote_checks,
        "network_timeout_s": _body_float(body.get("network_timeout_s"), 3.0),
        "operator_review_required_for_repair": True,
        "refs": [_ref_scan_task_ref(row) for row in rows],
        "allowed_ops": [
            "identity_ref_index_read",
            "filesystem_stat",
            "filesystem_hash",
            "http_head",
            "ecs_path_stat",
            "git_manifest_diff",
            "graphiti_uuid_probe",
            "obsidian_frontmatter_uuid_probe",
        ],
        "disallowed_ops": [
            "file_move",
            "file_delete",
            "manifest_write",
            "identity_ref_index_write",
            "graphiti_mutation",
            "l2b_mutation",
            "ecs_write",
        ],
    }
    return _receipt(
        action="memory.identity_ref_index.ref_scan_plan",
        success=True,
        dry_run=True,
        operator_mode=False,
        data={
            "task_type": "ref_scan",
            "priority": str(body.get("priority") or "normal"),
            "params": params,
            "ref_scan_plan": rows,
            "counts": counts,
            "source_index_path": str(index.path),
            "git_manifest": {
                "manifest_path": str(manifest_path),
                "git_root": str(git_root),
                "diff_policy": "compare_previous_manifest_and_git_status",
                "write_policy": "propose_manifest_delta_only",
                "apply_policy": "operator_review_then_git_commit",
                "nanobot_may_write": False,
            },
            "result_flow": (
                "Web draft -> Scheduler/Nanobot ref_scan -> MCP checks -> "
                f"{result_channel} -> IdentityRefIndex verify/apply review"
            ),
            "operator_required_for_dispatch": True,
            "dispatch_route": "/api/memory/identity-ref-index/ref-scan-dispatch",
            "result_history_route": "/api/memory/identity-ref-index/ref-scan-results",
            "preserved_ref_fields": [
                "ref_id",
                "kind",
                "canonical_uuid",
                "canonical_uri",
                "locators",
                "content_hash",
                "size",
                "mime_type",
                "version",
                "valid_from",
                "valid_to",
                "health",
                "managed_by",
                "git_commit",
                "meta",
            ],
            "mutated": False,
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "direct_ecs_write": False,
            "app_dto": False,
            "remote_checks": remote_checks,
            "remote_check_policy": {
                "default": "disabled",
                "enabled_by_operator": remote_checks,
                "mutation_allowed": False,
                "graphiti_lookup_mode": "search_probe_until_uuid_crud_route_exists",
                "ecs_mode": "local_read_only_stat_when_worker_runs_on_ecs",
                "url_mode": "HEAD_only_no_body_read",
            },
            "core_candidate": "CORE-015",
            "shared_status": "candidate_only",
            "policy": (
                "Plan-only contract. It classifies refs and proposes Nanobot/MCP "
                "checks but performs no IO beyond reading the IdentityRefIndex."
            ),
        },
    )


async def dispatch_memory_ref_scan_plan(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dispatch a read-only CORE-015 ref scan task under operator mode."""

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_memory_ref_scan_plan(body)
    draft["action"] = "memory.identity_ref_index.ref_scan_dispatch"
    draft["dry_run"] = dry_run
    draft["operator_mode"] = operator_mode
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_dispatch"] = True
        draft["data"]["dispatch_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    try:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        params = dict(draft["data"]["params"])
        params["scan_mode"] = "read_only"
        params["allow_mutation"] = False
        task_id = await do_dispatch_task(
            "ref_scan",
            params=params,
            priority=draft["data"]["priority"],
        )
        return _receipt(
            action="memory.identity_ref_index.ref_scan_dispatch",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={
                **draft["data"],
                "params": params,
                "task_id": task_id,
                "dispatched": True,
                "mutation_scope": "scheduler_nanobot_queue_only",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_file_move": False,
                "direct_ecs_write": False,
                "app_dto": False,
                "result_history_route": "/api/memory/identity-ref-index/ref-scan-results",
            },
        )
    except Exception as exc:
        return _receipt(
            action="memory.identity_ref_index.ref_scan_dispatch",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "error": f"{type(exc).__name__}: {exc}"},
        )


async def memory_ref_scan_result_history(limit: int = 20) -> dict[str, Any]:
    """Read recent Scheduler-ledger results for CORE-015 ref scan tasks."""

    limit, limit_error = _body_int_limit(limit, default=20, maximum=50)
    if limit_error:
        return _receipt(
            action="memory.identity_ref_index.ref_scan_results",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={"rows": [], "error": limit_error},
        )

    from parrot.shared.constants import CH_TRIGGER_RESULTS, STREAM_TRIGGER_RESULTS

    try:
        from parrot.shared.redis_client import get_redis

        redis = await get_redis()
        raw_rows = await redis.xrevrange(STREAM_TRIGGER_RESULTS, count=limit * 3)
    except Exception as exc:
        return _receipt(
            action="memory.identity_ref_index.ref_scan_results",
            success=True,
            dry_run=True,
            operator_mode=False,
            data={
                "available": False,
                "stream": STREAM_TRIGGER_RESULTS,
                "channel": CH_TRIGGER_RESULTS,
                "rows": [],
                "error": f"{type(exc).__name__}: {exc}",
            },
        )

    rows: list[dict[str, Any]] = []
    for stream_id, fields in raw_rows:
        if not isinstance(fields, dict):
            continue
        row = _ref_scan_result_history_row(str(stream_id), fields)
        if row:
            rows.append(row)
        if len(rows) >= limit:
            break

    return _receipt(
        action="memory.identity_ref_index.ref_scan_results",
        success=True,
        dry_run=True,
        operator_mode=False,
        data={
            "available": True,
            "stream": STREAM_TRIGGER_RESULTS,
            "channel": CH_TRIGGER_RESULTS,
            "rows": rows,
            "count": len(rows),
            "read_model": "Scheduler trigger-result ledger",
            "result_channel": "memory_ref_scan_result",
            "web_only": True,
            "apply_policy": "operator_review_then_identity_ref_verify_or_apply",
        },
    )


def scan_obsidian_vault(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Scan an Obsidian vault and preview L1.5-ready note payloads.

    This is a Web-only read surface for the Source Board. It deliberately stops
    before publishing ``obsidian_note`` events: the operator should inspect the
    profile, UUID policy, target bucket, and payload before a later import
    action sends anything through the trigger bus.
    """
    from parrot.brain.obsidian_vault import (
        check_obsidian_vault,
        collect_markdown_files,
        note_to_ingest_payload,
    )

    body = payload or {}
    vault = _default_obsidian_vault_path(body.get("vault_path"))
    limit, limit_error = _body_int_limit(body.get("limit"), default=24, maximum=80)
    if limit_error:
        return _receipt(
            action="l15.obsidian_vault.scan",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": limit_error,
                "vault": {"vault_path": str(vault), "status": "not_scanned"},
                "notes": [],
                "invalid_notes": [],
                "profiles": _obsidian_profile_descriptions(),
                "operator_required_for_import": True,
            },
        )
    check = check_obsidian_vault(vault, sample_limit=min(limit, 12))
    notes: list[dict[str, Any]] = []
    invalid_notes: list[dict[str, Any]] = []
    selected_paths = _obsidian_selected_paths(body.get("paths") or body.get("selected_paths"))
    seen_selected_paths: set[str] = set()
    invalid_preview_limit = min(limit, 24)
    if vault.exists():
        for path in collect_markdown_files(vault):
            rel_path = _relative_path(path, vault)
            is_selected_path = rel_path in selected_paths
            if is_selected_path:
                seen_selected_paths.add(rel_path)
            if (
                not selected_paths
                and len(notes) >= limit
                and len(invalid_notes) >= invalid_preview_limit
            ):
                break
            payload_row = note_to_ingest_payload(path)
            if payload_row is None:
                if is_selected_path or len(invalid_notes) < invalid_preview_limit:
                    invalid_notes.append({
                        "path": rel_path,
                        "reason": "missing_frontmatter_or_ref_target",
                    })
                continue
            if len(notes) >= limit and not is_selected_path:
                continue
            profile = str(payload_row.get("profile") or "daily")
            notes.append({
                "path": rel_path,
                "profile": profile,
                "label": str(payload_row.get("label") or path.stem),
                "obsidian_uuid": str(payload_row.get("obsidian_uuid") or ""),
                "obsidian_note_key": str(payload_row.get("obsidian_note_key") or ""),
                "target_bucket": _obsidian_profile_target(profile),
                "uuid_free_allowed": profile in {"daily", "roleplay"},
                "import_ready": True,
                "payload": payload_row,
            })
            if selected_paths and selected_paths <= seen_selected_paths:
                break

    return _receipt(
        action="l15.obsidian_vault.scan",
        success=check.status != "missing_path",
        dry_run=True,
        operator_mode=False,
        data={
            "vault": _jsonable(check),
            "notes": notes,
            "invalid_notes": invalid_notes,
            "profiles": _obsidian_profile_descriptions(),
            "operator_required_for_import": True,
        },
    )


def draft_graphiti_l2b_import_plan(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build one reviewable plan for Graphiti -> L2-B pointer materialization.

    Graphiti export and graph-placement policy used to be two separate UI
    previews. Keeping them separate made the operator experience feel fake:
    the Source Board could show observations or a destination policy, but not
    one coherent import route. This Web-only wrapper still exposes the legacy
    L1.5 observation draft, but the apply path now points at the reviewed L2-B
    materializer so Graphiti raw data remains authoritative and queryable.
    """

    from parrot.brain.graphiti_console import draft_graphiti_subgraph_export
    from parrot.web_console.graph_policy import (
        draft_graphiti_bundle_projection,
        draft_import_destination,
    )

    body = payload or {}
    requested_execution = {
        "dry_run": _body_bool(body.get("dry_run"), True),
        "operator_mode": _body_bool(body.get("operator_mode"), False),
        "ignored_for_plan": True,
    }
    dry_run = True
    operator_mode = False
    raw_partition = str(body.get("partition") or "goslo").strip() or "goslo"
    partition = raw_partition
    query = str(body.get("query") or "").strip()

    export_draft = draft_graphiti_subgraph_export(
        {**body, "dry_run": True, "operator_mode": False}
    )
    export_data = dict(export_draft.get("data") or {})
    partition = str(export_data.get("partition") or raw_partition).strip() or raw_partition
    observations = [
        row for row in export_data.get("observations", []) if isinstance(row, dict)
    ]
    edge_drafts = [
        row for row in export_data.get("edge_drafts", []) if isinstance(row, dict)
    ]
    raw_envelopes = [
        row for row in export_data.get("graphiti_raw_envelopes", []) if isinstance(row, dict)
    ]
    graphiti_bundle = (
        dict(export_data.get("graphiti_bundle"))
        if isinstance(export_data.get("graphiti_bundle"), dict)
        else {}
    )
    identity_ref_drafts = [
        row for row in export_data.get("identity_ref_drafts", []) if isinstance(row, dict)
    ]
    item_ids = [
        str(
            row.get("graphiti_uuid")
            or row.get("provenance_stream_id")
            or row.get("label")
            or index
        )
        for index, row in enumerate(observations)
    ]
    proposed_edges = [
        {
            "source": row.get("source_graphiti_uuid"),
            "target": row.get("target_graphiti_uuid"),
            "kind": row.get("kind") or "graphiti_fact",
            "strength": row.get("strength"),
            "label": row.get("label"),
            "source_graphiti_uuid": row.get("source_graphiti_uuid"),
            "target_graphiti_uuid": row.get("target_graphiti_uuid"),
            "hit_graphiti_uuid": row.get("hit_graphiti_uuid"),
            "write_policy": row.get("write_policy"),
            "edge_source": "graphiti",
            "meta": row.get("meta") if isinstance(row.get("meta"), dict) else {},
        }
        for row in edge_drafts
    ]
    policy_receipt: dict[str, Any] | None = None
    policy_skipped_reason = ""
    if observations:
        policy_receipt = draft_import_destination(
            {
                "destination": body.get("destination") or "isolated_compartment",
                "source_kind": "graphiti",
                "source_id": body.get("source_id") or f"{partition}:{query or 'search'}",
                "workspace_id": body.get("workspace_id") or "memory_graph",
                "subgraph_id": body.get("subgraph_id") or "",
                "subgraph_label": body.get("subgraph_label") or query or partition,
                "item_ids": item_ids,
                "proposed_edges": proposed_edges,
                "dry_run": True,
                "operator_mode": False,
            }
        )
    else:
        # Empty imports must not display a plausible graph placement policy.
        policy_skipped_reason = "no_graphiti_observations"
    policy_data = dict((policy_receipt or {}).get("data") or {})
    policy_success = bool(policy_receipt and policy_receipt.get("success"))
    success = bool(export_draft.get("success")) and bool(observations) and policy_success
    transform_receipt: dict[str, Any] | None = None
    transform_data: dict[str, Any] = {}
    if graphiti_bundle:
        transform_receipt = draft_graphiti_bundle_projection(
            {
                "graphiti_bundle": graphiti_bundle,
                "partition": partition,
                "query": query,
                "destination": body.get("destination") or "isolated_compartment",
                "subgraph_id": body.get("subgraph_id") or "",
                "label": body.get("subgraph_label") or query or partition,
                "dry_run": True,
                "operator_mode": False,
            }
        )
        transform_data = dict(transform_receipt.get("data") or {})
    if graphiti_bundle:
        graphiti_bundle["import_overlay"] = {
            "destination": body.get("destination") or "isolated_compartment",
            "source_kind": "graphiti",
            "materialization_state": "preview_only_not_materialized",
            "import_policy": policy_data.get("policy", {}),
            "import_draft": policy_data.get("draft", {}),
            "transform_preview": transform_data,
            "policy_skipped_reason": policy_skipped_reason,
            "l15_export_route": "/api/graphiti/subgraph/export",
            "apply_route": "/api/graphiti/subgraph/materialize-l2b",
            "apply_preconditions": {
                "dry_run": False,
                "operator_mode": True,
                "materialize_l2b": "reviewed Graphiti bundle projection writes deterministic pointer nodes/edges",
                "preserve_raw_graphiti": True,
            },
            "context_route_policy": {
                "route": "/api/l2b/subgraphs/context",
                "requires_materialized_l2b_uuid": True,
                "preview_uuid_prefix": "graphiti:",
                "preview_uuid_status": "not_queryable_until_l2b_materialization",
            },
        }
    return _receipt(
        action="graphiti.subgraph.import_plan",
        success=success,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "partition": partition,
            "query": query,
            "selected_count": len(observations),
            "observations": observations,
            "edge_drafts": edge_drafts,
            "graphiti_raw_envelopes": raw_envelopes,
            "graphiti_bundle": graphiti_bundle,
            "identity_ref_drafts": identity_ref_drafts,
            "identity_ref_write_policy": export_data.get("identity_ref_write_policy", ""),
            "subgraph": export_data.get("subgraph", {}),
            "export_write_path": export_data.get(
                "write_path",
                "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            ),
            "edge_write_policy": export_data.get("edge_write_policy", ""),
            "import_policy": policy_data.get("policy", {}),
            "import_draft": policy_data.get("draft", {}),
            "l2b_transform_preview": transform_data,
            "transform_receipt_id": str(
                ((transform_receipt or {}).get("receipt") or {}).get("receipt_id", "")
            ),
            "direct_graphiti_write": False,
            "direct_l2b_write": False,
            "materialization_state": "preview_only_not_materialized",
            "context_route_policy": {
                "route": "/api/l2b/subgraphs/context",
                "requires_materialized_l2b_uuid": True,
                "preview_uuid_prefix": "graphiti:",
                "preview_uuid_status": "not_queryable_until_l2b_materialization",
                "reason": "import-plan returns Graphiti bundle projection UUIDs; live context reads get_l2b_graph() by durable L2-B UUID only.",
            },
            "policy_skipped_reason": policy_skipped_reason,
            "flow_steps": [
                "Graphiti.search scoped by partition",
                "operator selects hits",
                "draft Observation(source=USER_EXPLICIT) rows",
                "preview CORE-013 import destination / overlay policy",
                "preview Graphiti bundle -> L2-B/RustWorkX projection without persisting rwx indices",
                "operator materializes deterministic Graphiti pointer subgraph into L2-B",
            ],
            "operator_required_for_execute": True,
            "l15_export_route": "/api/graphiti/subgraph/export",
            "apply_route": "/api/graphiti/subgraph/materialize-l2b",
            "apply_preconditions": {
                "dry_run": False,
                "operator_mode": True,
                "materialize_l2b": "reviewed Graphiti bundle projection writes deterministic pointer nodes/edges",
                "preserve_raw_graphiti": True,
            },
            "warnings": list(export_data.get("warnings") or []),
            "core_candidates": ["CORE-008", "CORE-013", "CORE-015"],
            "requested_execution": requested_execution,
            "policy_receipt_id": ((policy_receipt or {}).get("receipt") or {}).get(
                "receipt_id",
                "",
            ),
            "export_receipt_id": str(
                export_draft.get("receipt_id")
                or (export_draft.get("receipt") or {}).get("receipt_id", "")
            ),
        },
    )


def materialize_graphiti_l2b_subgraph(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Materialize a reviewed Graphiti bundle projection into live L2-B.

    This is the operator apply companion to ``draft_graphiti_l2b_import_plan``.
    Graphiti remains the authoritative temporal/provenance graph; L2-B receives
    deterministic pointer nodes and reviewed local topology so subgraph/context
    tools can traverse the result. The route never writes Graphiti/FalkorDB.
    """

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    if _remote_operator_base_url() and not _body_bool(body.get("_remote_proxy_disable"), False):
        remote_payload = dict(body)
        remote_payload["_remote_proxy_disable"] = True
        remote = _remote_operator_request(
            "/api/graphiti/subgraph/materialize-l2b",
            payload=remote_payload,
        )
        if isinstance(remote, dict) and remote.get("action"):
            remote_data = dict(remote.get("data") or {})
            remote_data["remote_proxy"] = {
                "enabled": bool(remote.get("success")),
                "base_url": _remote_operator_base_url(),
                "reason": "web_console_l2b_remote_url_configured",
                "error": remote.get("error") or "",
            }
            remote["data"] = remote_data
            return remote

    projection = _graphiti_l2b_materialization_projection(body)
    if not projection.get("success"):
        return _receipt(
            action="graphiti.subgraph.materialize_l2b",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                **projection,
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "operator_required_for_execute": True,
            },
        )

    transform = dict(projection.get("transform_preview") or {})
    l2b_nodes = [row for row in transform.get("l2b_nodes", []) if isinstance(row, dict)]
    l2b_edges = [row for row in transform.get("l2b_edges", []) if isinstance(row, dict)]
    episode_links = [row for row in transform.get("episode_links", []) if isinstance(row, dict)]
    edge_rows = [*l2b_edges, *episode_links]
    identity_payloads = _graphiti_l2b_identity_payloads(
        l2b_nodes=l2b_nodes,
        fact_pointers=[
            row for row in transform.get("fact_pointers", []) if isinstance(row, dict)
        ],
        edge_rows=edge_rows,
        partition=str(projection.get("partition") or body.get("partition") or "goslo"),
    )
    base_data = {
        **projection,
        "l2b_nodes": l2b_nodes,
        "l2b_edges": l2b_edges,
        "episode_links": episode_links,
        "node_count": len(l2b_nodes),
        "edge_count": len(edge_rows),
        "node_uuids": [str(row.get("uuid") or "") for row in l2b_nodes if row.get("uuid")],
        "operator_required_for_execute": True,
        "context_route": "/api/l2b/subgraphs/context",
        "context_node_uuids": [
            str(row.get("uuid") or "") for row in l2b_nodes[:8] if row.get("uuid")
        ],
        "identity_ref_index_would_write": bool(identity_payloads),
        "identity_ref_index_payload_count": len(identity_payloads),
        "materialization_policy": {
            "node_uuid_policy": "deterministic_graphiti_pointer_uuid",
            "preserve_raw_graphiti": True,
            "edge_dedupe_key": "source,target,kind,edge_source,graphiti_uuid",
            "graphiti_write": "never",
            "falkordb_write": "never",
        },
    }
    if dry_run or not operator_mode:
        return _receipt(
            action="graphiti.subgraph.materialize_l2b",
            success=True,
            dry_run=True,
            operator_mode=False,
            data={
                **base_data,
                "would_materialize": True,
                "apply_skipped_reason": "dry_run_or_operator_mode_missing",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_falkordb_write": False,
                "identity_ref_index_write": False,
            },
        )

    try:
        from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex
        from parrot.dsg.l2b_graph import (
            get_l2b_graph,
            persist_materialized_graphiti_pointers,
        )

        graph = get_l2b_graph()
        before_nodes = graph.node_count()
        before_edges = len(graph.all_edges())
        node_reports = [_materialize_graphiti_l2b_node(graph, row) for row in l2b_nodes]
        existing_edge_keys = _existing_l2b_edge_keys(graph)
        edge_reports = [
            _materialize_graphiti_l2b_edge(graph, row, existing_edge_keys)
            for row in edge_rows
        ]
        identity_reports: list[dict[str, Any]] = []
        identity_write = _body_bool(body.get("write_identity_ref_index"), True)
        if identity_write and identity_payloads:
            index = MemoryIdentityRefIndex()
            for identity_payload in identity_payloads:
                identity, ref = index.upsert(identity_payload)
                identity_reports.append({
                    "canonical_uuid": identity.canonical_uuid,
                    "l2b_uuid": identity.l2b_uuid,
                    "ref_id": ref.ref_id if ref is not None else "",
                    "conflict_count": index.last_upsert_report.get("conflict_count", 0),
                })
            index.save()
        after_nodes = graph.node_count()
        after_edges = len(graph.all_edges())
        nodes_upserted = sum(1 for row in node_reports if row.get("upserted"))
        edges_added = sum(1 for row in edge_reports if row.get("connected"))
        edges_skipped = sum(1 for row in edge_reports if row.get("skipped_duplicate"))
        persistence_report: dict[str, Any]
        try:
            store_path = persist_materialized_graphiti_pointers(graph)
            persistence_report = {
                "persisted": True,
                "path": str(store_path),
                "store_kind": "l2b_materialized_graphiti_pointers",
                "rwx_indices_persisted": False,
            }
        except Exception as persist_exc:
            persistence_report = {
                "persisted": False,
                "error": f"{type(persist_exc).__name__}: {persist_exc}",
                "store_kind": "l2b_materialized_graphiti_pointers",
                "rwx_indices_persisted": False,
            }
        return _receipt(
            action="graphiti.subgraph.materialize_l2b",
            success=bool(l2b_nodes) and all(row.get("ok") for row in node_reports),
            dry_run=False,
            operator_mode=True,
            data={
                **base_data,
                "would_materialize": False,
                "mutated": True,
                "direct_l2b_write": True,
                "direct_graphiti_write": False,
                "direct_falkordb_write": False,
                "identity_ref_index_write": bool(identity_write and identity_payloads),
                "persistent_l2b_pointer_store": persistence_report,
                "nodes_upserted": nodes_upserted,
                "edges_added": edges_added,
                "edges_skipped_duplicate": edges_skipped,
                "node_reports": node_reports,
                "edge_reports": edge_reports,
                "identity_ref_index_reports": identity_reports,
                "before": {"node_count": before_nodes, "edge_count": before_edges},
                "after": {"node_count": after_nodes, "edge_count": after_edges},
                "materialization_state": "materialized_l2b_pointer_graph",
            },
        )
    except Exception as exc:
        return _receipt(
            action="graphiti.subgraph.materialize_l2b",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={
                **base_data,
                "error": f"{type(exc).__name__}: {exc}",
                "mutated": False,
                "direct_l2b_write": False,
                "direct_graphiti_write": False,
                "direct_falkordb_write": False,
            },
        )


def _remote_operator_base_url() -> str:
    raw = (
        os.getenv("PARROT_WEB_CONSOLE_L2B_URL")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_URL")
        or os.getenv("PARROT_GRAPHITI_REMOTE_URL")
        or ""
    )
    return str(raw).strip().rstrip("/")


def _remote_operator_timeout_s() -> float:
    raw = (
        os.getenv("PARROT_WEB_CONSOLE_L2B_TIMEOUT_S")
        or os.getenv("PARROT_WEB_CONSOLE_GRAPHITI_TIMEOUT_S")
        or os.getenv("PARROT_GRAPHITI_REMOTE_TIMEOUT_S")
        or "30"
    )
    try:
        parsed = float(raw)
    except (TypeError, ValueError):
        parsed = 30.0
    return max(0.5, min(parsed, 300.0))


def _remote_operator_request(
    path: str,
    *,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Proxy operator Graphiti/L2-B calls from the local Web Console to ECS."""

    base_url = _remote_operator_base_url()
    if not base_url:
        return {"success": False, "action": "remote.operator.proxy", "error": "missing_remote_url"}
    url = f"{base_url}/{path.lstrip('/')}"
    data: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=_remote_operator_timeout_s()) as response:
            raw = response.read().decode("utf-8", errors="replace")
        parsed = json.loads(raw) if raw else {}
        if isinstance(parsed, dict):
            return parsed
        return {"success": False, "action": "remote.operator.proxy", "error": "non_object_json", "raw": parsed}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "success": False,
            "action": "remote.operator.proxy",
            "error": f"{type(exc).__name__}: {exc}",
            "url": url,
        }


def _graphiti_l2b_materialization_projection(body: dict[str, Any]) -> dict[str, Any]:
    """Return the same Graphiti bundle projection used by import-plan previews."""

    from parrot.web_console.graph_policy import draft_graphiti_bundle_projection

    partition = str(body.get("partition") or "goslo").strip() or "goslo"
    query = str(body.get("query") or "").strip()
    bundle = body.get("graphiti_bundle") or body.get("bundle")
    if isinstance(bundle, dict) and bundle:
        projection_receipt = draft_graphiti_bundle_projection(
            {
                "graphiti_bundle": bundle,
                "partition": str(body.get("partition") or bundle.get("partition") or partition),
                "query": query or str(bundle.get("query") or ""),
                "destination": body.get("destination") or "isolated_compartment",
                "subgraph_id": body.get("subgraph_id") or "",
                "label": body.get("subgraph_label") or query or partition,
                "dry_run": True,
                "operator_mode": False,
            }
        )
        data = dict(projection_receipt.get("data") or {})
        return {
            "success": bool(projection_receipt.get("success")),
            "partition": data.get("partition") or partition,
            "query": data.get("query") or query,
            "selected_count": _graphiti_bundle_selected_count(bundle, data),
            "graphiti_bundle": bundle,
            "transform_preview": data,
            "transform_receipt_id": str((projection_receipt.get("receipt") or {}).get("receipt_id", "")),
            "projection_source": "graphiti_bundle_payload",
        }

    plan = draft_graphiti_l2b_import_plan(
        {**body, "dry_run": True, "operator_mode": False}
    )
    data = dict(plan.get("data") or {})
    transform = dict(data.get("l2b_transform_preview") or {})
    return {
        "success": bool(plan.get("success")) and bool(transform),
        "partition": data.get("partition") or partition,
        "query": data.get("query") or query,
        "selected_count": data.get("selected_count", 0),
        "observations": data.get("observations", []),
        "edge_drafts": data.get("edge_drafts", []),
        "graphiti_bundle": data.get("graphiti_bundle", {}),
        "identity_ref_drafts": data.get("identity_ref_drafts", []),
        "subgraph": data.get("subgraph", {}),
        "transform_preview": transform,
        "source_import_plan_receipt_id": str((plan.get("receipt") or {}).get("receipt_id", "")),
        "transform_receipt_id": str(data.get("transform_receipt_id") or ""),
        "projection_source": "import_plan_preview",
    }


def _graphiti_bundle_selected_count(
    bundle: dict[str, Any],
    transform_data: dict[str, Any],
) -> int:
    """Return selected hits for a bundle without treating episode-only bundles as empty."""

    selection = bundle.get("selection") if isinstance(bundle.get("selection"), dict) else {}
    raw_selected = selection.get("selected_count") if isinstance(selection, dict) else None
    try:
        selected = int(raw_selected)
    except (TypeError, ValueError):
        selected = -1
    if selected >= 0:
        return selected

    section_counts = (
        transform_data.get("section_counts")
        if isinstance(transform_data.get("section_counts"), dict)
        else {}
    )
    total = 0
    for key in ("facts", "entities", "episodes", "communities"):
        try:
            total += max(0, int(section_counts.get(key, 0)))
        except (TypeError, ValueError):
            continue
    return total


def _graphiti_l2b_identity_payloads(
    *,
    l2b_nodes: list[dict[str, Any]],
    fact_pointers: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    partition: str,
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in l2b_nodes:
        node_uuid = str(row.get("uuid") or "").strip()
        graphiti_uuid = str(row.get("graphiti_uuid") or "").strip()
        graphiti_kind = str(row.get("graphiti_kind") or "graphiti_entity").strip()
        if not node_uuid or not graphiti_uuid:
            continue
        ref_id = str(row.get("ref_id") or f"graphiti:{partition}:entity:{graphiti_uuid}")
        signal_key = _identity_signal_key_for_graphiti_kind(graphiti_kind)
        raw_meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
        payload = {
            "canonical_uuid": node_uuid,
            "l2b_uuid": node_uuid,
            signal_key: graphiti_uuid,
            "ref_id": ref_id,
            "ref_kind": graphiti_kind,
            "locator": str(row.get("source_ref") or f"graphiti://{partition}/entity/{graphiti_uuid}"),
            "canonical_uri": str(row.get("source_ref") or f"graphiti://{partition}/entity/{graphiti_uuid}"),
            "managed_by": "graphiti",
            "label": str(row.get("label") or ""),
            "confidence": 0.7,
            "resolution_state": "weak",
            "graphiti_raw": {
                "schema_version": 1,
                "projection_row": row,
                "raw": raw_meta.get("graphiti_raw") if isinstance(raw_meta, dict) else {},
                "preserve_raw_graphiti": True,
            },
            "meta": {
                "source_tool": "web_console.graphiti_l2b_materialize",
                "graphiti_partition": partition,
                "graphiti_kind": graphiti_kind,
                "node_uuid_policy": "deterministic_graphiti_pointer_uuid",
            },
        }
        _append_unique_identity_payload(payloads, seen, payload)
    fact_rows_by_uuid = {
        str(row.get("graphiti_uuid") or row.get("uuid") or "").strip(): row
        for row in fact_pointers
        if str(row.get("graphiti_uuid") or row.get("uuid") or "").strip()
    }
    for row in edge_rows:
        fact_uuid = str(row.get("graphiti_uuid") or "").strip()
        if not fact_uuid:
            continue
        fact_row = fact_rows_by_uuid.get(fact_uuid, {})
        ref_id = str(row.get("ref_ids", [""])[0] if isinstance(row.get("ref_ids"), list) and row.get("ref_ids") else "")
        if not ref_id:
            ref_id = str(fact_row.get("ref_id") or f"graphiti:{partition}:fact:{fact_uuid}")
        source_ref = str(fact_row.get("source_ref") or f"graphiti://{partition}/fact/{fact_uuid}")
        raw_meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
        payload = {
            "canonical_uuid": f"graphiti:{partition}:fact:{fact_uuid}",
            "graphiti_edge_uuid": fact_uuid,
            "ref_id": ref_id,
            "ref_kind": "graphiti_fact",
            "locator": source_ref,
            "canonical_uri": source_ref,
            "managed_by": "graphiti",
            "label": str(row.get("label") or raw_meta.get("fact_text") or ""),
            "confidence": 0.65,
            "resolution_state": "weak",
            "graphiti_raw": {
                "schema_version": 1,
                "projection_edge": row,
                "fact_pointer": fact_row,
                "raw": raw_meta.get("graphiti_raw") if isinstance(raw_meta, dict) else {},
                "preserve_raw_graphiti": True,
            },
            "meta": {
                "source_tool": "web_console.graphiti_l2b_materialize",
                "graphiti_partition": partition,
                "graphiti_kind": "graphiti_fact",
            },
        }
        _append_unique_identity_payload(payloads, seen, payload)
    return payloads


def _append_unique_identity_payload(
    payloads: list[dict[str, Any]],
    seen: set[str],
    payload: dict[str, Any],
) -> None:
    key = "|".join(
        str(payload.get(item) or "")
        for item in (
            "canonical_uuid",
            "l2b_uuid",
            "graphiti_entity_uuid",
            "graphiti_edge_uuid",
            "graphiti_episode_uuid",
            "ref_id",
        )
    )
    if key in seen:
        return
    seen.add(key)
    payloads.append(payload)


def _identity_signal_key_for_graphiti_kind(graphiti_kind: str) -> str:
    text = str(graphiti_kind or "").lower()
    if "episode" in text:
        return "graphiti_episode_uuid"
    if "edge" in text or "fact" in text:
        return "graphiti_edge_uuid"
    return "graphiti_entity_uuid"


def _materialize_graphiti_l2b_node(graph: Any, row: dict[str, Any]) -> dict[str, Any]:
    from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind, Salience, SemanticNode

    node_uuid = str(row.get("uuid") or "").strip()
    if not node_uuid:
        return {"ok": False, "upserted": False, "error": "missing_node_uuid"}
    before = graph.get_node(node_uuid)
    node_kind = _parse_enum(NodeKind, row.get("node_kind") or NodeKind.OBJECT.value) or NodeKind.OBJECT
    confirmation = (
        _parse_enum(ConfirmationStatus, row.get("confirmation") or ConfirmationStatus.EXPECTED.value)
        or ConfirmationStatus.EXPECTED
    )
    attention = max(0.0, min(_body_float(row.get("attention"), 0.35), 1.0))
    meta = dict(row.get("meta")) if isinstance(row.get("meta"), dict) else {}
    source_meta = dict(row.get("source_meta")) if isinstance(row.get("source_meta"), dict) else {}
    source_ref = str(row.get("source_ref") or "")
    ref_id = str(row.get("ref_id") or "")
    meta.update(
        {
            "materialization_state": "materialized_l2b_pointer",
            "materialized_by": "web_console.graphiti_l2b_materialize",
            "source_ref": source_ref,
            "ref_id": ref_id,
            "preserve_raw_graphiti": True,
        }
    )
    raw_graphiti = meta.get("graphiti_raw") if isinstance(meta.get("graphiti_raw"), dict) else {}
    known_facts = _unique_texts([
        value
        for value in (
            row.get("label"),
            raw_graphiti.get("summary"),
            raw_graphiti.get("content"),
            raw_graphiti.get("fact"),
        )
        if value not in (None, "")
    ])[:8]
    graph.upsert_node(
        SemanticNode(
            uuid=node_uuid,
            kind=node_kind,
            label=str(row.get("label") or node_uuid)[:160],
            graphiti_uuid=str(row.get("graphiti_uuid") or ""),
            category=str(row.get("graphiti_kind") or "graphiti_pointer"),
            description=str(row.get("description") or "")[:400],
            known_facts=known_facts,
            tags=_unique_texts(["graphiti", row.get("partition"), row.get("graphiti_kind")]),
            attention=attention,
            salience=Salience.ACTIVE if attention >= 0.55 else Salience.BACKGROUND,
            confirmation=confirmation,
            evidence_score=attention,
            provenance_stream_id=f"web:graphiti:{row.get('partition') or 'goslo'}:{row.get('graphiti_uuid') or node_uuid}",
            bucket_id="graphiti_import_materialized",
            source="graphiti",
            source_meta={
                **source_meta,
                "materialization_state": "materialized_l2b_pointer",
                "source_ref": source_ref,
                "ref_id": ref_id,
            },
            meta=meta,
        )
    )
    return {
        "ok": True,
        "upserted": before is None,
        "uuid": node_uuid,
        "graphiti_uuid": str(row.get("graphiti_uuid") or ""),
        "kind": node_kind.value,
        "label": str(row.get("label") or ""),
    }


def _existing_l2b_edge_keys(graph: Any) -> set[tuple[str, str, str, str, str]]:
    return {
        _materialized_edge_key(
            source=str(getattr(src, "uuid", "") or ""),
            target=str(getattr(dst, "uuid", "") or ""),
            kind=_enum_value(getattr(edge, "kind", "")),
            edge_source=str(getattr(edge, "source", "") or ""),
            graphiti_uuid=str(getattr(edge, "graphiti_uuid", "") or ""),
        )
        for src, dst, edge in graph.all_edges()
    }


def _materialize_graphiti_l2b_edge(
    graph: Any,
    row: dict[str, Any],
    existing_keys: set[tuple[str, str, str, str, str]],
) -> dict[str, Any]:
    from parrot.dsg.l2b_types import EdgeKind, SemanticEdge, edge_view_classes

    source = str(row.get("source") or row.get("from_uuid") or "").strip()
    target = str(row.get("target") or row.get("to_uuid") or "").strip()
    if not source or not target:
        return {"ok": False, "connected": False, "error": "missing_edge_endpoint", "edge": row}
    edge_kind = _parse_enum(EdgeKind, row.get("kind") or EdgeKind.ASSOCIATED_WITH.value)
    if edge_kind is None:
        edge_kind = EdgeKind.ASSOCIATED_WITH
    edge_source = str(row.get("edge_source") or row.get("source") or "graphiti").strip() or "graphiti"
    graphiti_uuid = str(row.get("graphiti_uuid") or "").strip()
    key = _materialized_edge_key(
        source=source,
        target=target,
        kind=edge_kind.value,
        edge_source=edge_source,
        graphiti_uuid=graphiti_uuid,
    )
    if key in existing_keys:
        return {
            "ok": True,
            "connected": False,
            "skipped_duplicate": True,
            "source": source,
            "target": target,
            "kind": edge_kind.value,
            "graphiti_uuid": graphiti_uuid,
        }
    ref_ids = tuple(_unique_texts(row.get("ref_ids") or []))
    meta = dict(row.get("meta")) if isinstance(row.get("meta"), dict) else {}
    meta.update(
        {
            "materialization_state": "materialized_l2b_pointer_edge",
            "materialized_by": "web_console.graphiti_l2b_materialize",
            "label": str(row.get("label") or meta.get("fact_text") or ""),
            "write_policy": "operator_reviewed_l2b_pointer_topology",
            "preserve_raw_graphiti": True,
        }
    )
    edge = SemanticEdge(
        kind=edge_kind,
        strength=max(0.0, min(_body_float(row.get("strength"), 0.5), 1.0)),
        source=edge_source,
        graphiti_uuid=graphiti_uuid,
        source_graphiti_uuid=str(row.get("source_graphiti_uuid") or meta.get("source_graphiti_uuid") or ""),
        target_graphiti_uuid=str(row.get("target_graphiti_uuid") or meta.get("target_graphiti_uuid") or ""),
        ref_ids=ref_ids,
        view_classes=edge_view_classes(edge_kind),
        meta=meta,
    )
    connected = graph.connect(source, target, edge)
    if connected:
        existing_keys.add(key)
    return {
        "ok": bool(connected),
        "connected": bool(connected),
        "skipped_duplicate": False,
        "source": source,
        "target": target,
        "kind": edge_kind.value,
        "graphiti_uuid": graphiti_uuid,
        "error": "" if connected else "l2b_endpoint_not_found",
    }


def _materialized_edge_key(
    *,
    source: str,
    target: str,
    kind: str,
    edge_source: str,
    graphiti_uuid: str,
) -> tuple[str, str, str, str, str]:
    return (
        str(source or ""),
        str(target or ""),
        str(kind or ""),
        str(edge_source or ""),
        str(graphiti_uuid or ""),
    )


def draft_obsidian_l2b_import_plan(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build one reviewable plan for Obsidian vault notes.

    The Source Board should show the operator the whole path before any write:
    local vault scan, note selection, UserTagFilter normalization, L1.5 admit,
    and the optional L2-B overlay/subgraph placement policy. This remains a
    draft-only Web surface and does not publish the Obsidian trigger event.
    """

    from parrot.web_console.graph_policy import draft_import_destination

    body = payload or {}
    requested_execution = {
        "dry_run": _body_bool(body.get("dry_run"), True),
        "operator_mode": _body_bool(body.get("operator_mode"), False),
        "ignored_for_plan": True,
    }
    dry_run = True
    operator_mode = False
    draft = draft_obsidian_vault_import(
        {**body, "dry_run": True, "operator_mode": False}
    )
    data = dict(draft.get("data") or {})
    items = [row for row in data.get("items", []) if isinstance(row, dict)]
    errors = [row for row in data.get("errors", []) if isinstance(row, dict)]
    vault = (data.get("scan_summary") or {}).get("vault", {})
    vault_path = str(
        body.get("vault_path")
        or (vault.get("vault_path") if isinstance(vault, dict) else "")
        or "obsidian_vault"
    )
    item_ids = [
        str(
            row.get("path")
            or (row.get("event") if isinstance(row.get("event"), dict) else {}).get(
                "provenance_stream_id"
            )
            or (row.get("observation") if isinstance(row.get("observation"), dict) else {}).get(
                "label"
            )
            or index
        )
        for index, row in enumerate(items)
    ]
    policy_receipt: dict[str, Any] | None = None
    policy_skipped_reason = ""
    if items:
        policy_receipt = draft_import_destination(
            {
                "destination": body.get("destination") or "isolated_compartment",
                "source_kind": "obsidian",
                "source_id": body.get("source_id") or vault_path,
                "workspace_id": body.get("workspace_id") or "memory_graph",
                "subgraph_id": body.get("subgraph_id") or "",
                "subgraph_label": body.get("subgraph_label") or "Obsidian source pack",
                "item_ids": item_ids,
                "dry_run": True,
                "operator_mode": False,
            }
        )
    else:
        # Keep an empty or invalid note selection visibly empty in Source Board.
        policy_skipped_reason = "no_importable_obsidian_items"
    policy_data = dict((policy_receipt or {}).get("data") or {})
    policy_success = bool(policy_receipt and policy_receipt.get("success"))
    return _receipt(
        action="l15.obsidian_vault.import_plan",
        success=bool(items) and not errors and policy_success,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "items": items,
            "errors": errors,
            "selected_count": len(items),
            "scan_summary": data.get("scan_summary", {}),
            "write_path": data.get(
                "write_path",
                "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)",
            ),
            "runtime_path": data.get(
                "runtime_path",
                "ObsidianIngestTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
            ),
            "import_policy": policy_data.get("policy", {}),
            "import_draft": policy_data.get("draft", {}),
            "policy_skipped_reason": policy_skipped_reason,
            "flow_steps": [
                "scan local Obsidian vault",
                "operator selects ready daily / roleplay / ref notes",
                "UserTagFilter normalizes selected notes into Observations",
                "preview CORE-013 import destination / overlay policy",
                "real import, if chosen later, must admit through L1.5 under operator mode",
            ],
            "operator_required_for_execute": True,
            "apply_route": "/api/l15/obsidian-vault/import",
            "apply_preconditions": {"dry_run": False, "operator_mode": True},
            "core_candidates": ["CORE-008", "CORE-013"],
            "requested_execution": requested_execution,
            "policy_receipt_id": ((policy_receipt or {}).get("receipt") or {}).get(
                "receipt_id",
                "",
            ),
            "import_receipt_id": (draft.get("receipt") or {}).get("receipt_id", ""),
        },
    )


def draft_obsidian_vault_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a batch import from scanned Obsidian notes into L1.5.

    This route is the batch companion to ``l15.obsidian_node.draft``. It
    rescans the local vault server-side, applies optional path/profile filters,
    converts each ready note through the same ``UserTagFilter`` used by the
    runtime Obsidian trigger, and returns a reviewable receipt. It does not
    publish Redis events and does not commit to L1.5/L2-B.
    """

    items, errors, scan_receipt = _obsidian_vault_import_items(payload)
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    return _receipt(
        action="l15.obsidian_vault.import_draft",
        success=bool(items) and not errors,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "items": items,
            "errors": errors,
            "selected_count": len(items),
            "scan_summary": {
                "vault": (scan_receipt.get("data") or {}).get("vault", {}),
                "ready_count": len((scan_receipt.get("data") or {}).get("notes", [])),
                "invalid_count": len((scan_receipt.get("data") or {}).get("invalid_notes", [])),
            },
            "write_path": "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)",
            "runtime_path": "ObsidianIngestTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
            "operator_required_for_import": True,
        },
    )


async def apply_obsidian_vault_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Import selected Obsidian notes through L1.5 under operator mode only.

    Runtime Obsidian sync still uses the trigger/event path. This direct
    ``L15Pool.admit`` route is intentionally Web-only so an operator can test
    source-pack imports without requiring the full Brain/Redis trigger runner
    to be alive. It must stay behind explicit operator mode.
    """

    from parrot.dsg.l1_5.pool import get_l1_5_pool

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_obsidian_vault_import(
        {**body, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    draft["action"] = "l15.obsidian_vault.import"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    observations = tuple(
        _observation_from_json(item["observation"])
        for item in draft["data"]["items"]
        if isinstance(item, dict) and isinstance(item.get("observation"), dict)
    )
    outcome = await get_l1_5_pool().admit(observations)
    return _receipt(
        action="l15.obsidian_vault.import",
        success=not bool(outcome.rejected),
        dry_run=False,
        operator_mode=True,
        data={
            "imported_count": len(observations),
            "admit_outcome": _jsonable(outcome),
            "write_path": "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)",
        },
    )


def preview_google_calendar_events(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Preview Google Calendar event normalization and L1.5 observations.

    The preview uses the same CalendarTrigger conversion helpers as the real
    trigger path, but it does not return commit_observations to the runner and
    does not mutate L1.5/L2-B.
    """
    from parrot.dsg.l2b_graph import get_l2b_graph
    from parrot.dsg.triggers.calendar_trigger import (
        CalendarTrigger,
        _extract_event_list,
        _loads_jsonish,
    )

    body = payload or {}
    raw_events = body.get("events")
    if not isinstance(raw_events, list):
        raw_input = body.get("result") if "result" in body else body.get("raw")
        raw_events = _extract_event_list(_loads_jsonish(raw_input))
    raw_dicts = [dict(item) for item in raw_events[:20] if isinstance(item, dict)]
    trigger = CalendarTrigger(get_l2b_graph())
    normalized = [trigger._normalize_event(ev) for ev in raw_dicts]
    observations = []
    for event in normalized:
        start_ts = trigger._parse_time(str(event.get("start_time") or ""))
        end_ts = trigger._parse_time(str(event.get("end_time") or ""))
        observations.append(trigger._event_to_observation(event, start_ts, end_ts))
    mapping_rows = _calendar_mapping_rows(normalized, observations)

    return _receipt(
        action="google.calendar.preview",
        success=bool(raw_dicts),
        dry_run=True,
        operator_mode=False,
        data={
            "raw_events": raw_dicts,
            "normalized_events": normalized,
            "observations": observations,
            "mapping_rows": mapping_rows,
            "write_path": "CalendarTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
            "preserved_fields": [
                "calendar_id",
                "calendar_event_id",
                "start_time",
                "end_time",
                "timezone",
                "location",
                "html_link",
                "etag",
                "status",
                "ical_uid",
                "updated",
                "objects",
            ],
            "operator_required_for_import": True,
        },
    )


def draft_google_calendar_fetch(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a Scheduler/Nanobot Google Calendar fetch task.

    Browser code must not own Google OAuth. The real fetch path is the existing
    Scheduler -> Nanobot -> Google Workspace MCP route, and this receipt shows
    the exact task that would be dispatched.
    """

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    params = _calendar_fetch_params(body)
    return _receipt(
        action="google.calendar.fetch.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "task_type": "calendar_fetch",
            "priority": str(body.get("priority") or "normal"),
            "params": params,
            "operator_required_for_execute": True,
            "result_flow": "Scheduler -> Nanobot -> Google Workspace MCP -> calendar_result -> CalendarTrigger -> L1.5",
        },
    )


async def dispatch_google_calendar_fetch(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dispatch a Google Calendar fetch only under explicit operator mode."""

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_google_calendar_fetch(
        {**body, "dry_run": dry_run, "operator_mode": operator_mode}
    )
    draft["action"] = "google.calendar.fetch.dispatch"
    if dry_run or not operator_mode:
        draft["data"]["would_dispatch"] = True
        draft["data"]["dispatch_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    try:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        task_id = await do_dispatch_task(
            "calendar_fetch",
            params=draft["data"]["params"],
            priority=draft["data"]["priority"],
        )
        return _receipt(
            action="google.calendar.fetch.dispatch",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "task_id": task_id, "dispatched": True},
        )
    except Exception as exc:
        return _receipt(
            action="google.calendar.fetch.dispatch",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "error": f"{type(exc).__name__}: {exc}"},
        )


async def google_calendar_result_history(limit: int = 20) -> dict[str, Any]:
    """Read the Scheduler-owned trigger-result ledger for Calendar results.

    This endpoint is intentionally read-only and Web-only. The authoritative
    runtime path is still Pub/Sub:
    Scheduler -> ``CH_TRIGGER_RESULTS`` -> TriggerRunner -> L1.5/L2-B. The
    Redis stream is a bounded observability ledger so operators can understand
    what recently returned from Nanobot after the Pub/Sub moment has passed.
    """

    limit, limit_error = _body_int_limit(limit, default=20, maximum=50)
    if limit_error:
        return _receipt(
            action="google.calendar.results",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={"rows": [], "error": limit_error},
        )

    from parrot.shared.constants import CH_TRIGGER_RESULTS, STREAM_TRIGGER_RESULTS

    try:
        from parrot.shared.redis_client import get_redis

        redis = await get_redis()
        raw_rows = await redis.xrevrange(STREAM_TRIGGER_RESULTS, count=limit * 3)
    except Exception as exc:
        return _receipt(
            action="google.calendar.results",
            success=True,
            dry_run=True,
            operator_mode=False,
            data={
                "available": False,
                "stream": STREAM_TRIGGER_RESULTS,
                "channel": CH_TRIGGER_RESULTS,
                "rows": [],
                "error": f"{type(exc).__name__}: {exc}",
            },
        )

    rows: list[dict[str, Any]] = []
    for stream_id, fields in raw_rows:
        if not isinstance(fields, dict):
            continue
        row = _calendar_result_history_row(str(stream_id), fields)
        if row:
            rows.append(row)
        if len(rows) >= limit:
            break

    return _receipt(
        action="google.calendar.results",
        success=True,
        dry_run=True,
        operator_mode=False,
        data={
            "available": True,
            "stream": STREAM_TRIGGER_RESULTS,
            "channel": CH_TRIGGER_RESULTS,
            "rows": rows,
            "count": len(rows),
            "read_model": "Scheduler trigger-result ledger",
            "web_only": True,
        },
    )


async def fetch_google_calendar_api(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch Google Calendar events directly through OAuth2 + official API.

    This read path exists for the Web Console test bench. It does not replace
    the Scheduler -> Nanobot -> Google Workspace MCP task path, but it lets an
    operator verify real Calendar bytes without requiring a local Redis result
    ledger to be running.
    """

    body = payload or {}
    limit, limit_error = _body_int_limit(body.get("limit"), default=20, maximum=50)
    if limit_error:
        return _receipt(
            action="google.calendar.api_fetch",
            success=False,
            dry_run=False,
            operator_mode=False,
            data={"available": False, "events": [], "error": limit_error},
        )

    calendar_id = str(body.get("calendar_id") or body.get("calendarId") or "primary")
    timezone_name = str(body.get("timezone") or "Asia/Shanghai")
    time_min, time_max = _calendar_time_window(body, timezone_name=timezone_name)
    show_deleted = _body_bool(body.get("show_deleted"), False)

    try:
        api_result = await _fetch_google_calendar_events_from_api(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            limit=limit,
            show_deleted=show_deleted,
        )
    except Exception as exc:
        return _receipt(
            action="google.calendar.api_fetch",
            success=False,
            dry_run=False,
            operator_mode=False,
            data={
                "available": False,
                "calendar_id": calendar_id,
                "time_min": time_min,
                "time_max": time_max,
                "events": [],
                "error": f"{type(exc).__name__}: {exc}",
                "read_model": "Google Calendar API events.list via OAuth2",
            },
        )

    raw_events = [
        {**dict(item), "calendar_id": str(item.get("calendar_id") or calendar_id)}
        for item in api_result.get("items", [])
        if isinstance(item, dict)
    ]
    preview = preview_google_calendar_events({"events": raw_events})
    preview_data = dict(preview.get("data") or {})
    return _receipt(
        action="google.calendar.api_fetch",
        success=True,
        dry_run=False,
        operator_mode=False,
        data={
            "available": True,
            "calendar_id": calendar_id,
            "time_min": time_min,
            "time_max": time_max,
            "timezone": timezone_name,
            "count": len(raw_events),
            "events": raw_events,
            "normalized_events": preview_data.get("normalized_events", []),
            "observations": preview_data.get("observations", []),
            "mapping_rows": preview_data.get("mapping_rows", []),
            "next_sync_token_present": bool(api_result.get("nextSyncToken")),
            "next_page_token_present": bool(api_result.get("nextPageToken")),
            "credential_source": api_result.get("credential_source", "google_workspace_mcp"),
            "read_model": "Google Calendar API events.list via OAuth2",
            "write_path": preview_data.get(
                "write_path",
                "CalendarTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
            ),
            "operator_required_for_import": True,
            "apply_route": "/api/google/calendar/import",
            "source_kind": "google_calendar_api",
        },
    )


async def fetch_google_calendar_nanobot(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch Google Calendar events through the ECS Nanobot MCP path.

    This is the Web Console's true remote smoke test: Web -> Nanobot API ->
    Google Workspace MCP -> Google Calendar. It is intentionally read-only and
    does not replace the Scheduler dispatch path used by periodic triggers.
    """

    body = payload or {}
    limit, limit_error = _body_int_limit(body.get("limit"), default=20, maximum=50)
    if limit_error:
        return _receipt(
            action="google.calendar.nanobot_fetch",
            success=False,
            dry_run=False,
            operator_mode=False,
            data={"available": False, "events": [], "error": limit_error},
        )

    calendar_id = str(body.get("calendar_id") or body.get("calendarId") or "primary")
    timezone_name = str(body.get("timezone") or "Asia/Shanghai")
    time_min, time_max = _calendar_time_window(body, timezone_name=timezone_name)
    account = str(
        body.get("account")
        or os.getenv("PARROT_WEB_CONSOLE_GOOGLE_ACCOUNT")
        or "gosloparrot@gmail.com"
    )
    show_deleted = _body_bool(body.get("show_deleted"), False)

    try:
        nanobot_result = await _fetch_google_calendar_events_from_nanobot(
            account=account,
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            timezone_name=timezone_name,
            limit=limit,
            show_deleted=show_deleted,
        )
    except Exception as exc:
        return _receipt(
            action="google.calendar.nanobot_fetch",
            success=False,
            dry_run=False,
            operator_mode=False,
            data={
                "available": False,
                "calendar_id": calendar_id,
                "time_min": time_min,
                "time_max": time_max,
                "events": [],
                "error": f"{type(exc).__name__}: {exc}",
                "read_model": "ECS Nanobot -> Google Workspace MCP manage_calendar",
            },
        )

    parsed = _parse_nanobot_calendar_response(nanobot_result)
    raw_events = [
        {**dict(item), "calendar_id": str(item.get("calendar_id") or calendar_id)}
        for item in parsed["events"]
        if isinstance(item, dict)
    ]
    preview = preview_google_calendar_events({"events": raw_events})
    preview_data = dict(preview.get("data") or {})
    status = str(parsed.get("status") or "").strip().lower()
    nanobot_success = status not in {"error", "failed", "failure"}
    return _receipt(
        action="google.calendar.nanobot_fetch",
        success=nanobot_success,
        dry_run=False,
        operator_mode=False,
        data={
            "available": True,
            "nanobot_success": nanobot_success,
            "status": status or "unknown",
            "account": account,
            "calendar_id": calendar_id,
            "time_min": time_min,
            "time_max": time_max,
            "timezone": timezone_name,
            "count": len(raw_events),
            "nanobot_event_count": parsed.get("event_count"),
            "events": raw_events,
            "normalized_events": preview_data.get("normalized_events", []),
            "observations": preview_data.get("observations", []),
            "mapping_rows": preview_data.get("mapping_rows", []),
            "nanobot_reply": parsed.get("reply_sample", ""),
            "parse_error": parsed.get("parse_error", ""),
            "read_model": "ECS Nanobot -> Google Workspace MCP manage_calendar",
            "write_path": preview_data.get(
                "write_path",
                "CalendarTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
            ),
            "operator_required_for_import": True,
            "apply_route": "/api/google/calendar/import",
            "source_kind": "google_calendar_nanobot",
        },
    )


def draft_google_calendar_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft Google Calendar observations for L1.5 import.

    This stays Web-only and mirrors the real CalendarTrigger conversion path.
    The receipt lets the operator inspect raw event fields, normalized event
    fields, and the exact Observation objects before any L1.5 admission.
    """

    body = payload or {}
    preview = preview_google_calendar_events(body)
    data = dict(preview.get("data") or {})
    observations = [
        item for item in data.get("observations", []) if isinstance(item, dict)
    ]
    normalized_events = [
        item for item in data.get("normalized_events", []) if isinstance(item, dict)
    ]
    mapping_rows = [
        item for item in data.get("mapping_rows", []) if isinstance(item, dict)
    ]
    errors: list[dict[str, Any]] = []
    if not observations:
        errors.append({"error": "no_calendar_observations"})
    return _receipt(
        action="google.calendar.import_draft",
        success=bool(observations),
        dry_run=True,
        operator_mode=False,
        data={
            "raw_events": data.get("raw_events", []),
            "normalized_events": normalized_events,
            "observations": observations,
            "mapping_rows": mapping_rows,
            "observation_count": len(observations),
            "errors": errors,
            "write_path": "CalendarTrigger._event_to_observation -> L15Pool.admit(GOOGLE_CALENDAR)",
            "operator_required_for_import": True,
        },
    )


def draft_google_calendar_l2b_import_plan(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one reviewable plan for Google Calendar -> L1.5 -> L2-B.

    Manual fetch/import is the current phase. Google watch/syncToken remains a
    later server-side feature, so this function only joins the existing
    CalendarTrigger preview with the graph-placement policy draft.
    """

    from parrot.web_console.graph_policy import draft_import_destination

    body = payload or {}
    requested_execution = {
        "dry_run": _body_bool(body.get("dry_run"), True),
        "operator_mode": _body_bool(body.get("operator_mode"), False),
        "ignored_for_plan": True,
    }
    dry_run = True
    operator_mode = False
    draft = draft_google_calendar_import({**body, "dry_run": True, "operator_mode": False})
    data = dict(draft.get("data") or {})
    observations = [
        item for item in data.get("observations", []) if isinstance(item, dict)
    ]
    normalized_events = [
        item for item in data.get("normalized_events", []) if isinstance(item, dict)
    ]
    mapping_rows = [
        item for item in data.get("mapping_rows", []) if isinstance(item, dict)
    ]
    errors = [row for row in data.get("errors", []) if isinstance(row, dict)]
    item_ids = [
        str(
            row.get("merge_key")
            or row.get("provider_ref")
            or row.get("calendar_event_id")
            or index
        )
        for index, row in enumerate(mapping_rows)
    ]
    calendar_ids = sorted({
        str(row.get("calendar_id") or "primary")
        for row in mapping_rows
        if isinstance(row, dict)
    })
    policy_receipt: dict[str, Any] | None = None
    policy_skipped_reason = ""
    if observations:
        policy_receipt = draft_import_destination(
            {
                "destination": body.get("destination") or "isolated_compartment",
                "source_kind": "google_calendar",
                "source_id": body.get("source_id") or ",".join(calendar_ids) or "google_calendar",
                "workspace_id": body.get("workspace_id") or "memory_graph",
                "subgraph_id": body.get("subgraph_id") or "",
                "subgraph_label": body.get("subgraph_label") or "Google Calendar source pack",
                "item_ids": item_ids,
                "dry_run": True,
                "operator_mode": False,
            }
        )
    else:
        # A Calendar plan without normalized observations should not imply a graph write.
        policy_skipped_reason = "no_calendar_observations"
    policy_data = dict((policy_receipt or {}).get("data") or {})
    policy_success = bool(policy_receipt and policy_receipt.get("success"))
    return _receipt(
        action="google.calendar.import_plan",
        success=bool(observations) and not errors and policy_success,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "raw_events": data.get("raw_events", []),
            "normalized_events": normalized_events,
            "observations": observations,
            "mapping_rows": mapping_rows,
            "observation_count": len(observations),
            "errors": errors,
            "write_path": data.get(
                "write_path",
                "CalendarTrigger._event_to_observation -> L15Pool.admit(GOOGLE_CALENDAR)",
            ),
            "import_policy": policy_data.get("policy", {}),
            "import_draft": policy_data.get("draft", {}),
            "policy_skipped_reason": policy_skipped_reason,
            "flow_steps": [
                "manual fetch or pasted Nanobot/Google JSON",
                "CalendarTrigger normalizes event identity, time, status, and object hints",
                "draft GOOGLE_CALENDAR Observations for L1.5",
                "preview CORE-013 import destination / overlay policy",
                "real import, if chosen later, must admit through L1.5 under operator mode",
            ],
            "operator_required_for_execute": True,
            "apply_route": "/api/google/calendar/import",
            "apply_preconditions": {"dry_run": False, "operator_mode": True},
            "sync_policy": "manual_fetch_import_v1; google_watch_sync_token_v2_later",
            "core_candidates": ["CORE-008", "CORE-013"],
            "requested_execution": requested_execution,
            "policy_receipt_id": ((policy_receipt or {}).get("receipt") or {}).get(
                "receipt_id",
                "",
            ),
            "import_receipt_id": (draft.get("receipt") or {}).get("receipt_id", ""),
        },
    )


async def apply_google_calendar_import(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Admit Google Calendar observations into L1.5 under operator gate.

    The default mode is an apply preview: it reports the exact observations that
    would be admitted and marks the write as skipped. A real import requires
    both ``dry_run=false`` and ``operator_mode=true``.
    """

    from parrot.dsg.l1_5.pool import get_l1_5_pool

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_google_calendar_import(body)
    draft["action"] = "google.calendar.import"
    draft["dry_run"] = dry_run
    draft["operator_mode"] = operator_mode
    draft["receipt"]["audit_level"] = "operator" if operator_mode else "draft"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    observations = tuple(
        _observation_from_json(item)
        for item in draft["data"]["observations"]
        if isinstance(item, dict)
    )
    outcome = await get_l1_5_pool().admit(observations)
    return _receipt(
        action="google.calendar.import",
        success=not bool(outcome.rejected),
        dry_run=False,
        operator_mode=True,
        data={
            "imported_count": len(observations),
            "admit_outcome": _jsonable(outcome),
            "mapping_rows": draft["data"].get("mapping_rows", []),
            "write_path": "CalendarTrigger._event_to_observation -> L15Pool.admit(GOOGLE_CALENDAR)",
        },
    )


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
        "edge": _edge_payload_from_body(body, kind.value),
        "operator_required_for_execute": True,
    }
    return _receipt(
        action="l2b.edge.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data=edge,
    )


def draft_l2b_edge_update(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft an update to an existing L2-B edge payload.

    The console identifies an edge by endpoints plus optional match_kind/source.
    That is deliberate: RustWorkX edge indexes are runtime-local and should not
    become Web DTOs. If exact parallel-edge surgery becomes common, the next
    step is to store a stable edge id inside ``SemanticEdge.meta``.
    """
    from parrot.dsg.l2b_types import EdgeKind

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    from_uuid = str(body.get("from_uuid") or body.get("source_uuid") or "").strip()
    to_uuid = str(body.get("to_uuid") or body.get("target_uuid") or "").strip()
    kind = _parse_enum(EdgeKind, str(body.get("kind") or EdgeKind.ASSOCIATED_WITH.value))
    if not from_uuid or not to_uuid or kind is None:
        return _receipt(
            action="l2b.edge.update_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={
                "error": "missing_or_invalid_edge_fields",
                "valid_kinds": [item.value for item in EdgeKind],
            },
        )
    return _receipt(
        action="l2b.edge.update_draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "from_uuid": from_uuid,
            "to_uuid": to_uuid,
            "match_kind": str(body.get("match_kind") or ""),
            "match_source": str(body.get("match_source") or ""),
            "edge": _edge_payload_from_body(body, kind.value),
            "would_update": True,
            "operator_required_for_execute": True,
        },
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
            graphiti_uuid=str(edge_data.get("graphiti_uuid") or ""),
            source_graphiti_uuid=str(edge_data.get("source_graphiti_uuid") or ""),
            target_graphiti_uuid=str(edge_data.get("target_graphiti_uuid") or ""),
            ref_ids=tuple(str(item) for item in edge_data.get("ref_ids") or ()),
            view_classes=tuple(str(item) for item in edge_data.get("view_classes") or ()),
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


async def apply_l2b_edge_update(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Update an existing edge only under explicit operator execution."""
    from parrot.dsg.l2b_graph import get_l2b_graph
    from parrot.dsg.l2b_types import EdgeKind, SemanticEdge

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_l2b_edge_update({**body, "dry_run": dry_run, "operator_mode": operator_mode})
    draft["action"] = "l2b.edge.update"
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    edge_data = draft["data"]["edge"]
    ok = get_l2b_graph().update_edge_between(
        str(draft["data"]["from_uuid"]),
        str(draft["data"]["to_uuid"]),
        SemanticEdge(
            kind=EdgeKind(edge_data["kind"]),
            strength=float(edge_data["strength"]),
            source=str(edge_data["source"]),
            graphiti_uuid=str(edge_data.get("graphiti_uuid") or ""),
            source_graphiti_uuid=str(edge_data.get("source_graphiti_uuid") or ""),
            target_graphiti_uuid=str(edge_data.get("target_graphiti_uuid") or ""),
            ref_ids=tuple(str(item) for item in edge_data.get("ref_ids") or ()),
            view_classes=tuple(str(item) for item in edge_data.get("view_classes") or ()),
            meta=dict(edge_data.get("meta") or {}),
        ),
        match_kind=str(draft["data"].get("match_kind") or ""),
        match_source=str(draft["data"].get("match_source") or ""),
    )
    return _receipt(
        action="l2b.edge.update",
        success=ok,
        dry_run=False,
        operator_mode=True,
        data={**draft["data"], "updated": ok},
    )


async def delete_l2b_edge(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Delete an L2-B edge by endpoints, defaulting to dry-run.

    This is Web-operator surgery. Runtime graph writes remain explicit and
    auditable; the default response only reports what would be removed.
    """
    from parrot.dsg.l2b_graph import get_l2b_graph

    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    from_uuid = str(body.get("from_uuid") or body.get("source_uuid") or "").strip()
    to_uuid = str(body.get("to_uuid") or body.get("target_uuid") or "").strip()
    if not from_uuid or not to_uuid:
        return _receipt(
            action="l2b.edge.delete",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={"error": "missing_edge_endpoint"},
        )
    data = {
        "from_uuid": from_uuid,
        "to_uuid": to_uuid,
        "match_kind": str(body.get("match_kind") or ""),
        "match_source": str(body.get("match_source") or ""),
        "operator_required_for_execute": True,
    }
    if dry_run or not operator_mode:
        return _receipt(
            action="l2b.edge.delete",
            success=True,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data={**data, "would_delete": True, "apply_skipped_reason": "dry_run_or_operator_mode_missing"},
        )
    ok = get_l2b_graph().remove_edge_between(
        from_uuid,
        to_uuid,
        match_kind=str(data["match_kind"]),
        match_source=str(data["match_source"]),
    )
    return _receipt(
        action="l2b.edge.delete",
        success=ok,
        dry_run=False,
        operator_mode=True,
        data={**data, "deleted": ok},
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


def _trigger_taxonomy_for(trigger_name: str) -> dict[str, Any]:
    """Classify a trigger along stable operator-facing review dimensions."""

    name = str(trigger_name or "").strip()
    lowered = name.lower()
    taxonomy: dict[str, list[str]] | None = None
    for key, candidate in _TRIGGER_TAXONOMY_BY_KEY.items():
        if key in lowered:
            taxonomy = candidate
            break
    if taxonomy is None:
        taxonomy = {
            "ascending_channels": ["memory_maintenance"],
            "interaction_modules": ["l2_b_graph"],
            "information_tags": ["status_notice"],
        }

    ascending_channels = _unique_texts(taxonomy.get("ascending_channels", []))
    interaction_modules = _unique_texts(taxonomy.get("interaction_modules", []))
    information_tags = _unique_texts(taxonomy.get("information_tags", []))
    return {
        "ascending_channels": ascending_channels,
        "interaction_modules": interaction_modules,
        "information_tags": information_tags,
        "taxonomy": {
            "schema": "dsg.trigger.taxonomy.v1",
            "primary_ascending_channel": ascending_channels[0] if ascending_channels else "",
            "ascending_channels": ascending_channels,
            "interaction_modules": interaction_modules,
            "information_tags": information_tags,
            "operator_note": (
                "Ascending channels are review/filter lanes. They do not change "
                "the trigger firing semantics or publish channel."
            ),
        },
    }


def _trigger_taxonomy_catalog() -> dict[str, Any]:
    return {
        "schema": "dsg.trigger.taxonomy.v1",
        "default_group_dimension": "ascending_channel",
        "dimensions": {
            "ascending_channel": _taxonomy_definition_rows(_TRIGGER_CHANNEL_DEFINITIONS),
            "interaction_module": _taxonomy_definition_rows(_TRIGGER_MODULE_DEFINITIONS),
            "information_tag": _taxonomy_definition_rows(_TRIGGER_INFORMATION_DEFINITIONS),
        },
        "policy": (
            "Classifications are operator-visible filter/view tags. Trigger execution "
            "still follows TriggerKind and the CH_DSG_EVENTS publish path."
        ),
    }


def _taxonomy_definition_rows(definitions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": key,
            "label": str(value.get("label") or key),
            "description": str(value.get("description") or ""),
        }
        for key, value in definitions.items()
    ]


def _trigger_catalog_groups(
    triggers: list[dict[str, Any]],
    *,
    field: str,
    definitions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, definition in definitions.items():
        matched = [
            str(trigger.get("name") or "")
            for trigger in triggers
            if key in set(_unique_texts(trigger.get(field, [])))
        ]
        if not matched:
            continue
        rows.append(
            {
                "id": key,
                "label": str(definition.get("label") or key),
                "description": str(definition.get("description") or ""),
                "trigger_names": matched,
                "count": len(matched),
            }
        )
    return rows


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


def _obsidian_vault_import_items(
    payload: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Return selected Obsidian note drafts plus validation errors.

    The source board sends relative vault paths chosen by the operator. The
    server rescans the vault instead of trusting browser-provided note payloads
    so preview/import receipts are always based on current local files.
    """

    from parrot.dsg.ingest.user_tag_filter import UserTagFilter

    body = payload or {}
    scan_receipt = scan_obsidian_vault(body)
    notes = list((scan_receipt.get("data") or {}).get("notes") or [])
    selected_paths = _obsidian_selected_paths(body.get("paths") or body.get("selected_paths"))
    selected_profiles = _obsidian_selected_profiles(body.get("profiles"))
    limit, limit_error = _body_int_limit(body.get("limit"), default=24, maximum=80)

    filter_ = UserTagFilter()
    items: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    ready_paths_seen: set[str] = set()
    if limit_error:
        errors.append(limit_error)
        return items, errors, scan_receipt
    for note in notes:
        rel_path = str(note.get("path") or "").replace("\\", "/")
        profile = str(note.get("profile") or "daily").strip().lower()
        if selected_paths and rel_path not in selected_paths:
            continue
        ready_paths_seen.add(rel_path)
        # A selected path is explicit operator intent. Report profile mismatches
        # instead of silently dropping the note from the receipt.
        if selected_profiles and profile not in selected_profiles:
            if selected_paths:
                errors.append({
                    "path": rel_path,
                    "profile": profile,
                    "error": "selected_profile_mismatch",
                    "expected_profiles": sorted(selected_profiles),
                })
            continue
        if len(items) >= limit:
            if selected_paths:
                errors.append({
                    "path": rel_path,
                    "profile": profile,
                    "error": "selected_path_over_limit",
                    "limit": limit,
                })
                continue
            break
        payload_row = note.get("payload")
        if not isinstance(payload_row, dict):
            errors.append({"path": rel_path, "error": "missing_note_payload"})
            continue
        event = _obsidian_event(dict(payload_row))
        outcome = filter_.process_tag(
            dict(payload_row),
            provenance_stream_id=str(event.get("provenance_stream_id") or ""),
        )
        if outcome.rejected or not outcome.observations:
            errors.append({
                "path": rel_path,
                "profile": profile,
                "error": outcome.reason or "filter_rejected",
            })
            continue
        observation = outcome.observations[0]
        items.append({
            "path": rel_path,
            "profile": profile,
            "label": str(note.get("label") or payload_row.get("label") or ""),
            "target_bucket": _obsidian_profile_target(profile),
            "uuid_free_allowed": profile in {"daily", "roleplay"},
            "bind_policy": (
                "ref_bind_existing_node"
                if profile == "ref"
                else "setting_node_uuid_free_allowed"
            ),
            "event": event,
            "observation": _jsonable(observation),
        })
    if selected_paths:
        invalid_by_path = {
            str(row.get("path") or "").replace("\\", "/"): row
            for row in (scan_receipt.get("data") or {}).get("invalid_notes", [])
            if isinstance(row, dict)
        }
        for path in sorted(selected_paths - ready_paths_seen):
            if path in invalid_by_path:
                errors.append({
                    "path": path,
                    "error": "note_not_import_ready",
                    "reason": invalid_by_path[path].get("reason", ""),
                })
            else:
                errors.append({"path": path, "error": "selected_path_not_found"})
    return items, errors, scan_receipt


def _observation_from_json(data: dict[str, Any]) -> Any:
    """Rehydrate a Web receipt observation for the final L1.5 admit call.

    Web receipts are JSON snapshots of the Observation produced by source
    normalizers such as CalendarTrigger. Keep temporal fields intact here:
    EVENT nodes need ``observed_at`` / ``time_span`` for timeline rendering and
    for later refreshes to update the right L2-B event view in place.
    """

    from parrot.dsg.ingest.base import Observation, ObservationSource
    from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

    source_raw = str(data.get("source") or ObservationSource.USER_TAG_OBSIDIAN.value)
    kind_raw = str(data.get("kind") or NodeKind.OBJECT.value)
    confirmation_raw = str(data.get("confirmation") or ConfirmationStatus.CONFIRMED.value)
    try:
        source = ObservationSource(source_raw)
    except ValueError:
        source = ObservationSource.USER_TAG_OBSIDIAN
    try:
        kind = NodeKind(kind_raw)
    except ValueError:
        kind = NodeKind.OBJECT
    try:
        confirmation = ConfirmationStatus(confirmation_raw)
    except ValueError:
        confirmation = ConfirmationStatus.CONFIRMED

    observation_kwargs: dict[str, Any] = dict(
        source=source,
        provenance_stream_id=str(data.get("provenance_stream_id") or ""),
        obsidian_uuid=str(data.get("obsidian_uuid") or ""),
        graphiti_uuid=str(data.get("graphiti_uuid") or ""),
        label=str(data.get("label") or "").strip()[:128],
        kind=kind,
        description=str(data.get("description") or "")[:400],
        confidence=max(0.0, min(_body_float(data.get("confidence"), 1.0), 1.0)),
        confirmation=confirmation,
        meta=dict(data.get("meta") or {}),
    )
    obs_id = str(data.get("obs_id") or "").strip()
    if obs_id:
        observation_kwargs["obs_id"] = obs_id
    observed_at = _optional_body_float(data.get("observed_at"))
    if observed_at is not None:
        observation_kwargs["observed_at"] = observed_at
    time_span = _time_span_from_json(data.get("time_span"))
    if time_span is not None:
        observation_kwargs["time_span"] = time_span
    return Observation(**observation_kwargs)


def _obsidian_event(node_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "obsidian_note",
        "source": "web_console.obsidian_node",
        "provenance_stream_id": f"web:obsidian:{uuid.uuid4().hex[:12]}",
        "payload": node_payload,
        "timestamp": time.time(),
    }


def _default_obsidian_vault_path(raw: Any = "") -> Path:
    candidate = str(raw or os.environ.get("GOSLO_OBSIDIAN_VAULT") or "").strip()
    if candidate:
        return Path(candidate).expanduser().resolve()
    root = Path("D:/GOSLOParrot/GOSLObsidian")
    return root.resolve()


def _obsidian_profile_target(profile: str) -> str:
    if profile == "roleplay":
        return "obsidian_setting_roleplay"
    if profile == "ref":
        return "ref_binding"
    return "obsidian_setting_daily"


def _obsidian_profile_descriptions() -> dict[str, str]:
    return {
        "daily": "UUID-free setting profile",
        "roleplay": "UUID-free mode/profile; may contain many source packs",
        "ref": "binding profile; requires existing target UUID",
    }


def _calendar_fetch_params(body: dict[str, Any]) -> dict[str, Any]:
    """Build the Nanobot task params shared by draft and dispatch receipts."""

    return {
        "query": str(body.get("query") or "Fetch today's Google Calendar events for the user"),
        "instructions": str(
            body.get("instructions")
            or (
                "Use the Google Calendar API or MCP tool to get today's events. "
                "For each event, extract: id, title, start_time (ISO 8601), "
                "end_time, location, description, html_link, etag, updated, "
                "status, iCalUID, and any mentioned objects or items to prepare. "
                "Also flag if the event is marked urgent/important. Return as "
                "JSON only: "
                '[{"id": str, "title": str, "start_time": str, "end_time": str, '
                '"location": str, "description": str, "objects": [str], '
                '"is_urgent": bool, "html_link": str, "etag": str, '
                '"updated": str, "status": str, "iCalUID": str}]'
            )
        ),
        "result_channel": str(body.get("result_channel") or "calendar_result"),
    }


def _calendar_time_window(
    body: dict[str, Any],
    *,
    timezone_name: str,
) -> tuple[str, str]:
    time_min = str(body.get("time_min") or body.get("timeMin") or "").strip()
    time_max = str(body.get("time_max") or body.get("timeMax") or "").strip()
    if time_min and time_max:
        return time_min, time_max

    date_text = str(body.get("date") or "").strip()
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        tz = timezone.utc
    if date_text:
        day = datetime.fromisoformat(date_text).date()
        start = datetime.combine(day, datetime.min.time(), tzinfo=tz)
    else:
        start = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return time_min or start.isoformat(), time_max or end.isoformat()


async def _fetch_google_calendar_events_from_api(
    *,
    calendar_id: str,
    time_min: str,
    time_max: str,
    limit: int,
    show_deleted: bool,
) -> dict[str, Any]:
    creds, source = _load_google_calendar_credentials()

    def _request() -> dict[str, Any]:
        import requests
        from google.auth.transport.requests import Request

        if not creds.valid:
            creds.refresh(Request())

        url = (
            "https://www.googleapis.com/calendar/v3/calendars/"
            f"{requests.utils.quote(calendar_id, safe='')}/events"
        )
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {creds.token}"},
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": str(limit),
                "showDeleted": "true" if show_deleted else "false",
            },
            timeout=20,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Google Calendar API {response.status_code}: {response.text[:240]}"
            )
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Google Calendar API returned a non-object payload")
        data["credential_source"] = source
        return data

    import asyncio

    return await asyncio.to_thread(_request)


def _load_google_calendar_credentials():
    from google.oauth2.credentials import Credentials

    path = _google_calendar_credentials_path()
    if not path.exists():
        raise FileNotFoundError(
            "Google Workspace OAuth credentials not found. "
            "Run scripts/google_oauth.py or mount ECS google-workspace credentials."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    scopes = data.get("scopes") or str(data.get("scope") or "").split()
    client_id = str(data.get("client_id") or os.getenv("GOOGLE_CLIENT_ID") or "")
    client_secret = str(data.get("client_secret") or os.getenv("GOOGLE_CLIENT_SECRET") or "")
    token_uri = str(data.get("token_uri") or "https://oauth2.googleapis.com/token")
    token = str(data.get("token") or data.get("access_token") or "")
    refresh_token = str(data.get("refresh_token") or "")
    if not token or not refresh_token or not client_id or not client_secret:
        raise RuntimeError("Google OAuth credentials are incomplete")

    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes or None,
    )
    expiry = data.get("expiry")
    if expiry:
        try:
            creds.expiry = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
        except ValueError:
            pass
    elif data.get("expiry_date"):
        try:
            creds.expiry = datetime.fromtimestamp(float(data["expiry_date"]) / 1000.0)
        except (TypeError, ValueError):
            pass
    return creds, _google_calendar_credential_source(path)


def _google_calendar_credentials_path() -> Path:
    configured = str(
        os.getenv("PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH")
        or os.getenv("GOOGLE_WORKSPACE_CREDENTIALS_PATH")
        or ""
    ).strip()
    if configured:
        return Path(configured).expanduser()

    appdata = os.getenv("APPDATA")
    candidates: list[Path] = []
    if appdata:
        base = Path(appdata) / "google-workspace-mcp" / "credentials"
        candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    base = Path.home() / ".nanobot" / "google-workspace-credentials"
    candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    base = Path.home() / ".local" / "share" / "google-workspace-mcp" / "credentials"
    candidates.extend([base / "credentials_python.json", base / "credentials.json"])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else Path("credentials_python.json")


def _google_calendar_credential_source(path: Path) -> str:
    if os.getenv("PARROT_WEB_CONSOLE_GOOGLE_CREDENTIALS_PATH") or os.getenv(
        "GOOGLE_WORKSPACE_CREDENTIALS_PATH"
    ):
        return "configured_oauth_file"
    path_parts = {part.lower() for part in path.parts}
    if ".nanobot" in path_parts and "google-workspace-credentials" in path_parts:
        return "ecs_nanobot_google_workspace_mcp"
    if "google-workspace-mcp" in path_parts:
        return "local_google_workspace_mcp"
    return "local_oauth_file"


async def _fetch_google_calendar_events_from_nanobot(
    *,
    account: str,
    calendar_id: str,
    time_min: str,
    time_max: str,
    timezone_name: str,
    limit: int,
    show_deleted: bool,
) -> dict[str, Any]:
    url = _nanobot_chat_completions_url()
    timeout_s = _env_float("PARROT_WEB_CONSOLE_NANOBOT_TIMEOUT_S", 90.0)
    model = str(os.getenv("PARROT_WEB_CONSOLE_NANOBOT_MODEL") or "gemini-2.5-flash")
    session_id = f"web-calendar-{uuid.uuid4().hex[:12]}"
    prompt = _calendar_nanobot_prompt(
        account=account,
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max,
        timezone_name=timezone_name,
        limit=limit,
        show_deleted=show_deleted,
    )

    def _request() -> dict[str, Any]:
        import requests

        response = requests.post(
            url,
            json={
                "model": model,
                "session_id": session_id,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout_s,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Nanobot API {response.status_code}: {response.text[:240]}")
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Nanobot API returned a non-object payload")
        return data

    import asyncio

    return await asyncio.to_thread(_request)


def _calendar_nanobot_prompt(
    *,
    account: str,
    calendar_id: str,
    time_min: str,
    time_max: str,
    timezone_name: str,
    limit: int,
    show_deleted: bool,
) -> str:
    return (
        "Task: calendar_fetch. Use the google-workspace skill and the "
        "manage_calendar MCP tool with account "
        f"{account}. List events from calendar {calendar_id!r} between "
        f"{time_min} and {time_max} ({timezone_name}), max {limit}. "
        f"show_deleted={str(show_deleted).lower()}. Return only valid JSON, "
        "no markdown, with this schema: "
        '{"status":"success","event_count":number,"events":[{"id":str,'
        '"calendar_id":str,"summary":str,"title":str,"start_time":str,'
        '"end_time":str,"location":str,"description":str,"html_link":str,'
        '"etag":str,"updated":str,"status":str,"iCalUID":str,'
        '"objects":[str],"is_urgent":bool}],"error":str}. '
        "Do not include OAuth tokens, authorization headers, emails other than "
        "the configured account, or credential file paths."
    )


def _nanobot_chat_completions_url() -> str:
    configured = str(
        os.getenv("PARROT_WEB_CONSOLE_NANOBOT_API_URL")
        or os.getenv("NANOBOT_API_URL")
        or "http://127.0.0.1:8900/v1/chat/completions"
    ).strip()
    if not configured:
        configured = "http://127.0.0.1:8900/v1/chat/completions"
    cleaned = configured[:-1] if configured.endswith("/") else configured
    if cleaned.endswith("/chat/completions"):
        return cleaned
    if cleaned.endswith("/v1"):
        return f"{cleaned}/chat/completions"
    return f"{cleaned}/v1/chat/completions"


def _parse_nanobot_calendar_response(response: dict[str, Any]) -> dict[str, Any]:
    from parrot.dsg.triggers.calendar_trigger import _extract_event_list, _loads_jsonish

    content = _nanobot_message_content(response)
    parsed = _loads_jsonish(content) if content else response
    parse_error = ""
    if content and parsed == [] and content.strip() not in {"[]", "```json\n[]\n```", "```[]```"}:
        parse_error = "nanobot_reply_not_json"
    events = [
        dict(item)
        for item in _extract_event_list(parsed)
        if isinstance(item, dict)
    ]
    status = ""
    event_count: int | None = None
    if isinstance(parsed, dict):
        status = str(parsed.get("status") or parsed.get("state") or "")
        try:
            event_count = int(parsed["event_count"]) if "event_count" in parsed else None
        except (TypeError, ValueError):
            event_count = None
    elif isinstance(parsed, list):
        status = "success"
        event_count = len(events)
    if event_count is None:
        event_count = len(events)
    return {
        "status": status or ("success" if events or not parse_error else "error"),
        "event_count": event_count,
        "events": events,
        "reply_sample": _redact_secret_text(content)[:2000] if parse_error else "",
        "parse_error": parse_error,
    }


def _nanobot_message_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    return content
            text = first.get("text")
            if isinstance(text, str):
                return text
    for key in ("content", "result", "reply", "message"):
        value = response.get(key)
        if isinstance(value, str):
            return value
    return ""


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _redact_secret_text(value: str) -> str:
    text = str(value or "")
    secret_patterns = (
        r'(?i)("?(?:access_token|refresh_token|id_token|client_secret|authorization|api_key)"?\s*[:=]\s*)("[^"]+"|[^\s,}]+)',
        r"(?i)(bearer\s+)[a-z0-9._~+/=-]+",
        r"(?i)(ya29\.)[a-z0-9._~+/=-]+",
        r"(?i)(sk-)[a-z0-9._-]+",
    )
    import re

    redacted = text
    for pattern in secret_patterns:
        redacted = re.sub(pattern, r"\1<redacted>", redacted)
    return redacted


def _calendar_mapping_rows(
    events: list[dict[str, Any]],
    observations: list[Any],
) -> list[dict[str, Any]]:
    """Explain how Calendar events will flow through source -> L1.5 -> L2-B.

    This is a Web-only readability layer. It deliberately does not add a shared
    DTO: the authoritative write still happens through
    ``CalendarTrigger._event_to_observation`` and ``L15Pool.admit``.
    """

    rows: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        observation = observations[index] if index < len(observations) else None
        meta = getattr(observation, "meta", {}) or {}
        calendar_id = str(
            event.get("calendar_id")
            or meta.get("calendar_id")
            or "primary"
        )
        event_id = str(
            event.get("id")
            or event.get("calendar_event_id")
            or meta.get("calendar_event_id")
            or ""
        )
        status = str(event.get("status") or meta.get("status") or "").lower()
        l2b_action = "upsert_event"
        policy_note = "merge_by_google_event_identity"
        if status in {"cancelled", "canceled", "deleted"}:
            l2b_action = "mark_historical_tombstone"
            policy_note = "keep_google_identity_and_set_ghost_state"
        rows.append(
            {
                "raw_index": index,
                "title": str(event.get("title") or getattr(observation, "label", "") or ""),
                "status": status or "confirmed_or_unspecified",
                "calendar_id": calendar_id,
                "calendar_event_id": event_id,
                "provider_ref": f"google_calendar:{calendar_id}:{event_id}" if event_id else "",
                "l15_bucket": "google_calendar",
                "l2b_kind": "event",
                "l2b_action": l2b_action,
                "merge_key": f"{calendar_id}:{event_id}" if event_id else "",
                "intent_workspace_policy": "not_used_for_read_sync",
                "nanobot_result_channel": "calendar_result",
                "policy_note": policy_note,
            }
        )
    return rows


def _calendar_result_history_row(
    stream_id: str,
    fields: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _load_result_payload(fields.get("payload"))
    result_channel = str(
        payload.get("type")
        or fields.get("result_channel")
        or ""
    )
    if result_channel != "calendar_result":
        return None

    events = _calendar_events_from_result_payload(payload)
    return {
        "stream_id": stream_id,
        "created_at": _body_float(fields.get("created_at"), 0.0),
        "task_id": str(payload.get("task_id") or fields.get("task_id") or ""),
        "result_channel": result_channel,
        "original_type": str(payload.get("original_type") or ""),
        "status": str(payload.get("status") or ""),
        "event_count": len(events),
        "event_sample": [
            {
                "id": str(event.get("id") or event.get("calendar_event_id") or ""),
                "title": str(event.get("title") or event.get("summary") or event.get("label") or ""),
                "status": str(event.get("status") or ""),
                "start": _calendar_event_start(event),
            }
            for event in events[:4]
            if isinstance(event, dict)
        ],
        "result_summary": _calendar_result_summary(payload, events),
        "payload": _redact_secrets(payload),
    }


def _load_result_payload(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return {"result": raw}
    return dict(decoded) if isinstance(decoded, dict) else {"result": decoded}


def _calendar_events_from_result_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        from parrot.dsg.triggers.calendar_trigger import _extract_event_list, _loads_jsonish

        raw_result = payload.get("result")
        source = raw_result if "result" in payload else payload
        return [
            dict(item)
            for item in _extract_event_list(_loads_jsonish(source))
            if isinstance(item, dict)
        ]
    except Exception:
        return []


def _calendar_result_summary(
    payload: dict[str, Any],
    events: list[dict[str, Any]],
) -> str:
    summary = str(payload.get("summary") or "").strip()
    if summary:
        return summary[:180]
    result = payload.get("result")
    if isinstance(result, str) and result.strip():
        return result.strip().replace("\n", " ")[:180]
    if events:
        titles = [
            str(event.get("title") or event.get("summary") or event.get("id") or "")
            for event in events[:3]
        ]
        return ", ".join(item for item in titles if item)[:180]
    return str(payload.get("status") or "")[:180]


def _calendar_event_start(event: dict[str, Any]) -> str:
    start = event.get("start")
    if isinstance(start, dict):
        return str(event.get("start_time") or start.get("dateTime") or start.get("date") or "")
    return str(event.get("start_time") or start or "")


def _ref_scan_result_history_row(
    stream_id: str,
    fields: dict[str, Any],
) -> dict[str, Any] | None:
    payload = _load_result_payload(fields.get("payload"))
    result_channel = str(
        payload.get("type")
        or fields.get("result_channel")
        or ""
    )
    if result_channel != "memory_ref_scan_result":
        return None

    result_body = _ref_scan_result_body(payload.get("result"))
    ref_results = _ref_scan_result_rows(result_body)
    manifest_delta = _ref_scan_manifest_delta(result_body)
    warnings = _ref_scan_warnings(result_body)
    return {
        "stream_id": stream_id,
        "created_at": _body_float(fields.get("created_at"), 0.0),
        "task_id": str(payload.get("task_id") or fields.get("task_id") or ""),
        "result_channel": result_channel,
        "original_type": str(payload.get("original_type") or ""),
        "status": str(payload.get("status") or ""),
        "scan_id": str(result_body.get("scan_id") or payload.get("scan_id") or ""),
        "ref_result_count": len(ref_results),
        "ref_result_sample": [
            {
                "ref_id": str(row.get("ref_id") or ""),
                "canonical_uuid": str(row.get("canonical_uuid") or ""),
                "health": str(row.get("health") or row.get("status") or ""),
                "resolved_locator": str(row.get("resolved_locator") or ""),
                "manifest_action": str(row.get("manifest_action") or ""),
            }
            for row in ref_results[:4]
            if isinstance(row, dict)
        ],
        "manifest_delta_count": len(manifest_delta),
        "warnings": warnings[:6],
        "result_summary": _ref_scan_result_summary(payload, result_body, ref_results),
        "payload": _redact_secrets(payload),
        "result_body": _redact_secrets(result_body),
    }


def _ref_scan_result_body(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, list):
        return {"ref_results": [dict(item) for item in raw if isinstance(item, dict)]}
    loaded = _load_result_payload(raw)
    result = loaded.get("result")
    if isinstance(result, list):
        return {"ref_results": [dict(item) for item in result if isinstance(item, dict)]}
    if isinstance(result, dict):
        return dict(result)
    return loaded


def _ref_scan_result_rows(body: dict[str, Any]) -> list[dict[str, Any]]:
    raw_rows = (
        body.get("ref_results")
        or body.get("refs")
        or body.get("rows")
        or body.get("locator_results")
    )
    if not isinstance(raw_rows, list):
        return []
    return [dict(item) for item in raw_rows if isinstance(item, dict)]


def _ref_scan_manifest_delta(body: dict[str, Any]) -> list[dict[str, Any]]:
    raw_delta = body.get("manifest_delta") or body.get("manifest_deltas")
    if isinstance(raw_delta, dict):
        return [dict(raw_delta)]
    if not isinstance(raw_delta, list):
        return []
    return [dict(item) for item in raw_delta if isinstance(item, dict)]


def _ref_scan_warnings(body: dict[str, Any]) -> list[str]:
    raw_warnings = body.get("warnings") or body.get("warning") or []
    if isinstance(raw_warnings, str):
        return [raw_warnings]
    if isinstance(raw_warnings, (list, tuple, set)):
        return [str(item) for item in raw_warnings if str(item)]
    return []


def _ref_scan_result_summary(
    payload: dict[str, Any],
    result_body: dict[str, Any],
    ref_results: list[dict[str, Any]],
) -> str:
    summary = str(result_body.get("summary") or payload.get("summary") or "").strip()
    if summary:
        return summary[:180]
    if ref_results:
        parts = [
            f"{str(row.get('ref_id') or '-')}: {str(row.get('health') or row.get('status') or 'unknown')}"
            for row in ref_results[:3]
            if isinstance(row, dict)
        ]
        return ", ".join(parts)[:180]
    raw_result = payload.get("result")
    if isinstance(raw_result, str) and raw_result.strip():
        return raw_result.strip().replace("\n", " ")[:180]
    return str(payload.get("status") or "")[:180]


def _obsidian_selected_paths(raw: Any) -> set[str]:
    if isinstance(raw, str):
        values: Any = [raw]
    else:
        values = raw
    if not isinstance(values, (list, tuple, set)):
        return set()
    return {
        str(item).strip().replace("\\", "/")
        for item in values
        if str(item).strip()
    }


def _obsidian_selected_profiles(raw: Any) -> set[str]:
    if isinstance(raw, str):
        values: Any = [raw]
    else:
        values = raw
    if not isinstance(values, (list, tuple, set)):
        return set()
    return {
        str(item).strip().lower().replace("-", "_")
        for item in values
        if str(item).strip()
    }


def _relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


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


def _edge_payload_from_body(body: dict[str, Any], kind: str) -> dict[str, Any]:
    """Normalize a Web edge form into the current SemanticEdge payload.

    The backend preserves both stable L2-B edge fields and the free-form
    ``meta`` dict. Stable fields exist for filters and graph algorithms; meta
    keeps source-specific details without losing Graphiti/Ref provenance.
    """
    from parrot.dsg.l2b_types import edge_view_classes

    meta = body.get("meta") if isinstance(body.get("meta"), dict) else {}
    graphiti_uuid = str(
        body.get("graphiti_uuid")
        or body.get("hit_graphiti_uuid")
        or meta.get("graphiti_uuid")
        or meta.get("hit_graphiti_uuid")
        or meta.get("graphiti_hit_uuid")
        or ""
    )
    source_graphiti_uuid = str(
        body.get("source_graphiti_uuid")
        or meta.get("source_graphiti_uuid")
        or ""
    )
    target_graphiti_uuid = str(
        body.get("target_graphiti_uuid")
        or meta.get("target_graphiti_uuid")
        or ""
    )
    raw_ref_ids = body.get("ref_ids") or meta.get("ref_ids") or ()
    if isinstance(raw_ref_ids, str):
        ref_ids = tuple(item.strip() for item in raw_ref_ids.split(",") if item.strip())
    elif isinstance(raw_ref_ids, (list, tuple, set)):
        ref_ids = tuple(str(item) for item in raw_ref_ids if str(item))
    else:
        ref_ids = ()
    view_classes = edge_view_classes(kind)
    meta = {
        **meta,
        "view_classes": view_classes,
    }
    if graphiti_uuid:
        meta.setdefault("graphiti_uuid", graphiti_uuid)
    if source_graphiti_uuid:
        meta.setdefault("source_graphiti_uuid", source_graphiti_uuid)
    if target_graphiti_uuid:
        meta.setdefault("target_graphiti_uuid", target_graphiti_uuid)
    if ref_ids:
        meta.setdefault("ref_ids", ref_ids)
    return {
        "kind": kind,
        "strength": max(0.0, min(_body_float(body.get("strength"), 0.5), 1.0)),
        "source": str(body.get("source") or "web_console"),
        "graphiti_uuid": graphiti_uuid,
        "source_graphiti_uuid": source_graphiti_uuid,
        "target_graphiti_uuid": target_graphiti_uuid,
        "ref_ids": ref_ids,
        "view_classes": view_classes,
        "meta": meta,
    }


def _select_resolved_graphiti_edge(
    resolver_result: dict[str, Any],
    body: dict[str, Any],
) -> dict[str, Any] | None:
    edges = resolver_result.get("edges")
    if not isinstance(edges, list) or not edges:
        return None
    requested = body.get("edge_index", body.get("selected_edge_index", body.get("index", 0)))
    try:
        requested_index = int(requested)
    except (TypeError, ValueError):
        requested_index = 0
    for edge in edges:
        if isinstance(edge, dict) and int(edge.get("index") or 0) == requested_index:
            return edge
    if _graphiti_edge_index_requested(body):
        return None
    first = edges[0]
    return first if isinstance(first, dict) else None


def _graphiti_edge_index_requested(body: dict[str, Any]) -> bool:
    return any(key in body for key in ("edge_index", "selected_edge_index", "index"))


def _graphiti_l2b_edge_apply_payload(
    body: dict[str, Any],
    resolver_result: dict[str, Any],
    selected_edge: dict[str, Any],
) -> dict[str, Any]:
    from parrot.dsg.l2b_types import EdgeKind

    draft = (
        dict(selected_edge.get("l2b_edge_draft"))
        if isinstance(selected_edge.get("l2b_edge_draft"), dict)
        else {}
    )
    meta = dict(draft.get("meta")) if isinstance(draft.get("meta"), dict) else {}
    requested_kind = str(draft.get("kind") or EdgeKind.GRAPHITI_FACT.value)
    kind = _parse_enum(EdgeKind, requested_kind)
    if kind is None:
        meta.setdefault("requested_kind", requested_kind)
        meta.setdefault("kind_normalized_reason", "invalid_graphiti_edge_kind")
        requested_kind = EdgeKind.GRAPHITI_FACT.value
    else:
        requested_kind = kind.value

    raw_edge = _selected_graphiti_raw_edge_body(body, int(selected_edge.get("index") or 0))
    if raw_edge:
        meta.setdefault("graphiti_raw_edge", raw_edge)
    graphiti_raw = body.get("graphiti_raw")
    if isinstance(graphiti_raw, dict):
        meta.setdefault("graphiti_raw", graphiti_raw)
    if draft.get("label"):
        meta.setdefault("fact_label", str(draft.get("label") or ""))
    meta.setdefault("materialized_by", "memory.identity_ref_index.apply_graphiti_edge")
    meta.setdefault(
        "graphiti_resolver",
        {
            "edge_index": selected_edge.get("index", 0),
            "partition": resolver_result.get("partition", ""),
            "ready_count": resolver_result.get("ready_count", 0),
            "blocked_count": resolver_result.get("blocked_count", 0),
            "source_status": (selected_edge.get("source") or {}).get("status", ""),
            "target_status": (selected_edge.get("target") or {}).get("status", ""),
            "fact_status": (selected_edge.get("fact") or {}).get("status", ""),
            "resolver": "MemoryIdentityRefIndex.resolve_graphiti_subgraph",
        },
    )
    return {
        "from_uuid": str(draft.get("source_uuid") or ""),
        "to_uuid": str(draft.get("target_uuid") or ""),
        "kind": requested_kind,
        "strength": _body_float(draft.get("strength"), 0.5),
        "source": "graphiti",
        "graphiti_uuid": str(draft.get("graphiti_uuid") or ""),
        "source_graphiti_uuid": str(draft.get("source_graphiti_uuid") or ""),
        "target_graphiti_uuid": str(draft.get("target_graphiti_uuid") or ""),
        "ref_ids": draft.get("ref_ids") or meta.get("ref_ids") or (),
        "meta": meta,
    }


async def _maybe_write_graphiti_ref_audit_episode(
    body: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    audit_draft = (
        dict(plan.get("audit_episode_draft"))
        if isinstance(plan.get("audit_episode_draft"), dict)
        else {}
    )
    if not _body_bool(body.get("write_graphiti_audit_episode"), False):
        return {
            "written": False,
            "write_skipped_reason": "write_graphiti_audit_episode_not_requested",
            "draft": audit_draft,
            "direct_graphiti_write": False,
        }
    try:
        from parrot.brain.graphiti_console import add_episode

        result = await add_episode(
            name=str(audit_draft.get("name") or "ref_writeback_audit"),
            body=str(audit_draft.get("body") or ""),
            partition=str(audit_draft.get("partition") or body.get("partition") or "goslo"),
            source_description=str(
                audit_draft.get("source_description")
                or "parrot-web-console-ref-writeback-audit"
            ),
            dry_run=False,
        )
        payload = result.as_json() if hasattr(result, "as_json") else _jsonable(result)
        return {
            "written": bool(
                isinstance(payload, dict)
                and payload.get("success") is True
                and not payload.get("dry_run", False)
            ),
            "write_skipped_reason": "",
            "draft": audit_draft,
            "result": payload,
            "direct_graphiti_write": True,
        }
    except Exception as exc:
        return {
            "written": False,
            "write_skipped_reason": "graphiti_audit_episode_write_failed",
            "draft": audit_draft,
            "error": str(exc),
            "direct_graphiti_write": False,
        }


def _selected_graphiti_raw_edge_body(body: dict[str, Any], selected_index: int) -> dict[str, Any]:
    raw_edges = body.get("edge_drafts")
    if raw_edges is None:
        raw_edges = body.get("edges")
    if raw_edges is None:
        raw_edges = body.get("graphiti_edges")
    if isinstance(raw_edges, list):
        if 0 <= selected_index < len(raw_edges) and isinstance(raw_edges[selected_index], dict):
            return dict(raw_edges[selected_index])
        return {}
    keys = (
        "source_graphiti_uuid",
        "source_node_uuid",
        "source",
        "target_graphiti_uuid",
        "target_node_uuid",
        "target",
        "hit_graphiti_uuid",
        "graphiti_edge_uuid",
        "graphiti_uuid",
        "uuid",
        "label",
        "kind",
        "strength",
        "score",
        "meta",
    )
    return {key: body[key] for key in keys if key in body}


def _ref_scan_manifest_path(value: Any) -> Path:
    raw = str(value or os.getenv("PARROT_MEMORY_REF_MANIFEST_PATH") or "").strip()
    path = Path(raw) if raw else Path.cwd() / "codex_workspace" / "runtime_manifests" / "memory_refs_manifest.json"
    return path.expanduser().resolve()


def _ref_scan_git_root(value: Any) -> Path:
    raw = str(value or os.getenv("PARROT_GIT_ROOT") or "").strip()
    path = Path(raw) if raw else Path.cwd()
    return path.expanduser().resolve()


def _ref_scan_plan_row(ref: Any, *, index: Any, manifest_path: Path) -> dict[str, Any]:
    record = ref.to_dict() if hasattr(ref, "to_dict") else dict(ref)
    ref_id = str(record.get("ref_id") or "")
    canonical_uuid = str(record.get("canonical_uuid") or "")
    kind = str(record.get("kind") or "external")
    managed_by = str(record.get("managed_by") or "unknown")
    locators = _unique_texts(record.get("locators") or [])
    identity = index.identities.get(canonical_uuid) if canonical_uuid else None
    identity_links = _ref_scan_identity_links(identity)
    scan_targets = [_ref_scan_locator_target(locator, kind=kind) for locator in locators]
    checks = _ref_scan_checks(
        kind=kind,
        managed_by=managed_by,
        record=record,
        identity_links=identity_links,
        scan_targets=scan_targets,
    )
    mcp_tools = _unique_texts(
        [
            tool
            for target in scan_targets
            for tool in target.get("mcp_tools", [])
        ]
        + _ref_scan_tools_for_checks(checks)
    )
    row = {
        "ref_id": ref_id,
        "canonical_uuid": canonical_uuid,
        "kind": kind,
        "canonical_uri": str(record.get("canonical_uri") or f"parrot://refs/{ref_id}"),
        "locators": locators,
        "managed_by": managed_by,
        "current_health": str(record.get("health") or "unknown"),
        "content_hash": str(record.get("content_hash") or ""),
        "git_commit": str(record.get("git_commit") or ""),
        "identity_links": identity_links,
        "scan_targets": scan_targets,
        "nanobot_checks": checks,
        "mcp_tools": mcp_tools,
        "manifest_action": _ref_scan_manifest_action(
            record=record,
            scan_targets=scan_targets,
            checks=checks,
        ),
        "risk_level": _ref_scan_risk_level(record=record, scan_targets=scan_targets),
        "expected_result_fields": [
            "ref_id",
            "canonical_uuid",
            "health",
            "locator_results",
            "content_hash",
            "size",
            "mime_type",
            "mtime",
            "resolved_locator",
            "manifest_delta",
            "graphiti_uuid_statuses",
            "obsidian_uuid_statuses",
            "warnings",
        ],
        "manifest_path": str(manifest_path),
        "apply_policy": "operator_review_required",
        "write_back_route": "/api/memory/identity-ref-index/verify",
        "raw_ref": record,
    }
    return row


def _ref_scan_identity_links(identity: Any) -> dict[str, Any]:
    if identity is None:
        return {
            "l2b_uuid": "",
            "graphiti_entity_uuids": [],
            "graphiti_edge_uuids": [],
            "graphiti_episode_uuids": [],
            "obsidian_uuids": [],
            "provider_keys": [],
            "resolution_state": "missing_identity",
        }
    return {
        "l2b_uuid": str(getattr(identity, "l2b_uuid", "") or ""),
        "graphiti_entity_uuids": _unique_texts(getattr(identity, "graphiti_entity_uuids", [])),
        "graphiti_edge_uuids": _unique_texts(getattr(identity, "graphiti_edge_uuids", [])),
        "graphiti_episode_uuids": _unique_texts(getattr(identity, "graphiti_episode_uuids", [])),
        "obsidian_uuids": _unique_texts(getattr(identity, "obsidian_uuids", [])),
        "provider_keys": _unique_texts(getattr(identity, "provider_keys", [])),
        "resolution_state": str(getattr(identity, "resolution_state", "") or "unknown"),
    }


def _ref_scan_locator_target(locator: str, *, kind: str) -> dict[str, Any]:
    text = str(locator or "").strip()
    lowered = text.lower()
    target_type = "opaque_locator"
    checks = ["locator_reachable"]
    tools = ["mcp.locator_probe"]
    if lowered.startswith(("http://", "https://")):
        target_type = "url"
        checks = ["url_head", "url_metadata"]
        tools = ["mcp.http.head"]
    elif lowered.startswith(("ecs://", "ssh://", "sftp://")) or lowered.startswith("/root/") or lowered.startswith("root@"):
        target_type = "ecs_path"
        checks = ["ecs_path_stat", "remote_content_hash"]
        tools = ["mcp.ecs.filesystem.stat", "mcp.ecs.filesystem.hash"]
    elif lowered.startswith("graphiti://"):
        target_type = "graphiti_pointer"
        checks = ["graphiti_uuid_probe"]
        tools = ["mcp.graphiti.lookup"]
    elif _looks_like_path(text):
        target_type = "local_path"
        checks = ["local_path_stat", "local_content_hash"]
        tools = ["mcp.filesystem.stat", "mcp.filesystem.hash"]

    if "obsidian" in kind.lower() and "obsidian_frontmatter_uuid_probe" not in checks:
        checks.append("obsidian_frontmatter_uuid_probe")
        tools.append("mcp.filesystem.read_markdown_frontmatter")

    return {
        "locator": text,
        "target_type": target_type,
        "checks": checks,
        "mcp_tools": _unique_texts(tools),
    }


def _ref_scan_checks(
    *,
    kind: str,
    managed_by: str,
    record: dict[str, Any],
    identity_links: dict[str, Any],
    scan_targets: list[dict[str, Any]],
) -> list[str]:
    checks: list[str] = [
        check
        for target in scan_targets
        for check in target.get("checks", [])
    ]
    kind_lower = kind.lower()
    managed_lower = managed_by.lower()
    if not scan_targets:
        checks.append("missing_locator")
    if "graphiti" in kind_lower or any(
        identity_links.get(key)
        for key in ("graphiti_entity_uuids", "graphiti_edge_uuids", "graphiti_episode_uuids")
    ):
        checks.append("graphiti_uuid_probe")
    if "obsidian" in kind_lower or identity_links.get("obsidian_uuids"):
        checks.append("obsidian_uuid_probe")
    if "git" in managed_lower or record.get("git_commit"):
        checks.append("git_manifest_diff")
        checks.append("git_commit_reachability")
    if record.get("content_hash"):
        checks.append("content_hash_compare")
    if record.get("canonical_uuid"):
        checks.append("canonical_uuid_binding_check")
    return _unique_texts(checks)


def _ref_scan_tools_for_checks(checks: list[str]) -> list[str]:
    tools: list[str] = []
    mapping = {
        "graphiti_uuid_probe": "mcp.graphiti.lookup",
        "obsidian_uuid_probe": "mcp.filesystem.read_markdown_frontmatter",
        "obsidian_frontmatter_uuid_probe": "mcp.filesystem.read_markdown_frontmatter",
        "git_manifest_diff": "mcp.git.diff",
        "git_commit_reachability": "mcp.git.rev_parse",
        "canonical_uuid_binding_check": "identity_ref_index.lookup",
        "content_hash_compare": "mcp.filesystem.hash",
        "missing_locator": "identity_ref_index.report",
    }
    for check in checks:
        if check in mapping:
            tools.append(mapping[check])
    return tools


def _ref_scan_manifest_action(
    *,
    record: dict[str, Any],
    scan_targets: list[dict[str, Any]],
    checks: list[str],
) -> str:
    if not scan_targets:
        return "record_missing_locator"
    if "git_manifest_diff" in checks:
        return "compare_git_manifest_and_ref_record"
    if record.get("content_hash"):
        return "compare_manifest_fingerprint"
    return "propose_manifest_fingerprint"


def _ref_scan_risk_level(
    *,
    record: dict[str, Any],
    scan_targets: list[dict[str, Any]],
) -> str:
    health = str(record.get("health") or "").lower()
    target_types = {str(target.get("target_type") or "") for target in scan_targets}
    if health in {"missing", "broken", "tombstoned"} or not scan_targets:
        return "high"
    if "ecs_path" in target_types or "opaque_locator" in target_types:
        return "medium"
    return "low"


def _ref_scan_task_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ref_id": row.get("ref_id", ""),
        "canonical_uuid": row.get("canonical_uuid", ""),
        "kind": row.get("kind", ""),
        "locators": row.get("locators", []),
        "current_health": row.get("current_health", ""),
        "content_hash": row.get("content_hash", ""),
        "nanobot_checks": row.get("nanobot_checks", []),
        "mcp_tools": row.get("mcp_tools", []),
        "manifest_action": row.get("manifest_action", ""),
        "risk_level": row.get("risk_level", ""),
    }


def _ref_scan_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    by_target_type: dict[str, int] = {}
    by_check: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    for row in rows:
        kind = str(row.get("kind") or "external")
        by_kind[kind] = by_kind.get(kind, 0) + 1
        risk = str(row.get("risk_level") or "unknown")
        by_risk[risk] = by_risk.get(risk, 0) + 1
        for target in row.get("scan_targets", []):
            target_type = str(target.get("target_type") or "unknown")
            by_target_type[target_type] = by_target_type.get(target_type, 0) + 1
        for check in row.get("nanobot_checks", []):
            check_name = str(check)
            by_check[check_name] = by_check.get(check_name, 0) + 1
    return {
        "ref_count": len(rows),
        "by_kind": dict(sorted(by_kind.items())),
        "by_target_type": dict(sorted(by_target_type.items())),
        "by_check": dict(sorted(by_check.items())),
        "by_risk": dict(sorted(by_risk.items())),
    }


def _ref_scan_remote_checks(body: dict[str, Any]) -> list[str]:
    requested = {item.lower() for item in _unique_texts(body.get("remote_checks"))}
    aliases = {
        "http": "url",
        "http_head": "url",
        "url_head": "url",
        "ecs_path": "ecs",
        "ecs_path_stat": "ecs",
        "graphiti_uuid_probe": "graphiti",
        "graphiti_search_probe": "graphiti",
    }
    normalized = {aliases.get(item, item) for item in requested}
    if _body_bool(body.get("enable_url_check"), False):
        normalized.add("url")
    if _body_bool(body.get("enable_ecs_local_check"), False):
        normalized.add("ecs")
    if _body_bool(body.get("enable_graphiti_probe"), False):
        normalized.add("graphiti")
    return [item for item in ("url", "ecs", "graphiti") if item in normalized]


def _looks_like_path(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if text.startswith(("~", "/", "\\")):
        return True
    if len(text) >= 3 and text[1:3] in {":\\", ":/"}:
        return True
    return "\\" in text or "/" in text


def _unique_texts(values: Any) -> list[str]:
    if isinstance(values, str):
        iterable: list[Any] = [values]
    elif isinstance(values, (list, tuple, set)):
        iterable = list(values)
    else:
        iterable = []
    seen: set[str] = set()
    result: list[str] = []
    for item in iterable:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


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


def _identity_ref_payload_has_signal(body: dict[str, Any]) -> bool:
    for key in (
        "canonical_uuid",
        "l2b_uuid",
        "graphiti_uuid",
        "graphiti_entity_uuid",
        "graphiti_entity_uuids",
        "graphiti_edge_uuid",
        "graphiti_edge_uuids",
        "graphiti_episode_uuid",
        "graphiti_episode_uuids",
        "obsidian_uuid",
        "obsidian_uuids",
        "provider_key",
        "provider_keys",
        "ref_id",
        "locator",
        "locators",
        "path",
        "url",
    ):
        value = body.get(key)
        if isinstance(value, (list, tuple, set)) and any(str(item).strip() for item in value):
            return True
        if value is not None and str(value).strip():
            return True
    return False


def _bool_status_map(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, bool] = {}
    for key, item in value.items():
        text = str(key).strip()
        if text:
            out[text] = _body_bool(item, False)
    return out


def _body_float(value: Any, default: float) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _optional_body_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _time_span_from_json(value: Any) -> tuple[float, float | None] | None:
    if not isinstance(value, (list, tuple)) or not value:
        return None
    start = _optional_body_float(value[0])
    if start is None:
        return None
    end = _optional_body_float(value[1]) if len(value) > 1 else None
    return (start, end)


def _body_int_limit(
    value: Any,
    *,
    default: int,
    minimum: int = 1,
    maximum: int,
) -> tuple[int, dict[str, Any] | None]:
    if value is None or value == "":
        return default, None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default, {
            "field": "limit",
            "error": "invalid_limit",
            "value": str(value),
            "default": default,
            "minimum": minimum,
            "maximum": maximum,
        }
    return max(minimum, min(parsed, maximum)), None


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


def _redact_secrets(value: Any) -> Any:
    """Redact obvious secrets before returning operator history rows."""

    secret_markers = ("secret", "token", "authorization", "api_key", "apikey", "password")
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in secret_markers):
                out[key_text] = "<redacted>"
            else:
                out[key_text] = _redact_secrets(item)
        return out
    if isinstance(value, list):
        return [_redact_secrets(item) for item in value]
    if isinstance(value, str):
        lowered = value.lower()
        if value.startswith("sk-") or lowered.startswith("bearer "):
            return "<redacted>"
    return value
