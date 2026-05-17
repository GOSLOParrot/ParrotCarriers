"""Durable identity/ref index candidate for DSG memory.

This module is deliberately small and file-backed. It is a CORE-015 prototype,
not a promoted shared interface: callers should treat the JSON shape as a Web
Console review surface until App/Web agree on the final contract.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
RESOLUTION_STATES = {"weak", "confirmed", "conflicted", "tombstoned"}
MERGE_POLICY = (
    "single_existing_signal_merges; explicit_or_multi_canonical_overlap_marks_conflict; "
    "external UUIDs and refs are preserved without auto-rebinding existing records"
)


def default_index_path() -> Path:
    """Return the local durable index path.

    Tests and deployments can override this with
    ``PARROT_MEMORY_IDENTITY_REF_INDEX_PATH``. The default stays in the user's
    home directory so Web smoke runs do not silently dirty the repository.
    """

    configured = os.getenv("PARROT_MEMORY_IDENTITY_REF_INDEX_PATH", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".parrot" / "memory_identity_ref_index.json"


@dataclass
class IdentityRecord:
    canonical_uuid: str
    l2b_uuid: str = ""
    graphiti_entity_uuids: list[str] = field(default_factory=list)
    graphiti_edge_uuids: list[str] = field(default_factory=list)
    graphiti_episode_uuids: list[str] = field(default_factory=list)
    obsidian_uuids: list[str] = field(default_factory=list)
    ref_ids: list[str] = field(default_factory=list)
    provider_keys: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    confidence: float = 0.5
    resolution_state: str = "weak"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_verified_at: float = 0.0
    graphiti_raw: dict[str, Any] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IdentityRecord":
        record = cls(canonical_uuid=str(data.get("canonical_uuid") or ""))
        for key in (
            "l2b_uuid",
            "resolution_state",
        ):
            setattr(record, key, str(data.get(key) or getattr(record, key)))
        for key in (
            "graphiti_entity_uuids",
            "graphiti_edge_uuids",
            "graphiti_episode_uuids",
            "obsidian_uuids",
            "ref_ids",
            "provider_keys",
            "aliases",
        ):
            setattr(record, key, _unique_strings(data.get(key)))
        record.confidence = _float(data.get("confidence"), record.confidence)
        record.created_at = _float(data.get("created_at"), record.created_at)
        record.updated_at = _float(data.get("updated_at"), record.updated_at)
        record.last_verified_at = _float(data.get("last_verified_at"), 0.0)
        record.graphiti_raw = _dict(data.get("graphiti_raw"))
        record.conflicts = _list_of_dicts(data.get("conflicts"))
        record.meta = _dict(data.get("meta"))
        return record

    def to_dict(self) -> dict[str, Any]:
        return {
            "canonical_uuid": self.canonical_uuid,
            "l2b_uuid": self.l2b_uuid,
            "graphiti_entity_uuids": list(self.graphiti_entity_uuids),
            "graphiti_edge_uuids": list(self.graphiti_edge_uuids),
            "graphiti_episode_uuids": list(self.graphiti_episode_uuids),
            "obsidian_uuids": list(self.obsidian_uuids),
            "ref_ids": list(self.ref_ids),
            "provider_keys": list(self.provider_keys),
            "aliases": list(self.aliases),
            "confidence": self.confidence,
            "resolution_state": self.resolution_state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_verified_at": self.last_verified_at,
            "graphiti_raw": self.graphiti_raw,
            "conflicts": list(self.conflicts),
            "meta": self.meta,
        }


@dataclass
class RefRecord:
    ref_id: str
    kind: str = "external"
    canonical_uuid: str = ""
    canonical_uri: str = ""
    locators: list[str] = field(default_factory=list)
    content_hash: str = ""
    size: int = 0
    mime_type: str = ""
    version: str = ""
    valid_from: float = 0.0
    valid_to: float = 0.0
    health: str = "unknown"
    managed_by: str = "unknown"
    git_commit: str = ""
    last_seen: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RefRecord":
        record = cls(ref_id=str(data.get("ref_id") or ""))
        for key in (
            "kind",
            "canonical_uuid",
            "canonical_uri",
            "content_hash",
            "mime_type",
            "version",
            "health",
            "managed_by",
            "git_commit",
        ):
            setattr(record, key, str(data.get(key) or getattr(record, key)))
        record.locators = _unique_strings(data.get("locators"))
        record.size = int(_float(data.get("size"), 0.0))
        record.valid_from = _float(data.get("valid_from"), 0.0)
        record.valid_to = _float(data.get("valid_to"), 0.0)
        record.last_seen = _float(data.get("last_seen"), record.last_seen)
        record.created_at = _float(data.get("created_at"), record.created_at)
        record.updated_at = _float(data.get("updated_at"), record.updated_at)
        record.meta = _dict(data.get("meta"))
        return record

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref_id": self.ref_id,
            "kind": self.kind,
            "canonical_uuid": self.canonical_uuid,
            "canonical_uri": self.canonical_uri or f"parrot://refs/{self.ref_id}",
            "locators": list(self.locators),
            "content_hash": self.content_hash,
            "size": self.size,
            "mime_type": self.mime_type,
            "version": self.version,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "health": self.health,
            "managed_by": self.managed_by,
            "git_commit": self.git_commit,
            "last_seen": self.last_seen,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "meta": self.meta,
        }


class MemoryIdentityRefIndex:
    """File-backed CORE-015 candidate store."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_index_path()
        self.identities: dict[str, IdentityRecord] = {}
        self.refs: dict[str, RefRecord] = {}
        self.loaded_at = 0.0
        self.updated_at = 0.0
        self.last_upsert_report: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        self.loaded_at = time.time()
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.updated_at = _float(data.get("updated_at"), 0.0)
        self.identities = _load_identity_records(data.get("identities"))
        self.refs = _load_ref_records(data.get("refs"))

    def save(self) -> None:
        self.updated_at = time.time()
        data = {
            "schema_version": SCHEMA_VERSION,
            "updated_at": self.updated_at,
            "identities": {
                key: value.to_dict()
                for key, value in sorted(self.identities.items())
            },
            "refs": {
                key: value.to_dict()
                for key, value in sorted(self.refs.items())
            },
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def snapshot(self, *, limit: int | None = None) -> dict[str, Any]:
        identities = sorted(
            (item.to_dict() for item in self.identities.values()),
            key=lambda item: str(item.get("updated_at", 0)),
            reverse=True,
        )
        refs = sorted(
            (item.to_dict() for item in self.refs.values()),
            key=lambda item: str(item.get("updated_at", 0)),
            reverse=True,
        )
        if limit is not None:
            identities = identities[:limit]
            refs = refs[:limit]
        return {
            "schema_version": SCHEMA_VERSION,
            "path": str(self.path),
            "updated_at": self.updated_at,
            "identity_count": len(self.identities),
            "ref_count": len(self.refs),
            "identities": identities,
            "refs": refs,
        }

    def upsert(self, payload: dict[str, Any]) -> tuple[IdentityRecord, RefRecord | None]:
        now = time.time()
        resolution = self._resolve_upsert_target(payload, now=now)
        canonical_uuid = resolution["canonical_uuid"]
        conflicts = list(resolution["conflicts"])
        identity = self.identities.get(canonical_uuid)
        if identity is None:
            identity = IdentityRecord(canonical_uuid=canonical_uuid, created_at=now)
            self.identities[canonical_uuid] = identity
        conflicts.extend(
            _target_scalar_conflicts(
                identity,
                resolution["incoming_keys"],
                now=now,
            )
        )
        identity.updated_at = now
        _merge_identity_payload(identity, payload, allow_l2b_update=not _has_l2b_mismatch(conflicts))

        ref = _ref_record_from_payload(payload, canonical_uuid=canonical_uuid, now=now)
        persisted_ref: RefRecord | None = None
        ref_rebound = False
        if ref is not None:
            existing = self.refs.get(ref.ref_id)
            if existing is not None:
                ref_rebound = bool(
                    existing.canonical_uuid
                    and existing.canonical_uuid != canonical_uuid
                )
                if ref_rebound:
                    persisted_ref = existing
                else:
                    ref.created_at = existing.created_at
                    ref.locators = _merge_unique(existing.locators, ref.locators)
                    ref.meta = {**existing.meta, **ref.meta}
                    self.refs[ref.ref_id] = ref
                    persisted_ref = ref
            else:
                self.refs[ref.ref_id] = ref
                persisted_ref = ref
            if ref.ref_id not in identity.ref_ids:
                identity.ref_ids.append(ref.ref_id)
            if persisted_ref is not None and not persisted_ref.canonical_uuid:
                persisted_ref.canonical_uuid = canonical_uuid

        _apply_conflicts(self.identities, canonical_uuid, conflicts, now=now)
        _finalize_resolution_state(identity, payload, has_conflicts=bool(conflicts))
        self.last_upsert_report = {
            "merge_policy": MERGE_POLICY,
            "target_canonical_uuid": canonical_uuid,
            "target_reason": resolution["target_reason"],
            "matched_canonical_uuids": resolution["matched_canonical_uuids"],
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "ref_rebind_skipped": ref_rebound,
            "resolution_state": identity.resolution_state,
        }
        return identity, persisted_ref

    def _resolve_upsert_target(self, payload: dict[str, Any], *, now: float) -> dict[str, Any]:
        explicit_canonical_uuid = str(payload.get("canonical_uuid") or "").strip()
        incoming_keys = _incoming_identity_keys(payload)
        matches = self._find_signal_matches(incoming_keys)
        matched_canonical_uuids = sorted(matches)
        if explicit_canonical_uuid:
            canonical_uuid = explicit_canonical_uuid
            target_reason = "explicit_canonical_uuid"
        elif len(matched_canonical_uuids) == 1:
            canonical_uuid = matched_canonical_uuids[0]
            target_reason = "single_existing_signal"
        elif len(matched_canonical_uuids) > 1:
            canonical_uuid = matched_canonical_uuids[0]
            target_reason = "multiple_existing_signals_first_sorted"
        elif incoming_keys["l2b_uuid"]:
            canonical_uuid = incoming_keys["l2b_uuid"][0]
            target_reason = "l2b_uuid"
        else:
            canonical_uuid = _new_canonical_uuid()
            target_reason = "generated"

        conflicts: list[dict[str, Any]] = []
        for matched_uuid, signals in sorted(matches.items()):
            if matched_uuid == canonical_uuid:
                continue
            for signal in signals:
                conflicts.append(
                    _conflict_record(
                        kind=str(signal["kind"]),
                        value=str(signal["value"]),
                        target_canonical_uuid=canonical_uuid,
                        existing_canonical_uuid=matched_uuid,
                        reason="incoming_signal_already_bound",
                        now=now,
                        source=str(signal.get("source") or "identity_index"),
                    )
                )
        return {
            "canonical_uuid": canonical_uuid,
            "target_reason": target_reason,
            "incoming_keys": incoming_keys,
            "matched_canonical_uuids": matched_canonical_uuids,
            "conflicts": conflicts,
        }

    def _find_signal_matches(
        self,
        incoming_keys: dict[str, list[str]],
    ) -> dict[str, list[dict[str, str]]]:
        matches: dict[str, list[dict[str, str]]] = {}
        for canonical_uuid, record in self.identities.items():
            for signal in _identity_signal_overlaps(record, incoming_keys):
                matches.setdefault(canonical_uuid, []).append(signal)
        for ref_id in incoming_keys["ref_id"]:
            ref = self.refs.get(ref_id)
            if ref is not None and ref.canonical_uuid:
                matches.setdefault(ref.canonical_uuid, []).append(
                    {
                        "kind": "ref_id",
                        "value": ref_id,
                        "source": "ref_index",
                    }
                )
        return matches

    def verify(
        self,
        *,
        graphiti_uuid_statuses: dict[str, bool] | None = None,
        obsidian_uuid_statuses: dict[str, bool] | None = None,
        update: bool = False,
    ) -> dict[str, Any]:
        """Verify current ref and identity bindings.

        URL, ECS, and remote locators are reported as ``unknown`` until an
        explicit checker is added by a later nanobot/MCP-backed slice. This
        keeps the first route deterministic and safe for unit tests.
        """

        now = time.time()
        ref_checks = [
            _verify_ref_record(record)
            for record in sorted(self.refs.values(), key=lambda item: item.ref_id)
        ]
        identity_checks = [
            _verify_identity_record(
                record,
                graphiti_uuid_statuses=graphiti_uuid_statuses or {},
                obsidian_uuid_statuses=obsidian_uuid_statuses or {},
            )
            for record in sorted(self.identities.values(), key=lambda item: item.canonical_uuid)
        ]
        if update:
            for check in ref_checks:
                ref = self.refs.get(str(check.get("ref_id") or ""))
                if ref is not None:
                    ref.health = str(check.get("health") or "unknown")
                    ref.last_seen = now
                    ref.updated_at = now
            for check in identity_checks:
                identity = self.identities.get(str(check.get("canonical_uuid") or ""))
                if identity is not None:
                    identity.last_verified_at = now
                    identity.updated_at = now
        counts: dict[str, int] = {}
        for check in [*ref_checks, *identity_checks]:
            health = str(check.get("health") or "unknown")
            counts[health] = counts.get(health, 0) + 1
        return {
            "ref_checks": ref_checks,
            "identity_checks": identity_checks,
            "health_counts": counts,
            "checked_at": now,
            "updated": update,
        }

    def resolve_graphiti_subgraph(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Resolve Graphiti fact endpoints through the IdentityRefIndex.

        This is intentionally read-only. It answers whether a Graphiti fact
        edge can be materialized later by a separate L2-B edge apply route.
        """

        partition = str(payload.get("partition") or "goslo").strip() or "goslo"
        edge_rows = _extract_graphiti_resolve_edges(payload)
        resolved_edges = [
            self._resolve_graphiti_edge(row, partition=partition, index=index)
            for index, row in enumerate(edge_rows)
        ]
        ready_count = sum(
            1 for item in resolved_edges if item.get("can_materialize_l2b_edge") is True
        )
        missing_endpoints = 0
        conflicted_endpoints = 0
        canonical_only_endpoints = 0
        for item in resolved_edges:
            for endpoint_key in ("source", "target"):
                status = str((item.get(endpoint_key) or {}).get("status") or "")
                if status == "missing":
                    missing_endpoints += 1
                elif status == "conflicted":
                    conflicted_endpoints += 1
                elif status == "canonical_only":
                    canonical_only_endpoints += 1
        return {
            "partition": partition,
            "edge_count": len(resolved_edges),
            "ready_count": ready_count,
            "blocked_count": len(resolved_edges) - ready_count,
            "missing_endpoint_count": missing_endpoints,
            "conflicted_endpoint_count": conflicted_endpoints,
            "canonical_only_endpoint_count": canonical_only_endpoints,
            "edges": resolved_edges,
            "edge_apply_policy": (
                "Read-only resolver. A later L2-B edge apply route may write only "
                "when source and target are both resolved_l2b."
            ),
        }

    def _resolve_graphiti_edge(
        self,
        row: dict[str, Any],
        *,
        partition: str,
        index: int,
    ) -> dict[str, Any]:
        source_uuid = _clean_graphiti_uuid(
            row.get("source_graphiti_uuid")
            or row.get("source_node_uuid")
            or row.get("source")
        )
        target_uuid = _clean_graphiti_uuid(
            row.get("target_graphiti_uuid")
            or row.get("target_node_uuid")
            or row.get("target")
        )
        fact_uuid = _clean_graphiti_uuid(
            row.get("hit_graphiti_uuid")
            or row.get("graphiti_edge_uuid")
            or row.get("graphiti_uuid")
            or row.get("uuid")
        )
        source = self.resolve_graphiti_uuid(
            source_uuid,
            signal_kind="entity",
            partition=partition,
            parent_edge=row,
        )
        target = self.resolve_graphiti_uuid(
            target_uuid,
            signal_kind="entity",
            partition=partition,
            parent_edge=row,
        )
        fact = self.resolve_graphiti_uuid(
            fact_uuid,
            signal_kind="edge",
            partition=partition,
            parent_edge=row,
        )
        blocked_reasons = _graphiti_resolution_blocked_reasons(source, target)
        return {
            "index": index,
            "label": str(row.get("label") or ""),
            "source_graphiti_uuid": source_uuid,
            "target_graphiti_uuid": target_uuid,
            "hit_graphiti_uuid": fact_uuid,
            "source": source,
            "target": target,
            "fact": fact,
            "can_materialize_l2b_edge": not blocked_reasons,
            "blocked_reasons": blocked_reasons,
            "direct_l2b_write": False,
            "direct_graphiti_write": False,
            "write_policy": "requires_resolved_l2b_source_and_target",
            "l2b_edge_draft": (
                _resolved_l2b_edge_draft(row, source, target, fact, partition=partition)
                if not blocked_reasons
                else {}
            ),
        }

    def resolve_graphiti_uuid(
        self,
        value: str,
        *,
        signal_kind: str,
        partition: str,
        parent_edge: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        graphiti_uuid = _clean_graphiti_uuid(value)
        kind = _graphiti_signal_kind(signal_kind)
        if not graphiti_uuid:
            return {
                "kind": kind,
                "value": "",
                "status": "blank",
                "match_count": 0,
                "matches": [],
                "pointer_candidate": {},
            }
        matches = [
            _identity_resolution_summary(identity)
            for identity in sorted(self.identities.values(), key=lambda item: item.canonical_uuid)
            if _identity_has_graphiti_uuid(identity, graphiti_uuid, signal_kind=kind)
        ]
        pointer_candidate = _graphiti_pointer_candidate(
            kind=kind,
            value=graphiti_uuid,
            partition=partition,
            parent_edge=parent_edge or {},
        )
        if not matches:
            return {
                "kind": kind,
                "value": graphiti_uuid,
                "status": "missing",
                "match_count": 0,
                "matches": [],
                "pointer_candidate": pointer_candidate,
            }
        if len(matches) > 1:
            return {
                "kind": kind,
                "value": graphiti_uuid,
                "status": "conflicted",
                "match_count": len(matches),
                "matches": matches,
                "pointer_candidate": pointer_candidate,
            }
        match = matches[0]
        resolution_state = str(match.get("resolution_state") or "weak")
        if resolution_state == "tombstoned":
            status = "tombstoned"
        elif resolution_state == "conflicted" or match.get("conflict_count", 0):
            status = "conflicted"
        elif not match.get("l2b_uuid"):
            status = "canonical_only"
        else:
            status = "resolved_l2b"
        return {
            "kind": kind,
            "value": graphiti_uuid,
            "status": status,
            "canonical_uuid": match.get("canonical_uuid", ""),
            "l2b_uuid": match.get("l2b_uuid", ""),
            "resolution_state": resolution_state,
            "match_count": 1,
            "matches": matches,
            "pointer_candidate": {} if status == "resolved_l2b" else pointer_candidate,
        }

    def upsert_graphiti_ref_writeback(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Bind one Graphiti record pointer to mutable external refs.

        This is the M14 reviewed write-back helper. It mutates only this
        in-memory index instance; callers decide whether to save it. Graphiti
        audit is returned as an Episode draft rather than written here.
        """

        plan = _graphiti_ref_writeback_plan(payload, index=self)
        if not plan["ok"]:
            self.last_upsert_report = {
                "merge_policy": MERGE_POLICY,
                "target_reason": "invalid_graphiti_ref_writeback",
                "conflict_count": 0,
                "conflicts": [],
                "error": plan["error"],
            }
            return plan

        identity, _ = self.upsert(plan["identity_payload"])
        merge_reports = [dict(self.last_upsert_report)]
        external_ref_records: list[dict[str, Any]] = []
        for ref_payload in plan["external_ref_payloads"]:
            ref_payload["canonical_uuid"] = identity.canonical_uuid
            ref_payload.setdefault(plan["graphiti_signal_key"], plan["graphiti_uuid"])
            ref_payload.setdefault("graphiti_raw", plan["identity_payload"].get("graphiti_raw", {}))
            identity, ref = self.upsert(ref_payload)
            merge_reports.append(dict(self.last_upsert_report))
            if ref is not None:
                external_ref_records.append(ref.to_dict())

        plan.update(
            {
                "identity_binding": identity.to_dict(),
                "external_ref_records": external_ref_records,
                "merge_reports": merge_reports,
                "audit_episode_draft": _graphiti_ref_audit_episode_draft(
                    identity=identity,
                    graphiti_record_ref=plan["graphiti_record_ref"],
                    external_ref_records=external_ref_records,
                    ref_move_events=plan["ref_move_events"],
                    requested_by=str(payload.get("requested_by") or "web_console"),
                ),
                "mutated_index_instance": True,
            }
        )
        self.last_upsert_report = {
            "merge_policy": MERGE_POLICY,
            "target_canonical_uuid": identity.canonical_uuid,
            "target_reason": "graphiti_ref_writeback",
            "conflict_count": sum(
                int(report.get("conflict_count") or 0) for report in merge_reports
            ),
            "conflicts": [
                conflict
                for report in merge_reports
                for conflict in report.get("conflicts", [])
                if isinstance(conflict, dict)
            ],
            "resolution_state": identity.resolution_state,
        }
        return plan


def _new_canonical_uuid() -> str:
    return f"canon_{uuid.uuid4().hex[:12]}"


def _graphiti_ref_writeback_plan(
    payload: dict[str, Any],
    *,
    index: MemoryIdentityRefIndex,
) -> dict[str, Any]:
    graphiti_record_ref = _graphiti_record_ref_from_payload(payload)
    graphiti_uuid = str(graphiti_record_ref.get("graphiti_uuid") or "")
    graphiti_kind = str(graphiti_record_ref.get("graphiti_kind") or "entity")
    if not graphiti_uuid:
        return {
            "ok": False,
            "error": "missing_graphiti_uuid",
            "required_any_of": [
                "graphiti_uuid",
                "graphiti_entity_uuid",
                "graphiti_edge_uuid",
                "graphiti_episode_uuid",
                "graphiti_record.uuid",
            ],
            "mutated_index_instance": False,
        }
    signal_key = _graphiti_writeback_signal_key(graphiti_kind)
    raw_envelope = _dict(payload.get("graphiti_raw") or payload.get("raw_envelope"))
    identity_payload = {
        "canonical_uuid": str(payload.get("canonical_uuid") or "").strip(),
        "l2b_uuid": str(payload.get("l2b_uuid") or "").strip(),
        signal_key: graphiti_uuid,
        "aliases": _multi_values(payload, "alias", "aliases", "label", "name"),
        "confidence": _float(payload.get("confidence"), 0.65),
        "resolution_state": str(payload.get("resolution_state") or "weak"),
        "graphiti_raw": {
            "schema_version": 1,
            "graphiti_record_ref": graphiti_record_ref,
            "raw_envelope": raw_envelope,
            "preservation_policy": "preserve_raw_graphiti_envelope",
        },
        "meta": {
            **_dict(payload.get("meta")),
            "m14_writeback": True,
            "identity_owner": "MemoryIdentityRefIndex",
            "graphiti_partition": graphiti_record_ref["partition"],
            "graphiti_kind": graphiti_kind,
        },
    }
    identity_payload = {
        key: value
        for key, value in identity_payload.items()
        if value not in ("", [], {})
    }
    ref_move_events: list[dict[str, Any]] = []
    external_ref_payloads = [
        _external_ref_writeback_payload(
            ref_payload,
            graphiti_record_ref=graphiti_record_ref,
            signal_key=signal_key,
            graphiti_uuid=graphiti_uuid,
            index=index,
            ref_move_events=ref_move_events,
        )
        for ref_payload in _external_ref_inputs(payload)
    ]
    return {
        "ok": True,
        "error": "",
        "schema_version": SCHEMA_VERSION,
        "partition": graphiti_record_ref["partition"],
        "graphiti_uuid": graphiti_uuid,
        "graphiti_kind": graphiti_kind,
        "graphiti_signal_key": signal_key,
        "graphiti_record_ref": graphiti_record_ref,
        "identity_payload": identity_payload,
        "external_ref_payloads": external_ref_payloads,
        "ref_move_events": ref_move_events,
        "writeback_model": {
            "identity_binding_owner": "MemoryIdentityRefIndex",
            "graphiti_record_ref_owner": "Graphiti",
            "external_ref_owner": "RefIndex",
            "audit_owner": "Graphiti Episode draft",
            "l2b_owner": "runtime projection only",
        },
        "write_policy": (
            "Preview/apply split. Apply may persist IdentityRefIndex JSON only; "
            "Graphiti audit Episode and external file moves require separate operator routes."
        ),
        "mutated_index_instance": False,
    }


def _graphiti_record_ref_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    record = _dict(payload.get("graphiti_record"))
    raw_envelope = _dict(payload.get("graphiti_raw") or payload.get("raw_envelope"))
    graphiti_kind = _normalize_graphiti_record_kind(
        payload.get("graphiti_kind")
        or payload.get("graphiti_record_kind")
        or record.get("kind")
        or record.get("type")
        or _graphiti_kind_from_payload_keys(payload)
    )
    graphiti_uuid = _clean_graphiti_uuid(
        payload.get("graphiti_uuid")
        or payload.get("uuid")
        or payload.get("graphiti_entity_uuid")
        or payload.get("graphiti_edge_uuid")
        or payload.get("graphiti_episode_uuid")
        or record.get("uuid")
        or raw_envelope.get("uuid")
    )
    labels = _unique_strings(
        payload.get("raw_type_labels")
        or payload.get("labels")
        or record.get("labels")
        or raw_envelope.get("labels")
    )
    name = str(
        payload.get("graphiti_name")
        or payload.get("name")
        or record.get("name")
        or raw_envelope.get("name")
        or raw_envelope.get("fact")
        or ""
    ).strip()
    partition = str(
        payload.get("partition")
        or payload.get("group_id")
        or record.get("partition")
        or record.get("group_id")
        or raw_envelope.get("group_id")
        or "goslo"
    ).strip() or "goslo"
    ref_scope = "fact" if graphiti_kind == "edge" else graphiti_kind
    return {
        "partition": partition,
        "graphiti_uuid": graphiti_uuid,
        "graphiti_kind": graphiti_kind,
        "ref_id": f"graphiti:{partition}:{ref_scope}:{graphiti_uuid}" if graphiti_uuid else "",
        "name": name,
        "raw_type_labels": labels,
        "lookup_status": str(payload.get("lookup_status") or "not_checked_by_writeback_route"),
        "immutable_pointer": True,
        "raw_preserved": bool(raw_envelope),
    }


def _graphiti_kind_from_payload_keys(payload: dict[str, Any]) -> str:
    if payload.get("graphiti_edge_uuid"):
        return "edge"
    if payload.get("graphiti_episode_uuid"):
        return "episode"
    return "entity"


def _normalize_graphiti_record_kind(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"edge", "fact", "entityedge", "entity_edge", "graphiti_edge"}:
        return "edge"
    if text in {"episode", "episodic", "episodicnode", "episodic_node"}:
        return "episode"
    return "entity"


def _graphiti_writeback_signal_key(graphiti_kind: str) -> str:
    if graphiti_kind == "edge":
        return "graphiti_edge_uuid"
    if graphiti_kind == "episode":
        return "graphiti_episode_uuid"
    return "graphiti_entity_uuid"


def _external_ref_inputs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_refs = payload.get("external_refs")
    if raw_refs is None:
        raw_refs = payload.get("refs")
    if isinstance(raw_refs, list):
        refs = [
            dict(item)
            for item in raw_refs
            if isinstance(item, dict) and _has_external_ref_location_signal(item)
        ]
    else:
        refs = []
    if refs:
        return refs[:20]
    if _has_external_ref_location_signal(payload):
        return [payload]
    return []


def _has_external_ref_location_signal(payload: dict[str, Any]) -> bool:
    if _writeback_locators(payload):
        return True
    return bool(
        str(payload.get("canonical_uri") or "").strip()
        or str(payload.get("content_hash") or "").strip()
    )


def _external_ref_writeback_payload(
    payload: dict[str, Any],
    *,
    graphiti_record_ref: dict[str, Any],
    signal_key: str,
    graphiti_uuid: str,
    index: MemoryIdentityRefIndex,
    ref_move_events: list[dict[str, Any]],
) -> dict[str, Any]:
    ref_id = str(payload.get("ref_id") or "").strip()
    locators = _writeback_locators(payload)
    existing = index.refs.get(ref_id) if ref_id else None
    event = _ref_move_event_draft(
        ref_id=ref_id,
        existing=existing,
        incoming_locators=locators,
        graphiti_record_ref=graphiti_record_ref,
        requested_by=str(payload.get("requested_by") or "web_console"),
    )
    if event:
        ref_move_events.append(event)
    ref_meta = {
        **_dict(payload.get("ref_meta")),
        "m14_writeback": True,
        "graphiti_record_ref": graphiti_record_ref,
        "locator_kind": str(payload.get("locator_kind") or payload.get("ref_kind") or ""),
    }
    if event:
        ref_meta.setdefault("ref_move_events", []).append(event)
    return {
        signal_key: graphiti_uuid,
        "ref_id": ref_id,
        "ref_kind": str(
            payload.get("ref_kind")
            or payload.get("kind")
            or payload.get("locator_kind")
            or "external_ref"
        ),
        "locators": locators,
        "canonical_uri": str(payload.get("canonical_uri") or ""),
        "content_hash": str(payload.get("content_hash") or ""),
        "size": payload.get("size", 0),
        "mime_type": str(payload.get("mime_type") or ""),
        "version": str(payload.get("version") or ""),
        "health": str(payload.get("health") or "unknown"),
        "managed_by": str(payload.get("managed_by") or "unknown"),
        "git_commit": str(payload.get("git_commit") or ""),
        "ref_meta": ref_meta,
    }


def _writeback_locators(payload: dict[str, Any]) -> list[str]:
    return _multi_values(
        payload,
        "locator",
        "locators",
        "locator_value",
        "path",
        "url",
        "ecs_path",
        "obsidian_path",
    )


def _ref_move_event_draft(
    *,
    ref_id: str,
    existing: RefRecord | None,
    incoming_locators: list[str],
    graphiti_record_ref: dict[str, Any],
    requested_by: str,
) -> dict[str, Any]:
    if existing is None:
        if not incoming_locators:
            return {}
        return {
            "event_type": "ref_created",
            "ref_id": ref_id,
            "old_locators": [],
            "new_locators": incoming_locators,
            "graphiti_record_ref": graphiti_record_ref,
            "requested_by": requested_by,
            "created_at": time.time(),
            "write_policy": "record_in_refindex_then_emit_graphiti_audit_episode",
        }
    old_locators = list(existing.locators)
    added = [locator for locator in incoming_locators if locator not in old_locators]
    if not added:
        return {}
    return {
        "event_type": "locator_added",
        "ref_id": existing.ref_id,
        "old_locators": old_locators,
        "new_locators": _merge_unique(old_locators, incoming_locators),
        "added_locators": added,
        "graphiti_record_ref": graphiti_record_ref,
        "requested_by": requested_by,
        "created_at": time.time(),
        "write_policy": "record_in_refindex_then_emit_graphiti_audit_episode",
    }


def _graphiti_ref_audit_episode_draft(
    *,
    identity: IdentityRecord,
    graphiti_record_ref: dict[str, Any],
    external_ref_records: list[dict[str, Any]],
    ref_move_events: list[dict[str, Any]],
    requested_by: str,
) -> dict[str, Any]:
    partition = str(graphiti_record_ref.get("partition") or "goslo")
    graphiti_uuid = str(graphiti_record_ref.get("graphiti_uuid") or "")
    graphiti_kind = str(graphiti_record_ref.get("graphiti_kind") or "entity")
    ref_ids = [str(item.get("ref_id") or "") for item in external_ref_records]
    move_count = len(ref_move_events)
    body = {
        "type": "parrot_ref_writeback_audit",
        "requested_by": requested_by,
        "canonical_uuid": identity.canonical_uuid,
        "l2b_uuid": identity.l2b_uuid,
        "graphiti": graphiti_record_ref,
        "ref_ids": [item for item in ref_ids if item],
        "ref_move_events": ref_move_events,
        "policy": (
            "IdentityRefIndex owns current locators. Historical Graphiti "
            "Episodes remain immutable provenance."
        ),
    }
    return {
        "name": f"ref_writeback_{graphiti_kind}_{graphiti_uuid[:12] or 'unknown'}",
        "partition": partition,
        "source_description": "parrot-web-console-ref-writeback-audit",
        "body": json.dumps(body, ensure_ascii=False, sort_keys=True),
        "body_json": body,
        "write_route": "/api/graphiti/episode",
        "write_status": "draft_only",
        "move_event_count": move_count,
    }


def _extract_graphiti_resolve_edges(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("edge_drafts")
    if raw is None:
        raw = payload.get("edges")
    if raw is None:
        raw = payload.get("graphiti_edges")
    if isinstance(raw, list):
        rows = [dict(item) for item in raw[:50] if isinstance(item, dict)]
    else:
        rows = []
    if rows:
        return rows
    source_uuid = _clean_graphiti_uuid(
        payload.get("source_graphiti_uuid")
        or payload.get("source_node_uuid")
        or payload.get("source")
    )
    target_uuid = _clean_graphiti_uuid(
        payload.get("target_graphiti_uuid")
        or payload.get("target_node_uuid")
        or payload.get("target")
    )
    fact_uuid = _clean_graphiti_uuid(
        payload.get("hit_graphiti_uuid")
        or payload.get("graphiti_edge_uuid")
        or payload.get("graphiti_uuid")
        or payload.get("uuid")
    )
    if not source_uuid and not target_uuid and not fact_uuid:
        return []
    return [
        {
            "source_graphiti_uuid": source_uuid,
            "target_graphiti_uuid": target_uuid,
            "hit_graphiti_uuid": fact_uuid,
            "label": str(payload.get("label") or ""),
            "meta": _dict(payload.get("meta")),
        }
    ]


def _clean_graphiti_uuid(value: Any) -> str:
    text = str(value or "").strip()
    if text.startswith("graphiti:"):
        text = text.removeprefix("graphiti:")
    return text.strip()


def _graphiti_signal_kind(signal_kind: str) -> str:
    value = str(signal_kind or "").strip().lower()
    if value in {"edge", "fact", "graphiti_edge_uuid"}:
        return "graphiti_edge_uuid"
    if value in {"episode", "graphiti_episode_uuid"}:
        return "graphiti_episode_uuid"
    return "graphiti_entity_uuid"


def _identity_has_graphiti_uuid(
    identity: IdentityRecord,
    graphiti_uuid: str,
    *,
    signal_kind: str,
) -> bool:
    if signal_kind == "graphiti_edge_uuid":
        return graphiti_uuid in identity.graphiti_edge_uuids
    if signal_kind == "graphiti_episode_uuid":
        return graphiti_uuid in identity.graphiti_episode_uuids
    return graphiti_uuid in identity.graphiti_entity_uuids


def _identity_resolution_summary(identity: IdentityRecord) -> dict[str, Any]:
    return {
        "canonical_uuid": identity.canonical_uuid,
        "l2b_uuid": identity.l2b_uuid,
        "resolution_state": identity.resolution_state,
        "aliases": list(identity.aliases),
        "ref_ids": list(identity.ref_ids),
        "confidence": identity.confidence,
        "conflict_count": len(identity.conflicts),
    }


def _graphiti_resolution_blocked_reasons(
    source: dict[str, Any],
    target: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    for endpoint_name, resolution in (("source", source), ("target", target)):
        status = str(resolution.get("status") or "")
        if status == "resolved_l2b":
            continue
        if status == "missing":
            reasons.append(f"{endpoint_name}_missing")
        elif status == "canonical_only":
            reasons.append(f"{endpoint_name}_missing_l2b_uuid")
        elif status == "conflicted":
            reasons.append(f"{endpoint_name}_conflicted")
        elif status == "tombstoned":
            reasons.append(f"{endpoint_name}_tombstoned")
        elif status == "blank":
            reasons.append(f"{endpoint_name}_blank")
        else:
            reasons.append(f"{endpoint_name}_unresolved")
    return reasons


def _resolved_l2b_edge_draft(
    row: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    fact: dict[str, Any],
    *,
    partition: str,
) -> dict[str, Any]:
    return {
        "source_uuid": str(source.get("l2b_uuid") or ""),
        "target_uuid": str(target.get("l2b_uuid") or ""),
        "kind": str(row.get("kind") or "graphiti_fact"),
        "strength": _float(row.get("strength"), _float(row.get("score"), 0.5)),
        "label": str(row.get("label") or ""),
        "graphiti_uuid": str(fact.get("value") or row.get("hit_graphiti_uuid") or ""),
        "source_graphiti_uuid": str(source.get("value") or ""),
        "target_graphiti_uuid": str(target.get("value") or ""),
        "meta": {
            **_dict(row.get("meta")),
            "graphiti_partition": partition,
            "source_canonical_uuid": str(source.get("canonical_uuid") or ""),
            "target_canonical_uuid": str(target.get("canonical_uuid") or ""),
            "fact_canonical_uuid": str(fact.get("canonical_uuid") or ""),
            "resolver": "MemoryIdentityRefIndex.resolve_graphiti_subgraph",
        },
    }


def _graphiti_pointer_candidate(
    *,
    kind: str,
    value: str,
    partition: str,
    parent_edge: dict[str, Any],
) -> dict[str, Any]:
    if not value:
        return {}
    if kind == "graphiti_edge_uuid":
        key = "graphiti_edge_uuid"
        ref_kind = "graphiti_fact"
        ref_scope = "fact"
    elif kind == "graphiti_episode_uuid":
        key = "graphiti_episode_uuid"
        ref_kind = "graphiti_episode"
        ref_scope = "episode"
    else:
        key = "graphiti_entity_uuid"
        ref_kind = "graphiti_entity"
        ref_scope = "entity"
    return {
        key: value,
        "ref_id": f"graphiti:{partition}:{ref_scope}:{value}",
        "ref_kind": ref_kind,
        "resolution_state": "weak",
        "graphiti_raw": {
            "schema_version": 1,
            "kind": f"{ref_kind}_pointer",
            "partition": partition,
            "uuid": value,
            "parent_edge": parent_edge,
        },
        "apply_route": "/api/memory/identity-ref-index/apply",
        "write_policy": "operator_review_required",
    }


def _merge_identity_payload(
    identity: IdentityRecord,
    payload: dict[str, Any],
    *,
    allow_l2b_update: bool,
) -> None:
    incoming_l2b_uuid = str(payload.get("l2b_uuid") or "").strip()
    if incoming_l2b_uuid and (allow_l2b_update or not identity.l2b_uuid):
        identity.l2b_uuid = incoming_l2b_uuid
    identity.confidence = _float(payload.get("confidence"), identity.confidence)
    identity.graphiti_entity_uuids = _merge_unique(
        identity.graphiti_entity_uuids,
        _multi_values(payload, "graphiti_entity_uuid", "graphiti_entity_uuids", "graphiti_uuid"),
    )
    identity.graphiti_edge_uuids = _merge_unique(
        identity.graphiti_edge_uuids,
        _multi_values(payload, "graphiti_edge_uuid", "graphiti_edge_uuids"),
    )
    identity.graphiti_episode_uuids = _merge_unique(
        identity.graphiti_episode_uuids,
        _multi_values(payload, "graphiti_episode_uuid", "graphiti_episode_uuids"),
    )
    identity.obsidian_uuids = _merge_unique(
        identity.obsidian_uuids,
        _multi_values(payload, "obsidian_uuid", "obsidian_uuids"),
    )
    identity.provider_keys = _merge_unique(
        identity.provider_keys,
        _multi_values(payload, "provider_key", "provider_keys"),
    )
    identity.aliases = _merge_unique(
        identity.aliases,
        _multi_values(payload, "alias", "aliases", "label"),
    )
    if isinstance(payload.get("graphiti_raw"), dict):
        identity.graphiti_raw = {**identity.graphiti_raw, **payload["graphiti_raw"]}
    if isinstance(payload.get("meta"), dict):
        identity.meta = {**identity.meta, **payload["meta"]}


def _incoming_identity_keys(payload: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "l2b_uuid": _multi_values(payload, "l2b_uuid"),
        "graphiti_entity_uuid": _multi_values(
            payload,
            "graphiti_entity_uuid",
            "graphiti_entity_uuids",
            "graphiti_uuid",
        ),
        "graphiti_edge_uuid": _multi_values(
            payload,
            "graphiti_edge_uuid",
            "graphiti_edge_uuids",
        ),
        "graphiti_episode_uuid": _multi_values(
            payload,
            "graphiti_episode_uuid",
            "graphiti_episode_uuids",
        ),
        "obsidian_uuid": _multi_values(payload, "obsidian_uuid", "obsidian_uuids"),
        "provider_key": _multi_values(payload, "provider_key", "provider_keys"),
        "ref_id": _multi_values(payload, "ref_id", "ref_ids"),
    }


def _identity_signal_overlaps(
    record: IdentityRecord,
    incoming_keys: dict[str, list[str]],
) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    if record.l2b_uuid and record.l2b_uuid in incoming_keys["l2b_uuid"]:
        signals.append({"kind": "l2b_uuid", "value": record.l2b_uuid, "source": "identity_index"})
    list_fields = {
        "graphiti_entity_uuid": record.graphiti_entity_uuids,
        "graphiti_edge_uuid": record.graphiti_edge_uuids,
        "graphiti_episode_uuid": record.graphiti_episode_uuids,
        "obsidian_uuid": record.obsidian_uuids,
        "provider_key": record.provider_keys,
        "ref_id": record.ref_ids,
    }
    for kind, existing_values in list_fields.items():
        incoming_values = set(incoming_keys[kind])
        for value in existing_values:
            if value in incoming_values:
                signals.append({"kind": kind, "value": value, "source": "identity_index"})
    return signals


def _target_scalar_conflicts(
    identity: IdentityRecord,
    incoming_keys: dict[str, list[str]],
    *,
    now: float,
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    if not identity.l2b_uuid:
        return conflicts
    for incoming_l2b_uuid in incoming_keys["l2b_uuid"]:
        if incoming_l2b_uuid != identity.l2b_uuid:
            conflicts.append(
                _conflict_record(
                    kind="l2b_uuid",
                    value=incoming_l2b_uuid,
                    target_canonical_uuid=identity.canonical_uuid,
                    existing_canonical_uuid=identity.canonical_uuid,
                    reason="target_l2b_uuid_mismatch",
                    now=now,
                    source="identity_index",
                    existing_value=identity.l2b_uuid,
                )
            )
    return conflicts


def _has_l2b_mismatch(conflicts: list[dict[str, Any]]) -> bool:
    return any(
        item.get("kind") == "l2b_uuid"
        and item.get("reason") == "target_l2b_uuid_mismatch"
        for item in conflicts
    )


def _apply_conflicts(
    identities: dict[str, IdentityRecord],
    target_canonical_uuid: str,
    conflicts: list[dict[str, Any]],
    *,
    now: float,
) -> None:
    if not conflicts:
        return
    affected = {target_canonical_uuid}
    affected.update(str(item.get("existing_canonical_uuid") or "") for item in conflicts)
    for canonical_uuid in affected:
        identity = identities.get(canonical_uuid)
        if identity is None:
            continue
        identity.conflicts = _merge_conflict_records(identity.conflicts, conflicts)
        identity.updated_at = now
        if identity.resolution_state != "tombstoned":
            identity.resolution_state = "conflicted"


def _finalize_resolution_state(
    identity: IdentityRecord,
    payload: dict[str, Any],
    *,
    has_conflicts: bool,
) -> None:
    requested = _normalized_resolution_state(
        payload.get("resolution_state"),
        identity.resolution_state,
    )
    if (has_conflicts or identity.conflicts) and requested != "tombstoned":
        identity.resolution_state = "conflicted"
    else:
        identity.resolution_state = requested


def _normalized_resolution_state(value: Any, current: str) -> str:
    text = str(value or "").strip()
    if text in RESOLUTION_STATES:
        return text
    if current in RESOLUTION_STATES:
        return current
    return "weak"


def _conflict_record(
    *,
    kind: str,
    value: str,
    target_canonical_uuid: str,
    existing_canonical_uuid: str,
    reason: str,
    now: float,
    source: str,
    existing_value: str = "",
) -> dict[str, Any]:
    record = {
        "kind": kind,
        "value": value,
        "target_canonical_uuid": target_canonical_uuid,
        "existing_canonical_uuid": existing_canonical_uuid,
        "reason": reason,
        "source": source,
        "policy": "preserve_without_auto_merge",
        "created_at": now,
    }
    if existing_value:
        record["existing_value"] = existing_value
    return record


def _merge_conflict_records(
    existing: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in [*existing, *incoming]:
        key = (
            str(item.get("kind") or ""),
            str(item.get("value") or ""),
            str(item.get("target_canonical_uuid") or ""),
            str(item.get("existing_canonical_uuid") or ""),
            str(item.get("reason") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result


def _ref_record_from_payload(
    payload: dict[str, Any],
    *,
    canonical_uuid: str,
    now: float,
) -> RefRecord | None:
    ref_id = str(payload.get("ref_id") or "").strip()
    ref_kind = str(payload.get("ref_kind") or payload.get("kind") or "").strip()
    locator_values = _multi_values(payload, "locator", "locators", "path", "url")
    if not ref_id and not ref_kind and not locator_values:
        return None
    if not ref_id:
        ref_id = f"ref_{uuid.uuid4().hex[:12]}"
    ref = RefRecord(
        ref_id=ref_id,
        kind=ref_kind or "external",
        canonical_uuid=canonical_uuid,
        canonical_uri=str(payload.get("canonical_uri") or f"parrot://refs/{ref_id}"),
        locators=locator_values,
        content_hash=str(payload.get("content_hash") or ""),
        size=int(_float(payload.get("size"), 0.0)),
        mime_type=str(payload.get("mime_type") or ""),
        version=str(payload.get("version") or ""),
        valid_from=_float(payload.get("valid_from"), 0.0),
        valid_to=_float(payload.get("valid_to"), 0.0),
        health=str(payload.get("health") or "unknown"),
        managed_by=str(payload.get("managed_by") or "unknown"),
        git_commit=str(payload.get("git_commit") or ""),
        last_seen=_float(payload.get("last_seen"), now),
        created_at=now,
        updated_at=now,
        meta=_dict(payload.get("ref_meta")),
    )
    return ref


def _multi_values(payload: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = payload.get(key)
        if raw is None:
            continue
        if isinstance(raw, (list, tuple, set)):
            values.extend(str(item).strip() for item in raw if str(item).strip())
        else:
            text = str(raw).strip()
            if text:
                values.append(text)
    return _merge_unique([], values)


def _merge_unique(existing: list[str], incoming: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in [*existing, *incoming]:
        value = str(item).strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _unique_strings(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return _merge_unique([], [str(item) for item in value])


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _load_identity_records(value: Any) -> dict[str, IdentityRecord]:
    if isinstance(value, dict):
        items = value.items()
    elif isinstance(value, list):
        items = ((str(item.get("canonical_uuid") or ""), item) for item in value if isinstance(item, dict))
    else:
        items = []
    return {
        str(key): IdentityRecord.from_dict(item)
        for key, item in items
        if isinstance(item, dict) and str(key)
    }


def _load_ref_records(value: Any) -> dict[str, RefRecord]:
    if isinstance(value, dict):
        items = value.items()
    elif isinstance(value, list):
        items = ((str(item.get("ref_id") or ""), item) for item in value if isinstance(item, dict))
    else:
        items = []
    return {
        str(key): RefRecord.from_dict(item)
        for key, item in items
        if isinstance(item, dict) and str(key)
    }


def _verify_ref_record(record: RefRecord) -> dict[str, Any]:
    locator_checks = [_verify_locator(locator) for locator in record.locators]
    if not locator_checks:
        health = "unknown"
        reasons = ["no_locator"]
    elif any(item["health"] == "ok" for item in locator_checks):
        health = "ok"
        reasons = [item["reason"] for item in locator_checks if item["health"] == "ok"]
    elif all(item["health"] == "missing" for item in locator_checks):
        health = "missing"
        reasons = [item["reason"] for item in locator_checks]
    else:
        health = "unknown"
        reasons = [item["reason"] for item in locator_checks]
    return {
        "ref_id": record.ref_id,
        "kind": record.kind,
        "canonical_uuid": record.canonical_uuid,
        "health": health,
        "reasons": reasons,
        "locator_checks": locator_checks,
    }


def _verify_identity_record(
    record: IdentityRecord,
    *,
    graphiti_uuid_statuses: dict[str, bool],
    obsidian_uuid_statuses: dict[str, bool],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for value in record.graphiti_entity_uuids:
        checks.append(_status_map_check("graphiti_entity_uuid", value, graphiti_uuid_statuses))
    for value in record.graphiti_edge_uuids:
        checks.append(_status_map_check("graphiti_edge_uuid", value, graphiti_uuid_statuses))
    for value in record.graphiti_episode_uuids:
        checks.append(_status_map_check("graphiti_episode_uuid", value, graphiti_uuid_statuses))
    for value in record.obsidian_uuids:
        checks.append(_status_map_check("obsidian_uuid", value, obsidian_uuid_statuses))
    if not checks:
        health = "unknown"
        reasons = ["no_external_uuid"]
    elif any(item["health"] == "missing" for item in checks):
        health = "missing"
        reasons = [item["reason"] for item in checks if item["health"] == "missing"]
    elif all(item["health"] == "ok" for item in checks):
        health = "ok"
        reasons = [item["reason"] for item in checks]
    else:
        health = "unknown"
        reasons = [item["reason"] for item in checks]
    return {
        "canonical_uuid": record.canonical_uuid,
        "l2b_uuid": record.l2b_uuid,
        "health": health,
        "reasons": reasons,
        "checks": checks,
    }


def _verify_locator(locator: str) -> dict[str, Any]:
    text = str(locator or "").strip()
    lowered = text.lower()
    if not text:
        return {"locator": text, "health": "unknown", "reason": "blank_locator"}
    if lowered.startswith(("http://", "https://")):
        return {"locator": text, "health": "unknown", "reason": "url_not_checked"}
    if lowered.startswith(("ecs://", "s3://", "gs://")):
        return {"locator": text, "health": "unknown", "reason": "remote_locator_not_checked"}
    path = Path(text).expanduser()
    if path.exists():
        return {"locator": text, "health": "ok", "reason": "local_path_exists"}
    return {"locator": text, "health": "missing", "reason": "local_path_missing"}


def _status_map_check(kind: str, value: str, statuses: dict[str, bool]) -> dict[str, Any]:
    if value in statuses:
        exists = bool(statuses[value])
        return {
            "kind": kind,
            "value": value,
            "health": "ok" if exists else "missing",
            "reason": f"{kind}_{'exists' if exists else 'missing'}",
        }
    return {
        "kind": kind,
        "value": value,
        "health": "unknown",
        "reason": f"{kind}_not_checked",
    }


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
