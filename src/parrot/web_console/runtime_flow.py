"""Web-only Runtime Flow aggregation and HITL receipts.

The Runtime Flow surface is an operator read model for the Web Console. It
joins existing Plan, Scheduler, Blackboard, IntentWorkspace, Nanobot, trigger,
and message status into a graph-friendly shape without promoting those fields
to Unity/App DTOs.
"""

from __future__ import annotations

import json
import time
from typing import Any

from parrot.brain.app_live_state import build_app_live_state
from parrot.brain.plan import (
    PlanProposal,
    PlanState,
    PlanStepProposal,
    get_plan_registry,
)
from parrot.web_console.runtime_monitor import build_runtime_monitor_snapshot

_flow_sequence = 0
_flow_signature = ""


def build_runtime_flow_snapshot() -> dict[str, Any]:
    """Return a graph-friendly Runtime Flow snapshot for the React console."""
    global _flow_sequence, _flow_signature
    candidate_sequence = _flow_sequence + 1
    generated_at = time.time()
    monitor = build_runtime_monitor_snapshot()
    live_state = build_app_live_state(l2b_limit=80).as_json()
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    _add_intent_nodes(nodes, edges, events, live_state, candidate_sequence)
    _add_plan_nodes(nodes, edges, events, monitor, candidate_sequence)
    _add_blackboard_nodes(nodes, events, monitor, candidate_sequence)
    _add_scheduler_nodes(nodes, edges, events, monitor, candidate_sequence)
    _add_nanobot_nodes(nodes, edges, events, monitor, candidate_sequence)
    _add_trigger_message_nodes(nodes, edges, events, monitor, candidate_sequence)
    _prune_dangling_edges(nodes, edges)
    pending = pending_human_gates()["gates"]
    signature = _stable_signature(nodes=nodes, edges=edges, events=events, gates=pending)
    if signature != _flow_signature:
        _flow_sequence += 1
        _flow_signature = signature
    sequence = _flow_sequence
    _rewrite_event_sequence(events, sequence)

    return {
        "success": True,
        "action": "runtime.flow.snapshot",
        "sequence": sequence,
        "generated_at": generated_at,
        "lanes": _runtime_lanes(),
        "nodes": nodes,
        "edges": edges,
        "events": events[-80:],
        "pending_human_gates": pending,
        "source_sequences": {
            "live_state": live_state.get("sequence"),
            "runtime_monitor_generated_at": monitor.get("generated_at"),
        },
        "audit": {
            "web_only": True,
            "read_model": True,
            "shared_core_candidates": ["CORE-009", "CORE-010", "CORE-011"],
            "payload_policy": "summaries and redacted refs only",
        },
    }


def build_runtime_flow_changes(*, since: int = 0) -> dict[str, Any]:
    """Return a bounded changed-since envelope.

    V1 intentionally uses polling diff semantics. The snapshot is rebuilt for
    each request; SSE/WebSocket can replace this only after the read model
    proves useful and a shared stream contract is confirmed.
    """
    snapshot = build_runtime_flow_snapshot()
    sequence = int(snapshot.get("sequence") or 0)
    changed = sequence > max(0, int(since or 0))
    return {
        "success": True,
        "action": "runtime.flow.changes",
        "since": max(0, int(since or 0)),
        "sequence": sequence,
        "changed": changed,
        "events": snapshot["events"] if changed else [],
        "snapshot": snapshot if changed else None,
        "audit": snapshot["audit"],
    }


def pending_human_gates() -> dict[str, Any]:
    """List pending Plan/HITL gates for Web operator review."""
    gates: list[dict[str, Any]] = []
    try:
        registry = get_plan_registry()
        plans = registry.list_active()
    except Exception as exc:
        return {
            "success": False,
            "action": "runtime.hitl.pending",
            "gates": [],
            "error": f"{type(exc).__name__}: {exc}",
            "audit": _hitl_audit(),
        }

    for plan in plans:
        if getattr(plan, "state", None) != PlanState.AWAITING_USER_CONFIRMATION:
            continue
        plan_id = str(getattr(plan, "plan_id", ""))
        gates.append({
            "gate_id": f"plan:{plan_id}",
            "target_kind": "plan",
            "target_id": plan_id,
            "trace_id": f"plan:{plan_id}",
            "state": "pending",
            "prompt": "Plan is awaiting operator confirmation.",
            "summary": str(getattr(plan, "title", "") or plan_id),
            "options": ["approve", "approve_and_start", "reject", "revise", "cancel"],
            "created_at": float(getattr(plan, "drafted_at", 0.0) or 0.0),
            "expires_at": 0.0,
            "payload_ref": str(getattr(plan, "staged_ref_id", "") or ""),
        })
    return {
        "success": True,
        "action": "runtime.hitl.pending",
        "gates": gates,
        "audit": _hitl_audit(),
    }


def draft_human_gate_decision(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate a HITL decision and return a receipt without applying it."""
    body = payload or {}
    action = str(body.get("decision") or body.get("action") or "approve").strip().lower()
    gate_id = str(body.get("gate_id") or "").strip()
    plan_id = str(body.get("plan_id") or "").strip()
    if gate_id.startswith("plan:") and not plan_id:
        plan_id = gate_id.split(":", 1)[1]
    if not gate_id and plan_id:
        gate_id = f"plan:{plan_id}"
    valid_actions = {"approve", "approve_and_start", "reject", "revise", "cancel", "resume"}
    plan_exists = _plan_exists(plan_id) if plan_id else False
    success = bool(plan_id) and action in valid_actions and plan_exists
    data: dict[str, Any] = {
        "gate_id": gate_id,
        "target_kind": "plan",
        "target_id": plan_id,
        "decision": action,
        "operator_required_for_execute": True,
        "would_apply": False,
    }
    if not success:
        data.update({
            "error": "plan_not_found" if plan_id and action in valid_actions else "invalid_hitl_decision",
            "valid_actions": sorted(valid_actions),
        })
    return _receipt(
        action="runtime.hitl.draft_decision",
        success=success,
        dry_run=_body_bool(body.get("dry_run"), True),
        operator_mode=_body_bool(body.get("operator_mode"), False),
        data=data,
    )


async def apply_human_gate_decision(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply a HITL decision only when operator mode is explicit."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    draft = draft_human_gate_decision({
        **body,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
    })
    draft["action"] = "runtime.hitl.apply_decision"
    if not draft.get("success"):
        return draft
    draft["data"]["would_apply"] = True
    if dry_run or not operator_mode:
        draft["data"]["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return draft

    plan_id = str(draft["data"]["target_id"])
    decision = str(draft["data"]["decision"])
    try:
        registry = get_plan_registry()
        if decision in {"approve", "approve_and_start"}:
            await registry.approve(plan_id)
            if decision == "approve_and_start":
                await registry.start_executing(plan_id)
        elif decision in {"reject", "cancel"}:
            await registry.cancel(plan_id, reason=str(body.get("reason") or decision))
        elif decision == "resume":
            plan = registry.get(plan_id)
            if plan is not None and getattr(plan, "state", None) == PlanState.AWAITING_USER_CONFIRMATION:
                await registry.approve(plan_id)
            await registry.start_executing(plan_id)
        elif decision == "revise":
            await registry.revise(plan_id, _revision_proposal(body))
        return _receipt(
            action="runtime.hitl.apply_decision",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "applied": True},
        )
    except Exception as exc:
        return _receipt(
            action="runtime.hitl.apply_decision",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={**draft["data"], "applied": False, "error": f"{type(exc).__name__}: {exc}"},
        )


def _add_intent_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    live_state: dict[str, Any],
    sequence: int,
) -> None:
    refs = live_state.get("intent_workspace", {}).get("refs", []) or []
    for row in refs[:10]:
        ref_id = str(row.get("ref_id") or "")
        if not ref_id:
            continue
        node_id = f"intent:{ref_id}"
        nodes.append(_node(
            node_id=node_id,
            lane="intent",
            entity_kind="intent_ref",
            entity_id=ref_id,
            label=str(row.get("title") or row.get("role") or row.get("kind") or ref_id),
            status="active",
            summary=str(row.get("origin") or row.get("payload_source") or ""),
        ))
        related_node = str(row.get("related_node_uuid") or "")
        if related_node:
            edges.append(_edge(node_id, f"memory:{related_node}", "related_node"))
        events.append(_event(sequence, "intent_ref", ref_id, "observed", row.get("title") or ref_id))


def _add_plan_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    monitor: dict[str, Any],
    sequence: int,
) -> None:
    for plan in (monitor.get("plans", {}).get("plans", []) or [])[:12]:
        plan_id = str(plan.get("plan_id") or "")
        if not plan_id:
            continue
        plan_node_id = f"plan:{plan_id}"
        nodes.append(_node(
            node_id=plan_node_id,
            lane="plan",
            entity_kind="plan",
            entity_id=plan_id,
            label=str(plan.get("title") or plan_id),
            status=str(plan.get("state") or "unknown"),
            summary=f"{plan.get('step_count', 0)} step(s)",
        ))
        events.append(_event(sequence, "plan", plan_id, str(plan.get("state") or "observed"), plan.get("title") or plan_id))
        if str(plan.get("state")) == PlanState.AWAITING_USER_CONFIRMATION.value:
            gate_id = f"gate:plan:{plan_id}"
            nodes.append(_node(
                node_id=gate_id,
                lane="human_gate",
                entity_kind="human_gate",
                entity_id=f"plan:{plan_id}",
                label="Awaiting approval",
                status="pending",
                summary=str(plan.get("title") or plan_id),
            ))
            edges.append(_edge(plan_node_id, gate_id, "awaits_human"))
        for step in (plan.get("steps", []) or [])[:16]:
            step_id = str(step.get("step_id") or "")
            if not step_id:
                continue
            step_node_id = f"step:{plan_id}:{step_id}"
            nodes.append(_node(
                node_id=step_node_id,
                lane="plan",
                entity_kind="plan_step",
                entity_id=step_id,
                label=str(step.get("title") or step_id),
                status=str(step.get("state") or "unknown"),
                summary=str(step.get("expected_tool") or ""),
            ))
            edges.append(_edge(plan_node_id, step_node_id, "has_step"))
            for dep in step.get("depends_on", []) or []:
                edges.append(_edge(f"step:{plan_id}:{dep}", step_node_id, "depends_on"))


def _add_blackboard_nodes(
    nodes: list[dict[str, Any]],
    events: list[dict[str, Any]],
    monitor: dict[str, Any],
    sequence: int,
) -> None:
    for row in (monitor.get("blackboard", {}).get("present_keys", []) or [])[:16]:
        key = str(row.get("key") or "")
        if not key:
            continue
        nodes.append(_node(
            node_id=f"bb:{key}",
            lane="blackboard",
            entity_kind="blackboard_key",
            entity_id=key,
            label=key,
            status="present",
            summary=str(row.get("summary") or row.get("writer") or ""),
        ))
        events.append(_event(sequence, "blackboard_key", key, "present", row.get("summary") or key))


def _add_scheduler_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    monitor: dict[str, Any],
    sequence: int,
) -> None:
    for task in (monitor.get("scheduler", {}).get("active_tasks", []) or [])[:20]:
        task_id = str(task.get("task_id") or "")
        if not task_id:
            continue
        node_id = f"scheduler:{task_id}"
        nodes.append(_node(
            node_id=node_id,
            lane="scheduler",
            entity_kind="scheduler_task",
            entity_id=task_id,
            label=str(task.get("type") or task_id),
            status=str(task.get("status") or "active"),
            summary=str(task.get("destination") or ""),
        ))
        plan_id = str(task.get("plan_id") or "")
        step_id = str(task.get("step_id") or "")
        if plan_id and step_id:
            edges.append(_edge(f"step:{plan_id}:{step_id}", node_id, "dispatches"))
        events.append(_event(sequence, "scheduler_task", task_id, "active", task.get("type") or task_id))


def _add_nanobot_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    monitor: dict[str, Any],
    sequence: int,
) -> None:
    nanobot = monitor.get("nanobot", {}) or {}
    status = nanobot.get("status", {}) if isinstance(nanobot.get("status"), dict) else {}
    nodes.append(_node(
        node_id="nanobot:worker",
        lane="nanobot",
        entity_kind="nanobot_worker",
        entity_id="nanobot",
        label="Nanobot Worker",
        status=str(status.get("state") or "unknown"),
        summary=str(status.get("summary") or nanobot.get("worker_role") or ""),
    ))
    events.append(_event(sequence, "nanobot_worker", "nanobot", str(status.get("state") or "observed"), status.get("summary") or "Nanobot"))
    for task in (monitor.get("scheduler", {}).get("active_tasks", []) or [])[:20]:
        task_id = str(task.get("task_id") or "")
        if task_id:
            edges.append(_edge(f"scheduler:{task_id}", "nanobot:worker", "queued_to"))


def _add_trigger_message_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    monitor: dict[str, Any],
    sequence: int,
) -> None:
    for stage in (monitor.get("collaboration", {}).get("channel_flow", []) or [])[:8]:
        stage_id = str(stage.get("stage") or "")
        if not stage_id:
            continue
        node_id = f"flow:{stage_id}"
        nodes.append(_node(
            node_id=node_id,
            lane="trigger_message",
            entity_kind="runtime_channel",
            entity_id=stage_id,
            label=str(stage.get("label") or stage_id),
            status=str(stage.get("status") or "unknown"),
            summary=str(stage.get("detail") or stage.get("channel") or ""),
        ))
        events.append(_event(sequence, "runtime_channel", stage_id, str(stage.get("status") or "observed"), stage.get("detail") or stage_id))
    flow_nodes = [n["id"] for n in nodes if n.get("entity_kind") == "runtime_channel"]
    for source, target in zip(flow_nodes, flow_nodes[1:]):
        edges.append(_edge(source, target, "channel_flow"))


def _runtime_lanes() -> list[dict[str, str]]:
    return [
        {"id": "intent", "label": "GOSLO Intent"},
        {"id": "plan", "label": "Plan"},
        {"id": "human_gate", "label": "Human Gate"},
        {"id": "blackboard", "label": "Blackboard"},
        {"id": "intent_workspace", "label": "IntentWorkspace"},
        {"id": "scheduler", "label": "Scheduler"},
        {"id": "nanobot", "label": "Nanobot"},
        {"id": "trigger_message", "label": "Message / Trigger"},
    ]


def _node(
    *,
    node_id: str,
    lane: str,
    entity_kind: str,
    entity_id: str,
    label: str,
    status: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "lane": lane,
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "label": label,
        "status": status,
        "summary": summary,
    }


def _edge(source: str, target: str, kind: str) -> dict[str, str]:
    return {
        "id": f"{source}->{target}:{kind}",
        "source": source,
        "target": target,
        "kind": kind,
    }


def _event(
    sequence: int,
    entity_kind: str,
    entity_id: str,
    op: str,
    summary: Any,
) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "trace_id": f"{entity_kind}:{entity_id}",
        "span_id": f"{sequence}:{entity_kind}:{entity_id}:{op}",
        "parent_span_id": "",
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "op": op,
        "status": op,
        "source": "web_console.runtime_flow",
        "writer": "read_model",
        "summary": str(summary or ""),
        "created_at": time.time(),
        "payload_ref": "",
    }


def _stable_signature(
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    gates: list[dict[str, Any]],
) -> str:
    """Return a stable content signature for changed-since polling.

    Snapshot timestamps and synthetic span ids should not make a no-op poll
    look like a runtime change. The signature keeps entity/status/link content
    only, so `/changes?since=<current>` can return `changed=false`.
    """
    payload = {
        "nodes": sorted(nodes, key=lambda row: str(row.get("id") or "")),
        "edges": sorted(edges, key=lambda row: str(row.get("id") or "")),
        "events": sorted([
            {
                "trace_id": row.get("trace_id"),
                "entity_kind": row.get("entity_kind"),
                "entity_id": row.get("entity_id"),
                "op": row.get("op"),
                "status": row.get("status"),
                "summary": row.get("summary"),
                "payload_ref": row.get("payload_ref"),
            }
            for row in events
        ], key=lambda row: (
            str(row.get("trace_id") or ""),
            str(row.get("op") or ""),
            str(row.get("summary") or ""),
        )),
        "gates": sorted(gates, key=lambda row: str(row.get("gate_id") or "")),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)


def _prune_dangling_edges(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
    """Drop links whose endpoints are outside this read-model graph.

    Runtime Flow intentionally stays smaller than the full Memory Graph page.
    Related memory refs or truncated dependency nodes can be absent here; React
    Flow should receive a clean graph rather than dangling edge ids.
    """
    node_ids = {str(row.get("id") or "") for row in nodes}
    edges[:] = [
        row for row in edges
        if str(row.get("source") or "") in node_ids
        and str(row.get("target") or "") in node_ids
    ]


def _rewrite_event_sequence(events: list[dict[str, Any]], sequence: int) -> None:
    for row in events:
        row["sequence"] = sequence
        row["span_id"] = (
            f"{sequence}:{row.get('entity_kind', '')}:"
            f"{row.get('entity_id', '')}:{row.get('op', '')}"
        )


def _revision_proposal(body: dict[str, Any]) -> PlanProposal:
    revision = body.get("revision") if isinstance(body.get("revision"), dict) else {}
    steps_raw = revision.get("steps") if isinstance(revision.get("steps"), list) else []
    steps = []
    for idx, row in enumerate(steps_raw[:12]):
        if not isinstance(row, dict):
            continue
        steps.append(PlanStepProposal(
            step_id=str(row.get("step_id") or f"step_{idx + 1}"),
            title=str(row.get("title") or f"Revised step {idx + 1}"),
            expected_tool=str(row.get("expected_tool") or ""),
            inputs=row.get("inputs") if isinstance(row.get("inputs"), dict) else {},
            depends_on=tuple(str(dep) for dep in (row.get("depends_on") or [])),
        ))
    return PlanProposal(
        proposed_by="web_console.hitl",
        title=str(revision.get("title") or body.get("title") or "Revised Web Plan"),
        rationale=str(revision.get("rationale") or body.get("reason") or ""),
        suggested_steps=tuple(steps),
        blocks_conversation=_body_bool(revision.get("blocks_conversation"), True),
    )


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
        "receipt_id": f"web-{int(time.time() * 1000)}",
        "data": data,
        "audit": _hitl_audit() if action.startswith("runtime.hitl") else {
            "web_only": True,
            "operator_required_for_execute": True,
        },
    }


def _hitl_audit() -> dict[str, Any]:
    return {
        "web_only": True,
        "default_mode": "dry_run",
        "operator_required_for_execute": True,
        "core_candidate": "CORE-011",
    }


def _body_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _plan_exists(plan_id: str) -> bool:
    try:
        return get_plan_registry().get(plan_id) is not None
    except Exception:
        return False


__all__ = [
    "apply_human_gate_decision",
    "build_runtime_flow_changes",
    "build_runtime_flow_snapshot",
    "draft_human_gate_decision",
    "pending_human_gates",
]
