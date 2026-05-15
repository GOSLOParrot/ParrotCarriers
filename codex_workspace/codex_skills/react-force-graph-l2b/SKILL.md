---
name: react-force-graph-l2b
description: Use when building or reviewing the Web Console full-screen L2-B realtime graph monitor, React-Force-Graph renderer adapter, Obsidian-like graph filters/groups/local graph behavior, trigger/attention animations, or graph-engine switching between React Flow and force/canvas renderers.
metadata:
  owner: web-console
  status: draft
  category: frontend-graph-renderer
  scope: Web Console L2-B realtime graph monitor and renderer adapter only
  source: user requirements 2026-05-15; React-Force-Graph, React Flow, Obsidian Graph View, D3 force docs
---

# React-Force-Graph L2-B Skill

Use this skill after the Parrot DSG skills have already been read for data
semantics. This skill only covers the Web renderer and interaction pattern for
the full-screen L2-B monitor.

## Boundaries

- Keep React Flow for editable canvases: Memory operation canvas, Runtime Flow
  workflow/HITL workspace, ComfyUI-like Plan/Nanobot lanes.
- Use React-Force-Graph first for the full-screen L2-B realtime monitor:
  topology, cluster/filter views, selected-node focus, trigger/attention
  animation, Graphiti-search subgraphs, and high-volume canvas rendering.
- Do not use the full-screen L2-B monitor for detailed Ref-file management,
  Plan editing, Nanobot task workflow, or IntentWorkspace workflow edits.
- IntentWorkspace is a GOSLO Intent-layer workspace. If a UI action needs to
  guide or edit IntentWorkspace, route it through GOSLO Intent/task/workspace
  file/Plan-edit flows. Do not pretend that direct L2-B graph mutation edits
  the IntentWorkspace.
- L1.5 remains the default safe write path; direct graph writes stay dry-run or
  operator-gated with receipts.

## Reference URLs

- React-Force-Graph repository and API:
  https://github.com/vasturiano/react-force-graph
- React-Force-Graph examples directory:
  https://github.com/vasturiano/react-force-graph/tree/master/example
- React-Force-Graph large graph example:
  https://vasturiano.github.io/react-force-graph/example/large-graph/
- React Flow handles and loose connection mode:
  https://reactflow.dev/learn/customization/handles
- React Flow ConnectionMode reference:
  https://reactflow.dev/api-reference/types/connection-mode
- Obsidian Graph View help:
  https://obsidian.md/help/plugins/graph
- D3 force simulation reference:
  https://d3js.org/d3-force

## 2026-05-15 Source Notes

- React-Force-Graph consumes `{ nodes, links }`; node identity defaults to `id`,
  and link endpoints default to `source` / `target`. Keep backend/Web read
  models on stable L2-B UUIDs so renderer engines can be swapped.
- React-Force-Graph 2D supports `nodeCanvasObject` for custom canvas node
  painting, `nodeVal` / `nodeColor` / `nodeLabel`, link labels, link width,
  directional arrows/particles, hover/click/drag callbacks, `centerAt`,
  `zoom`, `d3Force`, and `d3ReheatSimulation`.
- React Flow remains the better editor/workflow tool. Its `ConnectionMode`
  `Loose` allows source-to-source style connections, but target-to-target is
  still not the intended interaction; use directional handles when exact side
  attachment matters.
- Obsidian Graph View's durable product pattern is not "show every field":
  global graph plus filters, colored groups, display toggles, force sliders,
  and local graph depth. Use that pattern for L2-B monitor overlays.

## Renderer Adapter Pattern

Create a component boundary before adding a second graph engine:

- `GraphRendererAdapter` selects `react_flow_editor`, `force_graph_2d`, or a
  future engine by props/config.
- `L2BForceGraphView` owns React-Force-Graph rendering, force tuning,
  interaction callbacks, and animation overlays.
- `L2BGraphOverlay` owns React `<div>` controls outside the canvas: search,
  filters, group toggles, selected-node drawer, status chips, and receipts.
- `useRealtimeGraphStream` owns polling/SSE/WebSocket reconnection and converts
  backend events into graph patches.

Keep route/API shape engine-agnostic:

- Nodes use stable L2-B business UUIDs, not renderer indices.
- Links use stable source/target ids and carry `edge_kind`, source bucket,
  provenance/ref ids, and optional visual fields.
- Renderer-only fields such as color, pulse, particle count, and camera target
  stay in Web view state unless promoted through a core candidate.

Repo-local starter:

- `web/console_app/src/graphModel.ts` converts `/api/app/live-state` L2-B
  snapshots into an engine-neutral `L2BRenderableGraph`. It is intentionally
  dependency-free and can feed React Flow today or React-Force-Graph later.

## Interaction Pattern

Start with these operations:

- Click node: select, focus drawer, show source bucket/ref/Graphiti links.
- Double-click node: expand ego graph / bounded neighborhood.
- Search: Graphiti natural-language search can load a bounded subgraph slice.
- Filter: bucket/source/kind/attention/stale/ref-bound/trigger-recent.
- Group: Obsidian-like colored groups based on search terms or source buckets.
- Local graph: selected node plus depth slider.
- Trigger animation: use directional particles/pulses on links and node rings.
- Attention animation: map salience/activation/decay to size, opacity, glow, or
  temporary particles without changing core semantics.

## Implementation Checklist

Before code:

- Re-read `dsg-rustworkx-master`, `dsg-l2b-node-organization-options`, and
  `graphiti`.
- If attention/decay/memory-validity fields change, read
  `dsg-attention-schema-papers`.
- Update `APP_WEB_PARALLEL_TODOLIST_20260513.md` and the Memory business file.

During code:

- Keep the first route/page full-screen and visually quiet; avoid dense form
  panels in the graph viewport.
- Keep right/left panels collapsible overlays, not permanent clutter.
- Use canvas/WebGL graph for the monitor, ordinary React panels for controls
  and drawers.
- Add comments only where the graph stream/patching/adapter logic is not
  obvious.

After code:

- Run frontend typecheck/build and browser smoke.
- Check console errors, graph nonblank state, interaction callbacks, zh/en text,
  and secret non-leak.
- Update the TODO, Memory business file, `_tmp` ledger, and core candidate
  queue only for real shared gaps.
