"""Source Pack envelopes for Web Console source-to-L2-B imports.

The Source Pack is a Web/operator contract, not a new source of truth.  It
normalizes external rows (Graphiti bundles, Google Calendar events, Obsidian
notes) into a small reviewable envelope so every source can share the same
preview/import/subgraph language while preserving its own raw provenance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


SOURCE_PACK_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SourcePackItem:
    """One imported/reviewed source item.

    ``raw`` is intentionally optional and bounded by callers.  L2-B should
    store pointers and stable identities; large payloads remain in their source
    system or the operator receipt.
    """

    item_id: str
    label: str
    source_ref: str = ""
    source_kind: str = ""
    provider_ref: str = ""
    l2b_kind: str = ""
    l2b_uuid: str = ""
    ref_ids: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


def build_source_pack(
    *,
    source_kind: str,
    source_id: str,
    label: str,
    items: list[dict[str, Any]],
    destination: str = "isolated_compartment",
    source_ref: str = "",
    raw_summary: dict[str, Any] | None = None,
    materialization_hint: str = "l1_5_admit_then_l2b_work_subgraph",
) -> dict[str, Any]:
    """Return a normalized Source Pack envelope for a source-board import."""

    normalized_items = [
        _source_pack_item(row, source_kind=source_kind)
        for row in items
        if isinstance(row, dict)
    ]
    pack_seed = {
        "source_kind": _clean_token(source_kind) or "unknown",
        "source_id": str(source_id or ""),
        "item_ids": [item.item_id for item in normalized_items],
    }
    pack_id = _stable_pack_id(pack_seed)
    return {
        "schema_version": SOURCE_PACK_SCHEMA_VERSION,
        "pack_id": pack_id,
        "source_kind": _clean_token(source_kind) or "unknown",
        "source_id": str(source_id or ""),
        "source_ref": source_ref or str(source_id or ""),
        "label": str(label or source_kind or "Source pack")[:120],
        "destination": _clean_token(destination) or "isolated_compartment",
        "item_count": len(normalized_items),
        "items": [_jsonable(item) for item in normalized_items],
        "item_ids": [item.item_id for item in normalized_items],
        "provider_refs": [
            item.provider_ref for item in normalized_items if item.provider_ref
        ],
        "ref_ids": sorted({
            ref_id for item in normalized_items for ref_id in item.ref_ids if ref_id
        }),
        "raw_summary": _jsonable(raw_summary or {}),
        "materialization": {
            "state": "preview_until_operator_apply",
            "hint": materialization_hint,
            "l2b_policy": "pointer_or_lightweight_event_nodes_with_source_meta",
            "external_write": "never_from_source_pack",
        },
        "work_subgraph": {
            "uuid": work_subgraph_uuid(
                source_kind=source_kind,
                source_id=source_id,
                item_ids=[item.item_id for item in normalized_items],
            ),
            "label": str(label or source_kind or "Source pack")[:120],
            "membership_policy": "members_are_nodes_admitted_from_this_source_pack",
        },
    }


def source_pack_summary(source_pack: dict[str, Any]) -> dict[str, Any]:
    """Return the small part that is safe to persist on a L2-B grouping node."""

    items = source_pack.get("items") if isinstance(source_pack.get("items"), list) else []
    return {
        "schema_version": source_pack.get("schema_version", SOURCE_PACK_SCHEMA_VERSION),
        "pack_id": str(source_pack.get("pack_id") or ""),
        "source_kind": str(source_pack.get("source_kind") or ""),
        "source_id": str(source_pack.get("source_id") or ""),
        "source_ref": str(source_pack.get("source_ref") or ""),
        "label": str(source_pack.get("label") or ""),
        "destination": str(source_pack.get("destination") or ""),
        "item_count": len(items),
        "item_ids": [
            str(row.get("item_id") or "") for row in items if isinstance(row, dict)
        ][:80],
        "provider_refs": [
            str(row.get("provider_ref") or "")
            for row in items
            if isinstance(row, dict) and row.get("provider_ref")
        ][:80],
        "ref_ids": [
            str(ref_id)
            for ref_id in (source_pack.get("ref_ids") or [])
            if str(ref_id).strip()
        ][:80],
    }


def work_subgraph_uuid(
    *,
    source_kind: str,
    source_id: str,
    item_ids: list[str] | tuple[str, ...],
) -> str:
    seed = {
        "source_kind": _clean_token(source_kind) or "unknown",
        "source_id": str(source_id or ""),
        "item_ids": [str(item) for item in item_ids if str(item).strip()],
    }
    digest = hashlib.sha1(
        json.dumps(seed, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]
    return f"work-subgraph:{seed['source_kind']}:{digest}"


def _source_pack_item(row: dict[str, Any], *, source_kind: str) -> SourcePackItem:
    observation = row.get("observation") if isinstance(row.get("observation"), dict) else {}
    event = row.get("event") if isinstance(row.get("event"), dict) else {}
    meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
    obs_meta = observation.get("meta") if isinstance(observation.get("meta"), dict) else {}
    raw = row.get("raw") if isinstance(row.get("raw"), dict) else {}
    source_ref = str(
        row.get("source_ref")
        or row.get("path")
        or row.get("html_link")
        or obs_meta.get("html_link")
        or event.get("provenance_stream_id")
        or ""
    )
    provider_ref = str(
        row.get("provider_ref")
        or row.get("merge_key")
        or obs_meta.get("calendar_event_id")
        or obs_meta.get("message_id")
        or observation.get("obsidian_uuid")
        or row.get("path")
        or ""
    )
    item_id = str(
        row.get("item_id")
        or provider_ref
        or source_ref
        or observation.get("obs_id")
        or row.get("label")
        or ""
    ).strip()
    if not item_id:
        item_id = _stable_pack_id({"source_kind": source_kind, "row": row})
    ref_values: list[Any] = []
    for candidate in (
        row.get("ref_id"),
        row.get("ref_ids"),
        obs_meta.get("ref_id"),
        obs_meta.get("related_refs"),
        provider_ref,
    ):
        if isinstance(candidate, (list, tuple, set)):
            ref_values.extend(candidate)
        elif candidate:
            ref_values.append(candidate)
    return SourcePackItem(
        item_id=item_id[:180],
        label=str(row.get("label") or observation.get("label") or item_id)[:160],
        source_ref=source_ref[:500],
        source_kind=_clean_token(row.get("source_kind") or source_kind) or _clean_token(source_kind),
        provider_ref=provider_ref[:260],
        l2b_kind=str(row.get("l2b_kind") or observation.get("kind") or "")[:80],
        l2b_uuid=str(row.get("l2b_uuid") or row.get("node_uuid") or "")[:180],
        ref_ids=tuple(_unique_texts(ref_values)[:24]),
        raw=_jsonable(raw),
        meta=_jsonable({**meta, "observation_meta": obs_meta}),
    )


def _stable_pack_id(seed: dict[str, Any]) -> str:
    digest = hashlib.sha1(
        json.dumps(seed, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()[:16]
    source = _clean_token(seed.get("source_kind") or "source")
    return f"source-pack:{source}:{digest}"


def _unique_texts(values: Any) -> list[str]:
    if isinstance(values, str):
        iterable: list[Any] = [values]
    elif isinstance(values, (list, tuple, set)):
        iterable = list(values)
    else:
        iterable = []
    seen: set[str] = set()
    out: list[str] = []
    for value in iterable:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _clean_token(value: Any) -> str:
    text = str(value or "").strip().lower().replace(" ", "_")
    return "".join(ch for ch in text if ch.isalnum() or ch in "._:-")[:96]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, SourcePackItem):
        return {
            "item_id": value.item_id,
            "label": value.label,
            "source_ref": value.source_ref,
            "source_kind": value.source_kind,
            "provider_ref": value.provider_ref,
            "l2b_kind": value.l2b_kind,
            "l2b_uuid": value.l2b_uuid,
            "ref_ids": list(value.ref_ids),
            "raw": _jsonable(value.raw),
            "meta": _jsonable(value.meta),
        }
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)
    return value


__all__ = [
    "SOURCE_PACK_SCHEMA_VERSION",
    "SourcePackItem",
    "build_source_pack",
    "source_pack_summary",
    "work_subgraph_uuid",
]
