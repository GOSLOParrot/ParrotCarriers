"""Web-only Runtime Flow aggregation and HITL receipts.

The Runtime Flow surface is an operator read model for the Web Console. It
joins existing Plan, Scheduler, Blackboard, IntentWorkspace, Nanobot, trigger,
and message status into a graph-friendly shape without promoting those fields
to Unity/App DTOs.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from parrot.brain.app_live_state import build_app_live_state
from parrot.brain.plan import (
    PlanProposal,
    PlanState,
    PlanStepProposal,
    get_plan_registry,
)
from parrot.brain.plan.plan_lifecycle import PlanLifecycle
from parrot.web_console.runtime_flow_models import (
    RuntimeFlowChanges,
    RuntimeFlowEdge,
    RuntimeFlowEvent,
    RuntimeFlowNode,
    RuntimeFlowSnapshot,
    RuntimeHumanGate,
    RuntimeReceipt,
)
from parrot.web_console.runtime_monitor import build_runtime_monitor_snapshot

_flow_sequence = 0
_flow_signature = ""

_VALID_HITL_ACTIONS = frozenset({
    "approve",
    "approve_and_start",
    "reject",
    "revise",
    "cancel",
    "resume",
})


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
    _normalize_runtime_graph(nodes, edges)
    pending = pending_human_gates()["gates"]
    signature = _stable_signature(nodes=nodes, edges=edges, events=events, gates=pending)
    if signature != _flow_signature:
        _flow_sequence += 1
        _flow_signature = signature
    sequence = _flow_sequence
    _rewrite_event_sequence(events, sequence)

    return RuntimeFlowSnapshot(
        sequence=sequence,
        generated_at=generated_at,
        lanes=_runtime_lanes(),
        nodes=nodes,
        edges=edges,
        events=events[-80:],
        pending_human_gates=pending,
        source_sequences={
            "live_state": live_state.get("sequence"),
            "runtime_monitor_generated_at": monitor.get("generated_at"),
        },
        audit={
            "web_only": True,
            "read_model": True,
            "typed_schema": "parrot.web_console.runtime_flow_models",
            "shared_core_candidates": ["CORE-009", "CORE-010", "CORE-011"],
            "payload_policy": "summaries and redacted refs only",
        },
    ).as_json()


def build_runtime_flow_changes(*, since: int = 0) -> dict[str, Any]:
    """Return a bounded changed-since envelope.

    V1 intentionally uses polling diff semantics. The snapshot is rebuilt for
    each request; SSE/WebSocket can replace this only after the read model
    proves useful and a shared stream contract is confirmed.
    """
    snapshot = build_runtime_flow_snapshot()
    sequence = int(snapshot.get("sequence") or 0)
    changed = sequence > max(0, int(since or 0))
    return RuntimeFlowChanges(
        since=max(0, int(since or 0)),
        sequence=sequence,
        changed=changed,
        events=snapshot["events"] if changed else [],
        snapshot=snapshot if changed else None,
        audit=snapshot["audit"],
    ).as_json()


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
        valid_actions = _valid_hitl_actions_for_state(plan)
        # Use the same state-aware policy that draft/apply validation uses, so
        # the Web workspace cannot render a button the BFF will refuse.
        gates.append(RuntimeHumanGate(
            gate_id=f"plan:{plan_id}",
            target_kind="plan",
            target_id=plan_id,
            trace_id=f"plan:{plan_id}",
            state="pending",
            plan_state=_plan_state_value(plan),
            prompt="Plan is awaiting operator confirmation.",
            summary=str(getattr(plan, "title", "") or plan_id),
            options=valid_actions,
            valid_actions_for_state=valid_actions,
            operator_required_for_execute=True,
            created_at=float(getattr(plan, "drafted_at", 0.0) or 0.0),
            expires_at=0.0,
            payload_ref=str(getattr(plan, "staged_ref_id", "") or ""),
        ).as_json())
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
    gate_id, target_kind, target_id = _parse_hitl_target(body)
    plan_id = target_id if target_kind == "plan" else ""
    unsupported_target = target_kind != "plan"
    plan = _plan_for_hitl(plan_id) if plan_id and not unsupported_target else None
    state_error = "unsupported_hitl_target" if unsupported_target else _hitl_decision_error(plan=plan, action=action)
    success = bool(plan_id) and state_error == ""
    data: dict[str, Any] = {
        "gate_id": gate_id,
        "target_kind": target_kind,
        "target_id": target_id,
        "decision": action,
        "plan_state": _plan_state_value(plan),
        "operator_required_for_execute": True,
        "would_apply": False,
    }
    if not success:
        data.update({
            "error": state_error,
            "valid_actions": [] if unsupported_target else sorted(_VALID_HITL_ACTIONS),
            "valid_actions_for_state": [] if unsupported_target else _valid_hitl_actions_for_state(plan),
        })
    if unsupported_target:
        # CORE-011 is currently ratified only as a Web Plan gate prototype.
        # Trigger/message gates stay explicit unsupported targets until their
        # state machine and receipts are designed instead of guessed here.
        data["valid_target_kinds"] = ["plan"]
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
        plan = registry.get(plan_id)
        plan_state = getattr(plan, "state", None)
        if decision == "approve":
            await registry.approve(plan_id)
        elif decision == "approve_and_start":
            if plan_state == PlanState.AWAITING_USER_CONFIRMATION:
                await registry.approve(plan_id)
            await registry.start_executing(plan_id)
        elif decision == "resume":
            if plan_state == PlanState.AWAITING_USER_CONFIRMATION:
                await registry.approve(plan_id)
            await registry.start_executing(plan_id)
        elif decision == "reject":
            await registry.cancel(plan_id, reason=str(body.get("reason") or decision))
        elif decision == "cancel":
            await registry.cancel(plan_id, reason=str(body.get("reason") or decision))
        elif decision == "revise":
            await registry.revise(plan_id, _revision_proposal(body))
        applied_plan = registry.get(plan_id)
        return _receipt(
            action="runtime.hitl.apply_decision",
            success=True,
            dry_run=False,
            operator_mode=True,
            data={
                **draft["data"],
                "applied": True,
                "plan_state_after": _plan_state_value(applied_plan),
            },
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
            payload_ref=ref_id,
        ))
        related_node = str(row.get("related_node_uuid") or "")
        if related_node:
            edges.append(_edge(node_id, f"memory:{related_node}", "related_node"))
        events.append(_event(
            sequence,
            "intent_ref",
            ref_id,
            "observed",
            row.get("title") or ref_id,
            payload_ref=ref_id,
        ))


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
            trace_id=f"plan:{plan_id}",
            payload_ref=str(plan.get("staged_ref_id") or ""),
        ))
        events.append(_event(
            sequence,
            "plan",
            plan_id,
            str(plan.get("state") or "observed"),
            plan.get("title") or plan_id,
            trace_id=f"plan:{plan_id}",
            payload_ref=str(plan.get("staged_ref_id") or ""),
        ))
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
                trace_id=f"plan:{plan_id}",
                payload_ref=str(plan.get("staged_ref_id") or ""),
            ))
            edges.append(_edge(plan_node_id, gate_id, "awaits_human", trace_id=f"plan:{plan_id}"))
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
                trace_id=f"plan:{plan_id}",
                payload_ref=str(step.get("result_ref_id") or ""),
            ))
            edges.append(_edge(plan_node_id, step_node_id, "has_step", trace_id=f"plan:{plan_id}"))
            for dep in step.get("depends_on", []) or []:
                edges.append(_edge(
                    f"step:{plan_id}:{dep}",
                    step_node_id,
                    "depends_on",
                    trace_id=f"plan:{plan_id}",
                ))


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
        plan_id = str(task.get("plan_id") or "")
        step_id = str(task.get("step_id") or "")
        trace_id = f"plan:{plan_id}" if plan_id else f"scheduler_task:{task_id}"
        node_id = f"scheduler:{task_id}"
        nodes.append(_node(
            node_id=node_id,
            lane="scheduler",
            entity_kind="scheduler_task",
            entity_id=task_id,
            label=str(task.get("type") or task_id),
            status=str(task.get("status") or "active"),
            summary=str(task.get("destination") or ""),
            trace_id=trace_id,
        ))
        if plan_id and step_id:
            edges.append(_edge(
                f"step:{plan_id}:{step_id}",
                node_id,
                "dispatches",
                trace_id=trace_id,
            ))
        events.append(_event(
            sequence,
            "scheduler_task",
            task_id,
            str(task.get("status") or "active"),
            task.get("type") or task_id,
            trace_id=trace_id,
            parent_span_id=f"step:{plan_id}:{step_id}" if plan_id and step_id else "",
        ))


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
            plan_id = str(task.get("plan_id") or "")
            edges.append(_edge(
                f"scheduler:{task_id}",
                "nanobot:worker",
                "queued_to",
                trace_id=f"plan:{plan_id}" if plan_id else f"scheduler_task:{task_id}",
            ))


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
    trace_id: str = "",
    payload_ref: str = "",
) -> dict[str, Any]:
    """Build a renderer node with CORE-010-compatible trace hints.

    `id`/`lane` are React Flow concerns; `trace_id`/`payload_ref` are the
    portable observability hints we may later promote if CORE-010 is approved.
    """
    return RuntimeFlowNode(
        id=node_id,
        lane=lane,
        entity_kind=entity_kind,
        entity_id=entity_id,
        trace_id=trace_id or f"{entity_kind}:{entity_id}",
        label=label,
        status=status,
        summary=summary,
        payload_ref=payload_ref,
    ).as_json()


def _edge(source: str, target: str, kind: str, *, trace_id: str = "") -> dict[str, Any]:
    """Build a React Flow edge.

    `source` and `target` are graph endpoint ids, not the same concept as the
    `source` field on trace events.
    """
    return RuntimeFlowEdge(
        id=f"{source}->{target}:{kind}",
        source=source,
        target=target,
        kind=kind,
        trace_id=trace_id,
    ).as_json()


def _event(
    sequence: int,
    entity_kind: str,
    entity_id: str,
    op: str,
    summary: Any,
    *,
    trace_id: str = "",
    parent_span_id: str = "",
    payload_ref: str = "",
) -> dict[str, Any]:
    """Build one bounded runtime event row.

    This deliberately mirrors trace/span vocabulary without making a shared
    protocol promise yet. It stays a Web read model until CORE-010 is ratified.
    """
    trace = trace_id or f"{entity_kind}:{entity_id}"
    return RuntimeFlowEvent(
        sequence=sequence,
        trace_id=trace,
        span_id=f"{sequence}:{entity_kind}:{entity_id}:{op}",
        parent_span_id=parent_span_id,
        entity_kind=entity_kind,
        entity_id=entity_id,
        op=op,
        status=op,
        event_source="web_console.runtime_flow",
        writer="read_model",
        summary=str(summary or ""),
        created_at=time.time(),
        payload_ref=payload_ref,
    ).as_json()


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
                "parent_span_id": row.get("parent_span_id"),
                "entity_kind": row.get("entity_kind"),
                "entity_id": row.get("entity_id"),
                "op": row.get("op"),
                "status": row.get("status"),
                "source": row.get("source"),
                "writer": row.get("writer"),
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


def _normalize_runtime_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
    """Keep the Web read-model graph deterministic and renderer-safe.

    Runtime Flow intentionally stays smaller than the full Memory Graph page.
    Related memory refs, duplicate Plan dependencies, or truncated step lists
    can produce duplicate or dangling edges. Those are renderer concerns, so
    they are cleaned here without changing the underlying Plan/Blackboard data.
    """
    seen_nodes: set[str] = set()
    unique_nodes: list[dict[str, Any]] = []
    for row in nodes:
        node_id = str(row.get("id") or "")
        if not node_id or node_id in seen_nodes:
            continue
        seen_nodes.add(node_id)
        unique_nodes.append(row)
    nodes[:] = unique_nodes

    node_ids = {str(row.get("id") or "") for row in nodes}
    seen_edges: set[str] = set()
    unique_edges: list[dict[str, Any]] = []
    for row in edges:
        edge_id = str(row.get("id") or "")
        if (
            not edge_id
            or edge_id in seen_edges
            or str(row.get("source") or "") not in node_ids
            or str(row.get("target") or "") not in node_ids
        ):
            continue
        seen_edges.add(edge_id)
        unique_edges.append(row)
    edges[:] = unique_edges


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
    audit = _hitl_audit() if action.startswith("runtime.hitl") else {
        "web_only": True,
        "operator_required_for_execute": True,
    }
    return RuntimeReceipt(
        action=action,
        success=success,
        dry_run=dry_run,
        operator_mode=operator_mode,
        receipt_id=f"web-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}",
        data=data,
        audit=audit,
    ).as_json()


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


def _plan_for_hitl(plan_id: str) -> Any | None:
    try:
        return get_plan_registry().get(plan_id)
    except Exception:
        return None


def _parse_hitl_target(payload: dict[str, Any]) -> tuple[str, str, str]:
    """Normalize Web HITL targets without broadening CORE-011.

    Runtime Flow can already display trigger/message nodes, but the executable
    HITL contract is still Plan-only. Returning the parsed target kind lets the
    route produce an explicit unsupported-target receipt instead of silently
    treating every gate as a Plan.
    """

    gate_id = str(payload.get("gate_id") or "").strip()
    target_kind = str(payload.get("target_kind") or "").strip().lower()
    target_id = str(payload.get("target_id") or payload.get("plan_id") or "").strip()
    if gate_id and ":" in gate_id:
        parsed_kind, parsed_id = gate_id.split(":", 1)
        parsed_kind = parsed_kind.strip().lower()
        if parsed_kind:
            target_kind = target_kind or parsed_kind
        if parsed_id and not target_id:
            target_id = parsed_id.strip()
    elif gate_id and not target_id:
        target_id = gate_id

    target_kind = target_kind or "plan"
    if not gate_id and target_id:
        gate_id = f"{target_kind}:{target_id}"
    return gate_id, target_kind, target_id


def _hitl_decision_error(*, plan: Any | None, action: str) -> str:
    """Return an error code when a HITL decision cannot apply to this Plan.

    CORE-011 is still only a candidate, so the Web BFF keeps the validation
    local and explicit: a dry-run receipt must be as trustworthy as the later
    operator execution attempt.
    """
    if action not in _VALID_HITL_ACTIONS:
        return "invalid_hitl_decision"
    if plan is None:
        return "plan_not_found"
    if action not in _valid_hitl_actions_for_state(plan):
        return "invalid_plan_state"
    return ""


def _valid_hitl_actions_for_state(plan: Any | None) -> list[str]:
    state = _plan_state(plan)
    if state is None:
        return []

    valid: set[str] = set()
    if PlanLifecycle.can_transition(state, PlanState.APPROVED):
        valid.add("approve")
    if state in {PlanState.AWAITING_USER_CONFIRMATION, PlanState.APPROVED}:
        valid.add("approve_and_start")
    if state in {
        PlanState.AWAITING_USER_CONFIRMATION,
        PlanState.APPROVED,
        PlanState.PARTIAL_COMPLETE,
    }:
        valid.add("resume")
    if state == PlanState.AWAITING_USER_CONFIRMATION:
        valid.add("reject")
    if PlanLifecycle.can_transition(state, PlanState.CANCELLED):
        valid.add("cancel")
    if PlanLifecycle.can_transition(state, PlanState.REVISED):
        valid.add("revise")
    return sorted(valid)


def _plan_state(plan: Any | None) -> PlanState | None:
    if plan is None:
        return None
    state = getattr(plan, "state", None)
    if isinstance(state, PlanState):
        return state
    try:
        return PlanState(str(state))
    except Exception:
        return None


def _plan_state_value(plan: Any | None) -> str:
    state = _plan_state(plan)
    return state.value if state is not None else ""


__all__ = [
    "apply_human_gate_decision",
    "build_runtime_flow_changes",
    "build_runtime_flow_snapshot",
    "draft_human_gate_decision",
    "pending_human_gates",
]
