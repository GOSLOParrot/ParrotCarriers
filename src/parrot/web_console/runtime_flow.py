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
from parrot.scheduler.task_catalog import is_nanobot_task_type
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

_RESULT_ROUTE_POLICIES: dict[str, dict[str, Any]] = {
    "view_only": {
        "sink": "web_console.receipt_rail",
        "route": "receipt_only",
        "route_state": "implemented",
        "enforcement": "web_receipt_only",
        "mutates_memory": False,
    },
    "return_to_goslo": {
        "sink": "goslo.intent_context",
        "route": "manual_context_return",
        "route_state": "metadata_only",
        "enforcement": "operator_or_agent_interprets_receipt",
        "mutates_memory": False,
    },
    "return_to_app": {
        "sink": "app.runtime_event",
        "route": "not_implemented",
        "route_state": "not_implemented",
        "enforcement": "future_core_candidate",
        "mutates_memory": False,
    },
    "stage_to_intent_workspace": {
        "sink": "brain.intent_workspace",
        "route": "PlanRegistry.draft/IntentWorkspace.stage",
        "route_state": "partially_implemented",
        "enforcement": "plan_step_input_carried",
        "mutates_memory": True,
    },
    "write_to_memory_draft": {
        "sink": "l1_5_l2b.memory_draft",
        "route": "capability.draft_route",
        "route_state": "operator_gated_route",
        "enforcement": "route_receipt",
        "mutates_memory": False,
    },
    "write_graphiti_episode": {
        "sink": "graphiti.episode",
        "route": "/api/graphiti/episode",
        "route_state": "candidate_route",
        "enforcement": "operator_gated_route",
        "mutates_memory": True,
    },
    "materialize_l2b": {
        "sink": "l2_b_graph",
        "route": "capability.route",
        "route_state": "operator_gated_route",
        "enforcement": "route_receipt",
        "mutates_memory": True,
    },
}


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
            "event_schema": "runtime_flow_delta_v1",
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


async def draft_workflow_plan(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert workbench capability nodes into a Plan awaiting HITL review."""
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    workflow_nodes, saved_workflow = _workflow_nodes_and_saved(body)
    workflow_id = str(body.get("workflow_id") or saved_workflow.get("workflow_id") or "")
    workflow = body.get("workflow") if isinstance(body.get("workflow"), dict) else {}
    title = str(
        body.get("title")
        or workflow.get("title")
        or saved_workflow.get("title")
        or workflow.get("name")
        or "Web Console workflow plan"
    ).strip()
    compatible_steps, skipped_nodes = _workflow_plan_steps(workflow_nodes)
    data: dict[str, Any] = {
        "title": title,
        "workflow_node_count": len(workflow_nodes),
        "compatible_step_count": len(compatible_steps),
        "source_workflow_id": workflow_id,
        "skipped_nodes": skipped_nodes,
        "steps": [
            {
                "step_id": step.step_id,
                "title": step.title,
                "expected_tool": step.expected_tool,
                "inputs": step.inputs,
                "depends_on": list(step.depends_on),
            }
            for step in compatible_steps
        ],
        "operator_required_for_execute": True,
        "would_create_plan": bool(compatible_steps),
        "result_contract": _workflow_result_contract(
            workflow_nodes,
            workflow_id=workflow_id,
            title=title,
        ),
    }
    if not compatible_steps:
        data["error"] = "no_plan_compatible_workflow_nodes"
        return _receipt(
            action="runtime.workflow.plan_draft",
            success=False,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data=data,
        )
    if dry_run or not operator_mode:
        data["apply_skipped_reason"] = "dry_run_or_operator_mode_missing"
        return _receipt(
            action="runtime.workflow.plan_draft",
            success=True,
            dry_run=dry_run,
            operator_mode=operator_mode,
            data=data,
        )

    try:
        proposal = PlanProposal(
            proposed_by="web_console.collaboration_flow",
            title=title,
            rationale=str(body.get("rationale") or "Imported from Runtime Flow capability workbench."),
            suggested_steps=tuple(compatible_steps),
            blocks_conversation=_body_bool(body.get("blocks_conversation"), False),
        )
        registry = get_plan_registry()
        plan = await registry.draft(proposal)
        await registry.submit_for_confirmation(plan.plan_id)
        data.update({
            "created_plan_id": plan.plan_id,
            "plan_state": _plan_state_value(plan),
            "pending_gate_id": f"plan:{plan.plan_id}",
            "staged_ref_id": getattr(plan, "staged_ref_id", ""),
            "blackboard_namespace": getattr(plan, "blackboard_namespace", ""),
            "created": True,
        })
        return _receipt(
            action="runtime.workflow.plan_draft",
            success=True,
            dry_run=False,
            operator_mode=True,
            data=data,
        )
    except Exception as exc:
        return _receipt(
            action="runtime.workflow.plan_draft",
            success=False,
            dry_run=False,
            operator_mode=True,
            data={**data, "created": False, "error": f"{type(exc).__name__}: {exc}"},
        )


async def draft_workflow_result_contract(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Preview result destinations for a Collaboration Flow draft.

    The contract is carried as Plan step input metadata, but Scheduler does not
    enforce chained result routing yet.
    """
    body = payload or {}
    workflow_nodes, saved_workflow = _workflow_nodes_and_saved(body)
    workflow_id = str(body.get("workflow_id") or saved_workflow.get("workflow_id") or "")
    workflow = body.get("workflow") if isinstance(body.get("workflow"), dict) else {}
    title = str(
        body.get("title")
        or workflow.get("title")
        or saved_workflow.get("title")
        or workflow.get("name")
        or "Runtime Flow result contract"
    ).strip()
    contract = _workflow_result_contract(
        workflow_nodes,
        workflow_id=workflow_id,
        title=title,
    )
    return _receipt(
        action="runtime.workflow.result_contract",
        success=bool(workflow_nodes),
        dry_run=True,
        operator_mode=False,
        data={
            "title": title,
            "workflow_id": workflow_id,
            "workflow_node_count": len(workflow_nodes),
            "result_contract": contract,
            "error": "" if workflow_nodes else "no_workflow_nodes",
        },
    )


async def run_workflow_draft(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Preview or run a saved Collaboration Flow workflow draft.

    This is intentionally a Web orchestration route. Trigger nodes keep using
    the DSG trigger bus, while Nanobot-compatible nodes keep using Plan/HITL.
    """
    body = payload or {}
    dry_run = _body_bool(body.get("dry_run"), True)
    operator_mode = _body_bool(body.get("operator_mode"), False)
    workflow_nodes, saved_workflow = _workflow_nodes_and_saved(body)
    workflow_id = str(body.get("workflow_id") or saved_workflow.get("workflow_id") or "")
    workflow = body.get("workflow") if isinstance(body.get("workflow"), dict) else {}
    title = str(
        body.get("title")
        or workflow.get("title")
        or saved_workflow.get("title")
        or workflow.get("name")
        or "Runtime Flow workflow run"
    ).strip()
    trigger_nodes = _trigger_workflow_nodes(workflow_nodes)
    compatible_steps, skipped_nodes = _workflow_plan_steps(workflow_nodes)
    result_contract = _workflow_result_contract(
        workflow_nodes,
        workflow_id=workflow_id,
        title=title,
    )
    trigger_receipts = []
    for node in trigger_nodes[:16]:
        trigger_receipts.append(await _execute_workflow_trigger_node(
            node,
            dry_run=dry_run,
            operator_mode=operator_mode,
        ))
    plan_receipt: dict[str, Any] | None = None
    if compatible_steps:
        plan_receipt = await draft_workflow_plan({
            "title": title,
            "workflow_id": workflow_id,
            "workflow_nodes": workflow_nodes,
            "dry_run": dry_run,
            "operator_mode": operator_mode,
            "rationale": str(body.get("rationale") or "Workflow run imported Nanobot-compatible nodes."),
        })
    data = {
        "title": title,
        "workflow_id": workflow_id,
        "workflow_node_count": len(workflow_nodes),
        "trigger_node_count": len(trigger_nodes),
        "plan_compatible_count": len(compatible_steps),
        "skipped_nodes": skipped_nodes,
        "trigger_receipts": trigger_receipts,
        "plan_receipt": plan_receipt,
        "result_contract": result_contract,
        "execution_model": {
            "web_orchestrated": True,
            "trigger_path": "/api/dsg/triggers/fire-event",
            "plan_path": "/api/runtime/workflow/plan-draft",
            "direct_scheduler_protocol": False,
            "operator_required_for_execute": True,
        },
    }
    success = bool(trigger_receipts or plan_receipt) and all(
        bool(row.get("success")) for row in trigger_receipts
    ) and (plan_receipt is None or bool(plan_receipt.get("success")))
    if not trigger_receipts and plan_receipt is None:
        data["error"] = "no_executable_workflow_nodes"
    return _receipt(
        action="runtime.workflow.run",
        success=success,
        dry_run=dry_run,
        operator_mode=operator_mode,
        data=data,
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


def _workflow_plan_steps(workflow_nodes: list[Any]) -> tuple[list[PlanStepProposal], list[dict[str, Any]]]:
    steps: list[PlanStepProposal] = []
    skipped: list[dict[str, Any]] = []
    previous_step_id = ""
    for idx, row in enumerate(workflow_nodes[:24]):
        if not isinstance(row, dict):
            skipped.append({"index": idx, "reason": "invalid_workflow_node"})
            continue
        capability = row.get("capability") if isinstance(row.get("capability"), dict) else row
        capability_id = str(capability.get("capability_id") or row.get("capability_id") or "").strip()
        task_type = str(capability.get("nanobot_task_type") or row.get("nanobot_task_type") or "").strip()
        if not task_type or not is_nanobot_task_type(task_type):
            skipped.append({
                "index": idx,
                "capability_id": capability_id,
                "reason": "not_nanobot_plan_compatible",
            })
            continue
        step_id = _safe_step_id(str(row.get("workflow_node_id") or capability_id or f"step_{idx + 1}"))
        inputs = {
            "source": "runtime_flow_workbench",
            "workflow_node_id": str(row.get("workflow_node_id") or ""),
            "capability_id": capability_id,
            "route": str(capability.get("route") or ""),
            "draft_route": str(capability.get("draft_route") or ""),
            "execution_policy": str(capability.get("execution_policy") or ""),
            "result_destinations": capability.get("result_destinations")
            if isinstance(capability.get("result_destinations"), list)
            else [],
            "result_contract_version": "workflow_result_contract_v1",
            "result_routes": _result_routes_for_capability(capability, row),
            "sample_payload": capability.get("sample_payload")
            if isinstance(capability.get("sample_payload"), dict)
            else {},
        }
        depends_on = (previous_step_id,) if previous_step_id else ()
        steps.append(PlanStepProposal(
            step_id=step_id,
            title=str(capability.get("title") or capability_id or f"Workflow step {idx + 1}"),
            expected_tool=task_type,
            inputs=inputs,
            depends_on=depends_on,
        ))
        previous_step_id = step_id
    return steps, skipped


def _workflow_result_contract(
    workflow_nodes: list[Any],
    *,
    workflow_id: str = "",
    title: str = "",
) -> dict[str, Any]:
    node_routes: list[dict[str, Any]] = []
    destination_counts: dict[str, int] = {}
    route_state_counts: dict[str, int] = {}
    for idx, row in enumerate(workflow_nodes[:48]):
        if not isinstance(row, dict):
            node_routes.append({
                "index": idx,
                "workflow_node_id": "",
                "capability_id": "",
                "kind": "",
                "result_routes": [],
                "error": "invalid_workflow_node",
            })
            continue
        capability = row.get("capability") if isinstance(row.get("capability"), dict) else row
        routes = _result_routes_for_capability(capability, row)
        for route in routes:
            destination = str(route.get("destination") or "")
            state = str(route.get("route_state") or "")
            destination_counts[destination] = destination_counts.get(destination, 0) + 1
            route_state_counts[state] = route_state_counts.get(state, 0) + 1
        node_routes.append({
            "index": idx,
            "workflow_node_id": str(row.get("workflow_node_id") or ""),
            "capability_id": str(capability.get("capability_id") or row.get("capability_id") or ""),
            "title": str(capability.get("title") or capability.get("capability_id") or ""),
            "kind": str(capability.get("kind") or ""),
            "plan_step_compatible": bool(capability.get("plan_step_compatible")),
            "nanobot_task_type": str(capability.get("nanobot_task_type") or ""),
            "result_routes": routes,
        })
    return {
        "schema": "workflow_result_contract_v1",
        "workflow_id": workflow_id,
        "title": title,
        "node_count": len(workflow_nodes),
        "node_routes": node_routes,
        "destination_counts": destination_counts,
        "route_state_counts": route_state_counts,
        "execution_model": {
            "web_only": True,
            "plan_step_input_carried": True,
            "scheduler_enforced": False,
            "autonomous_chaining": False,
            "operator_required_for_mutation": True,
        },
        "audit": {
            "core_candidate": "CORE-015",
            "durable_core_contract": False,
            "review_before_scheduler_enforcement": True,
        },
    }


def _result_routes_for_capability(
    capability: dict[str, Any],
    row: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    destinations = _result_destinations_for_capability(capability)
    routes: list[dict[str, Any]] = []
    for destination in destinations:
        policy = dict(_RESULT_ROUTE_POLICIES.get(destination, {
            "sink": "unknown",
            "route": "unknown",
            "route_state": "unknown",
            "enforcement": "metadata_only",
            "mutates_memory": False,
        }))
        route_hint = str(policy.get("route") or "")
        if route_hint == "capability.route":
            route_hint = str(capability.get("route") or "")
        elif route_hint == "capability.draft_route":
            route_hint = str(capability.get("draft_route") or capability.get("route") or "")
        route_state = str(policy.get("route_state") or "")
        if destination == "write_to_memory_draft" and not str(capability.get("draft_route") or capability.get("route") or ""):
            route_state = "metadata_only"
        if destination == "materialize_l2b" and not str(capability.get("route") or ""):
            route_state = "metadata_only"
        routes.append({
            "destination": destination,
            "sink": str(policy.get("sink") or ""),
            "route": route_hint,
            "route_state": route_state,
            "enforcement": str(policy.get("enforcement") or ""),
            "mutates_memory": bool(policy.get("mutates_memory")),
            "plan_step_input_carried": bool(capability.get("plan_step_compatible") or capability.get("nanobot_task_type")),
            "workflow_node_id": str((row or {}).get("workflow_node_id") or ""),
            "capability_id": str(capability.get("capability_id") or ""),
        })
    return routes


def _result_destinations_for_capability(capability: dict[str, Any]) -> list[str]:
    raw = capability.get("result_destinations")
    values = [str(item).strip() for item in raw] if isinstance(raw, list) else []
    out: list[str] = []
    seen: set[str] = set()
    for value in values or ["view_only"]:
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out[:12]


def _workflow_nodes_and_saved(body: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    workflow_nodes = _workflow_nodes_from_body(body)
    saved_workflow: dict[str, Any] = {}
    if not workflow_nodes and body.get("workflow_id"):
        from parrot.web_console.workflow_drafts import get_workflow_draft_record

        saved_workflow = get_workflow_draft_record(str(body.get("workflow_id") or "")) or {}
        nodes = saved_workflow.get("nodes")
        workflow_nodes = list(nodes) if isinstance(nodes, list) else []
    return workflow_nodes, saved_workflow


def _workflow_nodes_from_body(body: dict[str, Any]) -> list[Any]:
    """Accept both API-native and workflow-object draft shapes."""
    if isinstance(body.get("workflow_nodes"), list):
        return list(body["workflow_nodes"])
    workflow = body.get("workflow")
    if isinstance(workflow, dict) and isinstance(workflow.get("nodes"), list):
        return list(workflow["nodes"])
    return []


def _trigger_workflow_nodes(workflow_nodes: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in workflow_nodes:
        if not isinstance(row, dict):
            continue
        capability = row.get("capability") if isinstance(row.get("capability"), dict) else row
        if str(capability.get("kind") or "") == "trigger":
            rows.append(row)
    return rows


async def _execute_workflow_trigger_node(
    row: dict[str, Any],
    *,
    dry_run: bool,
    operator_mode: bool,
) -> dict[str, Any]:
    from parrot.web_console.memory_ops import draft_trigger_event, fire_trigger_event

    capability = row.get("capability") if isinstance(row.get("capability"), dict) else row
    sample_payload = capability.get("sample_payload") if isinstance(capability.get("sample_payload"), dict) else {}
    event = sample_payload.get("event") if isinstance(sample_payload.get("event"), dict) else {}
    if not event:
        event = {
            "type": "workflow_capability_fire",
            "kind": str(capability.get("trigger_name") or capability.get("capability_id") or "trigger"),
            "source": "runtime_flow_workbench",
        }
    event = {
        **event,
        "workflow_node_id": str(row.get("workflow_node_id") or ""),
        "workflow_capability_id": str(capability.get("capability_id") or ""),
    }
    body = {
        **sample_payload,
        "trigger_name": str(sample_payload.get("trigger_name") or capability.get("trigger_name") or ""),
        "event": event,
        "dry_run": dry_run,
        "operator_mode": operator_mode,
    }
    receipt = (
        await fire_trigger_event(body)
        if operator_mode and not dry_run
        else draft_trigger_event(body)
    )
    return {
        "workflow_node_id": str(row.get("workflow_node_id") or ""),
        "capability_id": str(capability.get("capability_id") or ""),
        "trigger_name": body["trigger_name"],
        "receipt": receipt,
        "success": bool(receipt.get("success")),
        "action": receipt.get("action"),
        "published": bool((receipt.get("data") or {}).get("published")) if isinstance(receipt.get("data"), dict) else False,
    }


def _safe_step_id(value: str) -> str:
    clean = "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")
    return (clean or f"step_{uuid.uuid4().hex[:6]}")[:48]


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
    "draft_workflow_plan",
    "draft_workflow_result_contract",
    "draft_human_gate_decision",
    "pending_human_gates",
    "run_workflow_draft",
]
