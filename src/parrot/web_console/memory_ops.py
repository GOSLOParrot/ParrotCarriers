"""Web Console BFF helpers for DSG memory/operator workflows.

This module is intentionally Web-only. It returns operator receipts and draft
payloads for the console without changing App-facing DTOs. Dangerous writes
default to dry-run and require an explicit operator flag.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
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
            "apply_route": "",
            "core_candidate": "CORE-006",
            "shared_status": "candidate_only",
            "policy": (
                "draft_only_until_CORE_006_is_ratified; Web operator apply must "
                "remain separate from Unity/App DTOs"
            ),
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
    """Build one reviewable plan for Graphiti -> L1.5 -> L2-B import.

    Graphiti export and graph-placement policy used to be two separate UI
    previews. Keeping them separate made the operator experience feel fake:
    the Source Board could show observations or a destination policy, but not
    one coherent import route. This Web-only wrapper joins both drafts without
    adding an apply route or bypassing L1.5.
    """

    from parrot.brain.graphiti_console import draft_graphiti_subgraph_export
    from parrot.web_console.graph_policy import draft_import_destination

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
            "subgraph": export_data.get("subgraph", {}),
            "export_write_path": export_data.get(
                "write_path",
                "L15Pool.admit(Observation(source=USER_EXPLICIT))",
            ),
            "edge_write_policy": export_data.get("edge_write_policy", ""),
            "import_policy": policy_data.get("policy", {}),
            "import_draft": policy_data.get("draft", {}),
            "policy_skipped_reason": policy_skipped_reason,
            "flow_steps": [
                "Graphiti.search scoped by partition",
                "operator selects hits",
                "draft Observation(source=USER_EXPLICIT) rows",
                "preview CORE-013 import destination / overlay policy",
                "real export, if chosen later, must admit through L1.5 under operator mode",
            ],
            "operator_required_for_execute": True,
            "apply_route": "/api/graphiti/subgraph/export",
            "apply_preconditions": {
                "dry_run": False,
                "operator_mode": True,
                "edge_apply": "separate L2-B edge route after node UUID resolution",
            },
            "warnings": list(export_data.get("warnings") or []),
            "core_candidates": ["CORE-008", "CORE-013"],
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

    The backend intentionally preserves the free-form ``meta`` dict. RustWorkX
    only needs the topology and edge payload object; source-specific tags,
    relation evidence, visual styles, or future attention hints can live inside
    ``meta`` until a field proves stable enough for promotion.
    """
    meta = body.get("meta") if isinstance(body.get("meta"), dict) else {}
    return {
        "kind": kind,
        "strength": max(0.0, min(_body_float(body.get("strength"), 0.5), 1.0)),
        "source": str(body.get("source") or "web_console"),
        "meta": meta,
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
