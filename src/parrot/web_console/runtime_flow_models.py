"""Typed Web-only Runtime Flow read models.

These dataclasses are intentionally scoped to the Web Console BFF. They give
the Runtime Flow code a typed construction layer without promoting the shape to
Unity/App DTOs or a shared bus protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeFlowNode:
    id: str
    lane: str
    entity_kind: str
    entity_id: str
    trace_id: str
    label: str
    status: str
    summary: str
    payload_ref: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "lane": self.lane,
            "entity_kind": self.entity_kind,
            "entity_id": self.entity_id,
            "trace_id": self.trace_id,
            "label": self.label,
            "status": self.status,
            "summary": self.summary,
            "payload_ref": self.payload_ref,
        }


@dataclass(frozen=True)
class RuntimeFlowEdge:
    id: str
    source: str
    target: str
    kind: str
    trace_id: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "trace_id": self.trace_id,
        }


@dataclass(frozen=True)
class RuntimeFlowEvent:
    sequence: int
    trace_id: str
    span_id: str
    parent_span_id: str
    entity_kind: str
    entity_id: str
    op: str
    status: str
    event_source: str
    writer: str
    summary: str
    created_at: float
    payload_ref: str = ""

    def as_json(self) -> dict[str, Any]:
        # The public route keeps the historical `source` key for compatibility.
        # Internally this field means event writer/system, not graph edge source.
        return {
            "sequence": self.sequence,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "entity_kind": self.entity_kind,
            "entity_id": self.entity_id,
            "op": self.op,
            "status": self.status,
            "source": self.event_source,
            "writer": self.writer,
            "summary": self.summary,
            "created_at": self.created_at,
            "payload_ref": self.payload_ref,
        }


@dataclass(frozen=True)
class RuntimeHumanGate:
    gate_id: str
    target_kind: str
    target_id: str
    trace_id: str
    state: str
    plan_state: str
    prompt: str
    summary: str
    options: list[str] = field(default_factory=list)
    valid_actions_for_state: list[str] = field(default_factory=list)
    operator_required_for_execute: bool = True
    created_at: float = 0.0
    expires_at: float = 0.0
    payload_ref: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "target_kind": self.target_kind,
            "target_id": self.target_id,
            "trace_id": self.trace_id,
            "state": self.state,
            "plan_state": self.plan_state,
            "prompt": self.prompt,
            "summary": self.summary,
            "options": list(self.options),
            "valid_actions_for_state": list(self.valid_actions_for_state),
            "operator_required_for_execute": self.operator_required_for_execute,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "payload_ref": self.payload_ref,
        }


@dataclass(frozen=True)
class RuntimeFlowSnapshot:
    sequence: int
    generated_at: float
    lanes: list[dict[str, str]]
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    events: list[dict[str, Any]]
    pending_human_gates: list[dict[str, Any]]
    source_sequences: dict[str, Any]
    audit: dict[str, Any]
    success: bool = True
    action: str = "runtime.flow.snapshot"

    def as_json(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "sequence": self.sequence,
            "generated_at": self.generated_at,
            "lanes": list(self.lanes),
            "nodes": list(self.nodes),
            "edges": list(self.edges),
            "events": list(self.events),
            "pending_human_gates": list(self.pending_human_gates),
            "source_sequences": dict(self.source_sequences),
            "audit": dict(self.audit),
        }


@dataclass(frozen=True)
class RuntimeFlowChanges:
    since: int
    sequence: int
    changed: bool
    events: list[dict[str, Any]]
    snapshot: dict[str, Any] | None
    audit: dict[str, Any]
    event_schema: str = "runtime_flow_delta_v1"
    success: bool = True
    action: str = "runtime.flow.changes"

    def as_json(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "event_schema": self.event_schema,
            "since": self.since,
            "sequence": self.sequence,
            "changed": self.changed,
            "events": list(self.events),
            "snapshot": self.snapshot,
            "audit": dict(self.audit),
        }


@dataclass(frozen=True)
class RuntimeReceipt:
    action: str
    success: bool
    dry_run: bool
    operator_mode: bool
    receipt_id: str
    data: dict[str, Any]
    audit: dict[str, Any]

    def as_json(self) -> dict[str, Any]:
        payload = {
            "success": self.success,
            "action": self.action,
            "dry_run": self.dry_run,
            "operator_mode": self.operator_mode,
            "receipt_id": self.receipt_id,
            "data": dict(self.data),
            "audit": dict(self.audit),
        }
        core_candidate = self.audit.get("core_candidate")
        if core_candidate:
            payload["core_candidate"] = core_candidate
        return payload
