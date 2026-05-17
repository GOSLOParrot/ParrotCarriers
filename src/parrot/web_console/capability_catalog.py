"""Web-only capability catalog for the Runtime/Collaboration Flow workbench."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from parrot.scheduler.task_catalog import NANOBOT_TASK_TYPES

_RESULT_DESTINATIONS = [
    "view_only",
    "return_to_goslo",
    "return_to_app",
    "stage_to_intent_workspace",
    "write_to_memory_draft",
    "write_graphiti_episode",
    "materialize_l2b",
]

_INTERACTION_MODES: list[dict[str, Any]] = [
    {
        "id": "L0",
        "label": "record_only",
        "title": "L0 record only",
        "description": "Archive or audit without surfacing into GOSLO context.",
        "mutation_allowed": False,
        "requires_operator": False,
        "current_status": "implemented",
    },
    {
        "id": "L1",
        "label": "working_set",
        "title": "L1 working set",
        "description": "Keep selected refs/nodes/results in local working memory or L1.5/L2-B staging.",
        "mutation_allowed": True,
        "requires_operator": True,
        "current_status": "implemented",
    },
    {
        "id": "L2",
        "label": "blackboard_notice",
        "title": "L2 blackboard notice",
        "description": "Make the result readable to Scheduler/Plan/runtime surfaces without direct speech.",
        "mutation_allowed": False,
        "requires_operator": False,
        "current_status": "implemented",
    },
    {
        "id": "C3",
        "label": "context_notice",
        "title": "C3 context notice",
        "description": "Stage or return context that may affect the next GOSLO reply without interrupting.",
        "mutation_allowed": True,
        "requires_operator": True,
        "current_status": "implemented",
    },
    {
        "id": "C4",
        "label": "safe_turn_speech",
        "title": "C4 safe-turn speech",
        "description": "Future reviewed safe-turn speech; current workbench must not auto-speak.",
        "mutation_allowed": False,
        "requires_operator": True,
        "current_status": "future_policy",
    },
    {
        "id": "I0",
        "label": "interrupt",
        "title": "I0 interrupt",
        "description": "Future immediate interruption channel; not available to workflow capabilities today.",
        "mutation_allowed": False,
        "requires_operator": True,
        "current_status": "future_policy",
    },
]


def build_runtime_capability_catalog(
    *,
    q: str = "",
    kind: str = "",
    execution_policy: str = "",
    interaction_mode: str = "",
) -> dict[str, Any]:
    """Return searchable Web capability rows backed by existing BFF routes."""
    capabilities = _all_capabilities()
    capabilities = _filter_capabilities(
        capabilities,
        q=str(q or "").strip(),
        kind=str(kind or "").strip(),
        execution_policy=str(execution_policy or "").strip(),
        interaction_mode=str(interaction_mode or "").strip(),
    )
    return {
        "success": True,
        "action": "runtime.capabilities.catalog",
        "capabilities": capabilities,
        "groups": _groups(capabilities),
        "result_destinations": _RESULT_DESTINATIONS,
        "interaction_modes": _interaction_modes_with_counts(capabilities),
        "audit": {
            "web_only": True,
            "read_model": True,
            "shared_core_candidates": ["CORE-010", "CORE-011", "CORE-015"],
            "true_connection_standard": (
                "Rows must declare read_only, draft_only, operator_gated, "
                "nanobot_dispatch, external_oauth, ecs_proxy, or not_implemented."
            ),
            "workflow_draft_status": "catalog_first_slice",
        },
    }


def _all_capabilities() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_runtime_capabilities())
    rows.extend(_trigger_capabilities())
    rows.extend(_nanobot_capabilities())
    rows.extend(_graphiti_capabilities())
    rows.extend(_l2b_capabilities())
    rows.extend(_ref_capabilities())
    rows.extend(_source_capabilities())
    rows.extend(_evidence_capabilities())
    return rows


def _runtime_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "runtime.flow.snapshot",
            "Runtime Flow snapshot",
            "Read Intent/Plan/HITL/Scheduler/Nanobot/runtime lanes as a graph.",
            kind="runtime_read",
            route="/api/runtime/flow",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["runtime_operator", "intent_workspace", "plan_registry", "scheduler_nanobot"],
            tags=["status_notice", "plan_request"],
        ),
        _capability(
            "runtime.flow.stream",
            "Runtime Flow SSE",
            "Read-only EventSource stream over runtime flow deltas.",
            kind="runtime_read",
            route="/api/runtime/flow/stream",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["runtime_operator", "scheduler_nanobot"],
            tags=["status_notice"],
        ),
        _capability(
            "runtime.hitl.pending",
            "Plan HITL gates",
            "List pending Plan human gates for review.",
            kind="hitl_gate",
            route="/api/runtime/hitl/pending",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["plan_registry", "runtime_operator"],
            tags=["plan_request", "status_notice"],
        ),
        _capability(
            "runtime.hitl.apply_decision",
            "Apply Plan HITL decision",
            "Operator-gated approve/reject/revise/cancel/resume route for Plan gates.",
            kind="hitl_gate",
            route="/api/runtime/hitl/apply-decision",
            draft_route="/api/runtime/hitl/draft-decision",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["plan_registry", "runtime_operator"],
            tags=["plan_request"],
            result_destinations=["return_to_goslo", "view_only"],
        ),
        _capability(
            "runtime.workflow.plan_draft",
            "Workflow to Plan draft",
            "Convert inserted Nanobot-compatible workflow nodes into a Plan/HITL gate.",
            kind="workflow_template",
            route="/api/runtime/workflow/plan-draft",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["plan_registry", "scheduler_nanobot", "intent_workspace"],
            tags=["plan_request", "nanobot_task"],
            result_destinations=["stage_to_intent_workspace", "return_to_goslo", "view_only"],
        ),
        _capability(
            "runtime.workflow.result_contract",
            "Workflow result contract",
            "Preview where workflow node results can go before Scheduler enforces chained result routing.",
            kind="workflow_template",
            route="/api/runtime/workflow/result-contract",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["runtime_operator", "plan_registry", "scheduler_nanobot", "intent_workspace"],
            tags=["plan_request", "status_notice", "nanobot_task"],
            result_destinations=["view_only", "return_to_goslo", "stage_to_intent_workspace"],
            notes="Produces workflow_result_contract_v1 and carries it in Plan step inputs; Scheduler enforcement is future CORE-015 work.",
        ),
        _capability(
            "runtime.workflow.validate",
            "Workflow schema validate",
            "Validate and normalize workflow_schema_v1 artifacts with redaction before import or CLI use.",
            kind="workflow_template",
            route="/api/runtime/workflow/validate",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["runtime_operator", "plan_registry"],
            tags=["plan_request", "status_notice", "workflow_schema"],
            result_destinations=["view_only"],
            notes="Shared schema helper for Web import/export/diff and the later thin CLI.",
        ),
        _capability(
            "runtime.workflow.export",
            "Workflow artifact export",
            "Export a saved Web workflow draft as redacted workflow_schema_v1 JSON.",
            kind="workflow_template",
            route="/api/runtime/workflow/export",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["runtime_operator", "plan_registry"],
            tags=["plan_request", "status_notice", "workflow_schema"],
            result_destinations=["view_only"],
            notes="Credentials stay outside workflow JSON; secret-like fields are redacted.",
        ),
        _capability(
            "runtime.workflow.import_preview",
            "Workflow import diff preview",
            "Validate an imported workflow artifact and preview node/capability diffs before saving.",
            kind="workflow_template",
            route="/api/runtime/workflow/import-preview",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["runtime_operator", "plan_registry"],
            tags=["plan_request", "status_notice", "workflow_schema"],
            result_destinations=["view_only"],
            notes="Non-mutating import preview. Persist through /api/runtime/workflows/drafts only after operator review.",
        ),
        _capability(
            "runtime.workflow.result_intake",
            "Workflow result intake",
            "Consume a workflow result payload against workflow_result_contract_v1 and stage reviewed results to IntentWorkspace.",
            kind="workflow_result",
            route="/api/runtime/workflow/result-intake",
            method="GET/POST/DELETE",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["runtime_operator", "scheduler_nanobot", "intent_workspace"],
            tags=["workflow_result", "plan_result", "intent_workspace"],
            result_destinations=["view_only", "stage_to_intent_workspace", "return_to_goslo"],
            notes="CFW-14 Web-only intake; only IntentWorkspace staging mutates today, Graphiti/L2-B destinations stay blocked; delete is smoke/operator cleanup.",
        ),
        _capability(
            "runtime.workflow.run",
            "Run workflow draft",
            "Preview or run a workflow by splitting trigger nodes to DSG trigger bus and Nanobot-compatible nodes to Plan/HITL.",
            kind="workflow_template",
            route="/api/runtime/workflow/run",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["runtime_operator", "plan_registry", "scheduler_nanobot"],
            tags=["plan_request", "nanobot_task", "status_notice"],
            result_destinations=["stage_to_intent_workspace", "return_to_goslo", "view_only"],
            notes="Web orchestration route; does not define a shared Scheduler workflow protocol.",
        ),
        _capability(
            "runtime.workflow.action_gates",
            "Workflow action gates",
            "Create durable Web-only gates for trigger/message workflow actions before operator execution.",
            kind="hitl_gate",
            route="/api/runtime/workflow/action-gates",
            method="GET/POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["runtime_operator", "scheduler_nanobot", "google_message"],
            tags=["plan_request", "status_notice", "google_message"],
            result_destinations=["view_only", "return_to_goslo"],
            notes="CFW-12 first slice; separate from Plan HITL and not a shared App DTO.",
        ),
        _capability(
            "runtime.workflow_drafts.registry",
            "Workflow draft registry",
            "Save, list, reload, and delete Web-only Collaboration Flow workflow drafts.",
            kind="workflow_template",
            route="/api/runtime/workflows/drafts",
            method="GET/POST/DELETE",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["runtime_operator", "plan_registry"],
            tags=["plan_request", "status_notice"],
            result_destinations=["view_only", "return_to_goslo"],
            notes="Durable Web draft storage only; not a shared Scheduler protocol.",
        ),
    ]


def _trigger_capabilities() -> list[dict[str, Any]]:
    from parrot.web_console.memory_ops import trigger_catalog

    catalog = trigger_catalog()
    rows: list[dict[str, Any]] = []
    for trigger in catalog.get("triggers", []):
        if not isinstance(trigger, dict):
            continue
        name = str(trigger.get("name") or "unknown_trigger").strip()
        event_hints = [
            hint for hint in trigger.get("event_hints", [])
            if isinstance(hint, dict)
        ]
        sample_event = event_hints[0] if event_hints else {
            "type": "workflow_capability_fire",
            "kind": name,
            "source": "runtime_flow_workbench",
        }
        rows.append(_capability(
            f"trigger.{name}",
            f"Trigger: {name}",
            "Draft or publish a DSG trigger event through the existing trigger bus route.",
            kind="trigger",
            route="/api/dsg/triggers/fire-event",
            draft_route="/api/dsg/triggers/draft-event",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            ascent_channels=_strings(trigger.get("ascending_channels")),
            modules=_strings(trigger.get("interaction_modules")),
            tags=_strings(trigger.get("information_tags")),
            trigger_name=name,
            fire_kinds=_strings(trigger.get("kinds")),
            sample_payload={
                "trigger_name": name,
                "event": sample_event,
                "dry_run": True,
                "operator_mode": False,
            },
            result_destinations=["stage_to_intent_workspace", "return_to_goslo", "view_only"],
            notes="Real publish requires operator_mode=true and dry_run=false.",
        ))
    return rows


def _nanobot_capabilities() -> list[dict[str, Any]]:
    route_by_task = {
        "calendar_fetch": "/api/google/calendar/nanobot-fetch",
        "message_check": "/api/google/messages/check",
        "ref_scan": "/api/memory/identity-ref-index/ref-scan-dispatch",
    }
    tags_by_task = {
        "calendar_fetch": ["calendar_event", "provider_identity"],
        "message_check": ["google_message", "provider_identity"],
        "ref_scan": ["staged_ref", "provider_identity"],
        "memory_consolidation": ["archive_request", "graphiti_context"],
        "research": ["plan_request"],
        "summarize": ["plan_request"],
        "remind": ["plan_request"],
        "vocabulary_learn": ["plan_request"],
    }
    rows: list[dict[str, Any]] = []
    for task_type in sorted(NANOBOT_TASK_TYPES):
        route = route_by_task.get(task_type)
        rows.append(_capability(
            f"nanobot.{task_type}",
            f"Nanobot task: {task_type}",
            "Scheduler/Nanobot-compatible task type usable by Plan steps.",
            kind="nanobot_task",
            route=route or "PlanRegistry/Scheduler dispatch",
            method="POST" if route else "INTERNAL",
            execution_policy="nanobot_dispatch" if route else "draft_only",
            true_connection_state="nanobot_dispatch" if route else "draft_route",
            modules=["scheduler_nanobot", "plan_registry"],
            tags=tags_by_task.get(task_type, ["nanobot_task"]),
            plan_step_compatible=True,
            nanobot_task_type=task_type,
            result_destinations=["return_to_goslo", "stage_to_intent_workspace", "view_only"],
            notes="Plan dispatch validates this against parrot.scheduler.task_catalog.NANOBOT_TASK_TYPES.",
        ))
    return rows


def _graphiti_capabilities() -> list[dict[str, Any]]:
    common = {
        "modules": ["graphiti", "l2_b_graph", "intent_workspace"],
        "tags": ["graphiti_context", "provider_identity"],
    }
    return [
        _capability(
            "graphiti.status",
            "Graphiti status",
            "Read local or ECS-proxied Graphiti status and partition list.",
            kind="graphiti_search",
            route="/api/graphiti/status",
            method="GET",
            execution_policy="read_only",
            true_connection_state="ecs_proxy",
            **common,
        ),
        _capability(
            "graphiti.subgraph.search",
            "Graphiti subgraph search",
            "Natural-language Graphiti search with strategy/SearchConfig fields and bundle preservation.",
            kind="graphiti_search",
            route="/api/graphiti/subgraph/search",
            method="POST",
            execution_policy="ecs_proxy",
            true_connection_state="ecs_proxy",
            result_destinations=["stage_to_intent_workspace", "materialize_l2b", "view_only"],
            **common,
        ),
        _capability(
            "graphiti.lookup",
            "Graphiti UUID lookup",
            "Lookup Graphiti fact/entity/episode UUIDs for raw payload enrichment.",
            kind="graphiti_search",
            route="/api/graphiti/lookup",
            method="POST",
            execution_policy="ecs_proxy",
            true_connection_state="ecs_proxy",
            **common,
        ),
        _capability(
            "graphiti.materialize_l2b",
            "Graphiti bundle to L2-B",
            "Operator-gated materialization of preserved Graphiti bundle pointers into L2-B.",
            kind="graphiti_search",
            route="/api/graphiti/subgraph/materialize-l2b",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            result_destinations=["materialize_l2b", "write_to_memory_draft", "view_only"],
            **common,
        ),
    ]


def _l2b_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "l2b.node.apply",
            "L2-B node apply",
            "Operator-gated semantic node create/update in the L2-B runtime graph.",
            kind="l2b_graph_op",
            route="/api/l2b/node",
            draft_route="/api/l2b/node/draft",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["l2_b_graph", "l1_5_pool"],
            tags=["l15_observation", "staged_ref"],
            result_destinations=["write_to_memory_draft", "view_only"],
        ),
        _capability(
            "l2b.edge.apply",
            "L2-B edge apply",
            "Operator-gated semantic edge create/update in the L2-B runtime graph.",
            kind="l2b_graph_op",
            route="/api/l2b/edge",
            draft_route="/api/l2b/edge/draft",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["l2_b_graph"],
            tags=["staged_ref", "graphiti_context"],
            result_destinations=["write_to_memory_draft", "view_only"],
        ),
        _capability(
            "l2b.subgraph.context",
            "L2-B subgraph context",
            "Read a bounded L2-B subgraph by stable node UUIDs.",
            kind="l2b_graph_op",
            route="/api/l2b/subgraphs/context",
            method="POST",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["l2_b_graph"],
            tags=["graphiti_context", "staged_ref"],
            result_destinations=["return_to_goslo", "view_only"],
        ),
        _capability(
            "l2b.transforms.draft",
            "L2-B transform draft",
            "Preview graph transform/rewrite policy without mutating L2-B.",
            kind="l2b_graph_op",
            route="/api/l2b/transforms/draft",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["l2_b_graph"],
            tags=["graphiti_context"],
        ),
    ]


def _ref_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "refs.identity.index",
            "IdentityRefIndex",
            "Read canonical UUID, Graphiti UUID, L2-B UUID, and external ref bindings.",
            kind="ref_op",
            route="/api/memory/identity-ref-index",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["l2_b_graph", "graphiti", "runtime_operator"],
            tags=["staged_ref", "provider_identity"],
        ),
        _capability(
            "refs.ref_scan.dispatch",
            "Ref scan dispatch",
            "Operator-gated read-only ref health scan through Scheduler/Nanobot.",
            kind="ref_op",
            route="/api/memory/identity-ref-index/ref-scan-dispatch",
            draft_route="/api/memory/identity-ref-index/ref-scan-plan",
            method="POST",
            execution_policy="nanobot_dispatch",
            true_connection_state="nanobot_dispatch",
            modules=["scheduler_nanobot", "graphiti", "l2_b_graph"],
            tags=["staged_ref", "provider_identity", "nanobot_task"],
            plan_step_compatible=True,
            nanobot_task_type="ref_scan",
            result_destinations=["stage_to_intent_workspace", "view_only"],
        ),
        _capability(
            "refs.graphiti.edge_apply",
            "Resolved Graphiti edge to L2-B",
            "Operator-gated materialization of already-resolved Graphiti facts as L2-B edges.",
            kind="ref_op",
            route="/api/memory/identity-ref-index/apply-graphiti-edge",
            draft_route="/api/memory/identity-ref-index/resolve-graphiti",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["graphiti", "l2_b_graph"],
            tags=["graphiti_context", "staged_ref"],
            result_destinations=["materialize_l2b", "view_only"],
        ),
    ]


def _source_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "source.google_calendar.nanobot_fetch",
            "Google Calendar Nanobot fetch",
            "Fetch Google Calendar through the Scheduler/Nanobot/OAuth path.",
            kind="source_import",
            route="/api/google/calendar/nanobot-fetch",
            method="POST",
            execution_policy="external_oauth",
            true_connection_state="nanobot_dispatch",
            modules=["google_calendar", "scheduler_nanobot", "l1_5_pool"],
            tags=["calendar_event", "provider_identity"],
            plan_step_compatible=True,
            nanobot_task_type="calendar_fetch",
            result_destinations=["stage_to_intent_workspace", "return_to_goslo", "view_only"],
        ),
        _capability(
            "source.google_calendar.import",
            "Google Calendar import",
            "Operator-gated Calendar event import to L1.5/L2-B source path.",
            kind="source_import",
            route="/api/google/calendar/import",
            draft_route="/api/google/calendar/import-plan",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["google_calendar", "l1_5_pool", "l2_b_graph"],
            tags=["calendar_event", "l15_observation"],
            result_destinations=["write_to_memory_draft", "view_only"],
        ),
        _capability(
            "source.obsidian.import_plan",
            "Obsidian import plan",
            "Preview/import Obsidian notes into L1.5/L2-B source path.",
            kind="source_import",
            route="/api/l15/obsidian-vault/import-plan",
            draft_route="/api/l15/obsidian-vault/import-draft",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["obsidian", "l1_5_pool", "l2_b_graph"],
            tags=["obsidian_note", "l15_observation"],
            result_destinations=["write_to_memory_draft", "view_only"],
        ),
    ]


def _evidence_capabilities() -> list[dict[str, Any]]:
    return [
        _capability(
            "evidence.status",
            "Evidence status",
            "Read frame/photo/evidence freshness and awareness notices.",
            kind="evidence_op",
            route="/api/vision/evidence/status",
            method="GET",
            execution_policy="read_only",
            true_connection_state="read_only_live",
            modules=["intent_workspace", "runtime_operator"],
            tags=["scene_context", "status_notice"],
        ),
        _capability(
            "evidence.stage_hint",
            "Stage evidence hint",
            "Stage visual evidence as a C3/context hint without direct L2-B write.",
            kind="evidence_op",
            route="/api/vision/evidence/stage-hint",
            method="POST",
            execution_policy="operator_gated",
            true_connection_state="operator_gated_write",
            modules=["intent_workspace", "l1_5_pool"],
            tags=["scene_context", "staged_ref"],
            result_destinations=["stage_to_intent_workspace", "return_to_goslo", "view_only"],
        ),
        _capability(
            "evidence.memory_draft",
            "Evidence memory draft",
            "Preview evidence promotion into L1.5/Ref/L2-B without apply route.",
            kind="evidence_op",
            route="/api/vision/evidence/memory-draft",
            method="POST",
            execution_policy="draft_only",
            true_connection_state="draft_route",
            modules=["l1_5_pool", "l2_b_graph"],
            tags=["scene_context", "staged_ref"],
        ),
    ]


def _capability(
    capability_id: str,
    title: str,
    description: str,
    *,
    kind: str,
    route: str,
    method: str,
    execution_policy: str,
    true_connection_state: str,
    draft_route: str = "",
    ascent_channels: list[str] | None = None,
    modules: list[str] | None = None,
    tags: list[str] | None = None,
    trigger_name: str = "",
    fire_kinds: list[str] | None = None,
    sample_payload: dict[str, Any] | None = None,
    plan_step_compatible: bool = False,
    nanobot_task_type: str = "",
    result_destinations: list[str] | None = None,
    interaction_modes: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    destinations = result_destinations or ["view_only"]
    mode_ids = _normalize_interaction_modes(
        interaction_modes
        or _infer_interaction_modes(
            kind=kind,
            execution_policy=execution_policy,
            modules=modules or [],
            tags=tags or [],
            result_destinations=destinations,
        )
    )
    return {
        "capability_id": capability_id,
        "title": title,
        "description": description,
        "kind": kind,
        "route": route,
        "draft_route": draft_route,
        "method": method,
        "execution_policy": execution_policy,
        "ascent_channels": ascent_channels or [],
        "interaction_modules": modules or [],
        "information_tags": tags or [],
        "trigger_name": trigger_name,
        "fire_kinds": fire_kinds or [],
        "sample_payload": sample_payload or {},
        "plan_step_compatible": bool(plan_step_compatible),
        "nanobot_task_type": nanobot_task_type,
        "result_destinations": destinations,
        "interaction_modes": mode_ids,
        "true_connection": {
            "state": true_connection_state,
            "proof_route": route,
            "draft_route": draft_route,
        },
        "notes": notes,
    }


def _filter_capabilities(
    capabilities: list[dict[str, Any]],
    *,
    q: str,
    kind: str,
    execution_policy: str,
    interaction_mode: str,
) -> list[dict[str, Any]]:
    if kind:
        capabilities = [
            row for row in capabilities
            if str(row.get("kind") or "") == kind
        ]
    if execution_policy:
        capabilities = [
            row for row in capabilities
            if str(row.get("execution_policy") or "") == execution_policy
        ]
    if interaction_mode:
        mode = _interaction_mode_id(interaction_mode)
        capabilities = [
            row for row in capabilities
            if mode in _strings(row.get("interaction_modes"))
        ]
    if q:
        needle = q.casefold()
        capabilities = [
            row for row in capabilities
            if needle in _search_blob(row)
        ]
    return capabilities


def _groups(capabilities: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, dict[str, int]] = {
        "kind": defaultdict(int),
        "execution_policy": defaultdict(int),
        "ascent_channel": defaultdict(int),
        "interaction_module": defaultdict(int),
        "information_tag": defaultdict(int),
        "interaction_mode": defaultdict(int),
    }
    for row in capabilities:
        grouped["kind"][str(row.get("kind") or "unknown")] += 1
        grouped["execution_policy"][str(row.get("execution_policy") or "unknown")] += 1
        for value in _strings(row.get("interaction_modes")):
            grouped["interaction_mode"][value] += 1
        for value in _strings(row.get("ascent_channels")):
            grouped["ascent_channel"][value] += 1
        for value in _strings(row.get("interaction_modules")):
            grouped["interaction_module"][value] += 1
        for value in _strings(row.get("information_tags")):
            grouped["information_tag"][value] += 1
    return {
        group: [
            {"id": key, "count": count}
            for key, count in sorted(values.items())
        ]
        for group, values in grouped.items()
    }


def _search_blob(row: dict[str, Any]) -> str:
    values: list[str] = []
    for key in (
        "capability_id",
        "title",
        "description",
        "kind",
        "route",
        "draft_route",
        "execution_policy",
        "trigger_name",
        "nanobot_task_type",
        "notes",
    ):
        values.append(str(row.get(key) or ""))
    values.extend(_strings(row.get("ascent_channels")))
    values.extend(_strings(row.get("interaction_modules")))
    values.extend(_strings(row.get("interaction_modes")))
    values.extend(_strings(row.get("information_tags")))
    values.extend(_strings(row.get("result_destinations")))
    values.extend(_strings(row.get("fire_kinds")))
    return " ".join(values).casefold()


def _infer_interaction_modes(
    *,
    kind: str,
    execution_policy: str,
    modules: list[str],
    tags: list[str],
    result_destinations: list[str],
) -> list[str]:
    """Map capability metadata to the stable L0/L1/L2/C3/C4/I0 policy ladder."""
    values = set(modules) | set(tags) | set(result_destinations)
    modes: list[str] = []
    if execution_policy in {"read_only", "draft_only"} or kind == "runtime_read":
        modes.append("L0")
    if values & {"write_to_memory_draft", "materialize_l2b", "l1_5_pool", "l2_b_graph", "staged_ref"}:
        modes.append("L1")
    if values & {"scheduler_nanobot", "plan_registry", "status_notice", "plan_request", "nanobot_task"}:
        modes.append("L2")
    if values & {"return_to_goslo", "stage_to_intent_workspace"}:
        modes.append("C3")
    return modes or ["L0"]


def _interaction_modes_with_counts(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = defaultdict(int)
    for row in capabilities:
        for mode in _strings(row.get("interaction_modes")):
            counts[mode] += 1
    return [
        {**mode, "count": counts[str(mode["id"])]}
        for mode in _INTERACTION_MODES
    ]


def _normalize_interaction_modes(values: list[str]) -> list[str]:
    known = {str(mode["id"]).casefold(): str(mode["id"]) for mode in _INTERACTION_MODES}
    known.update({str(mode["label"]).casefold(): str(mode["id"]) for mode in _INTERACTION_MODES})
    result: list[str] = []
    for raw in values:
        mode = _interaction_mode_id(raw)
        if mode in known.values() and mode not in result:
            result.append(mode)
    return result or ["L0"]


def _interaction_mode_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    folded = raw.casefold()
    for mode in _INTERACTION_MODES:
        if folded in {str(mode["id"]).casefold(), str(mode["label"]).casefold()}:
            return str(mode["id"])
    return raw.upper()


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item or "").strip()]


__all__ = ["build_runtime_capability_catalog"]
