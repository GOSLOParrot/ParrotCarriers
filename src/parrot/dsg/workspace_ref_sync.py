"""Workspace ref synchronization between IntentWorkspace, RefIndex, and L2-B.

This module is a small CORE-015 implementation slice. It does not move files,
rewrite Graphiti, or treat rustworkx indices as identity. Its job is to make a
reviewable bridge for large payloads:

local/remote locator -> IntentWorkspace staged handle -> IdentityRefIndex ref
record -> L2-B pointer node/edge.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any


DEFAULT_HASH_MAX_BYTES = 5 * 1024 * 1024


def draft_workspace_ref_sync(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Draft a large-file/ref sync plan without mutating any runtime surface."""

    body = dict(payload or {})
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    locator = _first_text(body, "locator", "path", "url")
    if not locator:
        return _receipt(
            action="memory.workspace_ref_sync.draft",
            success=False,
            dry_run=True,
            operator_mode=False,
            data={
                "error": "missing_locator",
                "mutated": False,
                "direct_l2b_write": False,
                "identity_ref_index_write": False,
                "intent_workspace_write": False,
            },
        )

    kind = _clean_text(body.get("ref_kind") or body.get("kind") or _kind_from_locator(locator))
    ref_id = _clean_text(body.get("ref_id") or _default_ref_id(locator, kind=kind))
    canonical_uuid = _clean_text(body.get("canonical_uuid") or f"ref:{ref_id}")
    l2b_uuid = _clean_text(body.get("l2b_uuid") or canonical_uuid)
    label = _clean_text(body.get("label") or _label_from_locator(locator))
    owner_id = _clean_text(body.get("owner_id") or body.get("nanobot_task_id"))
    workspace_id = _clean_text(body.get("workspace_id") or "memory_graph")
    related_node_uuid = _clean_text(body.get("related_node_uuid"))
    hash_max_bytes = _body_int(body.get("hash_max_bytes"), DEFAULT_HASH_MAX_BYTES)

    # Inspect only what is cheap and local. Remote URLs/ECS locators are left
    # to nanobot/MCP checkers so a Brain request cannot unexpectedly block on
    # network or remote filesystem work.
    locator_info = _inspect_locator(locator, hash_max_bytes=hash_max_bytes)
    content_hash = _clean_text(body.get("content_hash") or locator_info.get("content_hash"))
    size = _body_int(body.get("size"), int(locator_info.get("size") or 0))
    managed_by = _clean_text(body.get("managed_by") or "nanobot+git")
    storage_tier = _storage_tier_for_locator(locator, size=size)

    # This metadata is deliberately repeated into IntentWorkspace,
    # IdentityRefIndex, and L2-B. Each surface has a different lifecycle, so the
    # same sync receipt must be inspectable even if one layer is rebuilt later.
    common_meta = {
        "schema_version": 1,
        "workspace_id": workspace_id,
        "owner_id": owner_id,
        "related_node_uuid": related_node_uuid,
        "storage_tier": storage_tier,
        "locator_status": locator_info.get("health", "unknown"),
        "hash_status": locator_info.get("hash_status", "not_hashed"),
        "payload_policy": "pointer_only_no_inline_large_payload",
        "sync_owner": "workspace_ref_sync",
    }

    # IdentityRefIndex is the durable binding owner: it remembers where the file
    # currently lives and which UUIDs refer to it. It stores locators and hashes,
    # not the file payload.
    identity_payload = {
        "canonical_uuid": canonical_uuid,
        "l2b_uuid": l2b_uuid,
        "ref_id": ref_id,
        "ref_kind": kind,
        "locator": locator,
        "locators": [locator],
        "canonical_uri": _clean_text(body.get("canonical_uri") or f"parrot://refs/{ref_id}"),
        "content_hash": content_hash,
        "size": size,
        "mime_type": _clean_text(body.get("mime_type")),
        "version": _clean_text(body.get("version")),
        "health": _clean_text(locator_info.get("health") or body.get("health") or "unknown"),
        "managed_by": managed_by,
        "git_commit": _clean_text(body.get("git_commit")),
        "alias": label,
        "resolution_state": _clean_text(body.get("resolution_state") or "weak"),
        "ref_meta": {
            **_dict(body.get("ref_meta")),
            "workspace_sync": common_meta,
        },
        "meta": {
            **_dict(body.get("meta")),
            "workspace_sync": common_meta,
        },
    }
    provider_key = _clean_text(body.get("provider_key"))
    if provider_key:
        identity_payload["provider_key"] = provider_key
    obsidian_uuid = _clean_text(body.get("obsidian_uuid"))
    if obsidian_uuid:
        identity_payload["obsidian_uuid"] = obsidian_uuid
    graphiti_uuid = _clean_text(body.get("graphiti_uuid") or body.get("graphiti_entity_uuid"))
    if graphiti_uuid:
        identity_payload["graphiti_entity_uuid"] = graphiti_uuid

    # L2-B gets a pointer node only. This keeps RustWorkX graph traversal fast
    # and avoids loading large files into the runtime graph.
    l2b_node = {
        "uuid": l2b_uuid,
        "kind": "object",
        "label": label,
        "category": "workspace_ref_pointer",
        "description": _clean_text(body.get("description") or f"Pointer to {locator}"),
        "attention": 0.32,
        "salience": "background",
        "confirmation": "expected",
        "bucket_id": _clean_text(body.get("bucket_id") or "intent_workspace"),
        "source": "identity_ref_index",
        "source_meta": {
            "ref_id": ref_id,
            "canonical_uuid": canonical_uuid,
            "locator": locator,
            "content_hash": content_hash,
            "workspace_id": workspace_id,
            "owner_id": owner_id,
            "storage_tier": storage_tier,
        },
        "meta": {
            "is_pointer": True,
            "ref_id": ref_id,
            "canonical_uuid": canonical_uuid,
            "payload_policy": "pointer_only_no_inline_large_payload",
            "workspace_sync": common_meta,
        },
    }
    edge_draft = {}
    if related_node_uuid:
        # Optional edge: use HAS_REF to connect an already-known semantic node
        # to this pointer. If the related node is absent during apply, the node
        # is still materialized and the edge is skipped with a receipt reason.
        edge_draft = {
            "source_uuid": related_node_uuid,
            "target_uuid": l2b_uuid,
            "kind": "has_ref",
            "strength": 0.75,
            "edge_source": "workspace_ref_sync",
            "ref_ids": [ref_id],
            "meta": {
                "canonical_uuid": canonical_uuid,
                "locator": locator,
                "workspace_id": workspace_id,
                "pointer_edge": True,
            },
        }

    return _receipt(
        action="memory.workspace_ref_sync.draft",
        success=True,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data={
            "ref_id": ref_id,
            "canonical_uuid": canonical_uuid,
            "l2b_uuid": l2b_uuid,
            "locator": locator,
            "locator_info": locator_info,
            "hash": {
                "content_hash": content_hash,
                "status": locator_info.get("hash_status", "not_hashed"),
                "max_bytes": hash_max_bytes,
            },
            "storage_policy": {
                "intent_workspace": "stage_path_or_url_handle_only",
                "identity_ref_index": "current_locator_truth",
                "l2b": "pointer_node_no_payload",
                "nanobot": "scan_and_repair_executor",
                "git": "reviewable_manifest_delta_not_runtime_database",
            },
            "intent_workspace_request": {
                "kind": _intent_kind_for_ref_kind(kind),
                "payload_source": _payload_source_for_locator(locator),
                "payload_value": locator,
                "owner_id": owner_id,
                "metadata": {
                    "origin": "workspace_ref_sync",
                    "related_node_uuid": related_node_uuid,
                    "related_intent_event_id": _clean_text(body.get("intent_event_id")),
                    "related_plan_id": _clean_text(body.get("plan_id")),
                    "custom_meta": {
                        "role": _clean_text(body.get("role") or "workspace_ref_pointer"),
                        "ref_id": ref_id,
                        "canonical_uuid": canonical_uuid,
                        "l2b_uuid": l2b_uuid,
                        "workspace_id": workspace_id,
                        "locator": locator,
                        "storage_tier": storage_tier,
                    },
                },
            },
            "identity_ref_payload": identity_payload,
            "l2b_node_draft": l2b_node,
            "l2b_edge_draft": edge_draft,
            "apply_route": "call apply_workspace_ref_sync(...)",
            "operator_required_for_execute": True,
            "mutated": False,
            "intent_workspace_write": False,
            "identity_ref_index_write": False,
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "direct_file_move": False,
        },
    )


async def apply_workspace_ref_sync(
    payload: dict[str, Any] | None = None,
    *,
    intent_workspace: Any | None = None,
    identity_index: Any | None = None,
    l2b_graph: Any | None = None,
) -> dict[str, Any]:
    """Apply a drafted workspace ref sync under an explicit operator gate."""

    body = dict(payload or {})
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_workspace_ref_sync(body)
    draft["action"] = "memory.workspace_ref_sync.apply"
    draft["dry_run"] = dry_run
    draft["operator_mode"] = operator_mode
    if not draft.get("success"):
        return draft
    if dry_run or not operator_mode:
        draft["data"]["would_apply"] = True
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    data = dict(draft.get("data") or {})
    locator_info = dict(data.get("locator_info") or {})

    # The apply order is intentional:
    # 1. Stage a temporary IntentWorkspace handle for the active actor.
    # 2. Persist the durable locator/UUID binding.
    # 3. Materialize the lightweight L2-B pointer.
    # None of these steps moves or rewrites the underlying file.
    intent_result: dict[str, Any] = {
        "enabled": _body_bool(body.get("stage_to_intent_workspace"), True),
        "written": False,
        "ref_id": "",
    }
    if intent_result["enabled"]:
        if _payload_source_for_locator(data["locator"]) == "disk_path" and locator_info.get("health") == "missing":
            return _receipt(
                action="memory.workspace_ref_sync.apply",
                success=False,
                dry_run=False,
                operator_mode=True,
                data={
                    **data,
                    "error": "cannot_stage_missing_local_path",
                    "mutated": False,
                    "intent_workspace_write": False,
                    "identity_ref_index_write": False,
                    "direct_l2b_write": False,
                    "direct_graphiti_write": False,
                    "direct_file_move": False,
                },
            )
        intent_result = await _stage_intent_workspace_ref(
            data["intent_workspace_request"],
            workspace=intent_workspace,
        )

    identity_result = {
        "enabled": _body_bool(body.get("write_identity_ref_index"), True),
        "written": False,
        "canonical_uuid": data["canonical_uuid"],
        "ref_id": data["ref_id"],
        "conflict_count": 0,
    }
    if identity_result["enabled"]:
        identity_result = _write_identity_ref_payload(
            data["identity_ref_payload"],
            intent_result=intent_result,
            identity_index=identity_index,
        )

    l2b_result = {
        "enabled": _body_bool(body.get("materialize_l2b"), True),
        "written": False,
        "node_uuid": data["l2b_uuid"],
        "edge_connected": False,
    }
    if l2b_result["enabled"]:
        l2b_result = _materialize_l2b_pointer(
            data["l2b_node_draft"],
            data["l2b_edge_draft"],
            l2b_graph=l2b_graph,
        )

    return _receipt(
        action="memory.workspace_ref_sync.apply",
        success=True,
        dry_run=False,
        operator_mode=True,
        data={
            **data,
            "intent_workspace": intent_result,
            "identity_ref_index": identity_result,
            "l2b": l2b_result,
            "mutated": bool(
                intent_result.get("written")
                or identity_result.get("written")
                or l2b_result.get("written")
            ),
            "intent_workspace_write": bool(intent_result.get("written")),
            "identity_ref_index_write": bool(identity_result.get("written")),
            "direct_l2b_write": bool(l2b_result.get("written")),
            "direct_graphiti_write": False,
            "direct_file_move": False,
            "mutation_scope": "intent_workspace_handle_identity_ref_index_json_l2b_pointer",
        },
    )


async def _stage_intent_workspace_ref(
    request: dict[str, Any],
    *,
    workspace: Any | None,
) -> dict[str, Any]:
    from parrot.brain.intent_workspace import (
        PayloadSource,
        StagedRefKind,
        StagedRefMetadata,
        StagedRefRequest,
        get_intent_workspace,
    )

    ws = workspace or get_intent_workspace()
    meta_raw = _dict(request.get("metadata"))
    custom_meta = _dict(meta_raw.get("custom_meta"))
    kind = _enum_value(StagedRefKind, request.get("kind"), StagedRefKind.OTHER)
    source = _enum_value(PayloadSource, request.get("payload_source"), PayloadSource.INLINE_TEXT)
    payload_value: Any = request.get("payload_value")
    if source == PayloadSource.DISK_PATH:
        payload_value = Path(str(payload_value)).expanduser()
    metadata = StagedRefMetadata(
        origin=_clean_text(meta_raw.get("origin") or "workspace_ref_sync"),
        kind=kind,
        payload_source=source,
        related_node_uuid=_clean_text(meta_raw.get("related_node_uuid")),
        related_intent_event_id=_clean_text(meta_raw.get("related_intent_event_id")),
        related_plan_id=_clean_text(meta_raw.get("related_plan_id")),
        auto_evict_on_intent_close=_body_bool(meta_raw.get("auto_evict_on_intent_close"), True),
        expires_at=_body_float(meta_raw.get("expires_at"), 0.0),
        custom_meta=custom_meta,
    )
    stage_request = StagedRefRequest(
        kind=kind,
        payload_source=source,
        payload_value=payload_value,
        metadata=metadata,
    )
    owner_id = _clean_text(request.get("owner_id"))
    if owner_id:
        # Nanobot/Plan subtasks use scoped writes so sibling actors do not
        # accidentally inherit each other's transient large-file handles.
        handle = await ws.scope(owner_id).stage(stage_request)
    else:
        handle = await ws.stage(stage_request)
    return {
        "enabled": True,
        "written": True,
        "ref_id": handle.ref_id,
        "kind": handle.kind.value if handle.kind else "",
        "payload_source": handle.metadata.payload_source.value,
        "owner_id": owner_id,
    }


def _write_identity_ref_payload(
    payload: dict[str, Any],
    *,
    intent_result: dict[str, Any],
    identity_index: Any | None,
) -> dict[str, Any]:
    from parrot.dsg.identity_ref_index import MemoryIdentityRefIndex

    index = identity_index or MemoryIdentityRefIndex()
    body = dict(payload)
    ref_meta = _dict(body.get("ref_meta"))
    workspace_sync = _dict(ref_meta.get("workspace_sync"))
    if intent_result.get("ref_id"):
        # Store the temporary IntentWorkspace handle as metadata only. The
        # durable binding remains the canonical/ref UUID plus locator/hash.
        workspace_sync["intent_workspace_ref_id"] = intent_result["ref_id"]
        workspace_sync["intent_workspace_owner_id"] = intent_result.get("owner_id", "")
    ref_meta["workspace_sync"] = workspace_sync
    body["ref_meta"] = ref_meta
    identity, ref = index.upsert(body)
    if identity_index is None:
        index.save()
    else:
        save = getattr(index, "save", None)
        if callable(save):
            save()
    return {
        "enabled": True,
        "written": True,
        "canonical_uuid": identity.canonical_uuid,
        "l2b_uuid": identity.l2b_uuid,
        "ref_id": ref.ref_id if ref is not None else "",
        "conflict_count": int(index.last_upsert_report.get("conflict_count", 0)),
        "merge_report": dict(index.last_upsert_report),
    }


def _materialize_l2b_pointer(
    node_draft: dict[str, Any],
    edge_draft: dict[str, Any],
    *,
    l2b_graph: Any | None,
) -> dict[str, Any]:
    from parrot.dsg.l2b_graph import get_l2b_graph
    from parrot.dsg.l2b_types import (
        ConfirmationStatus,
        EdgeKind,
        Salience,
        SemanticEdge,
        SemanticNode,
    )

    graph = l2b_graph or get_l2b_graph()
    node_uuid = _clean_text(node_draft.get("uuid"))
    if not node_uuid:
        return {"enabled": True, "written": False, "node_uuid": "", "error": "missing_node_uuid"}
    node = SemanticNode(
        uuid=node_uuid,
        label=_clean_text(node_draft.get("label")),
        category=_clean_text(node_draft.get("category") or "workspace_ref_pointer"),
        description=_clean_text(node_draft.get("description")),
        known_facts=[_clean_text(node_draft.get("description"))],
        tags=["workspace_ref", "pointer"],
        attention=_body_float(node_draft.get("attention"), 0.32),
        salience=_enum_value(Salience, node_draft.get("salience"), Salience.BACKGROUND),
        confirmation=_enum_value(
            ConfirmationStatus,
            node_draft.get("confirmation"),
            ConfirmationStatus.EXPECTED,
        ),
        bucket_id=_clean_text(node_draft.get("bucket_id") or "intent_workspace"),
        source=_clean_text(node_draft.get("source") or "identity_ref_index"),
        source_meta=_dict(node_draft.get("source_meta")),
        meta=_dict(node_draft.get("meta")),
    )
    graph.upsert_node(node)
    edge_connected = False
    edge_skipped_reason = ""
    if edge_draft:
        source_uuid = _clean_text(edge_draft.get("source_uuid"))
        target_uuid = _clean_text(edge_draft.get("target_uuid") or node_uuid)
        if graph.get_node(source_uuid) and graph.get_node(target_uuid):
            edge = SemanticEdge(
                kind=EdgeKind.HAS_REF,
                strength=_body_float(edge_draft.get("strength"), 0.75),
                source=_clean_text(edge_draft.get("edge_source") or "workspace_ref_sync"),
                ref_ids=tuple(_unique_texts(edge_draft.get("ref_ids"))),
                meta=_dict(edge_draft.get("meta")),
            )
            edge_connected = graph.connect(source_uuid, target_uuid, edge)
        else:
            edge_skipped_reason = "missing_related_or_pointer_node"
    return {
        "enabled": True,
        "written": True,
        "node_uuid": node_uuid,
        "edge_connected": edge_connected,
        "edge_skipped_reason": edge_skipped_reason,
        "node_policy": "l2b_pointer_no_payload",
    }


def _inspect_locator(locator: str, *, hash_max_bytes: int) -> dict[str, Any]:
    text = _clean_text(locator)
    if _is_url(text):
        # URL health needs HEAD/GET policy, auth, and timeout handling; that
        # belongs in ref_scan/nanobot rather than this synchronous draft path.
        return {
            "locator": text,
            "target_type": "url",
            "health": "unknown",
            "reason": "url_not_checked_in_sync_draft",
            "hash_status": "not_hashable_by_local_draft",
        }
    if text.lower().startswith(("ecs://", "ssh://", "sftp://", "root@")):
        # ECS paths can only be trusted from an ECS-side worker with an allowed
        # root list. Local desktop code records the pointer and defers probing.
        return {
            "locator": text,
            "target_type": "ecs_path",
            "health": "unknown",
            "reason": "remote_path_requires_nanobot_mcp_scan",
            "hash_status": "deferred_to_ref_scan",
        }
    path = Path(text).expanduser()
    try:
        exists = path.exists()
    except OSError as exc:
        return {
            "locator": text,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"local_path_probe_failed:{type(exc).__name__}",
            "hash_status": "not_hashed_probe_failed",
        }
    if not exists:
        return {
            "locator": text,
            "target_type": "local_path",
            "health": "missing",
            "reason": "local_path_missing",
            "hash_status": "not_hashed_missing",
        }
    try:
        stat = path.stat()
    except OSError as exc:
        return {
            "locator": text,
            "target_type": "local_path",
            "health": "unknown",
            "reason": f"local_path_stat_failed:{type(exc).__name__}",
            "hash_status": "not_hashed_stat_failed",
        }
    result: dict[str, Any] = {
        "locator": text,
        "target_type": "local_path",
        "health": "ok",
        "reason": "local_path_exists",
        "size": int(stat.st_size),
        "mtime": float(stat.st_mtime),
        "is_dir": path.is_dir(),
        "hash_status": "not_hashed_directory" if path.is_dir() else "not_hashed",
    }
    if path.is_file():
        if stat.st_size > hash_max_bytes:
            # Hashing large files inline can freeze the Brain/Web request. The
            # manifest/ref_scan path can hash asynchronously and write a receipt.
            result["hash_status"] = "deferred_large_file"
            result["hash_deferred_to"] = "nanobot_ref_scan_or_git_lfs_manifest"
        else:
            result["content_hash"] = _sha256_file(path)
            result["hash_status"] = "sha256_complete"
    return result


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _payload_source_for_locator(locator: str) -> str:
    return "url" if _is_url(locator) else "disk_path"


def _intent_kind_for_ref_kind(kind: str) -> str:
    text = kind.lower()
    if "photo" in text or "image" in text:
        return "photo"
    if "video" in text:
        return "video_short"
    if "audio" in text:
        return "audio_clip"
    if "plan" in text:
        return "plan"
    if "report" in text:
        return "rich_report"
    if "url" in text:
        return "url"
    if "doc" in text or "obsidian" in text or "file" in text:
        return "doc"
    return "other"


def _kind_from_locator(locator: str) -> str:
    if _is_url(locator):
        return "url"
    suffix = Path(locator).suffix.lower()
    if suffix in {".md", ".txt", ".doc", ".docx", ".pdf"}:
        return "local_doc"
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return "photo"
    if suffix in {".mp4", ".mov", ".webm"}:
        return "video_short"
    return "local_path"


def _storage_tier_for_locator(locator: str, *, size: int) -> str:
    if _is_url(locator):
        return "remote_url_pointer"
    if locator.lower().startswith(("ecs://", "ssh://", "sftp://", "root@")):
        return "remote_path_pointer"
    if size > DEFAULT_HASH_MAX_BYTES:
        return "large_local_file_pointer"
    return "local_file_pointer"


def _default_ref_id(locator: str, *, kind: str) -> str:
    label = _slug(Path(locator).stem or kind or "ref")
    digest = hashlib.sha1(locator.encode("utf-8", "replace")).hexdigest()[:12]
    return f"{kind}:{label}:{digest}"


def _label_from_locator(locator: str) -> str:
    if _is_url(locator):
        return locator.rstrip("/").split("/")[-1] or locator
    return Path(locator).name or locator


def _is_url(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://"))


def _enum_value(enum_cls: Any, raw: Any, default: Any) -> Any:
    try:
        return enum_cls(str(raw))
    except (TypeError, ValueError):
        return default


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _body_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _body_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _first_text(body: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _clean_text(body.get(key))
        if value:
            return value
    return ""


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _unique_texts(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        values = []
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = _clean_text(item)
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _slug(value: str) -> str:
    out = []
    for char in value.lower():
        if char.isalnum():
            out.append(char)
        elif char in {"-", "_", "."}:
            out.append(char)
        else:
            out.append("-")
    text = "".join(out).strip("-")
    return text[:40] or "ref"


def _receipt(
    *,
    action: str,
    success: bool,
    dry_run: bool,
    operator_mode: bool,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action": action,
        "success": success,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
        "generated_at": time.time(),
        "data": data,
    }


__all__ = ["apply_workspace_ref_sync", "draft_workspace_ref_sync"]
