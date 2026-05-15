import type { LiveState } from "./types";

export type GraphEngineId = "react_flow_editor" | "force_graph_2d" | "future_dense_graph";

export type L2BVisualState =
  | "confirmed"
  | "tentative"
  | "uncertain"
  | "alert"
  | "ghost"
  | "default";

export type L2BGraphNode = {
  id: string;
  label: string;
  kind: string;
  group: string;
  source: string;
  bucket_id: string;
  event_id: string;
  scene_type: string;
  location_tag: string;
  salience: string;
  confirmation: string;
  attention: number;
  novelty: number;
  evidence_score: number;
  visual_state: L2BVisualState;
  tags: string[];
  raw: Record<string, unknown>;
};

export type L2BGraphLink = {
  id: string;
  source: string;
  target: string;
  kind: string;
  group: string;
  strength: number;
  edge_source: string;
  cross_compartment: string;
  created_at: number;
  raw: Record<string, unknown>;
};

export type L2BRenderableGraph = {
  engine_hint: GraphEngineId;
  sequence: number;
  generated_at: number;
  node_count: number;
  edge_count: number;
  nodes: L2BGraphNode[];
  links: L2BGraphLink[];
  groups: string[];
};

export type L2BGraphFilter = {
  kind?: string;
  source?: string;
  bucket_id?: string;
  event_id?: string;
  min_attention?: number;
  require_ref_bound?: boolean;
};

export function buildL2BRenderableGraph(
  liveState: LiveState,
  filter: L2BGraphFilter = {},
  engineHint: GraphEngineId = "force_graph_2d",
): L2BRenderableGraph {
  const snapshot = liveState.l2b ?? {};
  const nodes = asRows(snapshot.nodes).map(toGraphNode).filter((node) => nodeMatchesFilter(node, filter));
  const visibleIds = new Set(nodes.map((node) => node.id));
  const links = asRows(snapshot.edges)
    .map(toGraphLink)
    .filter((link) => visibleIds.has(link.source) && visibleIds.has(link.target));
  const groups = Array.from(new Set(nodes.map((node) => node.group).filter(Boolean))).sort();

  return {
    engine_hint: engineHint,
    sequence: numberValue(liveState.sequence),
    generated_at: numberValue(liveState.generated_at),
    node_count: numberValue(snapshot.node_count, nodes.length),
    edge_count: numberValue(snapshot.edge_count, links.length),
    nodes,
    links,
    groups,
  };
}

export function nodeVisualState(row: Record<string, unknown>): L2BVisualState {
  const salience = stringValue(row.salience).toLowerCase();
  const confirmation = stringValue(row.confirmation).toLowerCase();
  if (salience === "alert") return "alert";
  if (confirmation === "confirmed") return "confirmed";
  if (confirmation === "tentative" || confirmation === "expected") return "tentative";
  if (confirmation === "uncertain") return "uncertain";
  if (confirmation === "ghost") return "ghost";
  return "default";
}

export function nodeGroupKey(row: Record<string, unknown>): string {
  return (
    stringValue(row.bucket_id)
    || stringValue(row.source)
    || stringValue(row.kind)
    || "unclassified"
  );
}

function toGraphNode(row: Record<string, unknown>): L2BGraphNode {
  const uuid = stringValue(row.uuid) || stringValue(row.id);
  return {
    id: uuid,
    label: stringValue(row.label) || uuid || "L2-B Node",
    kind: stringValue(row.kind) || "object",
    group: nodeGroupKey(row),
    source: stringValue(row.source),
    bucket_id: stringValue(row.bucket_id) || "main",
    event_id: stringValue(row.event_id),
    scene_type: stringValue(row.scene_type),
    location_tag: stringValue(row.location_tag),
    salience: stringValue(row.salience) || "background",
    confirmation: stringValue(row.confirmation) || "expected",
    attention: numberValue(row.attention),
    novelty: numberValue(row.novelty),
    evidence_score: numberValue(row.evidence_score),
    visual_state: nodeVisualState(row),
    tags: stringList(row.tags),
    raw: row,
  };
}

function toGraphLink(row: Record<string, unknown>): L2BGraphLink {
  const source = stringValue(row.source);
  const target = stringValue(row.target);
  const kind = stringValue(row.kind) || "associated_with";
  const edgeSource = stringValue(row.edge_source);
  return {
    id: `${source}->${target}:${kind}:${edgeSource}:${numberValue(row.created_at)}`,
    source,
    target,
    kind,
    group: kind,
    strength: numberValue(row.strength, 0.5),
    edge_source: edgeSource,
    cross_compartment: stringValue(row.cross_compartment),
    created_at: numberValue(row.created_at),
    raw: row,
  };
}

function nodeMatchesFilter(node: L2BGraphNode, filter: L2BGraphFilter): boolean {
  if (filter.kind && filter.kind !== "all" && node.kind !== filter.kind) return false;
  if (filter.source && filter.source !== "all" && node.source !== filter.source) return false;
  if (filter.bucket_id && filter.bucket_id !== "all" && node.bucket_id !== filter.bucket_id) return false;
  if (filter.event_id && filter.event_id !== "all" && node.event_id !== filter.event_id) return false;
  if (filter.min_attention !== undefined && node.attention < filter.min_attention) return false;
  if (filter.require_ref_bound && !hasRefBinding(node.raw)) return false;
  return true;
}

function hasRefBinding(row: Record<string, unknown>): boolean {
  const meta = row.meta;
  const sourceMeta = row.source_meta;
  if (isRecord(meta) && (meta.ref_id || meta.ref_path || meta.ref_uuid)) return true;
  if (isRecord(sourceMeta) && (sourceMeta.ref_id || sourceMeta.ref_path || sourceMeta.ref_uuid)) return true;
  return Boolean(row.reference_image_path || row.last_sighting_path || row.graphiti_uuid || row.obsidian_uuid);
}

function asRows(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((row): row is Record<string, unknown> => isRecord(row))
    : [];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function stringValue(value: unknown): string {
  return typeof value === "string" ? value : value === undefined || value === null ? "" : String(value);
}

function numberValue(value: unknown, fallback = 0): number {
  const numeric = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
}

function stringList(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(stringValue).filter(Boolean);
  if (typeof value === "string") return value.split(",").map((item) => item.trim()).filter(Boolean);
  return [];
}
